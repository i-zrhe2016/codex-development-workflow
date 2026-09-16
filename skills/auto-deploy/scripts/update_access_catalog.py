#!/usr/bin/env python3
"""Maintain the deployment host's Tailscale-only access catalog."""

from __future__ import annotations

import argparse
import base64
from contextlib import contextmanager
import ctypes
from dataclasses import dataclass
from datetime import datetime, timezone
import errno
import fcntl
import hashlib
import hmac
import html
import ipaddress
import json
import os
from pathlib import Path
import secrets
import subprocess
import stat
import sys
import time
from typing import Any, Callable, Iterator
from urllib.parse import urlsplit


MAX_FILE_BYTES = 2_000_000
MAX_SERVICES = 1_000
MAX_TEXT_LENGTH = 512
MAX_FENCE_BYTES = 64_000
MAX_TRANSACTION_BYTES = 16_000_000
TRANSACTION_VERSION = 2
TRANSACTION_HMAC_FIELD = "catalog_hmac"
TRANSACTION_KEY_FIELD = "catalog_hmac_key"
TRANSACTION_KEY_BYTES = 32
SIDECAR_MODE = 0o660
REGISTRY_MODE = 0o660
LOCK_TIMEOUT_SECONDS = 5.0
LOCK_RETRY_SECONDS = 0.05
MUTATION_MIN_REMAINING_SECONDS = 0.25
# Linux uid_t/gid_t are unsigned 32-bit values; all-ones is the chown sentinel.
PLATFORM_ID_MAX = (1 << (ctypes.sizeof(ctypes.c_uint) * 8)) - 2
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


@dataclass
class StagedFile:
    """A private staging entry and its still-open identity descriptor."""

    path: Path
    descriptor: int
    directory: Path
    directory_descriptor: int
    parent: Path
    parent_descriptor: int
    name: str


def _has_control(value: str) -> bool:
    return any(
        ord(character) < 32
        or ord(character) == 127
        or 0xD800 <= ord(character) <= 0xDFFF
        for character in value
    )


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


def _validate_transaction_key(value: object) -> bytes:
    if (
        not isinstance(value, str)
        or len(value) != TRANSACTION_KEY_BYTES * 2
        or _has_control(value)
    ):
        raise FenceError("invalid catalog transaction key")
    try:
        key = bytes.fromhex(value)
    except ValueError as exc:
        raise FenceError("invalid catalog transaction key") from exc
    if len(key) != TRANSACTION_KEY_BYTES:
        raise FenceError("invalid catalog transaction key")
    return key


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


def _acquire_exclusive_lock(
    descriptor: int, error_type: type[CatalogError], message: str
) -> None:
    deadline = time.monotonic() + LOCK_TIMEOUT_SECONDS
    while True:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
            return
        except BlockingIOError:
            pass
        except OSError as exc:
            if exc.errno not in {errno.EACCES, errno.EAGAIN}:
                raise error_type(message) from exc
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise error_type(message)
        time.sleep(min(LOCK_RETRY_SECONDS, remaining))


def _fence_lock_path(fence_path: Path) -> Path:
    return fence_path.with_name(fence_path.name + ".lock")


def _open_fence_lock(fence_path: Path) -> int:
    lock_path = _fence_lock_path(fence_path)
    descriptor = -1
    try:
        descriptor = os.open(
            lock_path,
            os.O_RDWR
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
        )
        descriptor_stat = os.fstat(descriptor)
        if (
            not stat.S_ISREG(descriptor_stat.st_mode)
            or descriptor_stat.st_mode & 0o077
        ):
            raise FenceError("catalog fence lock is not owner-only")
        return descriptor
    except FenceError:
        if descriptor != -1:
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise
    except OSError as exc:
        if descriptor != -1:
            try:
                os.close(descriptor)
            except OSError:
                pass
        raise FenceError("cannot open the catalog fence lock") from exc


class FenceGuard:
    """Expose the deployment mutation authority's fenced file operations."""

    def __init__(
        self,
        path: Path,
        descriptor: int,
        authority_descriptor: int,
        owner: str,
        generation: int,
    ) -> None:
        self.path = path
        self.descriptor = descriptor
        self.authority_path = _fence_lock_path(path)
        self.authority_descriptor = authority_descriptor
        self.owner = owner
        self.generation = generation
        self.role = ""
        self._required_role: str | None = None
        self.transaction_key: bytes | None = None

    def assert_current(self) -> dict[str, Any]:
        try:
            authority_path_stat = os.lstat(self.authority_path)
            authority_descriptor_stat = os.fstat(self.authority_descriptor)
            path_stat = os.lstat(self.path)
            descriptor_stat = os.fstat(self.descriptor)
        except OSError as exc:
            raise FenceError("catalog fence cannot be inspected") from exc
        if (
            stat.S_ISLNK(authority_path_stat.st_mode)
            or not stat.S_ISREG(authority_path_stat.st_mode)
            or authority_path_stat.st_mode & 0o077
            or authority_path_stat.st_nlink != 1
            or authority_path_stat.st_dev != authority_descriptor_stat.st_dev
            or authority_path_stat.st_ino != authority_descriptor_stat.st_ino
        ):
            raise FenceError("catalog fence authority lock was replaced")
        if stat.S_ISLNK(path_stat.st_mode) or not stat.S_ISREG(path_stat.st_mode):
            raise FenceError("catalog fence must be a regular file")
        if (
            path_stat.st_dev != descriptor_stat.st_dev
            or path_stat.st_ino != descriptor_stat.st_ino
        ):
            raise FenceError("catalog fence was replaced")
        if path_stat.st_nlink != 1 or descriptor_stat.st_nlink != 1:
            raise FenceError("catalog fence must not have hard-link aliases")
        if path_stat.st_mode & 0o077:
            raise FenceError("catalog fence is accessible to another account")
        try:
            record = json.loads(_read_descriptor(self.descriptor, MAX_FENCE_BYTES))
        except CatalogError as exc:
            raise FenceError("catalog fence is unreadable") from exc
        except (UnicodeError, ValueError, RecursionError) as exc:
            raise FenceError("catalog fence is malformed") from exc
        if not isinstance(record, dict) or record.get("state") != "active":
            raise FenceError("catalog fence is not active")
        record_owner = _validate_fence_owner(record.get("owner"))
        record_generation = _validate_fence_generation(record.get("generation"))
        transaction_key = _validate_transaction_key(
            record.get(TRANSACTION_KEY_FIELD)
        )
        _validate_fence_expiry(record.get("expires_at"))
        role = record.get("role")
        if role not in {"deployment", "recovery"}:
            raise FenceError("catalog fence role is invalid")
        if self._required_role is not None and role != self._required_role:
            raise FenceError("catalog fence role changed")
        if record_owner != self.owner or record_generation != self.generation:
            raise FenceError("catalog fence is no longer current")
        if self.transaction_key is not None and self.transaction_key != transaction_key:
            raise FenceError("catalog transaction key changed")
        self.transaction_key = transaction_key
        self.role = role
        return record

    def pin_role(self) -> None:
        if self.role not in {"deployment", "recovery"}:
            raise FenceError("catalog fence role is invalid")
        self._required_role = self.role

    def _assert_mutation_window(self) -> None:
        record = self.assert_current()
        expiry_value = record["expires_at"]
        normalized = (
            expiry_value[:-1] + "+00:00"
            if expiry_value.endswith("Z")
            else expiry_value
        )
        expiry = datetime.fromisoformat(normalized).astimezone(timezone.utc)
        if (
            expiry - datetime.now(timezone.utc)
        ).total_seconds() < MUTATION_MIN_REMAINING_SECONDS:
            raise FenceError("catalog fence expires too soon for a mutation")

    def _authorized_mutation(self, operation: Callable[[], Any]) -> Any:
        """Run one filesystem mutation in the authority's acceptance window."""
        # _fenced_mutation holds this stable authority lock for the complete
        # operation. Keep the fence acceptance and the filesystem syscall in
        # this single authority operation so recovery cannot interleave them.
        self._assert_mutation_window()
        result = operation()
        self.assert_current()
        return result

    def replace(self, staged: StagedFile, destination: Path) -> None:
        """Accept one replacement only while this exact fence is current."""

        def replace_file() -> None:
            if Path(os.path.abspath(destination.parent)) != Path(
                os.path.abspath(staged.parent)
            ):
                raise FenceError("catalog replacement parent changed")
            try:
                staging_path_stat = os.lstat(staged.directory)
                staging_descriptor_stat = os.fstat(staged.directory_descriptor)
                parent_path_stat = os.lstat(staged.parent)
                parent_descriptor_stat = os.fstat(staged.parent_descriptor)
            except OSError as exc:
                raise FenceError("catalog replacement directory changed") from exc
            if (
                stat.S_ISLNK(staging_path_stat.st_mode)
                or not stat.S_ISDIR(staging_path_stat.st_mode)
                or staging_path_stat.st_dev != staging_descriptor_stat.st_dev
                or staging_path_stat.st_ino != staging_descriptor_stat.st_ino
                or stat.S_ISLNK(parent_path_stat.st_mode)
                or not stat.S_ISDIR(parent_path_stat.st_mode)
                or parent_path_stat.st_dev != parent_descriptor_stat.st_dev
                or parent_path_stat.st_ino != parent_descriptor_stat.st_ino
            ):
                raise FenceError("catalog replacement directory changed")
            temporary_stat = os.fstat(staged.descriptor)
            path_stat = os.stat(
                staged.name,
                dir_fd=staged.directory_descriptor,
                follow_symlinks=False,
            )
            if (
                not stat.S_ISREG(temporary_stat.st_mode)
                or temporary_stat.st_nlink != 1
                or stat.S_ISLNK(path_stat.st_mode)
                or not stat.S_ISREG(path_stat.st_mode)
                or path_stat.st_nlink != 1
                or path_stat.st_dev != temporary_stat.st_dev
                or path_stat.st_ino != temporary_stat.st_ino
            ):
                raise FenceError("catalog replacement source changed")
            os.replace(
                staged.name,
                destination.name,
                src_dir_fd=staged.directory_descriptor,
                dst_dir_fd=staged.parent_descriptor,
            )
            destination_stat = os.stat(
                destination.name,
                dir_fd=staged.parent_descriptor,
                follow_symlinks=False,
            )
            if (
                stat.S_ISLNK(destination_stat.st_mode)
                or not stat.S_ISREG(destination_stat.st_mode)
                or destination_stat.st_nlink != 1
                or destination_stat.st_dev != temporary_stat.st_dev
                or destination_stat.st_ino != temporary_stat.st_ino
            ):
                raise FenceError("catalog replacement target changed")

        self._authorized_mutation(replace_file)

    def unlink(self, path: Path) -> None:
        """Accept one unlink only while this exact fence is current."""
        self._authorized_mutation(path.unlink)

    def mutate(self, operation: Callable[[], Any]) -> Any:
        """Run a metadata mutation through the same fenced authority."""
        return self._authorized_mutation(operation)


@contextmanager
def _fenced_mutation(
    fence_path: Path | None, owner: str | None, generation: int | None
) -> Iterator[FenceGuard]:
    if fence_path is None or owner is None or generation is None:
        raise FenceError("an active catalog fence is required")
    fence_path = Path(fence_path)
    owner = _validate_fence_owner(owner)
    generation = _validate_fence_generation(generation)
    authority_descriptor = -1
    descriptor = -1
    locked = False
    try:
        authority_descriptor = _open_fence_lock(fence_path)
        _acquire_exclusive_lock(
            authority_descriptor,
            FenceError,
            "catalog fence authority lock is unavailable",
        )
        locked = True
        try:
            descriptor = os.open(
                fence_path,
                os.O_RDWR
                | getattr(os, "O_CLOEXEC", 0)
                | getattr(os, "O_NOFOLLOW", 0),
            )
        except OSError as exc:
            raise FenceError("cannot open the catalog fence") from exc
        guard = FenceGuard(
            fence_path,
            descriptor,
            authority_descriptor,
            owner,
            generation,
        )
        guard.assert_current()
        guard.pin_role()
        yield guard
    finally:
        if descriptor != -1:
            os.close(descriptor)
        if locked:
            try:
                fcntl.flock(authority_descriptor, fcntl.LOCK_UN)
            finally:
                os.close(authority_descriptor)
        elif authority_descriptor != -1:
            os.close(authority_descriptor)


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


def _read_regular_file(
    path: Path, maximum: int, description: str
) -> tuple[os.stat_result, bytes]:
    flags = (
        os.O_RDONLY
        | os.O_NONBLOCK
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise CatalogError(f"{description} is unreadable") from exc
    try:
        file_stat = os.fstat(descriptor)
        if not stat.S_ISREG(file_stat.st_mode):
            raise CatalogError(f"{description} must be a regular file")
        if file_stat.st_size > maximum:
            raise CatalogError(f"{description} is too large")
        return file_stat, _read_descriptor(descriptor, maximum)
    except CatalogError:
        raise
    except OSError as exc:
        raise CatalogError(f"{description} is unreadable") from exc
    finally:
        os.close(descriptor)


def _prepare_registry(path: Path, fence: FenceGuard) -> None:
    if not _path_exists(path):
        return
    try:
        file_stat = os.lstat(path)
    except OSError as exc:
        raise CatalogError("catalog registry cannot be inspected") from exc
    if stat.S_ISLNK(file_stat.st_mode) or not stat.S_ISREG(file_stat.st_mode):
        raise CatalogError("catalog registry must be a regular file")
    if file_stat.st_mode & 0o007:
        raise CatalogError("catalog registry permissions are too broad")
    group_id = _sidecar_gid(path.parent)
    if (
        file_stat.st_gid == group_id
        and (file_stat.st_mode & REGISTRY_MODE) == REGISTRY_MODE
    ):
        return
    if file_stat.st_uid != os.geteuid() and os.geteuid() != 0:
        raise CatalogError(
            "catalog registry needs an ownership-capable authority for recovery"
        )
    flags = (
        os.O_RDONLY
        | os.O_NONBLOCK
        | getattr(os, "O_CLOEXEC", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise CatalogError(
            "catalog registry cannot be opened safely for recovery"
        ) from exc
    try:
        descriptor_stat = os.fstat(descriptor)
        if (
            not stat.S_ISREG(descriptor_stat.st_mode)
            or descriptor_stat.st_dev != file_stat.st_dev
            or descriptor_stat.st_ino != file_stat.st_ino
        ):
            raise CatalogError("catalog registry changed during inspection")
        if descriptor_stat.st_mode & 0o007:
            raise CatalogError("catalog registry permissions are too broad")
        if (
            descriptor_stat.st_gid == group_id
            and (descriptor_stat.st_mode & REGISTRY_MODE) == REGISTRY_MODE
        ):
            return
        if descriptor_stat.st_uid != os.geteuid() and os.geteuid() != 0:
            raise CatalogError(
                "catalog registry needs an ownership-capable authority for recovery"
            )

        def repair_metadata() -> None:
            if descriptor_stat.st_gid != group_id:
                os.fchown(descriptor, descriptor_stat.st_uid, group_id)
            os.fchmod(descriptor, REGISTRY_MODE)
            _fsync_directory(path.parent)

        fence.mutate(repair_metadata)
    except CatalogError:
        raise
    except OSError as exc:
        raise CatalogError(
            "catalog registry cannot be made accessible to recovery"
        ) from exc
    finally:
        os.close(descriptor)


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
        file_stat, data = _read_regular_file(
            path, MAX_FILE_BYTES, "catalog registry"
        )
        if (
            (file_stat.st_mode & 0o007)
            or (file_stat.st_mode & REGISTRY_MODE) != REGISTRY_MODE
        ):
            raise CatalogError("catalog registry permissions are unsafe")
        value = json.loads(data.decode("utf-8"))
    except CatalogError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
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


def _sidecar_gid(directory: Path) -> int:
    try:
        directory_stat = os.stat(directory)
    except OSError as exc:
        raise CatalogError("catalog sidecar directory is unreadable") from exc
    if not stat.S_ISDIR(directory_stat.st_mode) or directory_stat.st_mode & 0o002:
        raise CatalogError("catalog sidecar directory is not safe")
    return directory_stat.st_gid


def _prepare_sidecar(
    descriptor: int, directory: Path, fence: FenceGuard
) -> None:
    group_id = _sidecar_gid(directory)
    try:
        descriptor_stat = os.fstat(descriptor)
        if not stat.S_ISREG(descriptor_stat.st_mode):
            raise CatalogError("catalog sidecar must be a regular file")
        if (
            descriptor_stat.st_gid == group_id
            and (descriptor_stat.st_mode & 0o777) == SIDECAR_MODE
        ):
            return

        def repair_metadata() -> None:
            current_stat = os.fstat(descriptor)
            if not stat.S_ISREG(current_stat.st_mode):
                raise CatalogError("catalog sidecar must be a regular file")
            if current_stat.st_gid != group_id:
                os.fchown(descriptor, current_stat.st_uid, group_id)
            os.fchmod(descriptor, SIDECAR_MODE)

        fence.mutate(repair_metadata)
    except CatalogError:
        raise
    except OSError as exc:
        raise CatalogError(
            "catalog sidecar is not accessible to the recovery authority"
        ) from exc


def _is_group_member(group_id: int) -> bool:
    try:
        return group_id == os.getegid() or group_id in os.getgroups()
    except OSError:
        return False


def _registry_metadata(
    snapshot: FileSnapshot, directory: Path
) -> tuple[int, int, int]:
    group_id = _sidecar_gid(directory)
    if not snapshot.existed:
        return os.geteuid(), group_id, REGISTRY_MODE
    if os.geteuid() == 0 or (
        snapshot.uid == os.geteuid()
        and (snapshot.gid == os.getegid() or _is_group_member(snapshot.gid))
    ):
        return snapshot.uid, snapshot.gid, snapshot.mode
    if snapshot.gid == group_id and _is_group_member(group_id):
        return os.geteuid(), group_id, REGISTRY_MODE
    raise CatalogError(
        "catalog registry writer is not compatible with its recovery group"
    )


def _output_metadata(snapshot: FileSnapshot) -> tuple[int, int, int]:
    if not snapshot.existed:
        return os.geteuid(), os.getegid(), 0o644
    if snapshot.mode & 0o002:
        raise CatalogError("HTML output permissions are too broad")
    if os.geteuid() == 0 or (
        snapshot.uid == os.geteuid()
        and (snapshot.gid == os.getegid() or _is_group_member(snapshot.gid))
    ):
        return snapshot.uid, snapshot.gid, snapshot.mode
    if snapshot.mode & 0o040 and _is_group_member(snapshot.gid):
        return os.geteuid(), snapshot.gid, snapshot.mode
    if snapshot.mode & 0o004:
        return os.geteuid(), os.getegid(), snapshot.mode
    raise CatalogError(
        "HTML output owner is incompatible; use an ownership-capable writer"
    )


def _validate_preprovisioned_directory(directory: Path, description: str) -> None:
    """Require a pre-provisioned directory with safe path components."""
    if any(part in {".", ".."} for part in directory.parts):
        raise CatalogError(f"{description} path must be normalized")
    document_root = Path(os.path.abspath(directory))
    current = document_root
    while True:
        try:
            directory_stat = os.lstat(current)
        except OSError as exc:
            raise CatalogError(f"{description} must be pre-provisioned") from exc
        if stat.S_ISLNK(directory_stat.st_mode) or not stat.S_ISDIR(
            directory_stat.st_mode
        ):
            raise CatalogError(f"{description} must use real directories")
        if directory_stat.st_mode & 0o002:
            if current == document_root or not (directory_stat.st_mode & 0o1000):
                raise CatalogError(f"{description} permissions are too broad")
        parent = current.parent
        if parent == current:
            break
        current = parent


def _validate_output_directory(directory: Path) -> None:
    _validate_preprovisioned_directory(directory, "HTML document root")


def _validate_registry_directory(directory: Path) -> None:
    _validate_preprovisioned_directory(directory, "catalog registry directory")


def _recovery_metadata(
    path: Path, snapshot: FileSnapshot, *, registry: bool
) -> tuple[int, int, int]:
    if not snapshot.existed:
        return snapshot.uid, snapshot.gid, snapshot.mode
    if os.geteuid() == 0 or (
        snapshot.uid == os.geteuid()
        and (snapshot.gid == os.getegid() or _is_group_member(snapshot.gid))
    ):
        return snapshot.uid, snapshot.gid, snapshot.mode
    if registry:
        group_id = _sidecar_gid(path.parent)
        if _is_group_member(group_id):
            return os.geteuid(), group_id, REGISTRY_MODE
        raise CatalogError(
            "recovery cannot access the catalog registry group"
        )
    return _output_metadata(snapshot)


def _read_snapshot(path: Path, default_mode: int) -> FileSnapshot:
    if not _path_exists(path):
        return FileSnapshot(False, None, default_mode, os.geteuid(), os.getegid())
    try:
        path_stat, data = _read_regular_file(path, MAX_FILE_BYTES, "catalog file")
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


def _cleanup_staged_file(staged: StagedFile) -> None:
    try:
        os.close(staged.descriptor)
    except OSError:
        pass
    try:
        os.unlink(staged.name, dir_fd=staged.directory_descriptor)
    except (FileNotFoundError, OSError):
        pass
    try:
        staging_path_stat = os.stat(
            staged.directory.name,
            dir_fd=staged.parent_descriptor,
            follow_symlinks=False,
        )
        staging_descriptor_stat = os.fstat(staged.directory_descriptor)
        if (
            stat.S_ISDIR(staging_path_stat.st_mode)
            and staging_path_stat.st_dev == staging_descriptor_stat.st_dev
            and staging_path_stat.st_ino == staging_descriptor_stat.st_ino
        ):
            os.rmdir(
                staged.directory.name,
                dir_fd=staged.parent_descriptor,
            )
    except (FileNotFoundError, OSError):
        pass
    finally:
        for descriptor in (
            staged.directory_descriptor,
            staged.parent_descriptor,
        ):
            try:
                os.close(descriptor)
            except OSError:
                pass


def _validate_platform_id(value: object, description: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or not 0 <= value <= PLATFORM_ID_MAX
    ):
        raise CatalogError(f"catalog transaction {description} is malformed")
    return value


def _open_directory_descriptor(directory: Path) -> int:
    flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    descriptor = -1
    try:
        descriptor = os.open(directory, flags)
        directory_stat = os.fstat(descriptor)
        if not stat.S_ISDIR(directory_stat.st_mode):
            raise CatalogError("catalog staging parent must be a directory")
        return descriptor
    except CatalogError:
        if descriptor != -1:
            os.close(descriptor)
        raise
    except OSError as exc:
        if descriptor != -1:
            os.close(descriptor)
        raise CatalogError("catalog staging parent is unreadable") from exc


def _write_temp(
    directory: Path, basename: str, data: bytes, mode: int, uid: int, gid: int
) -> StagedFile:
    _validate_platform_id(uid, "UID")
    _validate_platform_id(gid, "GID")
    parent_descriptor = _open_directory_descriptor(directory)
    staging_name: str | None = None
    staging_directory: Path | None = None
    staging_created_stat: os.stat_result | None = None
    staging_descriptor = -1
    descriptor = -1
    temporary_name: str | None = None
    completed = False
    try:
        for _ in range(20):
            candidate = f".{basename}.staging-{secrets.token_hex(16)}"
            try:
                os.mkdir(candidate, 0o700, dir_fd=parent_descriptor)
            except FileExistsError:
                continue
            staging_name = candidate
            staging_created_stat = os.stat(
                candidate,
                dir_fd=parent_descriptor,
                follow_symlinks=False,
            )
            break
        if staging_name is None:
            raise CatalogError("catalog staging directory could not be created")
        staging_directory = directory / staging_name
        directory_flags = os.O_RDONLY | getattr(os, "O_CLOEXEC", 0)
        if hasattr(os, "O_DIRECTORY"):
            directory_flags |= os.O_DIRECTORY
        if hasattr(os, "O_NOFOLLOW"):
            directory_flags |= os.O_NOFOLLOW
        staging_descriptor = os.open(
            staging_name,
            directory_flags,
            dir_fd=parent_descriptor,
        )
        staging_path_stat = os.stat(
            staging_name,
            dir_fd=parent_descriptor,
            follow_symlinks=False,
        )
        staging_descriptor_stat = os.fstat(staging_descriptor)
        if (
            not stat.S_ISDIR(staging_descriptor_stat.st_mode)
            or staging_descriptor_stat.st_mode & 0o077
            or staging_path_stat.st_dev != staging_descriptor_stat.st_dev
            or staging_path_stat.st_ino != staging_descriptor_stat.st_ino
        ):
            raise CatalogError("catalog staging directory changed")

        file_flags = (
            os.O_RDWR
            | os.O_CREAT
            | os.O_EXCL
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0)
        )
        for _ in range(20):
            candidate = f".{basename}.{secrets.token_hex(16)}.tmp"
            try:
                descriptor = os.open(
                    candidate,
                    file_flags,
                    0o600,
                    dir_fd=staging_descriptor,
                )
            except FileExistsError:
                continue
            temporary_name = candidate
            break
        if descriptor == -1 or temporary_name is None:
            raise CatalogError("catalog staging file could not be created")
        temporary_stat = os.fstat(descriptor)
        temporary_path_stat = os.stat(
            temporary_name,
            dir_fd=staging_descriptor,
            follow_symlinks=False,
        )
        if (
            not stat.S_ISREG(temporary_stat.st_mode)
            or temporary_stat.st_nlink != 1
            or stat.S_ISLNK(temporary_path_stat.st_mode)
            or not stat.S_ISREG(temporary_path_stat.st_mode)
            or temporary_path_stat.st_nlink != 1
            or temporary_path_stat.st_dev != temporary_stat.st_dev
            or temporary_path_stat.st_ino != temporary_stat.st_ino
        ):
            raise CatalogError("catalog staging file changed")
        os.fchown(descriptor, uid, gid)
        os.fchmod(descriptor, mode)
        remaining = memoryview(data)
        while remaining:
            written = os.write(descriptor, remaining)
            if written <= 0:
                raise OSError(errno.EIO, "catalog staging write made no progress")
            remaining = remaining[written:]
        os.fsync(descriptor)
        completed = True
    except CatalogError:
        raise
    except (OSError, IOError, OverflowError, ValueError) as exc:
        raise CatalogError("catalog staging failed") from exc
    finally:
        if not completed and descriptor != -1:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if not completed and temporary_name is not None and staging_descriptor != -1:
            try:
                os.unlink(temporary_name, dir_fd=staging_descriptor)
            except (FileNotFoundError, OSError):
                pass
        if not completed and staging_name is not None:
            try:
                staging_path_stat = os.stat(
                    staging_name,
                    dir_fd=parent_descriptor,
                    follow_symlinks=False,
                )
                staging_descriptor_stat = (
                    os.fstat(staging_descriptor)
                    if staging_descriptor != -1
                    else staging_created_stat
                )
                if (
                    staging_descriptor_stat is not None
                    and stat.S_ISDIR(staging_path_stat.st_mode)
                    and staging_path_stat.st_dev == staging_descriptor_stat.st_dev
                    and staging_path_stat.st_ino == staging_descriptor_stat.st_ino
                ):
                    os.rmdir(staging_name, dir_fd=parent_descriptor)
            except (FileNotFoundError, OSError):
                pass
        if not completed:
            if staging_descriptor != -1:
                os.close(staging_descriptor)
            os.close(parent_descriptor)
    assert staging_directory is not None
    assert staging_name is not None
    assert temporary_name is not None
    return StagedFile(
        staging_directory / temporary_name,
        descriptor,
        staging_directory,
        staging_descriptor,
        directory,
        parent_descriptor,
        temporary_name,
    )


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


def _canonical_transaction_payload(payload: dict[str, Any]) -> bytes:
    try:
        return json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, UnicodeError, ValueError, RecursionError) as exc:
        raise CatalogError("catalog transaction cannot be authenticated") from exc


def _transaction_hmac(payload: dict[str, Any], key: bytes) -> str:
    return hmac.new(
        key,
        _canonical_transaction_payload(payload),
        hashlib.sha256,
    ).hexdigest()


def _transaction_key_for(fence: FenceGuard) -> bytes:
    if fence.transaction_key is None:
        raise FenceError("catalog transaction key is unavailable")
    return fence.transaction_key


def _authenticate_transaction_payload(
    payload: dict[str, Any], key: bytes
) -> dict[str, Any]:
    authenticated = dict(payload)
    authenticated[TRANSACTION_HMAC_FIELD] = _transaction_hmac(payload, key)
    return authenticated


def _verify_transaction_auth(value: object, key: bytes) -> None:
    if not isinstance(value, dict):
        raise CatalogError("catalog transaction is malformed")
    tag = value.get(TRANSACTION_HMAC_FIELD)
    if not isinstance(tag, str) or len(tag) != hashlib.sha256().digest_size * 2:
        raise CatalogError("catalog transaction authentication is missing")
    unsigned = dict(value)
    unsigned.pop(TRANSACTION_HMAC_FIELD, None)
    try:
        tag_bytes = bytes.fromhex(tag)
    except (UnicodeError, ValueError) as exc:
        raise CatalogError("catalog transaction authentication is malformed") from exc
    if len(tag_bytes) != hashlib.sha256().digest_size:
        raise CatalogError("catalog transaction authentication is malformed")
    expected = bytes.fromhex(_transaction_hmac(unsigned, key))
    if not hmac.compare_digest(tag_bytes, expected):
        raise CatalogError("catalog transaction authentication failed")


def _snapshot_from_payload(value: object) -> FileSnapshot:
    if not isinstance(value, dict) or not isinstance(value.get("existed"), bool):
        raise CatalogError("catalog transaction is malformed")
    mode = value.get("mode")
    uid = _validate_platform_id(value.get("uid"), "UID")
    gid = _validate_platform_id(value.get("gid"), "GID")
    if (
        isinstance(mode, bool)
        or not isinstance(mode, int)
        or not 0 <= mode <= 0o777
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


def _validate_snapshot_permissions(
    snapshot: FileSnapshot, *, registry: bool
) -> None:
    if registry:
        unsafe = bool(snapshot.mode & 0o007) or (
            snapshot.mode & REGISTRY_MODE
        ) != REGISTRY_MODE
    else:
        unsafe = bool(snapshot.mode & 0o002)
    if unsafe:
        description = "registry" if registry else "HTML output"
        raise CatalogError(
            f"catalog transaction {description} snapshot permissions are unsafe"
        )


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
    state: str


def _transaction_path(registry_path: Path) -> Path:
    return registry_path.with_name(registry_path.name + ".txn")


def _cleanup_transaction_path(journal_path: Path) -> Path:
    return journal_path.with_name(journal_path.name + ".cleanup")


def _reserved_catalog_paths(registry_path: Path) -> set[Path]:
    journal_path = _transaction_path(registry_path)
    return {
        registry_path.resolve(strict=False),
        registry_path.with_name(registry_path.name + ".lock").resolve(strict=False),
        journal_path.resolve(strict=False),
        _cleanup_transaction_path(journal_path).resolve(strict=False),
    }


def _transaction_payload(
    registry_path: Path,
    output_path: Path,
    owner: str,
    generation: int,
    registry_old: FileSnapshot,
    output_old: FileSnapshot,
    registry_new: FileSnapshot,
    output_new: FileSnapshot,
    *,
    state: str = "rollback",
) -> dict[str, Any]:
    return {
        "version": TRANSACTION_VERSION,
        "state": state,
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
    fence: FenceGuard,
) -> None:
    authenticated_payload = _authenticate_transaction_payload(
        payload, _transaction_key_for(fence)
    )
    data = (
        json.dumps(authenticated_payload, ensure_ascii=False, sort_keys=True) + "\n"
    ).encode("utf-8")
    if len(data) > MAX_TRANSACTION_BYTES:
        raise CatalogError("catalog transaction is too large")
    staged = _write_temp(
        journal_path.parent,
        journal_path.name,
        data,
        SIDECAR_MODE,
        os.geteuid(),
        _sidecar_gid(journal_path.parent),
    )
    try:
        fence.replace(staged, journal_path)
        _fsync_directory(journal_path.parent)
    finally:
        _cleanup_staged_file(staged)


def _load_transaction(
    journal_path: Path,
    registry_path: Path,
    output_path: Path,
    fence: FenceGuard,
) -> CatalogTransaction | None:
    if not _path_exists(journal_path):
        return None
    try:
        journal_stat, data = _read_regular_file(
            journal_path, MAX_TRANSACTION_BYTES, "catalog transaction"
        )
        if (
            (journal_stat.st_mode & 0o007)
            or (journal_stat.st_mode & SIDECAR_MODE) != SIDECAR_MODE
        ):
            raise CatalogError("catalog transaction sidecar permissions are unsafe")
        value = json.loads(data.decode("utf-8"))
    except CatalogError:
        raise
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise CatalogError("catalog transaction is unreadable") from exc
    _verify_transaction_auth(value, _transaction_key_for(fence))
    if not isinstance(value, dict) or value.get("version") != TRANSACTION_VERSION:
        raise CatalogError("catalog transaction is malformed")
    state = value.get("state")
    if state not in {
        "rollback",
        "committed",
        "prepared",
        "cleanup",
        "cleared",
    }:
        raise CatalogError("catalog transaction state is invalid")
    if state in {"cleanup", "cleared"}:
        cleanup_of = value.get("cleanup_of")
        if cleanup_of not in {"rollback", "committed"}:
            raise CatalogError("catalog cleanup marker is malformed")
    expected_registry = str(registry_path.resolve(strict=False))
    expected_output = str(output_path.resolve(strict=False))
    if (
        value.get("registry_path") != expected_registry
        or value.get("output_path") != expected_output
    ):
        raise CatalogError("catalog transaction targets different files")
    owner = _validate_fence_owner(value.get("fence_owner"))
    generation = _validate_fence_generation(value.get("fence_generation"))
    normalized_state = (
        f"cleanup:{value['cleanup_of']}"
        if state == "cleanup"
        else ("rollback" if state == "prepared" else state)
    )
    registry_old = _snapshot_from_payload(value.get("registry_old"))
    output_old = _snapshot_from_payload(value.get("output_old"))
    registry_new = _snapshot_from_payload(value.get("registry_new"))
    output_new = _snapshot_from_payload(value.get("output_new"))
    for snapshot in (registry_old, registry_new):
        _validate_snapshot_permissions(snapshot, registry=True)
    for snapshot in (output_old, output_new):
        _validate_snapshot_permissions(snapshot, registry=False)
    return CatalogTransaction(
        expected_registry,
        expected_output,
        owner,
        generation,
        registry_old,
        output_old,
        registry_new,
        output_new,
        normalized_state,
    )


def _load_cleanup_marker(
    marker_path: Path,
    registry_path: Path,
    output_path: Path,
    fence: FenceGuard,
) -> CatalogTransaction | None:
    transaction = _load_transaction(marker_path, registry_path, output_path, fence)
    if transaction is not None and transaction.state not in {
        "cleanup:rollback",
        "cleanup:committed",
        "cleared",
    }:
        raise CatalogError("catalog cleanup marker is invalid")
    return transaction


def _write_transaction_state(
    journal_path: Path,
    transaction: CatalogTransaction,
    fence: FenceGuard,
    state: str,
    *,
    cleanup_of: str | None = None,
) -> None:
    payload = _transaction_payload(
        Path(transaction.registry_path),
        Path(transaction.output_path),
        transaction.fence_owner,
        transaction.fence_generation,
        transaction.registry_old,
        transaction.output_old,
        transaction.registry_new,
        transaction.output_new,
        state=state,
    )
    if state in {"cleanup", "cleared"}:
        cleanup_phase = cleanup_of or transaction.state.removeprefix("cleanup:")
        if cleanup_phase not in {"rollback", "committed"}:
            raise CatalogError("catalog cleanup phase is invalid")
        payload["cleanup_of"] = cleanup_phase
    _write_transaction_journal(
        journal_path,
        payload,
        fence,
    )


def _clear_cleanup_marker(
    cleanup_path: Path,
    transaction: CatalogTransaction,
    fence: FenceGuard,
) -> None:
    if not _path_exists(cleanup_path):
        return
    cleanup_of = transaction.state.removeprefix("cleanup:")
    if cleanup_of == "cleared":
        fence.assert_current()
        return
    if cleanup_of not in {"rollback", "committed"}:
        raise CatalogError("catalog cleanup marker is invalid")
    try:
        _write_transaction_state(
            cleanup_path,
            transaction,
            fence,
            "cleared",
            cleanup_of=cleanup_of,
        )
        _fsync_directory(cleanup_path.parent)
    except (OSError, IOError) as exc:
        raise CatalogError("catalog cleanup marker sync failed") from exc


def _require_fresh_recovery_fence(
    transaction: CatalogTransaction, fence: FenceGuard
) -> None:
    if transaction.fence_generation == fence.generation:
        raise FenceError("pending recovery requires a new fence generation")


def _remove_transaction(
    journal_path: Path,
    transaction: CatalogTransaction,
    fence: FenceGuard,
    *,
    cleanup_of: str | None = None,
) -> None:
    cleanup_path = _cleanup_transaction_path(journal_path)
    _write_transaction_state(
        cleanup_path,
        transaction,
        fence,
        "cleanup",
        cleanup_of=cleanup_of,
    )
    if _path_exists(journal_path):
        try:
            fence.unlink(journal_path)
        except FileNotFoundError:
            pass
        _fsync_directory(journal_path.parent)
    _clear_cleanup_marker(cleanup_path, transaction, fence)


def _snapshot_matches(current: FileSnapshot, expected: FileSnapshot) -> bool:
    if not expected.existed:
        return not current.existed
    return current == expected


def _replace_snapshot(
    path: Path,
    snapshot: FileSnapshot,
    fence: FenceGuard,
    *,
    recovery: bool = False,
    registry: bool = False,
) -> None:
    if not snapshot.existed:
        if not _path_exists(path):
            return
        try:
            fence.unlink(path)
        except FileNotFoundError:
            return
        _fsync_directory(path.parent)
        return
    if snapshot.data is None:
        raise CatalogError("catalog replacement data is unavailable")
    uid, gid, mode = (
        _recovery_metadata(path, snapshot, registry=registry)
        if recovery
        else (snapshot.uid, snapshot.gid, snapshot.mode)
    )
    staged = _write_temp(
        path.parent,
        path.name,
        snapshot.data,
        mode,
        uid,
        gid,
    )
    try:
        fence.replace(staged, path)
        _fsync_directory(path.parent)
    finally:
        _cleanup_staged_file(staged)


def _reconcile_transaction(
    journal_path: Path,
    transaction: CatalogTransaction,
    fence: FenceGuard,
    *,
    rollback: bool,
) -> None:
    _validate_output_directory(Path(transaction.output_path).parent)
    _validate_registry_directory(Path(transaction.registry_path).parent)
    targets = (
        (
            Path(transaction.registry_path),
            transaction.registry_old,
            transaction.registry_new,
            True,
        ),
        (
            Path(transaction.output_path),
            transaction.output_old,
            transaction.output_new,
            False,
        ),
    )
    if rollback:
        for path, old, _new, is_registry in targets:
            _replace_snapshot(
                path,
                old,
                fence,
                recovery=True,
                registry=is_registry,
            )
        _remove_transaction(
            journal_path, transaction, fence, cleanup_of="rollback"
        )
        return
    current_states: list[tuple[Path, FileSnapshot, FileSnapshot, FileSnapshot]] = []
    for path, old, new, _is_registry in targets:
        current = _read_snapshot(path, old.mode)
        if not _snapshot_matches(current, old) and not _snapshot_matches(current, new):
            raise CatalogError("catalog transaction found unexpected file contents")
        current_states.append((path, current, old, new))
    for path, current, old, new in current_states:
        desired = new
        if current != desired:
            _replace_snapshot(path, desired, fence)
    _remove_transaction(
        journal_path, transaction, fence, cleanup_of="committed"
    )


def _write_catalog_files(
    registry_path: Path,
    output_path: Path,
    registry_data: bytes,
    html_data: bytes,
    fence: FenceGuard,
) -> None:
    if len(registry_data) > MAX_FILE_BYTES or len(html_data) > MAX_FILE_BYTES:
        raise CatalogError("generated catalog is too large")
    _validate_output_directory(output_path.parent)
    _validate_registry_directory(registry_path.parent)
    registry_old = _read_snapshot(registry_path, REGISTRY_MODE)
    if not registry_old.existed:
        registry_old = FileSnapshot(
            False,
            None,
            REGISTRY_MODE,
            os.geteuid(),
            _sidecar_gid(registry_path.parent),
        )
    output_old = _read_snapshot(output_path, 0o644)
    registry_uid, registry_gid, registry_mode = _registry_metadata(
        registry_old, registry_path.parent
    )
    output_uid, output_gid, output_mode = _output_metadata(output_old)
    registry_new = FileSnapshot(
        True,
        registry_data,
        registry_mode,
        registry_uid,
        registry_gid,
    )
    output_new = FileSnapshot(
        True,
        html_data,
        output_mode,
        output_uid,
        output_gid,
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
        "rollback",
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
        fence,
    )
    try:
        _replace_snapshot(registry_path, registry_new, fence)
        _replace_snapshot(output_path, output_new, fence)
    except FenceError as exc:
        raise CatalogError(
            "catalog fence changed; authorized recovery is required"
        ) from exc
    except (OSError, IOError, CatalogError) as exc:
        try:
            _write_transaction_state(journal_path, transaction, fence, "rollback")
        except FenceError as mark_exc:
            raise CatalogError(
                "catalog update failed; authorized recovery is required"
            ) from mark_exc
        except (OSError, IOError, CatalogError) as mark_exc:
            raise CatalogError(
                "catalog update failed; pending transaction needs recovery"
            ) from mark_exc
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
        _write_transaction_state(journal_path, transaction, fence, "committed")
    except FenceError as exc:
        raise CatalogError(
            "catalog committed; authorized recovery must reconcile its journal"
        ) from exc
    except (OSError, IOError, CatalogError) as exc:
        raise CatalogError(
            "catalog committed; pending transaction journal needs reconciliation"
        ) from exc
    try:
        _remove_transaction(
            journal_path, transaction, fence, cleanup_of="committed"
        )
    except FenceError as exc:
        raise CatalogError(
            "catalog committed; authorized recovery must remove its journal"
        ) from exc
    except (OSError, IOError, CatalogError) as exc:
        raise CatalogError(
            "catalog committed; pending transaction journal needs reconciliation"
        ) from exc


@contextmanager
def _catalog_lock(registry_path: Path, fence: FenceGuard) -> Iterator[None]:
    _validate_registry_directory(registry_path.parent)
    lock_path = registry_path.with_name(registry_path.name + ".lock")
    try:
        descriptor = os.open(
            lock_path,
            os.O_RDWR
            | os.O_CREAT
            | getattr(os, "O_CLOEXEC", 0)
            | getattr(os, "O_NOFOLLOW", 0),
            SIDECAR_MODE,
        )
    except OSError as exc:
        raise CatalogError("cannot create the catalog lock") from exc
    locked = False
    try:
        _acquire_exclusive_lock(
            descriptor, CatalogError, "catalog lock is unavailable"
        )
        locked = True
        _prepare_sidecar(descriptor, registry_path.parent, fence)
        yield
    except CatalogError:
        raise
    except OSError as exc:
        raise CatalogError("catalog lock failed") from exc
    finally:
        if locked:
            try:
                fcntl.flock(descriptor, fcntl.LOCK_UN)
            finally:
                os.close(descriptor)
        else:
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
    registry_resolved = registry_path.resolve(strict=False)
    output_resolved = output_path.resolve(strict=False)
    if registry_resolved == output_resolved:
        raise CatalogError("registry and HTML output must be different files")
    if registry_path.name.endswith((".lock", ".txn", ".txn.cleanup")):
        raise CatalogError("registry path uses a reserved catalog sidecar name")
    reserved_paths = _reserved_catalog_paths(registry_path)
    if output_resolved in reserved_paths:
        raise CatalogError("HTML output collides with a reserved catalog sidecar")
    if fence_file is not None:
        fence_path = Path(fence_file)
        fence_resolved = fence_path.resolve(strict=False)
        fence_lock_resolved = _fence_lock_path(fence_path).resolve(strict=False)
        if fence_resolved in (reserved_paths | {output_resolved}) or (
            fence_lock_resolved in (reserved_paths | {output_resolved})
        ):
            raise CatalogError("catalog fence collides with a reserved catalog sidecar")
    if recover_pending and (
        initialize or service_name is not None or deployment_address is not None
    ):
        raise CatalogError("recover-pending cannot include a catalog update")

    with _fenced_mutation(fence_file, fence_owner, fence_generation) as fence:
        _validate_output_directory(output_path.parent)
        if recover_pending:
            if fence.role != "recovery":
                raise FenceError("pending recovery requires a recovery fence")
            with _catalog_lock(registry_path, fence):
                journal_path = _transaction_path(registry_path)
                cleanup_path = _cleanup_transaction_path(journal_path)
                transaction = _load_transaction(
                    journal_path, registry_path, output_path, fence
                )
                if transaction is None:
                    cleanup = _load_cleanup_marker(
                        cleanup_path, registry_path, output_path, fence
                    )
                    if cleanup is None:
                        raise CatalogError(
                            "no pending catalog transaction to recover"
                        )
                    _require_fresh_recovery_fence(cleanup, fence)
                    _clear_cleanup_marker(cleanup_path, cleanup, fence)
                    return {"status": "recovered"}
                if transaction.state.startswith("cleanup:") or (
                    transaction.state == "cleared"
                ):
                    raise CatalogError("catalog cleanup marker is misplaced")
                _require_fresh_recovery_fence(transaction, fence)
                _reconcile_transaction(
                    journal_path, transaction, fence, rollback=True
                )
            return {"status": "recovered"}

        if fence.role != "deployment":
            raise FenceError("normal catalog mutation requires a deployment fence")
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
        elif service_name is None or deployment_address is None:
            raise CatalogError("service name and deployment address are required")
        else:
            service_name = _validate_service_name(service_name)
            deployment_address = _validate_deployment_address(
                deployment_address, current_ip
            )

        with _catalog_lock(registry_path, fence):
            journal_path = _transaction_path(registry_path)
            cleanup_path = _cleanup_transaction_path(journal_path)
            transaction = _load_transaction(
                journal_path, registry_path, output_path, fence
            )
            if transaction is not None:
                if transaction.state.startswith("cleanup:") or (
                    transaction.state == "cleared"
                ):
                    raise CatalogError("catalog cleanup marker is misplaced")
                same_fence = (
                    transaction.fence_owner == fence.owner
                    and transaction.fence_generation == fence.generation
                )
                if not same_fence:
                    raise FenceError(
                        "pending catalog transaction requires authorized recovery"
                    )
                if transaction.state == "rollback":
                    _reconcile_transaction(
                        journal_path, transaction, fence, rollback=True
                    )
                elif transaction.state == "committed":
                    _reconcile_transaction(
                        journal_path, transaction, fence, rollback=False
                    )
                else:
                    raise CatalogError("catalog transaction state is invalid")
            elif _path_exists(cleanup_path):
                cleanup = _load_cleanup_marker(
                    cleanup_path, registry_path, output_path, fence
                )
                if cleanup is not None:
                    _clear_cleanup_marker(cleanup_path, cleanup, fence)
            _prepare_registry(registry_path, fence)
            registry = _load_registry(registry_path, current_ip, output_path)
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
            locked_ip = _discover_tailscale_ip()
            if locked_ip != current_ip:
                raise CatalogError(
                    "local Tailscale IPv4 changed while acquiring the catalog lock"
                )
            current_ip = locked_ip
            if not initialize:
                deployment_address = _validate_deployment_address(
                    deployment_address, current_ip
                )
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
