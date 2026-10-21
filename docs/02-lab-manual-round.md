# 2. Lab: one manual round

Time: about 45 minutes. No API key needed.

## Step 1: Read the story and the weak harness

Open `data/stories/train/REF-001.md`, then everything in `harnesses/v1/`. The agent prompt
is two lines and the skill only describes the output format.

Before scoring, write down which test cases **you** would design for REF-001.

## Step 2: Score v1

```bash
python scripts/score.py --run sample_runs/v1 --show-missed
```

v1 covers **32%**. Look at what it produced (`sample_runs/v1/REF-001.json`): four
reasonable happy-path cases and nothing else. Look at the type breakdown:

```
audit 0/5   boundary 0/9   data-integrity 0/6   security 0/2   positive 14/16
```

The agent is not "bad at testing". It was never told *how* to test or *what the business
rules are*.

## Step 3: Read the feedback the editor would get

```bash
python scripts/score.py --run sample_runs/v1 --feedback
```

It lists weak **areas** (return-window 0/2, idempotency 0/3, refund-cap 0/3, ...) but no
scenario descriptions. Discuss with your group why giving the editor the full list of missed
scenarios would be a mistake. Hint: what would the editor write into the harness?

## Step 4: Diagnose the causes

Sort the misses into causes. This is the core skill of harness engineering.

| Cause | Example miss | Fix type |
|---|---|---|
| Missing technique | No day 30 / day 31 tests | invariant: `techniques.md` |
| Missing knowledge | Refund cap, rounding, audit (not in any story) | domain: `domain/refunds.md` |
| No self-check | Gaps never noticed | invariant: `checklist.md` |
| Weak procedure | Stops after happy paths | invariant: agent prompt |
| Format too narrow | Only `positive` / `negative` allowed | invariant: `format.md` |

## Step 5: Compare with v2

Read `harnesses/v2/CHANGES.md`, then the v2 files. Every edit maps to one cause above.
Note that `domain/refunds.md` holds business rules that no story states, such as
"refunds can never exceed the amount paid". Real teams keep these in a wiki, and agents
miss them unless the harness includes them.

```bash
python scripts/score.py --run sample_runs/v1 --run sample_runs/v2 --split all
```

| | Train | Holdout |
|---|---|---|
| v1 | 32.0% | 33.3% |
| v2 | 92.0% | 87.5% |

The holdout stories (damaged items, bulk refunds) were never used to design v2, yet
coverage jumped there too. That is the evidence that v2 generalises.

## Step 6: Find what v2 still misses

```bash
python scripts/score.py --run sample_runs/v2 --split all --show-missed
```

Seven scenarios remain, including a zero quantity, rejecting without a reason, and a
duplicate bulk run. Exercise 1 asks you to fix these **without** naming them in the harness.

## Discussion questions

1. Which v2 edit do you think contributed most? How would you prove it? (See exercise 3.)
2. v2 writes about twice as many test cases. When does more coverage become noise?
3. Which parts of v2 would work unchanged for a payments or a travel-booking product?
