import sys
from pathlib import Path
import tempfile
import unittest


SCRIPT_DIR = Path(__file__).parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import scan_debt  # noqa: E402


class ScanDebtTests(unittest.TestCase):
    def test_matches_standalone_inline_and_block_comments(self) -> None:
        source = "\n".join(
            (
                "# ponytail: standalone",
                "value = 1# ponytail: inline",
                "foo();/* ponytail: c block */",
                "/** ponytail: javadoc */",
                "<!-- ponytail: html -->",
                "/*",
                " * ponytail: continuation",
                " */",
            )
        )

        self.assertEqual(scan_debt.marker_lines(source), [1, 2, 3, 4, 5, 7])

    def test_ignores_strings_and_nested_comment_prose(self) -> None:
        source = "\n".join(
            (
                'value = "# ponytail: string"',
                'value = "x // ponytail: string"',
                "// Use # ponytail: in Python",
                "/* Explain // ponytail: as prose */",
                "# ponytail: real marker",
            )
        )

        self.assertEqual(scan_debt.marker_lines(source), [5])

    def test_skips_prose_and_build_directories(self) -> None:
        with tempfile.TemporaryDirectory(prefix="ponytail-debt-test-") as temporary:
            root = Path(temporary)
            (root / "source.py").write_text(
                "# ponytail: source\nvalue = 1# ponytail: inline\n",
                encoding="utf-8",
            )
            (root / "README.md").write_text(
                "# ponytail: documentation example\n",
                encoding="utf-8",
            )
            build = root / "build"
            build.mkdir()
            (build / "generated.py").write_text(
                "# ponytail: generated\n",
                encoding="utf-8",
            )

            findings = list(scan_debt.scan(root))

        self.assertEqual(
            [(path, line_number) for path, line_number, _ in findings],
            [("source.py", 1), ("source.py", 2)],
        )


if __name__ == "__main__":
    unittest.main()
