#!/usr/bin/env python3
"""Maintain the deployment host's Tailscale-only access catalog."""

from __future__ import annotations

import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import fcntl
import html
import ipaddress
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
from typing import Any, Iterator
from urllib.parse import urlsplit


MAX_FILE_BYTES = 2_000_000
MAX_SERVICES = 1_000
MAX_TEXT_LENGTH = 512
TAILSCALE_NETWORK = ipaddress.ip_network(".".join(("100", "64", "0", "0")) + "/10")


class CatalogError(Exception):
    """A safe, user-actionable catalog update failure."""


def _has_control(value: str) -> bool:
    return any(ord(character) < 32 or ord(character) == 127 for character in value)


def _validate_tailscale_ip(value: object) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_TEXT_LENGTH:
        raise CatalogError("invalid Tailscale IPv4")
    candidate = value.strip()
    if candidate != value or _has_control(candidate):
        raise CatalogError("invalid Tailscale IPv4")
    try:
        address = ipaddress.ip_address(candidate)
    except ValueError as exc:
        raise CatalogError("invalid Tailscale IPv4") from exc
    if address.version != 4 or address not in TAILSCALE_NETWORK:
        raise CatalogError("invalid Tailscale IPv4")
    return str(address)


def _discover_tailscale_ip() -> str:
    try:
        completed = subprocess.run(
            ["tailscale", "ip", "-4"],
            check=False,
            capture_output=True,
            text=True,
            timeout=5,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise CatalogError("cannot discover the local Tailscale IPv4") from exc
    if completed.returncode != 0:
        raise CatalogError("cannot discover the local Tailscale IPv4")
    lines = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
    if len(lines) != 1:
        raise CatalogError("local Tailscale IPv4 is ambiguous")
    return _validate_tailscale_ip(lines[0])


def _validate_service_name(value: object) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_TEXT_LENGTH:
        raise CatalogError("invalid service name")
    if value.strip() != value or _has_control(value):
        raise CatalogError("invalid service name")
    return value


def _validate_timestamp(value: object) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_TEXT_LENGTH:
        raise CatalogError("invalid catalog timestamp")
    if _has_control(value):
        raise CatalogError("invalid catalog timestamp")
    return value


def _validate_deployment_address(value: object, tailscale_ip: str) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_TEXT_LENGTH:
        raise CatalogError("invalid deployment address")
    if value.strip() != value or _has_control(value):
        raise CatalogError("invalid deployment address")
    try:
        parsed = urlsplit(value)
        scheme = parsed.scheme.lower()
        hostname = parsed.hostname
        port = parsed.port
    except ValueError as exc:
        raise CatalogError("invalid deployment address") from exc
    if scheme not in {"http", "https"} or not parsed.netloc:
        raise CatalogError("invalid deployment address")
    if parsed.username is not None or parsed.password is not None:
        raise CatalogError("deployment address cannot contain credentials")
    if parsed.query or parsed.fragment or hostname is None:
        raise CatalogError("deployment address must be a plain target URL")
    if port is not None and not 1 <= port <= 65535:
        raise CatalogError("invalid deployment address")
    try:
        host = ipaddress.ip_address(hostname)
    except ValueError as exc:
        raise CatalogError("deployment address must use the target Tailscale IP") from exc
    if host.version != 4 or str(host) != tailscale_ip:
        raise CatalogError("deployment address must use the target Tailscale IP")
    return value


def _now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _empty_registry(tailscale_ip: str) -> dict[str, Any]:
    return {"tailscale_ip": tailscale_ip, "updated_at": _now(), "services": []}


def _validate_registry(value: object, tailscale_ip: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise CatalogError("catalog registry is malformed")
    stored_ip = _validate_tailscale_ip(value.get("tailscale_ip"))
    if stored_ip != tailscale_ip:
        raise CatalogError("catalog belongs to a different Tailscale host")
    updated_at = _validate_timestamp(value.get("updated_at"))
    services = value.get("services")
    if not isinstance(services, list) or len(services) > MAX_SERVICES:
        raise CatalogError("catalog services are malformed")
    normalized: list[dict[str, str]] = []
    seen: set[str] = set()
    for service in services:
        if not isinstance(service, dict):
            raise CatalogError("catalog services are malformed")
        name = _validate_service_name(service.get("name"))
        address = _validate_deployment_address(service.get("address"), tailscale_ip)
        service_updated_at = _validate_timestamp(service.get("updated_at"))
        key = name.casefold()
        if key in seen:
            raise CatalogError("catalog contains duplicate services")
        seen.add(key)
        normalized.append(
            {"name": name, "address": address, "updated_at": service_updated_at}
        )
    normalized.sort(key=lambda item: item["name"].casefold())
    return {
        "tailscale_ip": tailscale_ip,
        "updated_at": updated_at,
        "services": normalized,
    }


def _load_registry(path: Path, tailscale_ip: str) -> dict[str, Any]:
    if not path.exists():
        return _empty_registry(tailscale_ip)
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            raise CatalogError("catalog registry is too large")
        value = json.loads(path.read_text(encoding="utf-8"))
    except CatalogError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CatalogError("catalog registry is unreadable") from exc
    return _validate_registry(value, tailscale_ip)


def _render_html(registry: dict[str, Any]) -> str:
    tailscale_ip = html.escape(registry["tailscale_ip"], quote=True)
    rows = registry["services"]
    if rows:
        rendered_rows = "\n".join(
            "        <tr>"
            f"<td>{html.escape(row['name'], quote=True)}</td>"
            f"<td><a href=\"{html.escape(row['address'], quote=True)}\">"
            f"{html.escape(row['address'], quote=True)}</a></td>"
            f"<td>{html.escape(row['updated_at'], quote=True)}</td>"
            "</tr>"
            for row in rows
        )
    else:
        rendered_rows = '        <tr><td colspan="3">No services recorded.</td></tr>'
    return (
        "<!doctype html>\n"
        '<html lang="en">\n'
        "  <head>\n"
        '    <meta charset="utf-8">\n'
        "    <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        "    <title>Deployment Access Catalog</title>\n"
        "  </head>\n"
        "  <body>\n"
        "    <main>\n"
        "      <h1>Deployment Access Catalog</h1>\n"
        f"      <p>Tailscale address: <code>{tailscale_ip}</code></p>\n"
        "      <table>\n"
        "        <thead><tr><th>Service</th><th>Deployment address</th>"
        "<th>Updated</th></tr></thead>\n"
        f"{rendered_rows}\n"
        "      </table>\n"
        "    </main>\n"
        "  </body>\n"
        "</html>\n"
    )


def _fsync_directory(directory: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(directory, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _file_mode(path: Path, default: int) -> int:
    try:
        return path.stat().st_mode & 0o777
    except OSError:
        return default


def _read_snapshot(path: Path) -> tuple[bool, bytes | None, int]:
    if not path.exists():
        return False, None, _file_mode(path, 0o644)
    try:
        if path.stat().st_size > MAX_FILE_BYTES:
            raise CatalogError("catalog file is too large")
        return True, path.read_bytes(), _file_mode(path, 0o644)
    except CatalogError:
        raise
    except (OSError, IOError) as exc:
        raise CatalogError("catalog file is unreadable") from exc


def _write_temp(directory: Path, basename: str, data: bytes, mode: int) -> Path:
    descriptor, name = tempfile.mkstemp(
        prefix=f".{basename}.", suffix=".tmp", dir=str(directory)
    )
    try:
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    finally:
        if descriptor != -1:
            os.close(descriptor)
    return Path(name)


def _restore_snapshot(
    path: Path, existed: bool, data: bytes | None, mode: int
) -> None:
    if not existed:
        try:
            path.unlink()
        except FileNotFoundError:
            pass
        _fsync_directory(path.parent)
        return
    if data is None:
        raise CatalogError("catalog restore data is unavailable")
    temporary = _write_temp(path.parent, path.name, data, mode)
    try:
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    finally:
        try:
            temporary.unlink()
        except FileNotFoundError:
            pass


def _write_catalog_files(
    registry_path: Path,
    output_path: Path,
    registry_data: bytes,
    html_data: bytes,
) -> None:
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    registry_existed, registry_old, registry_mode = _read_snapshot(registry_path)
    output_existed, output_old, output_mode = _read_snapshot(output_path)
    registry_temporary: Path | None = None
    output_temporary: Path | None = None
    registry_replaced = False
    output_replaced = False
    try:
        registry_temporary = _write_temp(
            registry_path.parent, registry_path.name, registry_data, 0o600
        )
        output_temporary = _write_temp(
            output_path.parent, output_path.name, html_data, output_mode
        )
        os.replace(registry_temporary, registry_path)
        registry_replaced = True
        registry_temporary = None
        _fsync_directory(registry_path.parent)
        os.replace(output_temporary, output_path)
        output_replaced = True
        output_temporary = None
        _fsync_directory(output_path.parent)
    except (OSError, IOError, CatalogError) as exc:
        try:
            if registry_replaced:
                _restore_snapshot(
                    registry_path, registry_existed, registry_old, registry_mode
                )
            if output_replaced:
                _restore_snapshot(output_path, output_existed, output_old, output_mode)
        except (OSError, IOError, CatalogError) as restore_exc:
            raise CatalogError("catalog update and restore both failed") from restore_exc
        raise CatalogError("catalog update failed") from exc
    finally:
        for temporary in (registry_temporary, output_temporary):
            if temporary is not None:
                try:
                    temporary.unlink()
                except FileNotFoundError:
                    pass


@contextmanager
def _catalog_lock(registry_path: Path) -> Iterator[None]:
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = registry_path.with_name(registry_path.name + ".lock")
    try:
        descriptor = os.open(lock_path, os.O_RDWR | os.O_CREAT, 0o600)
    except OSError as exc:
        raise CatalogError("cannot create the catalog lock") from exc
    try:
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    except OSError as exc:
        raise CatalogError("catalog lock failed") from exc
    finally:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def update_catalog(
    registry_path: Path,
    output_path: Path,
    *,
    tailscale_ip: str | None = None,
    service_name: str | None = None,
    deployment_address: str | None = None,
    initialize: bool = False,
) -> dict[str, Any]:
    registry_path = Path(registry_path)
    output_path = Path(output_path)
    if registry_path.resolve(strict=False) == output_path.resolve(strict=False):
        raise CatalogError("registry and HTML output must be different files")
    current_ip = (
        _discover_tailscale_ip()
        if tailscale_ip is None
        else _validate_tailscale_ip(tailscale_ip)
    )
    if initialize:
        if service_name is not None or deployment_address is not None:
            raise CatalogError("initialize cannot include a service update")
    elif service_name is None or deployment_address is None:
        raise CatalogError("service name and deployment address are required")
    else:
        service_name = _validate_service_name(service_name)
        deployment_address = _validate_deployment_address(
            deployment_address, current_ip
        )

    with _catalog_lock(registry_path):
        registry = _load_registry(registry_path, current_ip)
        if initialize:
            if registry["services"]:
                raise CatalogError("cannot initialize a non-empty catalog")
        else:
            services = [
                service
                for service in registry["services"]
                if service["name"].casefold() != service_name.casefold()
            ]
            services.append(
                {
                    "name": service_name,
                    "address": deployment_address,
                    "updated_at": _now(),
                }
            )
            services.sort(key=lambda item: item["name"].casefold())
            registry["services"] = services
        registry["updated_at"] = _now()
        registry["tailscale_ip"] = current_ip
        registry_data = (
            json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=False) + "\n"
        ).encode("utf-8")
        html_data = _render_html(registry).encode("utf-8")
        _write_catalog_files(registry_path, output_path, registry_data, html_data)
    return registry


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--tailscale-ip")
    parser.add_argument("--service-name")
    parser.add_argument("--deployment-address")
    parser.add_argument(
        "--initialize",
        action="store_true",
        help="create or refresh an empty baseline catalog",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(argv)
    try:
        update_catalog(
            args.registry,
            args.output,
            tailscale_ip=args.tailscale_ip,
            service_name=args.service_name,
            deployment_address=args.deployment_address,
            initialize=args.initialize,
        )
    except CatalogError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
