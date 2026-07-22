# Methodology

## Sourcing thesis

Early company signals surface on X before they appear in structured databases. A
deterministic engine can convert a sourcing thesis into official X API queries,
separate builders from commentary, verify public product artifacts, and produce
an auditable diligence queue within a fixed budget.

## Query design

The engine uses three role-topic groups by three discovery lanes and ships a
small curated set rather than every lane by topic combination.

Discovery lanes:

- product_artifact: product launches and open-source artifacts
- founder_transition: leaving a job, building in stealth, seeking a cofounder
- early_traction: design partners, first customers, production use

The pilot shipped six curated queries. The broad-market run expanded to twenty
queries across five market groups (ai, non_ai_b2b, hardware_deeptech,
physical_products, cross_sector). The exact query strings are in
`config/pilot_queries.example.yaml` and `config/broad_queries.example.yaml`, and
they are displayed verbatim on the methodology page of the demo.

A validator runs before any API call. It rejects unsupported operators such as
min_faves, enforces the allowed operator set, requires a standalone term
alongside conjunction-required operators such as has:links, and enforces the
512-character recent-search limit.

## Deterministic rules

- Scoring and classification are deterministic Python. No language model assigns
  a score or a disposition.
- Time decay applies only to time-sensitive signals, never to enduring facts.
- Engagement and follower counts are non-scoring and cannot advance a lead.

## Enrichment strategy

Only shortlisted profiles are enriched, to respect the budget and avoid
unnecessary paid calls. Enrichment examines founder and executive roles, company
links, and identity evidence. It ignores follower count and verification status
for advancement.

## Human review

The engine organizes evidence and structures comparison. It did not select the
investment candidate. The final decision was human judgment. The scorecard was a
decision aid, not the decision.
