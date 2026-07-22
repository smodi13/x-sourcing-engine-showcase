# Sanitized engine excerpts

These modules are sanitized, self-contained excerpts of the deterministic X
sourcing engine. They preserve the actual technical approach for query
validation, evidence classification, builder attribution, URL handling,
deduplication, consolidation, selective enrichment, and budget governance.

They contain no credentials, no bearer-token handling, no private paths, and no
raw API payloads, and they perform no network calls. They are illustrative of
the private engine's logic and are exercised by the test suite in `tests/`.

The full production engine (the complete CLI, the X client, the persisted
approval and lock stores, and the raw run outputs) is kept private.

Layout:

- `search/` query validation and count preflight
- `classification/` evidence levels, builder attribution, URL resolution, ownership
- `consolidation/` deduplication and company consolidation
- `enrichment/` selective profile enrichment logic
- `cost_controls/` Decimal money math, request fingerprints, approvals, locks
- `reporting/` run metrics
