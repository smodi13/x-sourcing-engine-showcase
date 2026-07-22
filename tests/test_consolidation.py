"""Deduplication and consolidation tests."""
from engine.consolidation.dedup import (
    dedupe_authors, dedupe_within_run, remove_cross_run_duplicates,
)
from engine.consolidation.consolidate import consolidate, consolidation_key, normalize_name


def test_within_run_dedup_and_multi_query():
    records = [
        {"post_id": "1", "author_id": "a", "source_queries": ["q01"]},
        {"post_id": "1", "author_id": "a", "source_queries": ["q02"]},  # duplicate post, second query
        {"post_id": "2", "author_id": "b", "source_queries": ["q01"]},
    ]
    out, removed, multi = dedupe_within_run(records)
    assert removed == 1
    assert multi == 1  # post 1 matched two queries
    post1 = next(r for r in out if r["post_id"] == "1")
    assert post1["source_queries"] == ["q01", "q02"]


def test_cross_run_dedup():
    records = [{"post_id": "1"}, {"post_id": "2"}, {"post_id": "3"}]
    kept, removed = remove_cross_run_duplicates(records, {"2"})
    assert removed == 1
    assert {r["post_id"] for r in kept} == {"1", "3"}


def test_author_dedup_counts_unique():
    records = [{"author_id": "a"}, {"author_id": "a"}, {"author_id": "b"}, {"author_id": None}]
    assert dedupe_authors(records) == 2


def test_normalize_name_strips_suffix():
    assert normalize_name("Omninode AI") == "omninode"
    assert normalize_name("Acme Labs") == "acme"
    assert normalize_name("Foo, Inc.") == "foo"


def test_consolidation_key_falls_back_to_domain():
    rec = {"normalized_company_or_project_name": "", "artifact_urls": ["https://acme.dev/x"], "post_id": "p1"}
    assert consolidation_key(rec) == "acme"


def test_consolidate_groups_by_project():
    records = [
        {"post_id": "1", "author_id": "a", "normalized_company_or_project_name": "omninode",
         "artifact_urls": ["https://omninode.ai"], "source_queries": ["q01"]},
        {"post_id": "2", "author_id": "b", "normalized_company_or_project_name": "Omninode",
         "artifact_urls": ["https://omninode.ai/docs"], "source_queries": ["q02"]},
    ]
    groups = consolidate(records)
    assert len(groups) == 1
    g = groups[0]
    assert g["post_count"] == 2
    assert g["author_count"] == 2
    assert set(g["source_queries"]) == {"q01", "q02"}
