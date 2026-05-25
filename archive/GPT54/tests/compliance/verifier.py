import json
import os
import re
from pathlib import Path


class ComplianceVerifier:

    def __init__(self, kb_root):
        self.kb_root = Path(kb_root)

    def verify(self, scenario, llm_output):
        scenario_id = scenario["id"]
        results = {
            "scenario_id": scenario_id,
            "passed": True,
            "checks": [],
        }

        if scenario_id == "S1":
            results = self._verify_s1(scenario["expected"], llm_output, results)
        elif scenario_id == "S2":
            results = self._verify_s2(scenario["expected"], llm_output, results)
        elif scenario_id == "S3":
            results = self._verify_s3(scenario["expected"], llm_output, results)
        elif scenario_id == "S4":
            results = self._verify_s4(scenario["expected"], llm_output, results)
        elif scenario_id == "S5":
            results = self._verify_s5(scenario["expected"], llm_output, results)

        return results

    def _check_frontmatter(self, filepath, key, value):
        if not os.path.exists(filepath):
            return False, f"File not found: {filepath}"
        content = Path(filepath).read_text(encoding="utf-8")
        pattern = rf"{key}:\s*{re.escape(value)}"
        if re.search(pattern, content):
            return True, f"Frontmatter {key}={value} found"
        return False, f"Frontmatter {key}={value} not found"

    def _check_wikilinks(self, filepath, min_count=1):
        if not os.path.exists(filepath):
            return False, f"File not found: {filepath}"
        content = Path(filepath).read_text(encoding="utf-8")
        links = re.findall(r"\[\[.+?\]\]", content)
        if len(links) >= min_count:
            return True, f"Found {len(links)} wikilinks (>= {min_count})"
        return False, f"Found {len(links)} wikilinks (< {min_count})"

    def _verify_s1(self, expected, llm_output, results):
        nodes_dir = self.kb_root / "docs" / "nodes"
        concept_files = list(nodes_dir.glob("*.md")) if nodes_dir.exists() else []

        if not concept_files:
            results["checks"].append({
                "check": "file_location",
                "passed": False,
                "detail": "No concept files found in docs/nodes/",
            })
            results["passed"] = False
            return results

        for cf in concept_files:
            ok, msg = self._check_frontmatter(str(cf), "type", "concept")
            results["checks"].append({"check": "structure.type", "passed": ok, "detail": msg})
            if not ok:
                results["passed"] = False

            ok, msg = self._check_wikilinks(str(cf), 1)
            results["checks"].append({"check": "structure.wikilink", "passed": ok, "detail": msg})
            if not ok:
                results["passed"] = False

        return results

    def _verify_s2(self, expected, llm_output, results):
        reports_dir = self.kb_root / "audit" / "reports"
        report_files = list(reports_dir.glob("*.json")) if reports_dir.exists() else []

        if not report_files:
            results["checks"].append({
                "check": "file_location",
                "passed": False,
                "detail": "No audit reports found",
            })
            results["passed"] = False
            return results

        latest_report = max(report_files, key=lambda p: p.stat().st_mtime)
        report = json.loads(latest_report.read_text(encoding="utf-8"))

        has_issues = "issues" in report
        results["checks"].append({
            "check": "structure.has_defect_list",
            "passed": has_issues,
            "detail": "Issues list present" if has_issues else "No issues list",
        })
        if not has_issues:
            results["passed"] = False

        has_severity = any(
            issue.get("severity") for issue in report.get("issues", [])
        )
        results["checks"].append({
            "check": "structure.has_priority",
            "passed": has_severity,
            "detail": "Severity/priority present" if has_severity else "No severity",
        })

        return results

    def _verify_s3(self, expected, llm_output, results):
        index_path = self.kb_root / "docs" / "index.md"
        if not index_path.exists():
            results["checks"].append({
                "check": "file_location",
                "passed": False,
                "detail": "docs/index.md not found",
            })
            results["passed"] = False
            return results

        content = index_path.read_text(encoding="utf-8")
        has_links = bool(re.findall(r"\[\[.+?\]\]", content))
        results["checks"].append({
            "check": "structure.index_contains_new_page",
            "passed": has_links,
            "detail": f"Index has wikilinks: {has_links}",
        })
        if not has_links:
            results["passed"] = False

        return results

    def _verify_s4(self, expected, llm_output, results):
        results["checks"].append({
            "check": "manual_review",
            "passed": True,
            "detail": "S4 requires LLM output analysis - manual review needed",
        })
        return results

    def _verify_s5(self, expected, llm_output, results):
        results["checks"].append({
            "check": "manual_review",
            "passed": True,
            "detail": "S5 requires LLM output analysis - manual review needed",
        })
        return results
