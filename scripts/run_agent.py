#!/usr/bin/env python3
"""Run the test-case-creator agent with a given harness on every story in a split.

Each story runs in a fresh, isolated workspace. Agent memory is FROZEN during runs:
whatever the agent writes to memory is thrown away, so every candidate harness is
judged on the same footing. Lessons are added deliberately in the compose step.

Example
  python scripts/run_agent.py --harness harnesses/v1 --split train --out runs/v1-train
"""
import argparse
import shutil
from pathlib import Path

from common import AGENT_TOOLS, make_workspace, require_claude, run_claude
from score import SPLITS


def run_harness(harness, split, out, agent="test-case-creator", timeout=900, dry_run=False):
    out = Path(out)
    out.mkdir(parents=True, exist_ok=True)
    stories = sorted(p for name, d in SPLITS.items() if split in (name, "all") for p in d.glob("*.md"))
    if not dry_run:
        require_claude()
    for story in stories:
        prompt = (f"Use the {agent} subagent to write test cases for stories/{story.name}. "
                  f"The result must be saved as JSON to output/{story.stem}.json.")
        if dry_run:
            print(f"[dry-run] {story.stem}: claude -p \"{prompt}\"  (harness: {harness})")
            continue
        ws = make_workspace(harness, prefix=f"harness-ws-{story.stem}-")
        (ws / "stories").mkdir()
        (ws / "output").mkdir()
        shutil.copy(story, ws / "stories" / story.name)
        print(f"  running {story.stem} ...", flush=True)
        result = run_claude(prompt, ws, AGENT_TOOLS, timeout)
        produced = ws / "output" / f"{story.stem}.json"
        if produced.exists():
            shutil.copy(produced, out / produced.name)
        else:
            print(f"  ! {story.stem}: no output file (exit {result.returncode})")
            (out / f"{story.stem}.log").write_text(result.stdout + "\n" + result.stderr)
        shutil.rmtree(ws, ignore_errors=True)
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--harness", required=True, help="folder with agents/, skills/, agent-memory/")
    ap.add_argument("--split", choices=["train", "holdout", "all"], default="train")
    ap.add_argument("--out", required=True)
    ap.add_argument("--agent", default="test-case-creator")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()
    run_harness(args.harness, args.split, args.out, args.agent, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
