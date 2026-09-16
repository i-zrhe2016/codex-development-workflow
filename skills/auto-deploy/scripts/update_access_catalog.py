#!/usr/bin/env python3
"""Maintain the deployment host's Tailscale-only access catalog."""

from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timezone
import fcntl
import html
import ipaddress
import json
import os
from pathlib import Path
import subprocess
import stat
import sys
import tempfile
from typing import Any, Callable, Iterator
from urllib.parse import urlsplit


MAX_FILE_BYTES = 2_000_000
MAX_SERVICES = 1_000
MAX_TEXT_LENGTH = 512
MAX_FENCE_BYTES = 64_000
MAX_TRANSACTION_BYTES = 8_000_000
TAILSCALE_NETWORK = ipaddress.ip_network(".".join(("100", "64", "0", "0")) + "/10")


class CatalogError(Exception):
    """A safe, user-actionable catalog update failure."""


class FenceError(CatalogError):
    """The deployment mutation fence is unavailable or no longer current."""


@dataclass(frozen=True)
class FileSnapshot:
    """The content and serving metadata needed to reconcile one catalog file."""

    existed: bool
    data: bytes | None
    mode: int
    uid: int
    gid: int


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


def _validate_fence_owner(value: object) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_TEXT_LENGTH:
        raise FenceError("invalid catalog fence owner")
    if value.strip() != value or _has_control(value) or any(
        character.isspace() for character in value
    ):
        raise FenceError("invalid catalog fence owner")
    return value


def _validate_fence_generation(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value <= 0:
        raise FenceError("invalid catalog fence generation")
    return value


def _validate_fence_expiry(value: object) -> str:
    if not isinstance(value, str) or not value or len(value) > MAX_TEXT_LENGTH:
        raise FenceError("invalid catalog fence expiry")
    if _has_control(value):
        raise FenceError("invalid catalog fence expiry")
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    try:
        expiry = datetime.fromisoformat(normalized)
    except ValueError as exc:
        raise FenceError("invalid catalog fence expiry") from exc
    if expiry.tzinfo is None or expiry.utcoffset() is None:
        raise FenceError("catalog fence expiry must include a timezone")
    if expiry.astimezone(timezone.utc) <= datetime.now(timezone.utc):
        raise FenceError("catalog fence has expired")
    return value


def _read_descriptor(descriptor: int, maximum: int) -> bytes:
    try:
        size = os.fstat(descriptor).st_size
        if size > maximum:
            raise CatalogError("catalog metadata is too large")
        os.lseek(descriptor, 0, os.SEEK_SET)
        chunks: list[bytes] = []
        remaining = maximum + 1
        while remaining > 0:
            chunk = os.read(descriptor, min(64 * 1024, remaining))
            if not chunk:
                break
            chunks.append(chunk)
            remaining -= len(chunk)
        data = b"".join(chunks)
    except OSError as exc:
        raise CatalogError("catalog metadata is unreadable") from exc
    if len(data) > maximum:
        raise CatalogError("catalog metadata is too large")
    return data


class FenceGuard:
    """Hold the same file lock used by the deployment mutation authority."""

    def __init__(
        self, path: Path, descriptor: int, owner: str, generation: int
    ) -> None:
        self.path = path
        self.descriptor = descriptor
        self.owner = owner
        self.generation = generation
        self.role = ""

    def assert_current(self) -> dict[str, Any]:
        try:
            path_stat = os.lstat(self.path)
            descriptor_stat = os.fstat(self.descriptor)
        except OSError as exc:
            raise FenceError("catalog fence cannot be inspected") from exc
        if stat.S_ISLNK(path_stat.st_mode) or not stat.S_ISREG(path_stat.st_mode):
            raise FenceError("catalog fence must be a regular file")
        if (
            path_stat.st_dev != descriptor_stat.st_dev
            or path_stat.st_ino != descriptor_stat.st_ino
        ):
            raise FenceError("catalog fence was replaced")
        if path_stat.st_mode & 0o022:
            raise FenceError("catalog fence is writable by another account")
        try:
            record = json.loads(_read_descriptor(self.descriptor, MAX_FENCE_BYTES))
        except CatalogError as exc:
            raise FenceError("catalog fence is unreadable") from exc
        except (UnicodeError, json.JSONDecodeError) as exc:
            raise FenceError("catalog fence is malformed") from exc
        if not isinstance(record, dict) or record.get("state") != "active":
            raise FenceError("catalog fence is not active")
        record_owner = _validate_fence_owner(record.get("owner"))
        record_generation = _validate_fence_generation(record.get("generation"))
        _validate_fence_expiry(record.get("expires_at"))
        role = record.get("role")
        if role not in {"deployment", "recovery"}:
            raise FenceError("catalog fence role is invalid")
        if record_owner != self.owner or record_generation != self.generation:
            raise FenceError("catalog fence is no longer current")
        self.role = role
        return record


@contextmanager
def _fenced_mutation(
    fence_path: Path | None, owner: str | None, generation: int | None
) -> Iterator[FenceGuard]:
    if fence_path is None or owner is None or generation is None:
        raise FenceError("an active catalog fence is required")
    fence_path = Path(fence_path)
    owner = _validate_fence_owner(owner)
    generation = _validate_fence_generation(generation)
    try:
        descriptor = os.open(
            fence_path,
            os.O_RDWR | getattr(os, "O_CLOEXEC", 0) | getattr(os, "O_NOFOLLOW", 0),
        )
    except OSError as exc:
        raise FenceError("cannot open the catalog fence") from exc
    guard = FenceGuard(fence_path, descriptor, owner, generation)
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX)
            guard.assert_current()
        except FenceError:
            raise
        except OSError as exc:
            raise FenceError("catalog fence lock failed") from exc
        yield guard
    finally:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


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


def _path_exists(path: Path) -> bool:
    return os.path.lexists(path)


def _load_registry(
    path: Path, tailscale_ip: str, output_path: Path
) -> dict[str, Any]:
    if not _path_exists(path):
        if _path_exists(output_path):
            raise CatalogError(
                "catalog registry is missing while the HTML page still exists"
            )
        return _empty_registry(tailscale_ip)
    try:
        if path.is_symlink():
            raise CatalogError("catalog registry must be a regular file")
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


def _read_snapshot(path: Path, default_mode: int) -> FileSnapshot:
    if not _path_exists(path):
        return FileSnapshot(False, None, default_mode, os.geteuid(), os.getegid())
    try:
        path_stat = os.lstat(path)
        if stat.S_ISLNK(path_stat.st_mode) or not stat.S_ISREG(path_stat.st_mode):
            raise CatalogError("catalog file must be a regular file")
        if path_stat.st_size > MAX_FILE_BYTES:
            raise CatalogError("catalog file is too large")
        data = path.read_bytes()
        return FileSnapshot(
            True,
            data,
            path_stat.st_mode & 0o777,
            path_stat.st_uid,
            path_stat.st_gid,
        )
    except CatalogError:
        raise
    except (OSError, IOError) as exc:
        raise CatalogError("catalog file is unreadable") from exc


def _write_temp(
    directory: Path, basename: str, data: bytes, mode: int, uid: int, gid: int
) -> Path:
    descriptor, name = tempfile.mkstemp(
        prefix=f".{basename}.", suffix=".tmp", dir=str(directory)
    )
    temporary = Path(name)
    completed = False
    try:
        os.fchown(descriptor, uid, gid)
        os.fchmod(descriptor, mode)
        with os.fdopen(descriptor, "wb") as handle:
            descriptor = -1
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        completed = True
    except (OSError, IOError) as exc:
        raise CatalogError("catalog staging failed") from exc
    finally:
        if descriptor != -1:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if not completed:
            try:
                temporary.unlink()
            except (FileNotFoundError, OSError):
                pass
    return temporary


def _snapshot_payload(snapshot: FileSnapshot) -> dict[str, Any]:
    return {
        "existed": snapshot.existed,
        "data": (
            base64.b64encode(snapshot.data).decode("ascii")
            if snapshot.data is not None
            else None
        ),
        "mode": snapshot.mode,
        "uid": snapshot.uid,
        "gid": snapshot.gid,
    }


def _snapshot_from_payload(value: object) -> FileSnapshot:
    if not isinstance(value, dict) or not isinstance(value.get("existed"), bool):
        raise CatalogError("catalog transaction is malformed")
    mode = value.get("mode")
    uid = value.get("uid")
    gid = value.get("gid")
    if (
        isinstance(mode, bool)
        or not isinstance(mode, int)
        or not 0 <= mode <= 0o777
        or isinstance(uid, bool)
        or not isinstance(uid, int)
        or uid < 0
        or isinstance(gid, bool)
        or not isinstance(gid, int)
        or gid < 0
    ):
        raise CatalogError("catalog transaction metadata is malformed")
    encoded = value.get("data")
    if not value["existed"]:
        if encoded is not None:
            raise CatalogError("catalog transaction data is malformed")
        data = None
    else:
        if not isinstance(encoded, str) or len(encoded) > MAX_FILE_BYTES * 2:
            raise CatalogError("catalog transaction data is malformed")
        try:
            data = base64.b64decode(encoded.encode("ascii"), validate=True)
        except (UnicodeError, ValueError) as exc:
            raise CatalogError("catalog transaction data is malformed") from exc
        if len(data) > MAX_FILE_BYTES:
            raise CatalogError("catalog transaction data is too large")
    return FileSnapshot(value["existed"], data, mode, uid, gid)


@dataclass(frozen=True)
class CatalogTransaction:
    registry_path: str
    output_path: str
    fence_owner: str
    fence_generation: int
    registry_old: FileSnapshot
    output_old: FileSnapshot
    registry_new: FileSnapshot
    output_new: FileSnapshot


def _transaction_path(registry_path: Path) -> Path:
    return registry_path.with_name(registry_path.name + ".txn")


def _transaction_payload(
    registry_path: Path,
    output_path: Path,
    owner: str,
    generation: int,
    registry_old: FileSnapshot,
    output_old: FileSnapshot,
    registry_new: FileSnapshot,
    output_new: FileSnapshot,
) -> dict[str, Any]:
    return {
        "version": 1,
        "state": "prepared",
        "registry_path": str(registry_path.resolve(strict=False)),
        "output_path": str(output_path.resolve(strict=False)),
        "fence_owner": owner,
        "fence_generation": generation,
        "registry_old": _snapshot_payload(registry_old),
        "output_old": _snapshot_payload(output_old),
        "registry_new": _snapshot_payload(registry_new),
        "output_new": _snapshot_payload(output_new),
    }


def _write_transaction_journal(
    journal_path: Path,
    payload: dict[str, Any],
    fence_check: Callable[[], object],
) -> None:
    data = (json.dumps(payload, ensure_ascii=False, sort_keys=True) + "\n").encode(
        "utf-8"
    )
    if len(data) > MAX_TRANSACTION_BYTES:
        raise CatalogError("catalog transaction is too large")
    journal_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = _write_temp(
        journal_path.parent,
        journal_path.name,
        data,
        0o600,
        os.geteuid(),
        os.getegid(),
    )
    try:
        fence_check()
        os.replace(temporary, journal_path)
        temporary = None
        _fsync_directory(journal_path.parent)
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def _load_transaction(
    journal_path: Path, registry_path: Path, output_path: Path
) -> CatalogTransaction | None:
    if not _path_exists(journal_path):
        return None
    try:
        journal_stat = os.lstat(journal_path)
        if (
            stat.S_ISLNK(journal_stat.st_mode)
            or not stat.S_ISREG(journal_stat.st_mode)
            or journal_stat.st_mode & 0o022
        ):
            raise CatalogError("catalog transaction must be a regular file")
        if journal_stat.st_size > MAX_TRANSACTION_BYTES:
            raise CatalogError("catalog transaction is too large")
        value = json.loads(journal_path.read_text(encoding="utf-8"))
    except CatalogError:
        raise
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise CatalogError("catalog transaction is unreadable") from exc
    if not isinstance(value, dict) or value.get("version") != 1:
        raise CatalogError("catalog transaction is malformed")
    if value.get("state") != "prepared":
        raise CatalogError("catalog transaction state is invalid")
    expected_registry = str(registry_path.resolve(strict=False))
    expected_output = str(output_path.resolve(strict=False))
    if (
        value.get("registry_path") != expected_registry
        or value.get("output_path") != expected_output
    ):
        raise CatalogError("catalog transaction targets different files")
    owner = _validate_fence_owner(value.get("fence_owner"))
    generation = _validate_fence_generation(value.get("fence_generation"))
    return CatalogTransaction(
        expected_registry,
        expected_output,
        owner,
        generation,
        _snapshot_from_payload(value.get("registry_old")),
        _snapshot_from_payload(value.get("output_old")),
        _snapshot_from_payload(value.get("registry_new")),
        _snapshot_from_payload(value.get("output_new")),
    )


def _remove_transaction(
    journal_path: Path, fence_check: Callable[[], object]
) -> None:
    if not _path_exists(journal_path):
        return
    fence_check()
    try:
        journal_path.unlink()
    except FileNotFoundError:
        return
    _fsync_directory(journal_path.parent)


def _snapshot_matches(current: FileSnapshot, expected: FileSnapshot) -> bool:
    if not expected.existed:
        return not current.existed
    return current == expected


def _replace_snapshot(
    path: Path, snapshot: FileSnapshot, fence_check: Callable[[], object]
) -> None:
    if not snapshot.existed:
        if not _path_exists(path):
            return
        fence_check()
        try:
            path.unlink()
        except FileNotFoundError:
            return
        _fsync_directory(path.parent)
        return
    if snapshot.data is None:
        raise CatalogError("catalog replacement data is unavailable")
    temporary = _write_temp(
        path.parent,
        path.name,
        snapshot.data,
        snapshot.mode,
        snapshot.uid,
        snapshot.gid,
    )
    try:
        fence_check()
        os.replace(temporary, path)
        temporary = None
        _fsync_directory(path.parent)
    finally:
        if temporary is not None:
            try:
                temporary.unlink()
            except FileNotFoundError:
                pass


def _reconcile_transaction(
    journal_path: Path,
    transaction: CatalogTransaction,
    fence: FenceGuard,
    *,
    rollback: bool,
) -> None:
    targets = (
        (Path(transaction.registry_path), transaction.registry_old, transaction.registry_new),
        (Path(transaction.output_path), transaction.output_old, transaction.output_new),
    )
    current_states: list[tuple[Path, FileSnapshot, FileSnapshot, FileSnapshot]] = []
    for path, old, new in targets:
        current = _read_snapshot(path, old.mode)
        if not _snapshot_matches(current, old) and not _snapshot_matches(current, new):
            raise CatalogError("catalog transaction found unexpected file contents")
        current_states.append((path, current, old, new))
    for path, current, old, new in current_states:
        desired = old if rollback else new
        if current != desired:
            _replace_snapshot(path, desired, fence.assert_current)
    _remove_transaction(journal_path, fence.assert_current)


def _write_catalog_files(
    registry_path: Path,
    output_path: Path,
    registry_data: bytes,
    html_data: bytes,
    fence: FenceGuard,
) -> None:
    if len(registry_data) > MAX_FILE_BYTES or len(html_data) > MAX_FILE_BYTES:
        raise CatalogError("generated catalog is too large")
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    registry_old = _read_snapshot(registry_path, 0o600)
    output_old = _read_snapshot(output_path, 0o644)
    registry_new = FileSnapshot(
        True,
        registry_data,
        registry_old.mode if registry_old.existed else 0o600,
        registry_old.uid,
        registry_old.gid,
    )
    output_new = FileSnapshot(
        True,
        html_data,
        output_old.mode if output_old.existed else 0o644,
        output_old.uid,
        output_old.gid,
    )
    journal_path = _transaction_path(registry_path)
    if _path_exists(journal_path):
        raise CatalogError("pending catalog transaction must be reconciled first")
    transaction = CatalogTransaction(
        str(registry_path.resolve(strict=False)),
        str(output_path.resolve(strict=False)),
        fence.owner,
        fence.generation,
        registry_old,
        output_old,
        registry_new,
        output_new,
    )
    _write_transaction_journal(
        journal_path,
        _transaction_payload(
            registry_path,
            output_path,
            fence.owner,
            fence.generation,
            registry_old,
            output_old,
            registry_new,
            output_new,
        ),
        fence.assert_current,
    )
    try:
        _replace_snapshot(registry_path, registry_new, fence.assert_current)
        _replace_snapshot(output_path, output_new, fence.assert_current)
    except FenceError as exc:
        raise CatalogError(
            "catalog fence changed; authorized recovery is required"
        ) from exc
    except (OSError, IOError, CatalogError) as exc:
        try:
            _reconcile_transaction(
                journal_path, transaction, fence, rollback=True
            )
        except FenceError as restore_exc:
            raise CatalogError(
                "catalog update failed; authorized recovery is required"
            ) from restore_exc
        except (OSError, IOError, CatalogError) as restore_exc:
            raise CatalogError("catalog update and restore both failed") from restore_exc
        raise CatalogError("catalog update failed") from exc
    try:
        _remove_transaction(journal_path, fence.assert_current)
    except FenceError as exc:
        raise CatalogError(
            "catalog committed; authorized recovery must remove its journal"
        ) from exc
    except (OSError, IOError, CatalogError) as exc:
        raise CatalogError(
            "catalog committed; pending transaction journal needs reconciliation"
        ) from exc


@contextmanager
def _catalog_lock(registry_path: Path) -> Iterator[None]:
    registry_path.parent.mkdir(parents=True, exist_ok=True)
    lock_path = registry_path.with_name(registry_path.name + ".lock")
    try:
        descriptor = os.open(
            lock_path,
            os.O_RDWR
            | os.O_CREAT
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            0o600,
        )
    except OSError as exc:
        raise CatalogError("cannot create the catalog lock") from exc
    try:
        if os.fstat(descriptor).st_mode & 0o022:
            raise CatalogError("catalog lock is writable by another account")
        fcntl.flock(descriptor, fcntl.LOCK_EX)
        yield
    except CatalogError:
        raise
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
    fence_file: Path | None = None,
    fence_owner: str | None = None,
    fence_generation: int | None = None,
    recover_pending: bool = False,
) -> dict[str, Any]:
    registry_path = Path(registry_path)
    output_path = Path(output_path)
    if registry_path.resolve(strict=False) == output_path.resolve(strict=False):
        raise CatalogError("registry and HTML output must be different files")
    if recover_pending and (
        initialize or service_name is not None or deployment_address is not None
    ):
        raise CatalogError("recover-pending cannot include a catalog update")

    with _fenced_mutation(fence_file, fence_owner, fence_generation) as fence:
        current_ip = _discover_tailscale_ip()
        if tailscale_ip is not None:
            asserted_ip = _validate_tailscale_ip(tailscale_ip)
            if asserted_ip != current_ip:
                raise CatalogError(
                    "caller Tailscale IPv4 does not match local discovery"
                )
        fence.assert_current()
        if initialize:
            if service_name is not None or deployment_address is not None:
                raise CatalogError("initialize cannot include a service update")
        elif not recover_pending and (
            service_name is None or deployment_address is None
        ):
            raise CatalogError("service name and deployment address are required")
        elif not recover_pending:
            service_name = _validate_service_name(service_name)
            deployment_address = _validate_deployment_address(
                deployment_address, current_ip
            )

        with _catalog_lock(registry_path):
            journal_path = _transaction_path(registry_path)
            transaction = _load_transaction(
                journal_path, registry_path, output_path
            )
            if transaction is not None:
                same_fence = (
                    transaction.fence_owner == fence.owner
                    and transaction.fence_generation == fence.generation
                )
                if recover_pending and fence.role == "recovery":
                    _reconcile_transaction(
                        journal_path, transaction, fence, rollback=True
                    )
                elif same_fence:
                    _reconcile_transaction(
                        journal_path, transaction, fence, rollback=False
                    )
                else:
                    raise FenceError(
                        "pending catalog transaction requires authorized recovery"
                    )
            elif recover_pending:
                raise CatalogError("no pending catalog transaction to recover")

            registry = _load_registry(registry_path, current_ip, output_path)
            if recover_pending:
                return registry
            if initialize:
                if registry["services"]:
                    raise CatalogError("cannot initialize a non-empty catalog")
            else:
                services = [
                    service
                    for service in registry["services"]
                    if service["name"].casefold() != service_name.casefold()
                ]
                if len(services) >= MAX_SERVICES and all(
                    service["name"].casefold() != service_name.casefold()
                    for service in registry["services"]
                ):
                    raise CatalogError("catalog service limit reached")
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
                json.dumps(registry, ensure_ascii=False, indent=2, sort_keys=False)
                + "\n"
            ).encode("utf-8")
            html_data = _render_html(registry).encode("utf-8")
            _write_catalog_files(
                registry_path, output_path, registry_data, html_data, fence
            )
    return registry


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--registry", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--tailscale-ip",
        help="optional assertion; the local Tailscale IPv4 is always discovered",
    )
    parser.add_argument("--service-name")
    parser.add_argument("--deployment-address")
    parser.add_argument("--fence-file", type=Path, required=True)
    parser.add_argument("--fence-owner", required=True)
    parser.add_argument("--fence-generation", type=int, required=True)
    parser.add_argument(
        "--initialize",
        action="store_true",
        help="create or refresh an empty baseline catalog",
    )
    parser.add_argument(
        "--recover-pending",
        action="store_true",
        help="rollback a pending transaction under a recovery fence",
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
            fence_file=args.fence_file,
            fence_owner=args.fence_owner,
            fence_generation=args.fence_generation,
            recover_pending=args.recover_pending,
        )
    except CatalogError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
