import Link from "next/link";
import ReplayNotice from "@/components/ReplayNotice";
import MetricCard from "@/components/MetricCard";
import { getRunSummary } from "@/lib/data";

export default function HomePage() {
  const run = getRunSummary();

  return (
    <>
      <section className="section hero">
        <div className="container stack-lg">
          <div className="stack">
            <div className="eyebrow">Sanitized replay work sample</div>
            <h1>Deterministic X Sourcing Engine</h1>
            <p className="lede">
              The engine converts a sourcing thesis into official X API queries, separates actual
              builders from commentary and announcements, verifies public product artifacts, and
              creates an auditable diligence queue. This site is a read-only replay of the completed
              run.
            </p>
          </div>
          <ReplayNotice />
          <div className="btn-row">
            <Link className="btn" href="/results">Explore the sourcing run</Link>
            <Link className="btn secondary" href="/methodology">Review methodology</Link>
            <Link className="btn secondary" href="/cost-controls">Review cost controls</Link>
            <Link className="btn secondary" href="/results/aos-unicity-labs">View the AOS thesis</Link>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container stack-lg">
          <div className="stack">
            <div className="eyebrow">Why it was built</div>
            <h2>An early-stage venture sourcing assignment under a fixed budget</h2>
            <p className="muted" style={{ maxWidth: "72ch" }}>
              The task was to build a lightweight X sourcing engine, stay within a USD 25 estimated
              API allowance, produce actionable leads, select one compelling company, and explain why
              it is an interesting investment. The engine used the official X API, not scraping. No
              language model made any classification or disposition decision. The final company
              selection was made by human judgment.
            </p>
          </div>

          <div className="stack">
            <div className="eyebrow">Final run statistics</div>
            <h2>Broad-market run at a glance</h2>
            <p className="muted small">
              Hover any card for its exact definition. Counts describe Posts and consolidated
              projects, not incorporated startups or verified companies.
            </p>
            <div className="grid cols-5">
              {run.headline_metrics.map((m) => (
                <MetricCard key={m.key} value={m.value} label={m.label} note={m.note} />
              ))}
            </div>
          </div>

          <div className="callout stack">
            <strong>How to read this demo</strong>
            <ul className="muted" style={{ margin: 0, paddingLeft: "1.1rem" }}>
              <li>No live API credential is present, so no new API spending can occur.</li>
              <li>The interface is backed entirely by sanitized static JSON.</li>
              <li>The saved outputs give a stable and reproducible interview demonstration.</li>
              <li>The seven-day recent-search window was used. The engine did not search the entire startup market.</li>
              <li>API costs are estimates because the external Developer Console was not accessible.</li>
            </ul>
          </div>
        </div>
      </section>

      <section className="section">
        <div className="container stack">
          <div className="eyebrow">Official endpoints used</div>
          <h2>Official X API, not scraping</h2>
          <div className="table-wrap">
            <table>
              <thead>
                <tr><th>Method</th><th>Endpoint</th><th>Purpose</th></tr>
              </thead>
              <tbody>
                {run.official_endpoints.map((e) => (
                  <tr key={e.url}>
                    <td className="mono">{e.method}</td>
                    <td className="mono">{e.url}</td>
                    <td className="muted">{e.purpose}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
          <p className="faint small">The deployed demo does not call any of these endpoints.</p>
        </div>
      </section>
    </>
  );
}
