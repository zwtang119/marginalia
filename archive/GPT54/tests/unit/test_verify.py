import pathlib
import subprocess
import tempfile
import unittest

SCRIPTS_DIR = pathlib.Path(__file__).resolve().parents[2] / "scripts"
GPT54_ROOT = pathlib.Path(__file__).resolve().parents[2]


class VerifyScriptTest(unittest.TestCase):
    def test_verify_fails_on_invalid_task_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                check=True,
                capture_output=True,
                text=True,
            )
            task_file = root / "runtime" / "tasks" / "task-0001.md"
            task_file.write_text(
                "# Task\n\n- 任务编号：TASK-0001\n- 当前状态：running\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "verify.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("Invalid task state", completed.stdout)

    def test_verify_passes_on_valid_task_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                check=True,
                capture_output=True,
                text=True,
            )
            task_file = root / "runtime" / "tasks" / "task-0001.md"
            task_file.write_text(
                "# Task\n\n- 任务编号：TASK-0001\n- 当前状态：ready\n",
                encoding="utf-8",
            )
            completed = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "verify.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)
            self.assertIn("Verification passed", completed.stdout)


if __name__ == "__main__":
    unittest.main()
