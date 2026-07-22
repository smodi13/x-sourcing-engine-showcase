# Metrics reconciliation

This document reconciles the metric layers used across the sourcing run and this
public showcase. It is safe for public viewing and contains no private paths,
credentials, or personal data. The machine-readable version is
`public/demo-data/metrics-provenance.json`.

## Definitions

- Post resource: a returned Post from recent search. The broad run returned
  1,279 Post resources. This is not a count of unique Posts.
- Net-new Post: a unique Post after within-run and cross-run deduplication
  (1,166).
- Post with external product-artifact links: a Post carrying at least one
  resolved external product-artifact link (851). This is broader than the strict
  verified Level A standard and is never labeled Level A.
- Strict verified Level A Post: a Post that met the strict verified Level A
  standard with has_level_a true (737). A subset of the 851 artifact-bearing
  Posts.
- Actionable Post: a Post passing attribution and artifact checks (187).
- Engine-consolidated actionable project: a project produced by the
  deterministic engine consolidation (159).
- Analyst-adjudicated project: a project remaining after final analyst
  adjudication of the engine-consolidated set (153).
- Sanitized broad-run project record: a public record shown in the results table
  (122).

## Public funnel

1. 1,166 net-new Posts
2. 851 Posts with external product-artifact links
3. 737 strict verified Level A Posts
4. 190 direct-builder claims
5. 187 actionable Posts
6. 159 engine-consolidated actionable projects
7. 153 projects after final analyst adjudication
8. 122 sanitized broad-run project records displayed publicly
9. 1 separate featured AOS investment-analysis page

These are stage counts, not strictly nested subsets.

## Artifact-bearing Posts versus strict Level A: 851 and 737

- 851 Posts contained at least one resolved external product-artifact link.
  Source: the artifact evidence audit, counting Posts with one or more resolved
  external artifacts.
- 737 Posts met the strict verified Level A standard (has_level_a true). Source:
  the artifact evidence audit and global metrics.
- The difference of 114 is artifact-bearing Posts that did not meet the strict
  verified Level A standard. 851 is the broader artifact-bearing measure and is
  not Level A. 737 is the strict verified subset. Neither is an error.

## Engine-consolidated versus analyst-adjudicated projects: 159 and 153

- 159 is the count of actionable projects produced by the deterministic engine
  consolidation, formed from 124 keep_verified plus 35 keep_for_enrichment.
- 153 is the count remaining after final analyst adjudication that merged
  near-duplicate projects and reclassified a small number of borderline
  non-company projects.
- The final six-project reduction was preserved as an aggregate in the
  investment package, but the individual merge and reclassification decisions
  were not retained in a record-level audit file. We do not enumerate the six
  records, and the absence of the itemized delta is a records-retention gap, not
  an error in the counts.

## Public subset: 122 records

The results interface shows 122 sanitized broad-run project records. They are
generated from the 187 actionable Post records:

```
187 actionable Posts
 -  37 records with no engine-normalized project name (cannot be shown as a
        meaningful, safe public project row)
 = 150 named Posts
 -  28 same-project duplicate Posts (collapsed to one record by normalized-name
        slug)
 = 122 sanitized broad-run project records
```

Total excluded from public display: 65 (37 unnamed plus 28 duplicate collapses).

This public transformation starts from the 187 actionable Posts and is not a
direct subtraction from the 153 analyst-adjudicated project set. The public
subset consolidates by normalized project-name slug, a simpler key than the
engine consolidation. The private engine outputs remain unchanged.

## AOS / Unicity Labs

AOS / Unicity Labs is a separate featured investment-analysis page sourced from
the earlier pilot and targeted-enrichment comparison. It is not included in the
122 broad-run project records. Candidate detail pages total 123: 122 sanitized
broad-run project records and one featured AOS analysis page. These are detail
pages, not 123 equivalent candidates.

## Multi-query Posts

Per-query Post and actionable counts are attributed to each query and sum higher
than the deduplicated run totals of 1,166 net-new Posts and 187 actionable
Posts, because 68 Posts matched more than one query family. Query-level sums are
never presented as deduplicated global totals.

## What the site does not claim

- Not 1,279 unique Posts. 1,279 is returned Post resources.
- 851 is not a Level A count and is not a company count.
- Not 153 incorporated startups. 153 is analyst-adjudicated projects.
- Not 123 equivalent candidates. 123 is detail pages.
