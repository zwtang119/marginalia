import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"


class AuditTrendTest(unittest.TestCase):

    def test_audit_appends_trend_history(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                check=True,
                capture_output=True,
                text=True,
            )
            result = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "audit.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            history_path = root / "audit" / "snapshots" / "trend_history.jsonl"
            self.assertTrue(history_path.exists())
            lines = history_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 1)
            record = json.loads(lines[0])
            self.assertIn("total_defects", record)
            self.assertIn("direction", record)
            self.assertIn("history", record)

    def test_audit_trend_converging_after_fixes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                check=True,
                capture_output=True,
                text=True,
            )
            history_path = root / "audit" / "snapshots" / "trend_history.jsonl"
            for _ in range(3):
                subprocess.run(
                    ["python3", str(SCRIPTS_DIR / "audit.py"), "--root", str(root)],
                    capture_output=True,
                    text=True,
                )
            self.assertTrue(history_path.exists())
            lines = history_path.read_text(encoding="utf-8").strip().splitlines()
            self.assertEqual(len(lines), 3)
            for line in lines:
                record = json.loads(line)
                self.assertIn("direction", record)


class AuditSnapshotTest(unittest.TestCase):

    def test_snapshot_counts_stable_after_reinit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                check=True,
                capture_output=True,
                text=True,
            )
            result1 = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "audit.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            result2 = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "audit.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            report_path1 = Path(result1.stdout.strip().splitlines()[-1])
            report_path2 = Path(result2.stdout.strip().splitlines()[-1])
            report1 = json.loads(report_path1.read_text(encoding="utf-8"))
            report2 = json.loads(report_path2.read_text(encoding="utf-8"))
            self.assertEqual(report1["counts"], report2["counts"])

    def test_snapshot_detects_regression(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                check=True,
                capture_output=True,
                text=True,
            )
            result1 = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "audit.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            report_path1 = Path(result1.stdout.strip().splitlines()[-1])
            report1 = json.loads(report_path1.read_text(encoding="utf-8"))
            baseline_counts = report1["counts"]

            (root / "schema" / "ingest.md").unlink()
            result2 = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "audit.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            report_path2 = Path(result2.stdout.strip().splitlines()[-1])
            report2 = json.loads(report_path2.read_text(encoding="utf-8"))
            self.assertGreater(
                report2["counts"]["total"],
                baseline_counts["total"],
                "Regression not detected after removing ingest.md",
            )


if __name__ == "__main__":
    unittest.main()
