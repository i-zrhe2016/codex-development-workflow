#!/usr/bin/env python3

from __future__ import annotations

from contextlib import redirect_stderr
import hashlib
import io
import json
import os
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

import update_access_catalog as catalog  # noqa: E402
from update_access_catalog import (  # noqa: E402
    CatalogError,
    FenceError,
    main,
    update_catalog,
)


TAILSCALE_IP = ".".join(("100", "64", "12", "34"))
OTHER_TAILSCALE_IP = ".".join(("100", "64", "12", "35"))
DOCUMENTATION_IP = ".".join(("192", "0", "2", "1"))


class AccessCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="access-catalog-test-")
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.root = root
        self.registry = root / "catalog.json"
        self.output = root / "index.html"
        self.fence = root / "catalog-fence.json"
        self.fence.write_text(
            json.dumps(
                {
                    "state": "active",
                    "role": "deployment",
                    "owner": "deployment-run-1",
                    "generation": 1,
                    "expires_at": "2099-01-01T00:00:00Z",
                    "catalog_hmac_key": hashlib.sha256(
                        b"access-catalog-unit-test-key"
                    ).hexdigest(),
                }
            ),
            encoding="utf-8",
        )
        self.fence.chmod(0o600)
        self.fence_lock = self.fence.with_name(self.fence.name + ".lock")
        self.fence_lock.touch(mode=0o600)

    def run_update(self, *arguments: str) -> int:
        with patch(
            "update_access_catalog._discover_tailscale_ip",
            return_value=TAILSCALE_IP,
        ):
            return main(
                [
                    "--registry",
                    str(self.registry),
                    "--output",
                    str(self.output),
                    "--fence-file",
                    str(self.fence),
                    "--fence-owner",
                    "deployment-run-1",
                    "--fence-generation",
                    "1",
                    *arguments,
                ]
            )

    def update(self, **arguments: object) -> dict[str, object]:
        registry = Path(arguments.pop("registry", self.registry))
        output = Path(arguments.pop("output", self.output))
        arguments.update(
            {
                "fence_file": self.fence,
                "fence_owner": "deployment-run-1",
                "fence_generation": 1,
            }
        )
        with patch(
            "update_access_catalog._discover_tailscale_ip",
            return_value=TAILSCALE_IP,
        ):
            return update_catalog(registry, output, **arguments)

    def read_registry(self) -> dict[str, object]:
        return json.loads(self.registry.read_text(encoding="utf-8"))

    def leave_pending_transaction(self) -> Path:
        real_replace = catalog._replace_snapshot

        def interrupt_before_page(path: Path, snapshot: object, fence: object) -> None:
            if path == self.output:
                raise FenceError("simulated fence interruption")
            real_replace(path, snapshot, fence)

        with patch(
            "update_access_catalog._replace_snapshot",
            side_effect=interrupt_before_page,
        ):
            with self.assertRaises(CatalogError):
                self.update(
                    service_name="api",
                    deployment_address=f"http://{TAILSCALE_IP}:8080/",
                )
        transaction_path = self.registry.with_name("catalog.json.txn")
        self.assertTrue(transaction_path.exists())
        return transaction_path

    def use_recovery_fence(self) -> None:
        fence = json.loads(self.fence.read_text(encoding="utf-8"))
        fence.update(
            {"role": "recovery", "owner": "recovery-run-1", "generation": 2}
        )
        self.fence.write_text(json.dumps(fence), encoding="utf-8")
        self.fence.chmod(0o600)

    def test_initialize_writes_ip_and_empty_page(self) -> None:
        self.assertEqual(self.run_update("--initialize"), 0)

        registry = self.read_registry()
        self.assertEqual(registry["tailscale_ip"], TAILSCALE_IP)
        self.assertEqual(registry["services"], [])
        page = self.output.read_text(encoding="utf-8")
        self.assertIn("Deployment Access Catalog", page)
        self.assertIn(TAILSCALE_IP, page)
        self.assertIn("No services recorded.", page)
        self.assertTrue(self.registry.with_name("catalog.json.lock").exists())
        self.assertFalse(self.registry.with_name("catalog.json.txn").exists())
        self.assertEqual(self.registry.stat().st_mode & 0o777, 0o660)

    def test_missing_fence_lock_is_rejected_without_recreation(self) -> None:
        self.fence_lock.unlink()

        with self.assertRaises(FenceError):
            self.update(initialize=True)

        self.assertFalse(self.fence_lock.exists())

    def test_discovers_one_local_tailscale_ip_when_not_supplied(self) -> None:
        completed = subprocess.CompletedProcess(
            ["tailscale", "ip", "-4"], 0, f"{TAILSCALE_IP}\n", ""
        )
        with patch("update_access_catalog.subprocess.run", return_value=completed) as run:
            update_catalog(
                self.registry,
                self.output,
                service_name="api",
                deployment_address=f"http://{TAILSCALE_IP}:8080/",
                fence_file=self.fence,
                fence_owner="deployment-run-1",
                fence_generation=1,
            )

        self.assertEqual(run.call_args.args[0], ["tailscale", "ip", "-4"])
        self.assertEqual(run.call_args.kwargs["timeout"], 5)
        self.assertEqual(self.read_registry()["tailscale_ip"], TAILSCALE_IP)

    def test_rechecks_tailscale_ip_after_acquiring_catalog_lock(self) -> None:
        with patch(
            "update_access_catalog._discover_tailscale_ip",
            side_effect=(TAILSCALE_IP, OTHER_TAILSCALE_IP),
        ) as discover:
            with self.assertRaises(CatalogError):
                update_catalog(
                    self.registry,
                    self.output,
                    service_name="api",
                    deployment_address=f"http://{TAILSCALE_IP}:8080/",
                    fence_file=self.fence,
                    fence_owner="deployment-run-1",
                    fence_generation=1,
                )
        self.assertEqual(discover.call_count, 2)
        self.assertFalse(self.registry.exists())
        self.assertFalse(self.output.exists())

    def test_new_service_is_escaped_and_linked(self) -> None:
        service = "<img src=x onerror=alert(1)>"
        address = f"https://{TAILSCALE_IP}:8443/app"

        self.assertEqual(
            self.run_update(
                "--service-name",
                service,
                "--deployment-address",
                address,
            ),
            0,
        )

        registry = self.read_registry()
        self.assertEqual(len(registry["services"]), 1)
        page = self.output.read_text(encoding="utf-8")
        self.assertIn("&lt;img src=x onerror=alert(1)&gt;", page)
        self.assertNotIn("<img src=x onerror=alert(1)>", page)
        self.assertIn(f"https://{TAILSCALE_IP}:8443/app", page)

    def test_same_service_replaces_and_unrelated_service_survives(self) -> None:
        self.assertEqual(
            self.run_update(
                "--service-name",
                "api",
                "--deployment-address",
                f"http://{TAILSCALE_IP}:8001/old",
            ),
            0,
        )
        self.assertEqual(
            self.run_update(
                "--service-name",
                "worker",
                "--deployment-address",
                f"http://{TAILSCALE_IP}:8002/worker",
            ),
            0,
        )
        self.assertEqual(
            self.run_update(
                "--service-name",
                "API",
                "--deployment-address",
                f"https://{TAILSCALE_IP}:9001/new",
            ),
            0,
        )

        services = self.read_registry()["services"]
        self.assertEqual([service["name"] for service in services], ["API", "worker"])
        self.assertEqual(services[0]["address"], f"https://{TAILSCALE_IP}:9001/new")

    def test_rejects_public_different_host_and_unsafe_addresses(self) -> None:
        for address in (
            f"http://{DOCUMENTATION_IP}:8080/",
            f"http://{OTHER_TAILSCALE_IP}:8080/",
            f"javascript://{TAILSCALE_IP}/bad",
            f"http://user:pass@{TAILSCALE_IP}:8080/",
            f"http://{TAILSCALE_IP}:8080/?query=value",
        ):
            with self.subTest(address=address):
                with self.assertRaises(CatalogError):
                    self.update(
                        tailscale_ip=TAILSCALE_IP,
                        service_name="api",
                        deployment_address=address,
                    )
        self.assertFalse(self.registry.exists())
        self.assertFalse(self.output.exists())

    def test_rejects_invalid_tailscale_ip(self) -> None:
        with self.assertRaises(CatalogError):
            self.update(
                tailscale_ip=DOCUMENTATION_IP,
                service_name="api",
                deployment_address=f"http://{DOCUMENTATION_IP}:8080/",
            )

    def test_malformed_registry_fails_closed(self) -> None:
        self.registry.write_text("{\"services\": \"not-a-list\"}\n", encoding="utf-8")

        with self.assertRaises(CatalogError):
            self.update(
                tailscale_ip=TAILSCALE_IP,
                service_name="api",
                deployment_address=f"http://{TAILSCALE_IP}:8080/",
            )
        self.assertFalse(self.output.exists())

    def test_existing_registry_cannot_be_reused_by_another_tailscale_host(self) -> None:
        self.assertEqual(
            self.run_update(
                "--service-name",
                "api",
                "--deployment-address",
                f"http://{TAILSCALE_IP}:8080/",
            ),
            0,
        )
        with patch(
            "update_access_catalog._discover_tailscale_ip",
            return_value=OTHER_TAILSCALE_IP,
        ):
            with self.assertRaises(CatalogError):
                update_catalog(
                    self.registry,
                    self.output,
                    service_name="worker",
                    deployment_address=f"http://{OTHER_TAILSCALE_IP}:8081/",
                    fence_file=self.fence,
                    fence_owner="deployment-run-1",
                    fence_generation=1,
                )

    def test_caller_ip_must_match_fresh_local_discovery(self) -> None:
        with patch(
            "update_access_catalog._discover_tailscale_ip",
            return_value=OTHER_TAILSCALE_IP,
        ):
            with self.assertRaises(CatalogError):
                update_catalog(
                    self.registry,
                    self.output,
                    tailscale_ip=TAILSCALE_IP,
                    service_name="api",
                    deployment_address=f"http://{OTHER_TAILSCALE_IP}:8080/",
                    fence_file=self.fence,
                    fence_owner="deployment-run-1",
                    fence_generation=1,
                )

    def test_stale_fence_is_rejected(self) -> None:
        fence = json.loads(self.fence.read_text(encoding="utf-8"))
        fence["generation"] = 2
        self.fence.write_text(json.dumps(fence), encoding="utf-8")
        self.fence.chmod(0o600)

        with patch(
            "update_access_catalog._discover_tailscale_ip",
            side_effect=AssertionError("recovery must not discover Tailscale"),
        ):
            with self.assertRaises(FenceError):
                update_catalog(
                    self.registry,
                    self.output,
                    service_name="api",
                    deployment_address=f"http://{TAILSCALE_IP}:8080/",
                    fence_file=self.fence,
                    fence_owner="deployment-run-1",
                    fence_generation=1,
                )
        self.assertFalse(self.registry.exists())

    def test_fence_role_is_pinned_for_the_operation(self) -> None:
        with catalog._fenced_mutation(
            self.fence, "deployment-run-1", 1
        ) as fence:
            record = json.loads(self.fence.read_text(encoding="utf-8"))
            record["role"] = "recovery"
            self.fence.write_text(json.dumps(record), encoding="utf-8")
            self.fence.chmod(0o600)
            with self.assertRaises(FenceError):
                fence.assert_current()

    def test_hard_linked_fence_alias_is_rejected(self) -> None:
        alias = self.root / "fence-alias.json"
        alias_lock = alias.with_name(alias.name + ".lock")
        os.link(self.fence, alias)
        alias_lock.touch(mode=0o600)

        with self.assertRaises(FenceError):
            update_catalog(
                self.registry,
                self.output,
                initialize=True,
                fence_file=alias,
                fence_owner="deployment-run-1",
                fence_generation=1,
            )

    def test_replacement_rejects_a_swapped_source_alias(self) -> None:
        real_replace = catalog.os.replace

        def swap_source(
            source: object,
            destination: object,
            *,
            src_dir_fd: int | None = None,
            dst_dir_fd: int | None = None,
        ) -> None:
            if destination == self.output.name:
                attacker = self.root / "attacker.html"
                attacker.write_text("attacker", encoding="utf-8")
                assert src_dir_fd is not None
                os.unlink(source, dir_fd=src_dir_fd)
                os.symlink(attacker, source, dir_fd=src_dir_fd)
            real_replace(
                source,
                destination,
                src_dir_fd=src_dir_fd,
                dst_dir_fd=dst_dir_fd,
            )

        with patch.object(catalog.os, "replace", side_effect=swap_source):
            with self.assertRaises(CatalogError):
                self.update(initialize=True)

        self.assertTrue(self.output.is_symlink())

    def test_fence_authority_lock_blocks_replacement_by_new_generation(self) -> None:
        replacement = self.root / "replacement-fence.json"
        replacement.write_text(
            json.dumps(
                {
                    "state": "active",
                    "role": "recovery",
                    "owner": "recovery-run-1",
                    "generation": 2,
                    "expires_at": "2099-01-01T00:00:00Z",
                }
            ),
            encoding="utf-8",
        )
        replacement.chmod(0o600)
        with catalog._fenced_mutation(
            self.fence, "deployment-run-1", 1
        ):
            os.replace(replacement, self.fence)
            with patch.object(catalog, "LOCK_TIMEOUT_SECONDS", 0.0):
                with self.assertRaises(FenceError):
                    with catalog._fenced_mutation(
                        self.fence, "recovery-run-1", 2
                    ):
                        pass

    def test_pending_transaction_is_reconciled_before_next_update(self) -> None:
        real_replace = catalog._replace_snapshot

        def interrupt_before_page(path: Path, snapshot: object, check: object) -> None:
            if path == self.output:
                raise FenceError("simulated fence interruption")
            real_replace(path, snapshot, check)

        with patch(
            "update_access_catalog._replace_snapshot",
            side_effect=interrupt_before_page,
        ):
            with self.assertRaises(CatalogError):
                self.update(
                    service_name="api",
                    deployment_address=f"http://{TAILSCALE_IP}:8080/",
                )
        self.assertTrue(self.registry.with_name("catalog.json.txn").exists())
        self.assertEqual(
            json.loads(
                self.registry.with_name("catalog.json.txn").read_text(encoding="utf-8")
            )["state"],
            "rollback",
        )
        self.assertTrue(self.registry.exists())
        self.assertFalse(self.output.exists())
        self.assertEqual(
            self.registry.with_name("catalog.json.lock").stat().st_mode & 0o777,
            0o660,
        )
        self.assertEqual(
            self.registry.with_name("catalog.json.txn").stat().st_mode & 0o777,
            0o660,
        )

        self.update(
            service_name="api",
            deployment_address=f"https://{TAILSCALE_IP}:8443/",
        )
        self.assertFalse(self.registry.with_name("catalog.json.txn").exists())
        self.assertIn(
            f"https://{TAILSCALE_IP}:8443/", self.output.read_text(encoding="utf-8")
        )

    def test_cleanup_marker_survives_a_racing_journal_unlink(self) -> None:
        real_unlink = catalog.FenceGuard.unlink

        def unlink_then_lose_fence(guard: catalog.FenceGuard, path: Path) -> None:
            if path == self.registry.with_name("catalog.json.txn"):
                real_unlink(guard, path)
                raise FenceError("simulated fence change after journal unlink")
            real_unlink(guard, path)

        with patch.object(
            catalog.FenceGuard,
            "unlink",
            autospec=True,
            side_effect=unlink_then_lose_fence,
        ):
            with self.assertRaises(CatalogError):
                self.update(
                    service_name="api",
                    deployment_address=f"http://{TAILSCALE_IP}:8080/",
                )

        cleanup_marker = self.registry.with_name("catalog.json.txn.cleanup")
        self.assertFalse(self.registry.with_name("catalog.json.txn").exists())
        self.assertEqual(
            json.loads(cleanup_marker.read_text(encoding="utf-8"))["cleanup_of"],
            "committed",
        )

        fence = json.loads(self.fence.read_text(encoding="utf-8"))
        fence.update({"role": "recovery", "owner": "recovery-run-1", "generation": 2})
        self.fence.write_text(json.dumps(fence), encoding="utf-8")
        self.fence.chmod(0o600)
        with patch(
            "update_access_catalog._discover_tailscale_ip",
            side_effect=AssertionError("recovery must not discover Tailscale"),
        ):
            result = update_catalog(
                self.registry,
                self.output,
                fence_file=self.fence,
                fence_owner="recovery-run-1",
                fence_generation=2,
                recover_pending=True,
            )

        self.assertEqual(result["status"], "recovered")
        self.assertTrue(self.registry.exists())
        self.assertTrue(self.output.exists())
        self.assertEqual(
            json.loads(cleanup_marker.read_text(encoding="utf-8"))["state"],
            "cleared",
        )

    def test_recovery_rejects_unsafe_transaction_snapshot_permissions(self) -> None:
        real_replace = catalog._replace_snapshot

        def interrupt_before_page(path: Path, snapshot: object, fence: object) -> None:
            if path == self.output:
                raise FenceError("simulated fence interruption")
            real_replace(path, snapshot, fence)

        with patch(
            "update_access_catalog._replace_snapshot",
            side_effect=interrupt_before_page,
        ):
            with self.assertRaises(CatalogError):
                self.update(
                    service_name="api",
                    deployment_address=f"http://{TAILSCALE_IP}:8080/",
                )

        transaction_path = self.registry.with_name("catalog.json.txn")
        transaction = json.loads(transaction_path.read_text(encoding="utf-8"))
        transaction["output_old"]["mode"] = 0o666
        transaction_path.write_text(json.dumps(transaction), encoding="utf-8")
        transaction_path.chmod(0o660)

        fence = json.loads(self.fence.read_text(encoding="utf-8"))
        fence.update({"role": "recovery", "owner": "recovery-run-1", "generation": 2})
        self.fence.write_text(json.dumps(fence), encoding="utf-8")
        self.fence.chmod(0o600)
        with self.assertRaises(CatalogError):
            update_catalog(
                self.registry,
                self.output,
                fence_file=self.fence,
                fence_owner="recovery-run-1",
                fence_generation=2,
                recover_pending=True,
            )
        self.assertTrue(transaction_path.exists())

    def test_recovery_rejects_tampered_transaction_snapshot(self) -> None:
        transaction_path = self.leave_pending_transaction()
        transaction = json.loads(transaction_path.read_text(encoding="utf-8"))
        transaction["registry_old"]["data"] = "YXR0YWNrZXI="
        transaction_path.write_text(json.dumps(transaction), encoding="utf-8")
        transaction_path.chmod(0o660)
        self.use_recovery_fence()

        with self.assertRaisesRegex(CatalogError, "authentication"):
            update_catalog(
                self.registry,
                self.output,
                fence_file=self.fence,
                fence_owner="recovery-run-1",
                fence_generation=2,
                recover_pending=True,
            )
        self.assertTrue(transaction_path.exists())

    def test_malformed_json_loads_fail_closed_without_traceback(self) -> None:
        self.registry.write_text(
            '{"malformed": ' + ("9" * 5000) + "}\n", encoding="utf-8"
        )
        self.registry.chmod(0o660)

        with redirect_stderr(io.StringIO()):
            self.assertEqual(
                self.run_update(
                    "--service-name",
                    "api",
                    "--deployment-address",
                    f"http://{TAILSCALE_IP}:8080/",
                ),
                2,
            )

    def test_fence_recursion_error_fails_closed(self) -> None:
        self.fence.write_text("[" * 2000 + "]" * 2000, encoding="utf-8")
        self.fence.chmod(0o600)

        with self.assertRaises(FenceError):
            self.update(initialize=True)

    def test_transaction_recursion_error_fails_closed(self) -> None:
        transaction_path = self.leave_pending_transaction()
        transaction_path.write_text("[" * 2000 + "]" * 2000, encoding="utf-8")
        transaction_path.chmod(0o660)
        self.use_recovery_fence()

        with self.assertRaises(CatalogError):
            update_catalog(
                self.registry,
                self.output,
                fence_file=self.fence,
                fence_owner="recovery-run-1",
                fence_generation=2,
                recover_pending=True,
            )

    def test_recovery_rejects_platform_invalid_snapshot_id(self) -> None:
        transaction_path = self.leave_pending_transaction()
        transaction = json.loads(transaction_path.read_text(encoding="utf-8"))
        transaction["registry_old"]["uid"] = catalog.PLATFORM_ID_MAX + 1
        transaction.pop(catalog.TRANSACTION_HMAC_FIELD, None)
        transaction = catalog._authenticate_transaction_payload(
            transaction,
            bytes.fromhex(
                json.loads(self.fence.read_text(encoding="utf-8"))[
                    catalog.TRANSACTION_KEY_FIELD
                ]
            ),
        )
        transaction_path.write_text(json.dumps(transaction), encoding="utf-8")
        transaction_path.chmod(0o660)
        self.use_recovery_fence()

        with self.assertRaisesRegex(CatalogError, "UID"):
            update_catalog(
                self.registry,
                self.output,
                fence_file=self.fence,
                fence_owner="recovery-run-1",
                fence_generation=2,
                recover_pending=True,
            )
        self.assertTrue(transaction_path.exists())

    def test_cleanup_marker_sync_failure_keeps_a_durable_marker_path(self) -> None:
        self.update(
            service_name="api",
            deployment_address=f"http://{TAILSCALE_IP}:8080/",
        )
        cleanup_marker = self.registry.with_name("catalog.json.txn.cleanup")
        marker = json.loads(cleanup_marker.read_text(encoding="utf-8"))
        marker["state"] = "cleanup"
        marker.pop(catalog.TRANSACTION_HMAC_FIELD, None)
        marker = catalog._authenticate_transaction_payload(
            marker,
            bytes.fromhex(
                json.loads(self.fence.read_text(encoding="utf-8"))[
                    catalog.TRANSACTION_KEY_FIELD
                ]
            ),
        )
        cleanup_marker.write_text(json.dumps(marker), encoding="utf-8")
        cleanup_marker.chmod(0o660)
        with catalog._fenced_mutation(
            self.fence, "deployment-run-1", 1
        ) as fence:
            transaction = catalog._load_cleanup_marker(
                cleanup_marker, self.registry, self.output, fence
            )
        self.assertIsNotNone(transaction)
        assert transaction is not None

        with catalog._fenced_mutation(
            self.fence, "deployment-run-1", 1
        ) as fence:
            with patch.object(
                catalog,
                "_fsync_directory",
                side_effect=(None, OSError("simulated sync failure")),
            ):
                with self.assertRaises(CatalogError):
                    catalog._clear_cleanup_marker(
                        cleanup_marker, transaction, fence
                    )

        self.assertTrue(cleanup_marker.exists())
        self.assertEqual(
            json.loads(cleanup_marker.read_text(encoding="utf-8"))["state"],
            "cleared",
        )

    def test_recovery_fence_cannot_publish_a_normal_update(self) -> None:
        fence = json.loads(self.fence.read_text(encoding="utf-8"))
        fence["role"] = "recovery"
        self.fence.write_text(json.dumps(fence), encoding="utf-8")
        self.fence.chmod(0o600)

        with self.assertRaises(FenceError):
            self.update(
                service_name="api",
                deployment_address=f"http://{TAILSCALE_IP}:8080/",
            )

    def test_recovery_fence_can_rollback_a_pending_transaction(self) -> None:
        real_replace = catalog._replace_snapshot

        def interrupt_before_page(path: Path, snapshot: object, check: object) -> None:
            if path == self.output:
                raise FenceError("simulated fence interruption")
            real_replace(path, snapshot, check)

        with patch(
            "update_access_catalog._replace_snapshot",
            side_effect=interrupt_before_page,
        ):
            with self.assertRaises(CatalogError):
                self.update(
                    service_name="api",
                    deployment_address=f"http://{TAILSCALE_IP}:8080/",
                )

        fence = json.loads(self.fence.read_text(encoding="utf-8"))
        fence["role"] = "recovery"
        self.fence.write_text(json.dumps(fence), encoding="utf-8")
        self.fence.chmod(0o600)
        with self.assertRaises(FenceError):
            update_catalog(
                self.registry,
                self.output,
                fence_file=self.fence,
                fence_owner="deployment-run-1",
                fence_generation=1,
                recover_pending=True,
            )

        fence = json.loads(self.fence.read_text(encoding="utf-8"))
        fence.update({"role": "recovery", "owner": "recovery-run-1", "generation": 2})
        self.fence.write_text(json.dumps(fence), encoding="utf-8")
        self.fence.chmod(0o600)
        with patch(
            "update_access_catalog._discover_tailscale_ip",
            side_effect=AssertionError("recovery must not discover Tailscale"),
        ):
            registry = update_catalog(
                self.registry,
                self.output,
                fence_file=self.fence,
                fence_owner="recovery-run-1",
                fence_generation=2,
                recover_pending=True,
            )

        self.assertEqual(registry["status"], "recovered")
        self.assertFalse(self.registry.exists())
        self.assertFalse(self.output.exists())
        self.assertFalse(self.registry.with_name("catalog.json.txn").exists())

    def test_reserved_sidecar_output_is_rejected(self) -> None:
        for output in (
            self.registry.with_name("catalog.json.lock"),
            self.registry.with_name("catalog.json.txn"),
            self.registry.with_name("catalog.json.txn.cleanup"),
        ):
            with self.subTest(output=output):
                with self.assertRaises(CatalogError):
                    update_catalog(
                        self.registry,
                        output,
                        service_name="api",
                        deployment_address=f"http://{TAILSCALE_IP}:8080/",
                        fence_file=self.fence,
                        fence_owner="deployment-run-1",
                        fence_generation=1,
                    )

    def test_lock_contention_returns_after_bounded_timeout(self) -> None:
        with patch.object(
            catalog.fcntl, "flock", side_effect=BlockingIOError()
        ), patch.object(catalog.time, "monotonic", side_effect=(0.0, 6.0)):
            with self.assertRaises(CatalogError):
                catalog._acquire_exclusive_lock(
                    0, CatalogError, "catalog lock is unavailable"
                )

    def test_missing_registry_with_existing_page_fails_closed(self) -> None:
        self.output.write_text("existing catalog page", encoding="utf-8")

        with self.assertRaises(CatalogError):
            self.update(
                service_name="api",
                deployment_address=f"http://{TAILSCALE_IP}:8080/",
            )
        self.assertEqual(
            self.output.read_text(encoding="utf-8"), "existing catalog page"
        )

    def test_registry_rejects_world_accessible_permissions(self) -> None:
        self.run_update(
            "--service-name",
            "api",
            "--deployment-address",
            f"http://{TAILSCALE_IP}:8080/",
        )
        self.registry.chmod(0o644)

        with self.assertRaises(CatalogError):
            self.update(
                service_name="api",
                deployment_address=f"https://{TAILSCALE_IP}:8443/",
            )

    def test_registry_metadata_repair_uses_a_validated_descriptor(self) -> None:
        self.run_update(
            "--service-name",
            "api",
            "--deployment-address",
            f"http://{TAILSCALE_IP}:8080/",
        )
        self.registry.chmod(0o600)

        with patch.object(
            catalog.os,
            "chown",
            side_effect=AssertionError("pathname ownership repair is unsafe"),
        ):
            self.update(
                service_name="api",
                deployment_address=f"https://{TAILSCALE_IP}:8443/",
            )

        self.assertEqual(self.registry.stat().st_mode & 0o777, 0o660)

    def test_world_writable_page_is_rejected(self) -> None:
        self.run_update(
            "--service-name",
            "api",
            "--deployment-address",
            f"http://{TAILSCALE_IP}:8080/",
        )
        original_page = self.output.read_bytes()
        self.output.chmod(0o666)

        with self.assertRaises(CatalogError):
            self.update(
                service_name="api",
                deployment_address=f"https://{TAILSCALE_IP}:8443/",
            )

        self.assertEqual(self.output.read_bytes(), original_page)

    def test_output_directory_is_preprovisioned_and_safe(self) -> None:
        missing_output = self.root / "missing" / "index.html"
        with self.assertRaises(CatalogError):
            self.update(
                service_name="api",
                deployment_address=f"http://{TAILSCALE_IP}:8080/",
                output=missing_output,
            )
        self.assertFalse(self.registry.exists())

        document_root = self.root / "world-writable-root"
        document_root.mkdir()
        document_root.chmod(0o777)
        with self.assertRaises(CatalogError):
            self.update(
                service_name="api",
                deployment_address=f"http://{TAILSCALE_IP}:8080/",
                output=document_root / "index.html",
            )
        self.assertFalse((document_root / "index.html").exists())

    def test_registry_directory_is_preprovisioned_and_safe(self) -> None:
        missing_registry = self.root / "missing-registry" / "catalog.json"
        with self.assertRaises(CatalogError):
            self.update(
                registry=missing_registry,
                service_name="api",
                deployment_address=f"http://{TAILSCALE_IP}:8080/",
            )
        self.assertFalse(missing_registry.parent.exists())

        real_registry_root = self.root / "real-registry-root"
        real_registry_root.mkdir()
        linked_registry_root = self.root / "linked-registry-root"
        linked_registry_root.symlink_to(real_registry_root, target_is_directory=True)
        with self.assertRaises(CatalogError):
            self.update(
                registry=linked_registry_root / "catalog.json",
                service_name="api",
                deployment_address=f"http://{TAILSCALE_IP}:8080/",
            )

        world_registry_root = self.root / "world-registry-root"
        world_registry_root.mkdir()
        world_registry_root.chmod(0o777)
        with self.assertRaises(CatalogError):
            self.update(
                registry=world_registry_root / "catalog.json",
                service_name="api",
                deployment_address=f"http://{TAILSCALE_IP}:8080/",
            )

        group_registry_root = self.root / "group-registry-root"
        group_registry_root.mkdir()
        group_registry_root.chmod(0o770)
        result = self.update(
            registry=group_registry_root / "catalog.json",
            service_name="api",
            deployment_address=f"http://{TAILSCALE_IP}:8080/",
        )
        self.assertEqual(result["services"][0]["name"], "api")

    def test_non_ascii_transaction_authentication_fails_without_traceback(self) -> None:
        transaction_path = self.leave_pending_transaction()
        transaction = json.loads(transaction_path.read_text(encoding="utf-8"))
        transaction[catalog.TRANSACTION_HMAC_FIELD] = "é" * 64
        transaction_path.write_text(json.dumps(transaction), encoding="utf-8")
        transaction_path.chmod(0o660)
        self.use_recovery_fence()

        stderr = io.StringIO()
        with redirect_stderr(stderr):
            result = main(
                [
                    "--registry",
                    str(self.registry),
                    "--output",
                    str(self.output),
                    "--fence-file",
                    str(self.fence),
                    "--fence-owner",
                    "recovery-run-1",
                    "--fence-generation",
                    "2",
                    "--recover-pending",
                ]
            )

        self.assertEqual(result, 2)
        self.assertIn("catalog transaction authentication", stderr.getvalue())
        self.assertNotIn("Traceback", stderr.getvalue())

    def test_registry_fifo_is_rejected_without_blocking(self) -> None:
        self.registry.unlink(missing_ok=True)
        os.mkfifo(self.registry)

        with self.assertRaises(CatalogError):
            self.update(
                service_name="api",
                deployment_address=f"http://{TAILSCALE_IP}:8080/",
            )

    def test_catalog_lock_fifo_is_rejected(self) -> None:
        os.mkfifo(self.registry.with_name("catalog.json.lock"), 0o660)

        with self.assertRaises(CatalogError):
            self.update(
                service_name="api",
                deployment_address=f"http://{TAILSCALE_IP}:8080/",
            )

    def test_surrogate_text_is_rejected_before_encoding(self) -> None:
        with self.assertRaises(CatalogError):
            self.update(
                service_name="\ud800",
                deployment_address=f"http://{TAILSCALE_IP}:8080/",
            )

    def test_service_limit_rejects_new_name_without_corrupting_catalog(self) -> None:
        with patch("update_access_catalog.MAX_SERVICES", 1):
            self.update(
                service_name="api",
                deployment_address=f"http://{TAILSCALE_IP}:8080/",
            )
            with self.assertRaises(CatalogError):
                self.update(
                    service_name="worker",
                    deployment_address=f"http://{TAILSCALE_IP}:8081/",
                )
        self.assertEqual([row["name"] for row in self.read_registry()["services"]], ["api"])

    def test_generated_file_size_is_checked_before_write(self) -> None:
        with patch("update_access_catalog.MAX_FILE_BYTES", 100):
            with self.assertRaises(CatalogError):
                self.update(
                    service_name="api",
                    deployment_address=f"http://{TAILSCALE_IP}:8080/",
                )
        self.assertFalse(self.registry.exists())
        self.assertFalse(self.output.exists())

    def test_output_mode_and_owner_survive_replacement(self) -> None:
        self.run_update(
            "--service-name",
            "api",
            "--deployment-address",
            f"http://{TAILSCALE_IP}:8080/",
        )
        self.output.chmod(0o640)
        before = self.output.stat()

        self.run_update(
            "--service-name",
            "api",
            "--deployment-address",
            f"https://{TAILSCALE_IP}:8443/",
        )
        after = self.output.stat()
        self.assertEqual(after.st_mode & 0o777, 0o640)
        self.assertEqual((after.st_uid, after.st_gid), (before.st_uid, before.st_gid))


if __name__ == "__main__":
    unittest.main()
