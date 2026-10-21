# ShopEase refund rules

These rules apply to every refund story. Stories usually do not repeat them.

| # | Rule |
|---|------|
| R1 | Return window: 30 calendar days from the delivery date. Day 30 is allowed, day 31 is rejected. |
| R2 | Only orders with status Delivered or Partially Refunded can be refunded. Pending and Shipped orders cannot. Cancelled orders are voided, never refunded. |
| R3 | The total refunded for an order can never exceed the amount paid. |
| R4 | Money is in EUR with 2 decimals, rounded half up to the cent. A refund of €0.00 or less is never created. |
| R5 | A single refund above €500.00 needs Manager approval. Exactly €500.00 does not. |
| R6 | Refunds go to the original payment method. If that card is expired or closed, the refund is issued as store credit and the customer is notified. |
| R7 | Percentage promos apply per item. Fixed-amount promos are prorated across items by price. Promo codes are single use and are not reinstated after a refund. |
| R8 | Every refund request has a unique request ID. Repeating a request must never refund twice. |
| R9 | Customers can only request refunds for their own orders. Support Agents can issue refunds. Only Managers can approve. |
| R10 | Every refund, approval, rejection and skip writes an audit log entry (who, when, amount, reason). |
| R11 | If the payment provider fails, the refund is set to Failed, no money moves, and it can be retried. |
| R12 | The customer is emailed when a refund is processed, rejected or failed. |
