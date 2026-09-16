#!/usr/bin/env python3

from __future__ import annotations

import json
from pathlib import Path
import sys
import subprocess
import tempfile
import unittest
from unittest.mock import patch


SCRIPTS_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from update_access_catalog import CatalogError, main, update_catalog  # noqa: E402


TAILSCALE_IP = ".".join(("100", "64", "12", "34"))
OTHER_TAILSCALE_IP = ".".join(("100", "64", "12", "35"))
DOCUMENTATION_IP = ".".join(("192", "0", "2", "1"))


class AccessCatalogTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="access-catalog-test-")
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name)
        self.registry = root / "catalog.json"
        self.output = root / "index.html"

    def run_update(self, *arguments: str) -> int:
        return main(
            [
                "--registry",
                str(self.registry),
                "--output",
                str(self.output),
                "--tailscale-ip",
                TAILSCALE_IP,
                *arguments,
            ]
        )

    def read_registry(self) -> dict[str, object]:
        return json.loads(self.registry.read_text(encoding="utf-8"))

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
            )

        self.assertEqual(run.call_args.args[0], ["tailscale", "ip", "-4"])
        self.assertEqual(run.call_args.kwargs["timeout"], 5)
        self.assertEqual(self.read_registry()["tailscale_ip"], TAILSCALE_IP)

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
                    update_catalog(
                        self.registry,
                        self.output,
                        tailscale_ip=TAILSCALE_IP,
                        service_name="api",
                        deployment_address=address,
                    )
        self.assertFalse(self.registry.exists())
        self.assertFalse(self.output.exists())

    def test_rejects_invalid_tailscale_ip(self) -> None:
        with self.assertRaises(CatalogError):
            update_catalog(
                self.registry,
                self.output,
                tailscale_ip=DOCUMENTATION_IP,
                service_name="api",
                deployment_address=f"http://{DOCUMENTATION_IP}:8080/",
            )

    def test_malformed_registry_fails_closed(self) -> None:
        self.registry.write_text("{\"services\": \"not-a-list\"}\n", encoding="utf-8")

        with self.assertRaises(CatalogError):
            update_catalog(
                self.registry,
                self.output,
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
        with self.assertRaises(CatalogError):
            update_catalog(
                self.registry,
                self.output,
                tailscale_ip=OTHER_TAILSCALE_IP,
                service_name="worker",
                deployment_address=f"http://{OTHER_TAILSCALE_IP}:8081/",
            )


if __name__ == "__main__":
    unittest.main()
