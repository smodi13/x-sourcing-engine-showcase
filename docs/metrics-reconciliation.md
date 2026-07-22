# Metrics reconciliation

This document reconciles the metric layers used across the sourcing run and this
public showcase. It is safe for public viewing and contains no private paths,
credentials, or personal data. The machine-readable version is
`public/demo-data/metrics-provenance.json`.

## Metric layers

There are three layers:

1. Final adjudicated metrics, used in the completed investment package summary.
2. Intermediate processing-stage metrics, recorded by the engine mid-pipeline.
3. The sanitized public-display subset shown in this demo.

The public summary uses the final adjudicated metrics. Intermediate artifacts are
shown here for provenance. They are not errors. They measure different bars at
different stages.

## Definitions

- Post resource: a returned Post from recent search. The broad run returned
  1,279 Post resources. This is not a count of unique Posts.
- Net-new Post: a unique Post after within-run and cross-run deduplication
  (1,166).
- Artifact Post: a Post carrying at least one external product artifact link
  (851).
- Verifiable Level A Post: a Post whose artifact met the strict verifiable Level
  A bar after link resolution (737).
- Actionable Post: a Post passing attribution and artifact checks (187).
- Consolidated company or project: a consolidated project, not an incorporated
  startup (153 final, 159 intermediate).

## Level A: 737 versus 851

- 737 is the intermediate count of Posts whose external artifact met the strict
  verifiable Level A bar. Source: the engine global metrics and the artifact
  evidence audit, where 737 of 1,166 Posts have a verifiable Level A artifact.
- 851 is the count of Posts that carry at least one external product artifact
  link. Source: the same artifact evidence audit, counting Posts with one or
  more resolved external artifacts.
- The difference of 114 is Posts that carry an external artifact link but whose
  artifact did not meet the strict verifiable Level A bar at the intermediate
  stage. 851 is the broader artifact-bearing Post count. 737 is the strict
  verifiable subset. The final package uses 851 as the headline artifact-Post
  figure.

## Consolidated projects: 159 versus 153

- 159 is the engine's intermediate count of actionable consolidated projects,
  formed from 124 keep_verified plus 35 keep_for_enrichment in the consolidated
  company output.
- 153 is the final adjudicated count in the completed package, after a final
  manual adjudication that merged near-duplicate projects and reclassified a
  small number of borderline non-company projects.
- The 6-project reduction is a final-adjudication step. It is not itemized as a
  separate saved engine audit file, so the six records are not enumerated here.
  We do not guess at a per-record breakdown that the saved outputs do not record.

## Public subset: 122 records

The results interface shows 122 sanitized project records. They are derived from
the 187 broad-run actionable Posts:

```
187 actionable Posts
 -  37 Posts with no engine-normalized project name (cannot be shown as a
        meaningful, safe public project row)
 = 150 named Posts
 -  28 same-project duplicate Posts (collapsed to one record by normalized-name
        slug)
 = 122 unique public project records
```

Total excluded from public display: 65 (37 unnamed plus 28 duplicate collapses).

The public subset consolidates by normalized project-name slug, which is a
simpler key than the engine's final adjudicated consolidation (repo, domain, or
project plus author). For that reason, 122 is not a strict subtraction from 153.
The private engine outputs remain unchanged.

## AOS / Unicity Labs

AOS / Unicity Labs is not among the 122 broad-run records. It was surfaced by the
same engine in the earlier pilot and targeted-enrichment comparison, and is
presented separately as the featured investment-thesis page. Candidate detail
pages total 122 broad-run records plus 1 featured page, which is 123 pages
representing 122 unique broad-run sourced projects plus the featured thesis.

## Multi-query Posts

Per-query Post and actionable counts are attributed to each query and sum higher
than the deduplicated run totals of 1,166 net-new Posts and 187 actionable
Posts, because 68 Posts matched more than one query family. Query-level sums are
never presented as deduplicated global totals.

## What the site does not claim

- Not 1,279 unique Posts. 1,279 is returned Post resources.
- Not 851 companies. 851 is a Post count.
- Not 153 incorporated startups. 153 is consolidated companies or projects.
- Not a specific count of unique engine-sourced companies beyond the verified
  public records.
