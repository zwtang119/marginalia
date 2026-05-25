import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


class VerifyContractTest(unittest.TestCase):

    def _init_repo(self, tmp):
        root = Path(tmp) / "repo"
        subprocess.run(
            ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
            check=True,
            capture_output=True,
            text=True,
        )
        return root

    def _create_task(self, root, name, state):
        task_dir = root / "runtime" / "tasks"
        task_dir.mkdir(parents=True, exist_ok=True)
        (task_dir / name).write_text(
            f"# Task\n- 当前状态：{state}\n",
            encoding="utf-8",
        )

    def test_verify_accepts_valid_kb(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._init_repo(tmp)
            self._create_task(root, "t1.md", "ready")
            result = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "verify.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("Verification passed", result.stdout)

    def test_verify_rejects_invalid_kb(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._init_repo(tmp)
            self._create_task(root, "t1.md", "running")
            result = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "verify.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("Invalid task state", result.stdout)

    def test_verify_output_format(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._init_repo(tmp)
            result = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "verify.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue(
                "Verification passed" in result.stdout,
                "verify.py output does not match expected format",
            )


if __name__ == "__main__":
    unittest.main()
