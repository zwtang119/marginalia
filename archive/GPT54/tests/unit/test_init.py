import pathlib
import subprocess
import tempfile
import unittest

SCRIPTS_DIR = pathlib.Path(__file__).resolve().parents[2] / "scripts"
GPT54_ROOT = pathlib.Path(__file__).resolve().parents[2]


class InitScriptTest(unittest.TestCase):
    def test_init_creates_expected_structure(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "sandbox"
            completed = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertTrue((root / "docs" / "index.md").exists())
            self.assertTrue((root / "project" / "project.md").exists())
            self.assertTrue((root / "schema" / "rules.md").exists())
            self.assertIn("Initialized GPT54 skeleton", completed.stdout)

    def test_init_creates_claude_md_with_protocol_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "sandbox"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
                check=True,
            )
            claude = root / "CLAUDE.md"
            self.assertTrue(claude.exists())
            content = claude.read_text(encoding="utf-8")
            self.assertIn("GPT54-PROTOCOL-START", content)
            self.assertIn("GPT54-PROTOCOL-END", content)
            self.assertIn("schema/rules.md", content)
            self.assertIn("schema/ingest.md", content)

    def test_init_creates_ingest_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "sandbox"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
                check=True,
            )
            ingest = root / "schema" / "ingest.md"
            self.assertTrue(ingest.exists())
            content = ingest.read_text(encoding="utf-8")
            self.assertIn("触发条件", content)
            self.assertIn("执行顺序", content)
            self.assertIn("禁止项", content)

    def test_update_protocol_preserves_user_content(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "sandbox"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
                check=True,
            )
            claude = root / "CLAUDE.md"
            original = claude.read_text(encoding="utf-8")
            user_content = "\n## My Custom Section\n\nSome user notes here.\n"
            claude.write_text(original + user_content, encoding="utf-8")
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root), "--update-protocol"],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
                check=True,
            )
            updated = claude.read_text(encoding="utf-8")
            self.assertIn("My Custom Section", updated)
            self.assertIn("GPT54-PROTOCOL-START", updated)

    def test_platform_cursor_creates_cursorrules(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "sandbox"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root), "--platform", "cursor"],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
                check=True,
            )
            cursorrules = root / ".cursorrules"
            self.assertTrue(cursorrules.exists())
            content = cursorrules.read_text(encoding="utf-8")
            self.assertIn("GPT54-PROTOCOL-START", content)


if __name__ == "__main__":
    unittest.main()
