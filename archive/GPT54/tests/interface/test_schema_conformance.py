import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

SCRIPTS_DIR = Path(__file__).resolve().parents[2] / "scripts"


class SchemaConformanceTest(unittest.TestCase):

    def test_init_output_parseable_by_audit(self):
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
            report_path = Path(result.stdout.strip().splitlines()[-1])
            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertIn("counts", report)
            self.assertIn("issues", report)

    def test_verify_defects_consistent_with_audit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                check=True,
                capture_output=True,
                text=True,
            )
            audit_result = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "audit.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            verify_result = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "verify.py"), "--root", str(root)],
                capture_output=True,
                text=True,
            )
            if audit_result.returncode == 0:
                self.assertEqual(verify_result.returncode, 0)

    def test_schema_node_types_file_exists_and_has_header(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                check=True,
                capture_output=True,
                text=True,
            )
            node_types_path = root / "schema" / "node-types.md"
            self.assertTrue(node_types_path.exists())
            content = node_types_path.read_text(encoding="utf-8")
            self.assertIn("Node Types", content)


if __name__ == "__main__":
    unittest.main()
