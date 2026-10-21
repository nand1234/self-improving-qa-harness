# 1. Concepts

## Agent = model + harness

A model on its own only predicts text. The **harness** turns it into an agent: the
instructions, tools, knowledge, memory and checks around it. When an agent does poor
work, the cause is often the harness, not the model. Fixing the harness is faster,
cheaper and easier to review than switching or retraining the model.

## Harness² in Claude Code terms

| Harness² component | In this lab | Claude Code location |
|---|---|---|
| System prompt | Role + procedure | `.claude/agents/test-case-creator.md` (body) |
| Skills | Techniques, domain rules, format | `.claude/skills/test-case-creation/` |
| Memory | Lessons carried between tasks | `.claude/agent-memory/test-case-creator/MEMORY.md` |
| Guardrails | Self-check before saving | `skills/.../checklist.md` |
| Tool guidance | Allowed tools | `tools:` in the agent frontmatter |
| Subagents | One agent per role | more files in `.claude/agents/` |

The agent file links the rest together through its frontmatter:

```yaml
skills: test-case-creation   # load this skill at startup
memory: project              # give the agent .claude/agent-memory/test-case-creator/
```

## Why synthetic data with an answer key

Harness² works without an answer key, because real tasks rarely have one. When **you**
generate the tasks, you can write the answer key at the same time. For test design, the
answer key is the list of scenarios a strong tester would cover: boundaries, invalid states,
permissions, duplicates, failures, money rules and audit. Coverage of that list becomes
an objective score.

Look at `data/answer_keys/REF-001.json`. Each scenario has a category, an area, a
description and keyword groups used for matching:

```json
{"id": "REF-001-S03", "category": "boundary", "area": "return-window",
 "description": "Request on day 31 after delivery is rejected",
 "match": [["day 31", "31 days", "31st day"]]}
```

## The improvement loop

```
          ┌──────────── lessons + adopted harness ────────────┐
          ▼                                                    │
  run harness on TRAIN ──► score ──► PROPOSE edits ──► PROBE each on TRAIN
                                                              │
                                     GATE on HOLDOUT ◄── COMPOSE best
                                          │
                              adopt as v<N+1> (human reviews diff)
```

**Propose.** An editor model reads the harness, the agent's outputs and *area-level*
feedback, then suggests edits. It runs several times with different focuses:
**invariant** edits help in any domain (procedure, techniques, checklist), and **domain**
edits add product knowledge.

**Probe.** Every candidate runs on the same tasks, so differences come from the harness.

**Compose.** The evidence decides what is kept. This lab keeps the best candidate.
Harness² goes further and merges what worked across candidates.

**Gate.** A change counts only if it also improves the **holdout** stories. Holdout
stories are never used for tuning, so gains there show the harness learned something
general rather than memorising the train stories.

**Carry lessons forward.** Short lessons go into the agent's memory so the next task
starts smarter.

## Two rules that keep the loop honest

1. **The answer key never reaches the agent or the editor.** Agents run in temporary
   folders outside the repo. The editor sees "idempotency: 0/3", never the scenario text.
2. **Memory is frozen during scoring runs.** Each candidate is judged on equal footing.
   Lessons are written on purpose in the compose step, not as a side effect of a run.
