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
          The results interface displays {ps.public_broad_run_records} sanitized broad-run project
          records from the completed run. This is a sanitized public subset, not the complete private
          diligence dataset. Raw Post text and personal identity fields are intentionally excluded,
          and each row links to the original public X Post.
        </p>
        <ReplayNotice />
      </div>

      <div className="grid cols-4">
        <MetricCard value={file.count} label="Sanitized broad-run project records" note="Public records derived from the 187 actionable Posts." />
        <MetricCard value={187} label="Actionable Posts" note="Posts passing attribution and artifact checks across the run." />
        <MetricCard value={keepVerified} label="Keep verified" note="Direct builder with a verified Level A artifact." />
        <MetricCard value={forEnrichment} label="Keep for enrichment" note="Shortlisted for selective profile enrichment." />
      </div>

      <div className="callout">
        <strong>Featured AOS investment-analysis page:</strong>{" "}
        <Link href="/results/aos-unicity-labs">AOS / Unicity Labs</Link>. AOS / Unicity Labs is a
        separate featured investment-analysis page sourced from the earlier pilot and
        targeted-enrichment comparison. It is not included in the {ps.public_broad_run_records}{" "}
        broad-run public project records above.
      </div>

      <ResultsTable candidates={file.candidates} />

      <section className="stack">
        <h2>Metric provenance and the public funnel</h2>
        <p className="muted small">
          851 Posts contained at least one resolved external product-artifact link.{" "}
          {prov.artifact_vs_level_a.strict_level_a_posts} Posts met the strict verified Level A
          standard. The deterministic pipeline produced{" "}
          {prov.engine_vs_analyst_projects.engine_consolidated_projects} engine-consolidated
          actionable projects, and {prov.engine_vs_analyst_projects.analyst_adjudicated_projects}{" "}
          projects remained after final analyst adjudication. These are stage counts, not strictly
          nested subsets.
        </p>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Funnel stage</th><th>Count</th></tr></thead>
            <tbody>
              {prov.funnel.map((f) => (
                <tr key={f.key}>
                  <td>{f.label}</td>
                  <td className="mono">{f.value.toLocaleString("en-US")}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="faint small">{prov.funnel_note}</p>

        <h3 style={{ marginTop: "0.5rem" }}>Public exclusions</h3>
        <div className="callout small">
          <strong>How this table of {ps.public_broad_run_records} records is derived:</strong>{" "}
          {ps.derivation.formula}. This starts from the 187 actionable Posts and is not a direct
          subtraction from the {prov.engine_vs_analyst_projects.analyst_adjudicated_projects}{" "}
          analyst-adjudicated project set.
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
        <div className="callout small">{prov.engine_vs_analyst_projects.limitation}</div>
        <p className="faint small">
          {prov.multi_query_note} {ps.aos_note}{" "}
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
