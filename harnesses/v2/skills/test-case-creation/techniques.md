# Test design techniques

## Boundary value analysis
For every limit (days, amounts, quantities, counts, file sizes) test the value **at** the
limit, **just inside** and **just outside** it. Example: 30-day window -> day 30, day 31.
Also test zero and empty values for quantities and counts.

## Equivalence partitioning
Group inputs that should behave the same and pick one value per group: valid, invalid,
and each distinct type (e.g. each payment method, each promo type).

## Invalid states
List every status the object can be in and test the action in each status where it
should NOT be allowed.

## State transitions
Test each status change the story describes, including the final one
(e.g. Partially Refunded -> Refunded when the last item is refunded).

## Permissions and ownership
Test the action as the wrong role and as a different user who does not own the data.

## Duplicates and idempotency
Repeat the same request (double click, retry, same request ID). Nothing may happen twice.

## Integration failures
When an external system is involved (payment provider, email), test what happens when it
fails or times out.

## Data integrity
Money: 2 decimals, correct rounding, totals never exceed what was paid.

## Audit and notifications
Check the audit log entry and the customer message for every outcome.
