#!/usr/bin/env python3
"""Score test-case outputs against the hidden answer keys.

Examples
  python scripts/score.py --run sample_runs/v1
  python scripts/score.py --run sample_runs/v1 --run sample_runs/v2 --split all
  python scripts/score.py --run sample_runs/v1 --feedback      # what the editor is allowed to see
  python scripts/score.py --run sample_runs/v1 --show-missed   # full detail, for humans only
"""
import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SPLITS = {
    "train": ROOT / "data" / "stories" / "train",
    "holdout": ROOT / "data" / "stories" / "holdout",
}
KEYS = ROOT / "data" / "answer_keys"


def story_ids(split):
    dirs = SPLITS.values() if split == "all" else [SPLITS[split]]
    return sorted(p.stem for d in dirs for p in d.glob("*.md"))


def load_cases(run_dir, sid):
    """Return the list of test cases, or None if the file is missing or invalid."""
    f = Path(run_dir) / f"{sid}.json"
    if not f.exists():
        return None
    try:
        data = json.loads(f.read_text())
    except json.JSONDecodeError:
        return None
    cases = data.get("test_cases") if isinstance(data, dict) else data
    return cases if isinstance(cases, list) else None


def case_text(tc):
    parts = []
    for value in (tc.values() if isinstance(tc, dict) else [tc]):
        parts.extend(map(str, value) if isinstance(value, list) else [str(value)])
    return " ".join(parts).lower()


def matches(text, groups):
    """A scenario is covered when ONE test case matches every keyword group."""
    return all(any(alt.lower() in text for alt in group) for group in groups)


def llm_judge(scenario, cases):
    """Fallback for scenarios the keyword matcher missed. Needs the claude CLI."""
    prompt = (
        "You are grading test coverage.\n\nScenario that should be tested:\n"
        f"{scenario['description']}\n\nTest cases (JSON):\n{json.dumps(cases, indent=1)}\n\n"
        "Does at least one test case clearly test this scenario? Answer only YES or NO."
    )
    result = subprocess.run(["claude", "-p", prompt], capture_output=True, text=True, timeout=300)
    return result.stdout.strip().upper().startswith("YES")


def score_run(run_dir, split="train", judge="keyword"):
    if judge == "llm" and not shutil.which("claude"):
        sys.exit("--judge llm needs the claude CLI on your PATH")
    report = {"run": str(run_dir), "split": split, "stories": {}, "by_category": {}, "by_area": {}}
    covered_all = total_all = 0
    for sid in story_ids(split):
        key = json.loads((KEYS / f"{sid}.json").read_text())
        cases = load_cases(run_dir, sid)
        texts = [case_text(c) for c in cases or []]
        covered, missed = 0, []
        for sc in key["scenarios"]:
            hit = any(matches(t, sc["match"]) for t in texts)
            if not hit and judge == "llm" and cases:
                hit = llm_judge(sc, cases)
            for bucket, name in (("by_category", sc["category"]), ("by_area", sc["area"])):
                b = report[bucket].setdefault(name, {"covered": 0, "total": 0})
                b["total"] += 1
                b["covered"] += int(hit)
            covered += int(hit)
            if not hit:
                missed.append({"id": sc["id"], "category": sc["category"], "area": sc["area"],
                               "description": sc["description"]})
        report["stories"][sid] = {"covered": covered, "total": len(key["scenarios"]),
                                  "cases": len(cases or []), "valid": cases is not None, "missed": missed}
        covered_all += covered
        total_all += len(key["scenarios"])
    report["covered"], report["total"] = covered_all, total_all
    report["coverage"] = round(100 * covered_all / total_all, 1) if total_all else 0.0
    return report


def feedback_text(report):
    """Editor-safe feedback: weak AREAS and CATEGORIES only, never scenario descriptions.

    Giving the editor the exact missed scenarios would let it copy the answer key into
    the harness, which overfits to these stories and teaches nothing that generalises.
    """
    lines = [f"# Score feedback\n\nOverall coverage: {report['coverage']}% "
             f"({report['covered']}/{report['total']} expected scenarios)\n",
             "## Weak areas (covered / expected)"]
    areas = sorted(report["by_area"].items(), key=lambda kv: kv[1]["covered"] / kv[1]["total"])
    for name, b in areas:
        if b["covered"] < b["total"]:
            lines.append(f"- {name}: {b['covered']}/{b['total']}")
    lines.append("\n## By test type (covered / expected)")
    for name, b in sorted(report["by_category"].items()):
        lines.append(f"- {name}: {b['covered']}/{b['total']}")
    invalid = [s for s, r in report["stories"].items() if not r["valid"]]
    if invalid:
        lines.append(f"\n## Invalid or missing output files\n- {', '.join(invalid)}")
    return "\n".join(lines) + "\n"


def bar(pct, width=20):
    filled = round(pct / 100 * width)
    return "█" * filled + "░" * (width - filled)


def print_report(report, show_missed=False):
    print(f"\nRun: {report['run']}   split: {report['split']}")
    print(f"Coverage: {report['coverage']}%  {bar(report['coverage'])}  ({report['covered']}/{report['total']})\n")
    print(f"{'story':<10}{'covered':>9}{'cases':>7}")
    for sid, r in report["stories"].items():
        flag = "" if r["valid"] else "  (missing/invalid output)"
        print(f"{sid:<10}{r['covered']:>5}/{r['total']:<3}{r['cases']:>7}{flag}")
        if show_missed:
            for m in r["missed"]:
                print(f"           - [{m['category']}] {m['description']}")
    print("\nBy test type:")
    for name, b in sorted(report["by_category"].items()):
        pct = 100 * b["covered"] / b["total"]
        print(f"  {name:<16}{b['covered']:>3}/{b['total']:<3} {bar(pct, 10)}")


def print_comparison(reports):
    names = [Path(r["run"]).name for r in reports]
    print(f"\nSplit: {reports[0]['split']}")
    print(f"{'story':<10}" + "".join(f"{n:>12}" for n in names))
    for sid in reports[0]["stories"]:
        row = "".join(f"{r['stories'][sid]['covered']:>8}/{r['stories'][sid]['total']:<3}" for r in reports)
        print(f"{sid:<10}{row}")
    print(f"{'TOTAL':<10}" + "".join(f"{str(r['coverage']) + '%':>12}" for r in reports))
    print("\nBy test type:")
    for cat in sorted(reports[0]["by_category"]):
        row = "".join(f"{r['by_category'][cat]['covered']:>8}/{r['by_category'][cat]['total']:<3}" for r in reports)
        print(f"  {cat:<16}{row}")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--run", action="append", required=True, help="folder with <story_id>.json outputs (repeat to compare)")
    ap.add_argument("--split", choices=["train", "holdout", "all"], default="train")
    ap.add_argument("--judge", choices=["keyword", "llm"], default="keyword")
    ap.add_argument("--feedback", action="store_true", help="print editor-safe feedback only")
    ap.add_argument("--show-missed", action="store_true", help="list missed scenarios (humans only)")
    ap.add_argument("--json", help="write the report (single run) to this file")
    args = ap.parse_args()

    reports = [score_run(r, args.split, args.judge) for r in args.run]
    if args.json:
        Path(args.json).parent.mkdir(parents=True, exist_ok=True)
        Path(args.json).write_text(json.dumps(reports[0], indent=2))
    if args.feedback:
        print(feedback_text(reports[0]))
    elif len(reports) > 1:
        print_comparison(reports)
    else:
        print_report(reports[0], args.show_missed)


if __name__ == "__main__":
    main()
