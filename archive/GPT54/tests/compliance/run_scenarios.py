import argparse
import json
import os
import sys
from datetime import datetime
from pathlib import Path

SCENARIOS_DIR = Path(__file__).resolve().parent / "scenarios"
RESULTS_DIR = Path(__file__).resolve().parent / "results"

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verifier import ComplianceVerifier


def run_scenario(scenario_path, kb_root, model_command=None):
    scenario = json.loads(scenario_path.read_text(encoding="utf-8"))

    print(f"\n{'='*60}")
    print(f"Scenario: {scenario['id']} - {scenario['name']}")
    print(f"Description: {scenario['description']}")
    print(f"{'='*60}")

    if model_command:
        print(f"Model command: {model_command}")
        print(f"Task: {scenario['input']['task']}")
        print("\n[Manual step] Run the above task with your LLM, then provide output path.")
        llm_output_path = input("Path to LLM output (or Enter to skip): ").strip()
        if llm_output_path and os.path.exists(llm_output_path):
            llm_output = Path(llm_output_path).read_text(encoding="utf-8")
        else:
            llm_output = ""
    else:
        llm_output = ""

    verifier = ComplianceVerifier(kb_root)
    results = verifier.verify(scenario, llm_output)

    print(f"\nResults: {'PASS' if results['passed'] else 'FAIL'}")
    for check in results["checks"]:
        status = "PASS" if check["passed"] else "FAIL"
        print(f"  [{status}] {check['check']}: {check['detail']}")

    return results


def main():
    parser = argparse.ArgumentParser(description="Run L3 compliance scenarios")
    parser.add_argument("--kb-root", required=True, help="Path to knowledge base root")
    parser.add_argument("--scenario", help="Specific scenario ID to run (e.g. S1)")
    parser.add_argument("--model", help="Model command for LLM invocation")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    if args.scenario:
        matches = list(SCENARIOS_DIR.glob(f"*{args.scenario.lower()}*"))
        if not matches:
            print(f"Scenario {args.scenario} not found")
            sys.exit(1)
        results = [run_scenario(matches[0], args.kb_root, args.model)]
    else:
        results = []
        for scenario_file in sorted(SCENARIOS_DIR.glob("*.json")):
            results.append(run_scenario(scenario_file, args.kb_root, args.model))

    timestamp = datetime.now().strftime("%Y%m%dT%H%M%S")
    result_path = RESULTS_DIR / f"compliance-{timestamp}.json"
    result_path.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nResults saved to {result_path}")

    all_passed = all(r["passed"] for r in results)
    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
