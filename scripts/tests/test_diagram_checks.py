#!/usr/bin/env python3
"""Behavior checks for the changed-diagram pull request workflow step."""

from __future__ import annotations

import os
import subprocess
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "render-diagrams.yml"
RENDERED = b"<svg>current</svg>"


def workflow_script() -> str:
    lines = WORKFLOW.read_text(encoding="utf-8").splitlines()
    start = lines.index("      - name: Check changed PR diagrams via public Kroki")
    run = lines.index("        run: |", start) + 1
    script = []
    for line in lines[run:]:
        if line.startswith("      - name:"):
            break
        if line.startswith("          "):
            script.append(line[10:])
        elif not line:
            script.append("")
        else:
            break
    return "\n".join(script) + "\n"


class DiagramCheckWorkflowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.repo = self.root / "fixture"
        self.repo.mkdir()
        self.curl_bin = self.root / "bin"
        self.curl_bin.mkdir()
        self.curl_log = self.root / "curl.log"
        curl = self.curl_bin / "curl"
        curl.write_text(
            "#!/usr/bin/env python3\n"
            "import os, pathlib, sys\n"
            "args = sys.argv[1:]\n"
            "out = pathlib.Path(args[args.index('-o') + 1])\n"
            "out.write_bytes(b'<svg>current</svg>')\n"
            "with open(os.environ['CURL_LOG'], 'a', encoding='utf-8') as log:\n"
            "    log.write('called\\n')\n"
            "sys.stdout.write(os.environ.get('CURL_STATUS', '200'))\n",
            encoding="utf-8",
        )
        curl.chmod(0o755)
        self.git("init", "-q")
        self.git("config", "user.email", "test@example.com")
        self.git("config", "user.name", "Diagram workflow test")
        self.write("docs/changed/flow chart.puml", "@startuml\nold\n@enduml\n")
        self.write("docs/changed/flow chart.svg", RENDERED)
        self.write("docs/unrelated/broken.puml", "@startuml\nunrelated\n@enduml\n")
        self.write("docs/unrelated/broken.svg", "<svg>known drift</svg>")
        self.git("add", ".")
        self.git("commit", "-qm", "base")
        self.base = self.git("rev-parse", "HEAD").strip()

    def tearDown(self) -> None:
        self.temp.cleanup()

    def git(self, *args: str) -> str:
        return subprocess.run(
            ["git", *args], cwd=self.repo, check=True, text=True, capture_output=True
        ).stdout

    def write(self, relative: str, content: str | bytes) -> None:
        path = self.repo / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content if isinstance(content, bytes) else content.encode())

    def commit_head(self) -> str:
        self.git("add", ".")
        self.git("commit", "-qm", "head")
        return self.git("rev-parse", "HEAD").strip()

    def run_workflow(
        self, head: str, extra_env: dict[str, str] | None = None
    ) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        env.update(
            {
                "GITHUB_WORKSPACE": str(REPO_ROOT),
                "PR_BASE_SHA": self.base,
                "PR_HEAD_SHA": head,
                "CURL_LOG": str(self.curl_log),
                "PATH": f"{self.curl_bin}:{env['PATH']}",
            }
        )
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            ["bash", "-c", workflow_script()],
            cwd=self.repo,
            env=env,
            text=True,
            capture_output=True,
        )

    def assert_repository_unchanged(self, head: str) -> None:
        self.assertEqual(self.git("rev-parse", "HEAD").strip(), head)
        self.assertEqual(self.git("status", "--porcelain"), "")

    def test_changed_pair_checked_and_unrelated_drift_ignored(self) -> None:
        self.write("docs/changed/flow chart.puml", "@startuml\nnew\n@enduml\n")
        self.write("docs/changed/flow chart.svg", RENDERED)
        head = self.commit_head()

        result = self.run_workflow(head)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("processed: 1 diagram(s)", result.stdout)
        self.assertIn("ok: docs/changed/flow chart.puml", result.stdout)
        self.assertEqual(self.curl_log.read_text(), "called\n")
        self.assert_repository_unchanged(head)

    def test_no_changed_source_is_noop(self) -> None:
        head = self.base

        result = self.run_workflow(head)

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("No changed PlantUML sources.", result.stdout)
        self.assertFalse(self.curl_log.exists())
        self.assert_repository_unchanged(head)

    def test_missing_and_drifted_outputs_fail_without_checkout_changes(self) -> None:
        self.write("docs/changed/flow chart.puml", "@startuml\nnew\n@enduml\n")
        self.write("docs/changed/flow chart.svg", "<svg>outdated</svg>")
        head = self.commit_head()

        drift = self.run_workflow(head)
        self.assertNotEqual(drift.returncode, 0)
        self.assertIn("render drift", drift.stderr)
        self.assert_repository_unchanged(head)

        self.git("rm", "docs/changed/flow chart.svg")
        missing_head = self.commit_head()
        missing = self.run_workflow(missing_head)
        self.assertNotEqual(missing.returncode, 0)
        self.assertIn("render drift", missing.stderr)
        self.assert_repository_unchanged(missing_head)

    def test_renderer_failure_fails_without_checkout_changes(self) -> None:
        self.write("docs/changed/flow chart.puml", "@startuml\nnew\n@enduml\n")
        head = self.commit_head()

        result = self.run_workflow(head, {"CURL_STATUS": "503"})

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("render failed", result.stderr)
        self.assert_repository_unchanged(head)

if __name__ == "__main__":
    unittest.main()
