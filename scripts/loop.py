#!/usr/bin/env python3
"""One full improvement round: run -> score -> propose -> probe -> compose -> gate.

  1. Run the current harness on the TRAIN stories and score it (baseline).
  2. PROPOSE: the editor model writes N candidate harnesses from editor-safe feedback.
  3. PROBE: run every candidate on the same TRAIN stories and score it.
  4. COMPOSE (simplified): keep the best candidate - it must beat the baseline on train.
     Harness2 merges evidence from several candidates; exercise 4 adds that.
  5. GATE: run baseline and best candidate on the HOLDOUT stories. Adopt only if the
     candidate also wins there - otherwise it overfit to the train stories.
  6. Save the adopted harness as harnesses/v<N+1> and log the round. A human reviews
     the diff before installing it anywhere real.

Example
  python scripts/loop.py --harness harnesses/v1 --candidates 2
  python scripts/loop.py --harness harnesses/v1 --dry-run        # plan + cost, no calls
"""
import argparse
import json
import re
import shutil
from datetime import datetime
from pathlib import Path

from common import ROOT, copy_harness
from propose import propose
from run_agent import run_harness
from score import score_run, story_ids


def next_version():
    nums = [int(m.group(1)) for p in (ROOT / "harnesses").iterdir() if (m := re.fullmatch(r"v(\d+)", p.name))]
    return f"v{max(nums, default=0) + 1}"


def save(report, path):
    Path(path).write_text(json.dumps(report, indent=2))
    return report


def log(lines):
    f = ROOT / "experiments" / "log.md"
    with f.open("a") as fh:
        fh.write("\n" + "\n".join(lines) + "\n")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--harness", required=True)
    ap.add_argument("--candidates", type=int, default=2)
    ap.add_argument("--round", default=datetime.now().strftime("round-%Y%m%d-%H%M"))
    ap.add_argument("--dry-run", action="store_true", help="print the plan and number of model calls")
    args = ap.parse_args()

    harness, n = Path(args.harness), args.candidates
    rd = ROOT / "runs" / args.round
    n_train, n_hold = len(story_ids("train")), len(story_ids("holdout"))

    if args.dry_run:
        calls = n_train * (1 + n) + n + 2 * n_hold
        print(f"Round '{args.round}' with harness {harness} and {n} candidates")
        print(f"  baseline train runs : {n_train}")
        print(f"  editor calls        : {n}")
        print(f"  candidate train runs: {n_train * n}")
        print(f"  holdout gate runs   : {2 * n_hold}")
        print(f"  total claude calls  : {calls}  (each agent run may use several model turns)")
        run_harness(harness, "train", rd / "base-train", dry_run=True)
        propose(harness, {"coverage": 0, "covered": 0, "total": 0, "by_area": {}, "by_category": {}, "stories": {}},
                rd / "base-train", n, rd / "candidates", dry_run=True)
        return

    print("1. Baseline on train")
    run_harness(harness, "train", rd / "base-train")
    base = save(score_run(rd / "base-train", "train"), rd / "base-train.json")
    print(f"   baseline train coverage: {base['coverage']}%")

    print("2. Propose candidates")
    cands = propose(harness, base, rd / "base-train", n, rd / "candidates")

    print("3. Probe candidates on train")
    results = []
    for c in cands:
        run_harness(c / "harness", "train", c / "train")
        rep = save(score_run(c / "train", "train"), c / "train.json")
        results.append((rep["coverage"], c))
        print(f"   {c.name}: {rep['coverage']}%")

    best_cov, best = max(results, key=lambda r: r[0])
    entry = [f"## {args.round}", "", f"- Harness: `{harness}`",
             f"- Train: baseline {base['coverage']}% | " + " | ".join(f"{c.name} {cov}%" for cov, c in results)]
    if best_cov <= base["coverage"]:
        print("4. No candidate beat the baseline. Nothing adopted.")
        log(entry + ["- Result: **rejected** (no train improvement)"])
        return

    print(f"4. Best candidate: {best.name} ({best_cov}%). Gating on holdout")
    run_harness(harness, "holdout", rd / "base-holdout")
    run_harness(best / "harness", "holdout", best / "holdout")
    base_h = save(score_run(rd / "base-holdout", "holdout"), rd / "base-holdout.json")
    best_h = save(score_run(best / "holdout", "holdout"), best / "holdout.json")
    entry.append(f"- Holdout: baseline {base_h['coverage']}% | {best.name} {best_h['coverage']}%")

    if best_h["coverage"] <= base_h["coverage"]:
        print("5. Candidate did not improve on holdout - it overfit. Not adopted.")
        log(entry + ["- Result: **rejected** (overfit: train up, holdout not)"])
        return

    version = next_version()
    dest = ROOT / "harnesses" / version
    copy_harness(best / "harness", dest)
    if (best / "CHANGES.md").exists():
        shutil.copy(best / "CHANGES.md", dest / "CHANGES.md")
    print(f"5. Adopted as harnesses/{version}. Review {best / 'changes.diff'} before installing it.")
    log(entry + [f"- Result: **adopted** as `harnesses/{version}` (diff: `{best.relative_to(ROOT)}/changes.diff`)"])


if __name__ == "__main__":
    main()
