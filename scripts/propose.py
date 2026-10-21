#!/usr/bin/env python3
"""PROPOSE step: ask an editor model for candidate harness edits.

Each candidate gets a different focus, like Harness2's invariant vs domain edits.

Example
  python scripts/propose.py --harness harnesses/v1 --report runs/r1/base-train.json \
      --examples runs/r1/base-train --n 2 --out runs/r1/candidates
"""
import argparse
import json
import shutil
import subprocess
import tempfile
from pathlib import Path

from common import EDITOR_TOOLS, ROOT, copy_harness, require_claude, run_claude
from score import SPLITS, feedback_text

FOCUS = [
    "INVARIANT focus: improve the general procedure, techniques and self-checks - "
    "changes that would help in ANY product domain.",
    "DOMAIN focus: improve the product-domain knowledge in the skill - business rules and "
    "risk areas that apply to many stories in this domain.",
    "COMBINED focus: make the single most valuable change of any kind, then a second one.",
]


def propose(harness, report, examples, n, out, timeout=900, dry_run=False):
    out = Path(out)
    report = json.loads(Path(report).read_text()) if not isinstance(report, dict) else report
    candidates = []
    if not dry_run:
        require_claude()
    for i in range(n):
        focus = FOCUS[i % len(FOCUS)]
        cand = out / f"cand_{i + 1}"
        if dry_run:
            print(f"[dry-run] editor for cand_{i + 1}: {focus[:40]}...")
            candidates.append(cand)
            continue
        ws = Path(tempfile.mkdtemp(prefix=f"harness-editor-{i + 1}-"))
        copy_harness(harness, ws / "harness")
        (ws / "FEEDBACK.md").write_text(feedback_text(report))
        ex = ws / "examples"
        ex.mkdir()
        for f in Path(examples).glob("*.json"):
            shutil.copy(f, ex / f.name)
            story = next((d / f"{f.stem}.md" for d in SPLITS.values() if (d / f"{f.stem}.md").exists()), None)
            if story:
                shutil.copy(story, ex / story.name)
        prompt = (ROOT / "prompts" / "editor.md").read_text() + f"\n\nYour focus for this candidate: {focus}\n"
        print(f"  editor proposing cand_{i + 1} ...", flush=True)
        run_claude(prompt, ws, EDITOR_TOOLS, timeout)
        shutil.rmtree(cand, ignore_errors=True)
        copy_harness(ws / "harness", cand / "harness")
        if (ws / "CHANGES.md").exists():
            shutil.copy(ws / "CHANGES.md", cand / "CHANGES.md")
        diff = subprocess.run(["diff", "-ruN", str(harness), str(cand / "harness")], capture_output=True, text=True)
        (cand / "changes.diff").write_text(diff.stdout)
        shutil.rmtree(ws, ignore_errors=True)
        candidates.append(cand)
    return candidates


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--harness", required=True)
    ap.add_argument("--report", required=True, help="JSON report from score.py --json")
    ap.add_argument("--examples", required=True, help="run folder with the agent's outputs")
    ap.add_argument("--n", type=int, default=2)
    ap.add_argument("--out", required=True)
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    propose(args.harness, args.report, args.examples, args.n, args.out, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
