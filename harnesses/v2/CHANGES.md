# v1 -> v2 changes

Feedback for v1 (train split): 32% coverage. Weakest test types: audit 0/5, boundary 0/9,
data-integrity 0/6, security 0/2. Weakest areas: return-window, idempotency, refund-cap,
rounding, approval-threshold.

| Edit | Kind | Weakness it targets |
|------|------|---------------------|
| Agent prompt: 6-step procedure + rules | invariant | Agent wrote 4 happy-path cases and stopped |
| `techniques.md` | invariant | No boundary, permission, idempotency or failure tests |
| `checklist.md` | invariant | No self-check, so gaps were never noticed |
| `domain/refunds.md` | domain | Implicit business rules (cap, rounding, audit, roles) were unknown to the agent |
| `MEMORY.md` lessons | lesson | Carry the three biggest lessons into future tasks |
| `type` values widened in `format.md` | invariant | Output format allowed only positive/negative |

**Invariant** edits help in any product domain. **Domain** edits encode knowledge about
this product. Harness² proposes both kinds and keeps whichever the evidence supports.
