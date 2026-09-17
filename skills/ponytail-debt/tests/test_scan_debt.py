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

    def test_keeps_scanning_after_urls_and_rust_lifetimes(self) -> None:
        source = "\n".join(
            (
                'endpoint: https://host # ponytail: yaml marker',
                'let x: &\'static str = "it\'s Bob\'s"; // ponytail: rust marker',
            )
        )

        self.assertEqual(scan_debt.marker_lines(source), [1, 2])

    def test_distinguishes_uri_tokens_and_multiline_single_quotes(self) -> None:
        source = "\n".join(
            (
                "label:// ponytail: label marker",
                "label://ponytail: no-space label marker",
                "endpoint=https://host/#ponytail: url text # ponytail: real marker",
                "path=file://host/path # ponytail: file marker",
                "remote=git+ssh://host/path # ponytail: remote marker",
                "curl https://host;# ponytail: shell marker",
                "url: https://host/path;#ponytail:fragment",
                "value='first",
                "# ponytail: quoted text",
                "second'",
                "# ponytail: after quote",
            )
        )

        self.assertEqual(scan_debt.marker_lines(source), [1, 2, 3, 4, 5, 6, 11])
        self.assertEqual(
            scan_debt.marker_lines("curl https://host;#ponytail: shell marker", ".sh"),
            [1],
        )

    def test_keeps_rust_labels_out_of_single_quoted_values(self) -> None:
        source = "\n".join(
            (
                "'outer: loop { // ponytail: label marker",
                "    break 'outer; // ponytail: break marker",
                "value = 'foo: loop # ponytail: quoted text'",
                "key: 'foo # ponytail: quoted text'",
                "key: 'value' # ponytail: real marker",
            )
        )

        self.assertEqual(scan_debt.marker_lines(source), [1, 2, 5])

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
            self.assertEqual(list(scan_debt.scan(root / "README.md")), [])


if __name__ == "__main__":
    unittest.main()
