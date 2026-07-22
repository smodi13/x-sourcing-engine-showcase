import fs from "node:fs";
import path from "node:path";

// Server-side loader for the sanitized static demo JSON. All data is local.
// There is no network access here and no X API call anywhere in the app.

const DATA_DIR = path.join(process.cwd(), "public", "demo-data");

export class DemoDataError extends Error {}

function readJson<T>(file: string): T {
  const full = path.join(DATA_DIR, file);
  let raw: string;
  try {
    raw = fs.readFileSync(full, "utf8");
  } catch {
    throw new DemoDataError(`Missing demo data file: ${file}. Run scripts/build_sanitized_demo_data.py.`);
  }
  try {
    return JSON.parse(raw) as T;
  } catch {
    throw new DemoDataError(`Malformed JSON in demo data file: ${file}.`);
  }
}

// ---------------------------------------------------------------------------
// Types
// ---------------------------------------------------------------------------
export interface Provenance {
  source_file: string;
  transform_version: string;
  generated_at: string;
  note: string;
}

export interface HeadlineMetric {
  key: string;
  label: string;
  value: number | string;
  note: string;
}

export interface Endpoint {
  method: string;
  url: string;
  purpose: string;
}

export interface RunSummary {
  replay_notice: string;
  official_api_used: boolean;
  scraping_used: boolean;
  llm_in_classification_or_disposition: boolean;
  final_selection: string;
  billing_reconciled: boolean;
  recent_search_window_days: number;
  searched_entire_market: boolean;
  official_endpoints: Endpoint[];
  pilot: Record<string, number | string>;
  broad: Record<string, number | string>;
  metric_notes: Record<string, string>;
  headline_metrics: HeadlineMetric[];
  provenance: Provenance;
}

export interface Candidate {
  slug: string;
  name: string;
  sector_bucket: string | null;
  source_queries: string[];
  post_url: string | null;
  artifact_urls: string[];
  artifact_types: string[];
  artifact_owner_scope: string | null;
  evidence_levels: string[];
  announcement_attribution: string | null;
  actor_project_relation: string | null;
  broad_market_relevance: string | null;
  headline_mandate_fit: string | null;
  general_venture_attractiveness: string | null;
  research_score: number | null;
  reason_codes: string[];
  unresolved_questions: string[];
  lead_disposition: string | null;
  company_status: string;
  candidate_rank: number | null;
  is_featured: boolean;
}

export interface FeaturedCandidate {
  slug: string;
  name: string;
  sector_bucket: string;
  is_featured: true;
  company_status: string;
  summary: string;
  public_facts: { claim: string; evidence_class: string }[];
  artifact_urls: string[];
  artifact_types: string[];
  evidence_levels: string[];
  disposition_note: string;
  thesis_availability: string;
  thesis_note: string;
  unresolved_questions: string[];
}

export interface CandidatesFile {
  count: number;
  featured_count: number;
  candidates: Candidate[];
  featured: FeaturedCandidate[];
  data_dictionary: Record<string, string>;
  notes: string[];
  provenance: Provenance;
}

export interface PilotQuery {
  id: string;
  lane: string;
  topics: string[];
  query: string;
  objective: string;
  expected_strong_signals: string;
  expected_false_positives: string;
}

export interface BroadQuery {
  id: string;
  sector_bucket: string;
  discovery_lane: string;
  broad_group: string;
  query: string;
  objective: string;
  expected_strong_signal: string;
  expected_false_positives: string;
  count_preflight_estimate: number | null;
  posts_processed: number | null;
  actionable_leads: number | null;
  recommendation: string | null;
}

export interface QueryPerfRow {
  id: string;
  sector_bucket: string;
  discovery_lane: string;
  broad_group: string;
  count_preflight_estimate: number | null;
  posts_processed: number | null;
  actionable_leads: number | null;
  recommendation: string | null;
}

export interface QueryPerformance {
  count: number;
  columns: string[];
  recommendation_legend: Record<string, string>;
  rows: QueryPerfRow[];
  totals: Record<string, number>;
  totals_note: string;
  provenance: Provenance;
}

export interface CostLine {
  phase: string;
  detail: string;
  unit_price_usd: string | null;
  units: number | null;
  estimated_usd: string;
}

export interface CostLedger {
  currency: string;
  allowance_usd: string;
  estimated_activity_usd: string;
  estimated_remaining_usd: string;
  billing_status: string;
  reconciliation_status: string;
  reconciliation_note: string;
  lines: CostLine[];
  official_endpoints: Endpoint[];
  governance: Record<string, boolean | number | string>;
  provenance: Provenance;
}

export interface EvidenceFramework {
  levels: { level: string; label: string; definition: string }[];
  artifact_types: string[];
  builder_relations: { key: string; definition: string }[];
  attribution_classes: string[];
  dispositions: { key: string; definition: string }[];
  ownership_note: string;
  provenance: Provenance;
}

export interface Methodology {
  thesis: string;
  pilot_lanes: { lane: string; description: string }[];
  pipeline: string[];
  deterministic_rules: string[];
  enrichment: { why_selective: string; what_it_examined: string[]; what_it_ignored: string[] };
  human_decision: string;
  provenance: Provenance;
}

export interface TestSummary {
  original_engine_tests: number;
  showcase_note: string;
  categories: { category: string; description: string }[];
  provenance: Provenance;
}

export interface Limitations {
  limitations: string[];
  version_two: string[];
  provenance: Provenance;
}

export interface MetricsProvenance {
  counts: {
    net_new_posts: number;
    artifact_bearing_posts: number;
    strict_level_a_posts: number;
    direct_builder_claims: number;
    actionable_posts: number;
    engine_consolidated_projects: number;
    analyst_adjudicated_projects: number;
    public_broad_run_records: number;
    featured_analysis_pages: number;
    total_detail_pages: number;
  };
  count_definitions: Record<
    string,
    { value: number; stage: string; definition: string; source_label: string }
  >;
  artifact_vs_level_a: {
    artifact_bearing_posts: number;
    strict_level_a_posts: number;
    difference: number;
    explanation: string;
  };
  engine_vs_analyst_projects: {
    engine_consolidated_projects: number;
    analyst_adjudicated_projects: number;
    difference: number;
    explanation: string;
    limitation: string;
  };
  public_showcase: {
    public_broad_run_records: number;
    featured_analysis_pages: number;
    total_detail_pages: number;
    aos_included_in_public_records: boolean;
    source_label: string;
    derivation: {
      actionable_posts: number;
      excluded_unnamed_posts: number;
      named_posts: number;
      duplicate_project_posts_collapsed: number;
      public_broad_run_records: number;
      formula: string;
    };
    exclusion_count: number;
    exclusion_reasons: { reason: string; count: number; detail: string }[];
    consolidation_key_note: string;
    aos_note: string;
  };
  multi_query_posts: number;
  multi_query_note: string;
  funnel: { key: string; label: string; value: number }[];
  funnel_note: string;
  policy: string[];
  provenance: Provenance;
}

// ---------------------------------------------------------------------------
// Loaders
// ---------------------------------------------------------------------------
export const getRunSummary = () => readJson<RunSummary>("run-summary.json");
export const getCandidatesFile = () => readJson<CandidatesFile>("candidates.json");
export const getPilotQueries = () =>
  readJson<{ count: number; architecture: string; lanes: string[]; queries: PilotQuery[] }>("queries-pilot.json");
export const getBroadQueries = () =>
  readJson<{ count: number; broad_groups: string[]; queries: BroadQuery[] }>("queries-broad.json");
export const getQueryPerformance = () => readJson<QueryPerformance>("query-performance.json");
export const getCostLedger = () => readJson<CostLedger>("cost-ledger.json");
export const getEvidenceFramework = () => readJson<EvidenceFramework>("evidence-framework.json");
export const getMethodology = () => readJson<Methodology>("methodology.json");
export const getTestSummary = () => readJson<TestSummary>("test-summary.json");
export const getLimitations = () => readJson<Limitations>("limitations.json");
export const getMetricsProvenance = () => readJson<MetricsProvenance>("metrics-provenance.json");

export function getCandidateBySlug(slug: string): Candidate | FeaturedCandidate | null {
  const file = getCandidatesFile();
  const featured = file.featured.find((c) => c.slug === slug);
  if (featured) return featured;
  return file.candidates.find((c) => c.slug === slug) ?? null;
}

export function isFeatured(c: Candidate | FeaturedCandidate): c is FeaturedCandidate {
  return (c as FeaturedCandidate).is_featured === true;
}
