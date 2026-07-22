import type { Metadata } from "next";
import Link from "next/link";
import ReplayNotice from "@/components/ReplayNotice";
import MetricCard from "@/components/MetricCard";
import ResultsTable from "@/components/ResultsTable";
import { getCandidatesFile, getMetricsProvenance } from "@/lib/data";
import { GITHUB_URL } from "@/lib/site";

export const metadata: Metadata = {
  title: "Results",
  description:
    "Searchable, filterable table of the consolidated projects surfaced by the completed sourcing run.",
};

export default function ResultsPage() {
  const file = getCandidatesFile();
  const dict = file.data_dictionary;

  const keepVerified = file.candidates.filter((c) => c.lead_disposition === "keep_verified").length;
  const forEnrichment = file.candidates.filter((c) => c.lead_disposition === "keep_for_enrichment").length;
  const prov = getMetricsProvenance();
  const ps = prov.public_showcase;

  return (
    <div className="container section stack-lg">
      <div className="stack">
        <div className="eyebrow">Results</div>
        <h1>The consolidated sourcing run</h1>
        <p className="lede">
          The results interface displays {ps.sanitized_records} sanitized project records from the
          completed run. This is a sanitized public subset, not the complete private diligence
          dataset. Raw Post text and personal identity fields are intentionally excluded, and each
          row links to the original public X Post.
        </p>
        <ReplayNotice />
      </div>

      <div className="grid cols-4">
        <MetricCard value={file.count} label="Sanitized project records" note="Unique named projects derived from the 187 actionable Posts." />
        <MetricCard value={187} label="Actionable Posts" note="Posts passing attribution and artifact checks across the run." />
        <MetricCard value={keepVerified} label="Keep verified" note="Direct builder with a verified Level A artifact." />
        <MetricCard value={forEnrichment} label="Keep for enrichment" note="Shortlisted for selective profile enrichment." />
      </div>

      <div className="callout">
        <strong>Featured investment-thesis page:</strong>{" "}
        <Link href="/results/aos-unicity-labs">AOS / Unicity Labs</Link>. AOS is not among the{" "}
        {ps.sanitized_records} broad-run records above. It was surfaced by the same engine in the
        earlier pilot and comparison, and is presented separately as the featured thesis, advanced by
        human judgment for focused diligence rather than by an automated score.
      </div>

      <ResultsTable candidates={file.candidates} />

      <section className="stack">
        <h2>Metric provenance and public exclusions</h2>
        <p className="muted small">
          The final summary uses the adjudicated metrics from the completed sourcing run:{" "}
          {prov.canonical.level_a_posts} Level A artifact Posts and {prov.canonical.consolidated_projects}{" "}
          consolidated companies or projects. Earlier pipeline artifacts contain different counts
          ({prov.intermediate.level_a_posts} and {prov.intermediate.consolidated_projects}) because they
          represent intermediate processing stages before final reclassification and consolidation.
        </p>
        <div className="callout small">
          <strong>How this table of {ps.sanitized_records} records is derived:</strong> {ps.derivation.formula}.
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Excluded from public display</th><th>Count</th><th>Reason</th></tr></thead>
            <tbody>
              {ps.exclusion_reasons.map((e) => (
                <tr key={e.reason}>
                  <td className="mono">{e.reason}</td>
                  <td>{e.count}</td>
                  <td className="muted small">{e.detail}</td>
                </tr>
              ))}
              <tr>
                <td><strong>Total excluded from public display</strong></td>
                <td><strong>{ps.exclusion_count}</strong></td>
                <td className="muted small">The private engine outputs remain unchanged.</td>
              </tr>
            </tbody>
          </table>
        </div>
        <p className="faint small">
          {prov.multi_query_note} {ps.consolidation_key_note}{" "}
          <a href={`${GITHUB_URL}/blob/main/docs/metrics-reconciliation.md`} target="_blank" rel="noopener noreferrer">
            Full metrics reconciliation
          </a>.
        </p>
      </section>

      <section className="stack">
        <h2>Data dictionary</h2>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Column</th><th>Meaning</th></tr></thead>
            <tbody>
              {Object.entries(dict).map(([k, v]) => (
                <tr key={k}><td className="mono">{k}</td><td className="muted">{v}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <ul className="faint small">
          {file.notes.map((n) => <li key={n}>{n}</li>)}
        </ul>
      </section>
    </div>
  );
}
