# Cost controls

Spending is planned, gated, fingerprinted, locked, and tracked in exact Decimal
arithmetic against a fixed allowance.

## Cost estimation

Monetary values are never floats. They are stored as quoted decimal strings,
parsed with decimal.Decimal, and serialized as fixed-point strings. See
`src/engine/cost_controls/money.py`.

## Count preflight

A counts-only request sizes seven-day volume before any retrieval, so spend is
planned rather than discovered.

## Approval

Paid requests required explicit approval. Approvals were configuration specific,
not blanket approvals, and expired after fifteen minutes.

## Fingerprints

Each request was reduced to a canonical representation and hashed with SHA-256.
The fingerprint bound the approval to that exact configuration. Changing any
field that affects returned resources, cost, or interpretation changed the
fingerprint, so an approval could not be reused for a different request. See
`src/engine/cost_controls/approval.py`.

## Expiration and locks

Approvals expired after fifteen minutes. A run lock prevented duplicate paid
execution. Raw responses were stored before any derived output was written, and
the system failed closed if a control could not be verified.

## Raw before derived

Raw API responses were always stored before derived outputs. This makes the run
reproducible offline and ensures historical outputs are never altered by a later
run.

## Ledger for the completed run

| Phase | Estimated USD |
| --- | --- |
| Pilot phase (cumulative) | 1.085 |
| Broad count preflight (20 requests) | 0.100 |
| Broad retrieval (1,279 posts) | 6.395 |
| Broad profile enrichment (14 profiles) | 0.140 |
| Cumulative estimated activity | 7.720 |
| Estimated remaining allowance | 17.280 |

API activity is estimated, not reconciled against the external Developer
Console, which belonged to a separate project and was not accessible.
