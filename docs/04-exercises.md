# 4. Exercises

## 1. Push past 92% without overfitting

v2 still misses seven scenarios (`score.py --run sample_runs/v2 --split all --show-missed`).
Improve `harnesses/v2` into your own `harnesses/v3` so the agent would catch them.

Rule: you may not mention any story, order number or specific missed scenario. Every edit
must be a general technique or a domain rule. For example, "test zero and empty values for
every count and quantity" is allowed, while "test quantity 0 for T-shirts" is not.

If you have Claude Code, run your harness and score it:

```bash
python scripts/run_agent.py --harness harnesses/v3 --split all --out runs/v3
python scripts/score.py --run sample_runs/v2 --run runs/v3 --split all
```

## 2. Watch overfitting happen

Write a candidate harness that lists the exact missed scenarios from the train split.
Run it on train and holdout. Train should improve, holdout should not. Then run
`loop.py` with it as a candidate and confirm the gate rejects it.

## 3. Ablation: which edit mattered?

Make four copies of v2, each with one part removed: the procedure, `techniques.md`,
`domain/refunds.md`, or `checklist.md`. Score each. Rank the parts by how much coverage
drops without them. This tells you where to invest when building harnesses at work.

## 4. Real composition

`loop.py` keeps only the best candidate. Change it so that, after probing, an editor call
reads all candidates' `CHANGES.md` and scores and merges the edits that helped into one
composed harness, which is then probed once more. This is closer to Harness².

## 5. Calibrate the LLM judge

Pick 30 scenario/test-case pairs and label them yourself (covered / not covered). Run
`--judge llm` and measure agreement. Below 90%, improve the judge prompt in `score.py`.

## 6. Measure noise

Run the same harness three times on train. How much does coverage vary? A change is only
an improvement if it beats that noise. Add a `--repeats` option to `run_agent.py`.

## 7. Add your own product domain

1. Write 5 train and 2 holdout stories in `data/stories/` (keep the same format).
2. For each, write an answer key in `data/answer_keys/` with 8–12 scenarios across
   positive, negative, boundary, security, integration, data-integrity and audit.
   Include scenarios that depend on business rules the story does not state.
3. Run v1 to get a baseline, then let the loop improve it. Compare which edits are
   invariant (reusable from the refunds domain) and which are new domain edits.

Tip: an LLM can draft stories and answer keys quickly, but a domain expert must review the
answer keys. A wrong answer key trains the harness in the wrong direction.

## 8. Add a second agent

Add an `automation-writer` agent that turns the test cases into Playwright tests, with its
own skill (framework structure, rules, patterns). Score it differently: do the tests run,
and how many seeded bugs (mutations) do they catch? Improve each agent's harness with its
own loop.
