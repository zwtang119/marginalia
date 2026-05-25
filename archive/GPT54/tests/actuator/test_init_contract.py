import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


class InitContractTest(unittest.TestCase):

    def test_init_creates_expected_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            result = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            expected = [
                "README.md", "PRD.md", "SPEC.md", "CLAUDE.md",
                "docs/index.md",
                "project/project.md", "project/plan.md",
                "project/progress.md", "project/open-questions.md",
                "schema/rules.md", "schema/node-types.md",
                "schema/task-states.md", "schema/ingest.md",
            ]
            for f in expected:
                self.assertTrue(
                    (root / f).exists(),
                    f"Missing expected file: {f}",
                )

    def test_init_idempotent(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                check=True,
                capture_output=True,
                text=True,
            )
            first_claude = (root / "CLAUDE.md").read_text(encoding="utf-8")
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                check=True,
                capture_output=True,
                text=True,
            )
            second_claude = (root / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertEqual(first_claude, second_claude)


if __name__ == "__main__":
    unittest.main()
