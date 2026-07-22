# Evidence framework

Every material claim is tagged by evidence level. An artifact is never presented
as proven traction.

## Levels

- Level A: a direct external product artifact such as a GitHub repository,
  documentation, a product website, or a live demo.
- Level B: a founder or builder launch statement without a qualifying external
  artifact.
- Level C: indirect supporting evidence.
- Level D: weak, unresolved, or non-actionable evidence.

The strongest level present determines how a lead is treated. See
`src/engine/classification/evidence.py`.

## Artifact types

github_repository, documentation, product_website, live_demo, api_endpoint,
app_store_listing.

## Builder attribution

Before a lead is trusted, the engine decides who is speaking: direct builder,
employee, third-party reporter, reviewer, investor, industry commentator,
established-company announcement, or unrelated author. A first-person build
statement ("we launched", "I built") is a direct builder claim. See
`src/engine/classification/builder_attribution.py`.

## Ownership checks

An artifact alone does not prove ownership. The engine checks the relationship
between the author and the artifact's organization. A repository under an
established organization is not treated as the author's own company. See
`src/engine/classification/ownership.py`.

## Disposition logic

A lead is actionable when a direct builder is paired with a Level A artifact.
Actionable leads route to keep_verified or keep_for_enrichment. Third-party
announcements, commentary, and out-of-scope posts are archived with a reason
code. Ambiguous leads route to manual review.
