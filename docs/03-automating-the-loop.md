# 3. Automating the loop

## Try it offline first

```bash
PATH="$PWD/scripts/sim:$PATH" python scripts/loop.py --harness harnesses/v1 --round demo
cat experiments/log.md
```

`scripts/sim/claude` stands in for the real CLI. The "agent" returns the sample runs and
the "editor" copies in v2 files. You see every stage, workspace and log entry without
spending anything. Delete the generated `harnesses/v3` afterwards.

## Real runs with Claude Code

```bash
python scripts/loop.py --harness harnesses/v1 --dry-run
python scripts/loop.py --harness harnesses/v1 --candidates 2 --round r1
```

What happens:

| Stage | Script | Output in `runs/r1/` |
|---|---|---|
| Baseline on train | `run_agent.py` | `base-train/`, `base-train.json` |
| Propose N candidates | `propose.py` | `candidates/cand_N/harness/`, `CHANGES.md`, `changes.diff` |
| Probe on train | `run_agent.py` | `candidates/cand_N/train/` |
| Compose: best on train | `loop.py` | printed table |
| Gate on holdout | `run_agent.py` | `base-holdout/`, `candidates/cand_N/holdout/` |
| Adopt | `loop.py` | `harnesses/v<N+1>/`, entry in `experiments/log.md` |

Each agent run calls:

```bash
claude -p "Use the test-case-creator subagent to write test cases for stories/REF-001.md ..." \
       --allowedTools Read,Write,Edit,Agent
```

inside a temporary workspace that contains only `.claude/`, the story and an empty
`output/` folder. Check the flags in `scripts/common.py` against `claude --help` for your
version.

## Running it on a schedule

A nightly cron job or CI pipeline can run one round and open a pull request with the new
harness version. Keep a person in the loop: the script never installs a harness, it only
proposes one. Use `scripts/install_harness.py` after reviewing `changes.diff`.

## Scoring real outputs

Keyword matching is fast and free but can miss a test case written in unusual words.
For real runs, add the LLM judge as a fallback for anything the keywords missed:

```bash
python scripts/score.py --run runs/r1/base-train --judge llm
```

Before trusting the judge, hand-check 20–30 of its decisions (exercise 5).

## Pitfalls

| Pitfall | Symptom | Guard in this lab |
|---|---|---|
| Answer-key leak | Train score jumps to ~100% | Workspaces outside the repo; editor gets areas only |
| Overfitting | Train up, holdout flat | Holdout gate in `loop.py` |
| Story-specific edits | Harness mentions order numbers | Hard rule in `prompts/editor.md`; review the diff |
| Harness bloat | Prompt grows every round | Size limits in the editor prompt |
| Noisy comparisons | Scores jump between identical runs | Run each harness 2–3 times and average (exercise 6) |
| Runaway cost | Large bills | `--dry-run`, small splits, few candidates |
