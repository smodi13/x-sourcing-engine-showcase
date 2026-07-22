import type { Metadata } from "next";
import Link from "next/link";
import ReplayNotice from "@/components/ReplayNotice";
import MetricCard from "@/components/MetricCard";
import ResultsTable from "@/components/ResultsTable";
import { getCandidatesFile } from "@/lib/data";

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

  return (
    <div className="container section stack-lg">
      <div className="stack">
        <div className="eyebrow">Results</div>
        <h1>The consolidated sourcing run</h1>
        <p className="lede">
          Every row is a consolidated project derived from the saved run. Raw Post text and personal
          identity fields are intentionally excluded. Each row links to the original public X Post.
        </p>
        <ReplayNotice />
      </div>

      <div className="grid cols-4">
        <MetricCard value={file.count} label="Consolidated projects shown" note="Deduplicated named projects with a public artifact." />
        <MetricCard value={187} label="Actionable Posts" note="Posts passing attribution and artifact checks across the run." />
        <MetricCard value={keepVerified} label="Keep verified" note="Direct builder with a verified Level A artifact." />
        <MetricCard value={forEnrichment} label="Keep for enrichment" note="Shortlisted for selective profile enrichment." />
      </div>

      <div className="callout">
        <strong>Featured, human-selected candidate:</strong>{" "}
        <Link href="/results/aos-unicity-labs">AOS / Unicity Labs</Link>. Advanced by human judgment
        for focused diligence, not by an automated score.
      </div>

      <ResultsTable candidates={file.candidates} />

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
