import os
import pathlib
import subprocess
import tempfile
import unittest

SCRIPTS_DIR = pathlib.Path(__file__).resolve().parents[2] / "scripts"
GPT54_ROOT = pathlib.Path(__file__).resolve().parents[2]


class ProtocolDiscoveryTest(unittest.TestCase):
    def test_claude_md_points_to_all_schema_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                check=True,
                capture_output=True,
                text=True,
            )
            claude = root / "CLAUDE.md"
            content = claude.read_text(encoding="utf-8")
            for schema_file in [
                "schema/rules.md",
                "schema/node-types.md",
                "schema/task-states.md",
                "schema/ingest.md",
            ]:
                self.assertIn(schema_file, content, f"CLAUDE.md missing reference to {schema_file}")

    def test_ingest_schema_has_required_sections(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                check=True,
                capture_output=True,
                text=True,
            )
            ingest = root / "schema" / "ingest.md"
            content = ingest.read_text(encoding="utf-8")
            for section in ["触发条件", "执行顺序", "禁止项"]:
                self.assertIn(section, content, f"ingest.md missing section: {section}")

    def test_full_init_audit_verify_cycle(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp) / "repo"
            subprocess.run(
                ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                check=True,
                capture_output=True,
                text=True,
            )
            audit_result = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "audit.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(audit_result.returncode, 0, audit_result.stdout)
            verify_result = subprocess.run(
                ["python3", str(SCRIPTS_DIR / "verify.py"), "--root", str(root)],
                cwd=str(GPT54_ROOT),
                capture_output=True,
                text=True,
            )
            self.assertEqual(verify_result.returncode, 0, verify_result.stderr)


class ProtocolStaticDiscoveryTest(unittest.TestCase):

    def _init_repo(self, tmp):
        root = pathlib.Path(tmp) / "repo"
        subprocess.run(
            ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
            cwd=str(GPT54_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
        return root

    def test_entry_point_exists(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._init_repo(tmp)
            claude_md = root / "CLAUDE.md"
            self.assertTrue(claude_md.exists())
            content = claude_md.read_text(encoding="utf-8")
            self.assertIn("GPT54-PROTOCOL", content)

    def test_discovery_chain_complete(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._init_repo(tmp)
            claude_md = root / "CLAUDE.md"
            content = claude_md.read_text(encoding="utf-8")
            schema_dir = root / "schema"
            for schema_file in os.listdir(schema_dir):
                if schema_file.endswith(".md"):
                    self.assertIn(schema_file, content)

    def test_schema_files_well_formed(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._init_repo(tmp)
            schema_dir = root / "schema"
            for schema_file in os.listdir(schema_dir):
                if schema_file.endswith(".md"):
                    path = schema_dir / schema_file
                    content = path.read_text(encoding="utf-8")
                    self.assertTrue(len(content) > 0, f"{schema_file} is empty")

    def test_node_types_defined(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._init_repo(tmp)
            node_types_path = root / "schema" / "node-types.md"
            content = node_types_path.read_text(encoding="utf-8")
            for nt in ["concept", "decision", "task", "note"]:
                self.assertIn(nt, content)

    def test_no_circular_references(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._init_repo(tmp)
            schema_dir = root / "schema"
            refs = {}
            for schema_file in os.listdir(schema_dir):
                if schema_file.endswith(".md"):
                    path = schema_dir / schema_file
                    content = path.read_text(encoding="utf-8")
                    mentioned = [
                        f for f in os.listdir(schema_dir)
                        if f != schema_file and f in content
                    ]
                    refs[schema_file] = mentioned
            visited = set()
            for start in refs:
                path = []
                current = start
                while current and current not in path:
                    path.append(current)
                    next_refs = refs.get(current, [])
                    current = next_refs[0] if next_refs else None
                self.assertEqual(len(path), len(set(path)),
                                 f"Circular reference detected: {path}")


class ProtocolBehaviorDiscoveryTest(unittest.TestCase):

    def _init_repo(self, tmp):
        root = pathlib.Path(tmp) / "repo"
        subprocess.run(
            ["python3", str(SCRIPTS_DIR / "init.py"), "--root", str(root)],
            cwd=str(GPT54_ROOT),
            check=True,
            capture_output=True,
            text=True,
        )
        return root

    def test_agent_knows_reading_order(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._init_repo(tmp)
            claude_md = root / "CLAUDE.md"
            content = claude_md.read_text(encoding="utf-8")
            self.assertIn("schema/rules.md", content)

    def test_agent_finds_concept_template(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._init_repo(tmp)
            node_types_path = root / "schema" / "node-types.md"
            content = node_types_path.read_text(encoding="utf-8")
            self.assertIn("concept", content)

    def test_agent_knows_post_task_actions(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._init_repo(tmp)
            rules_path = root / "schema" / "rules.md"
            content = rules_path.read_text(encoding="utf-8")
            self.assertTrue(
                "progress" in content or "index" in content,
                "Rules do not mention post-task updates",
            )

    def test_agent_knows_audit_trigger(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = self._init_repo(tmp)
            ingest_path = root / "schema" / "ingest.md"
            content = ingest_path.read_text(encoding="utf-8")
            self.assertIn("触发条件", content)


if __name__ == "__main__":
    unittest.main()
