import json
import pathlib
import subprocess
import tempfile
import unittest

SCRIPTS_DIR = pathlib.Path(__file__).resolve().parents[2] / "scripts"
GPT54_ROOT = pathlib.Path(__file__).resolve().parents[2]


class AuditScriptTest(unittest.TestCase):
    def test_audit_reports_missing_required_file(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                check=True,
                capture_output=True,
                text=True,
            )
            (root / "project" / "plan.md").unlink()
            completed = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "audit.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            report_path = pathlib.Path(completed.stdout.strip().splitlines()[-1])
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["issues"][0]["type"], "missing_required_file")
            self.assertEqual(report["issues"][0]["severity"], "P0")

    def test_audit_passes_for_initialized_repository(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                check=True,
                capture_output=True,
                text=True,
            )
            completed = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "audit.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(completed.returncode, 0, completed.stderr)

    def test_audit_detects_missing_claude_md(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                check=True,
                capture_output=True,
                text=True,
            )
            (root / "CLAUDE.md").unlink()
            completed = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "audit.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            report_path = pathlib.Path(completed.stdout.strip().splitlines()[-1])
            report = json.loads(report_path.read_text(encoding="utf-8"))
            paths = [i["path"] for i in report["issues"]]
            self.assertIn("CLAUDE.md", paths)

    def test_audit_detects_missing_protocol_markers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                check=True,
                capture_output=True,
                text=True,
            )
            (root / "CLAUDE.md").write_text("# No markers here\n", encoding="utf-8")
            completed = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "audit.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            report_path = pathlib.Path(completed.stdout.strip().splitlines()[-1])
            report = json.loads(report_path.read_text(encoding="utf-8"))
            types = [i["type"] for i in report["issues"]]
            self.assertIn("missing_protocol_markers", types)

    def test_audit_detects_missing_ingest_schema(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                check=True,
                capture_output=True,
                text=True,
            )
            (root / "schema" / "ingest.md").unlink()
            completed = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "audit.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertNotEqual(completed.returncode, 0)
            report_path = pathlib.Path(completed.stdout.strip().splitlines()[-1])
            report = json.loads(report_path.read_text(encoding="utf-8"))
            paths = [i["path"] for i in report["issues"]]
            self.assertIn("schema/ingest.md", paths)


if __name__ == "__main__":
    unittest.main()
