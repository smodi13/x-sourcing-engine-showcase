import type { Metadata } from "next";
import ReplayNotice from "@/components/ReplayNotice";
import { EvidenceTag, Tag } from "@/components/EvidenceTag";
import {
  getMethodology,
  getPilotQueries,
  getBroadQueries,
  getEvidenceFramework,
} from "@/lib/data";

export const metadata: Metadata = {
  title: "Methodology",
  description:
    "Sourcing thesis, pilot and broad query design, deterministic evidence classification, builder attribution, deduplication, and human review.",
};

export default function MethodologyPage() {
  const m = getMethodology();
  const pilot = getPilotQueries();
  const broad = getBroadQueries();
  const ev = getEvidenceFramework();

  return (
    <div className="container section stack-lg">
      <div className="stack">
        <div className="eyebrow">Methodology</div>
        <h1>From thesis to auditable diligence queue</h1>
        <ReplayNotice />
      </div>

      <section className="stack" id="thesis">
        <h2>1. Sourcing thesis</h2>
        <p className="muted" style={{ maxWidth: "74ch" }}>{m.thesis}</p>
      </section>

      <section className="stack" id="lanes">
        <h2>2. Three pilot sourcing lanes</h2>
        <div className="grid cols-3">
          {m.pilot_lanes.map((l) => (
            <div className="card stack" key={l.lane}>
              <Tag variant="accent">{l.lane}</Tag>
              <div className="muted small">{l.description}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="stack" id="pilot">
        <h2>3. Six pilot query families</h2>
        <p className="muted small">{pilot.architecture} Query text is loaded verbatim from the saved pilot configuration.</p>
        <div className="stack-lg">
          {pilot.queries.map((q) => (
            <div className="card stack" key={q.id}>
              <div className="tags">
                <Tag variant="accent">{q.id}</Tag>
                <Tag>{q.lane}</Tag>
                {q.topics?.map((t) => <Tag key={t}>topic {t}</Tag>)}
              </div>
              <pre className="code">{q.query}</pre>
              <div className="dl">
                <dt>Objective</dt><dd>{q.objective}</dd>
                <dt>Strong signals</dt><dd>{q.expected_strong_signals}</dd>
                <dt>False positives</dt><dd>{q.expected_false_positives}</dd>
              </div>
            </div>
          ))}
        </div>
      </section>

      <section className="stack" id="broad">
        <h2>4. Twenty broad-market query families</h2>
        <p className="muted small">
          The broad run expanded across five market groups. Query text is loaded verbatim from the
          completed-run configuration. Counts are the count-preflight estimate, the Posts attributed
          to each query, and the actionable results.
        </p>
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th>Query</th><th>Sector</th><th>Lane</th><th>Group</th>
                <th>Preflight</th><th>Posts</th><th>Actionable</th>
              </tr>
            </thead>
            <tbody>
              {broad.queries.map((q) => (
                <tr key={q.id}>
                  <td className="mono">{q.id}</td>
                  <td className="muted">{q.sector_bucket}</td>
                  <td className="muted">{q.discovery_lane}</td>
                  <td className="muted">{q.broad_group}</td>
                  <td>{q.count_preflight_estimate ?? "n/a"}</td>
                  <td>{q.posts_processed ?? "n/a"}</td>
                  <td>{q.actionable_leads ?? "n/a"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <details className="card">
          <summary style={{ cursor: "pointer", fontWeight: 600 }}>Show verbatim query strings and objectives</summary>
          <div className="stack-lg" style={{ marginTop: "1rem" }}>
            {broad.queries.map((q) => (
              <div className="stack" key={q.id}>
                <div className="tags">
                  <Tag variant="accent">{q.id}</Tag>
                  <Tag>{q.sector_bucket}</Tag>
                  <Tag>{q.discovery_lane}</Tag>
                </div>
                <pre className="code">{q.query}</pre>
                <div className="dl">
                  <dt>Objective</dt><dd>{q.objective}</dd>
                  <dt>Strong signal</dt><dd>{q.expected_strong_signal}</dd>
                  <dt>False positives</dt><dd>{q.expected_false_positives}</dd>
                </div>
              </div>
            ))}
          </div>
        </details>
      </section>

      <section className="stack" id="evidence">
        <h2>5. Evidence framework</h2>
        <p className="muted small">Every material claim is tagged by level. An artifact is never presented as proven traction.</p>
        <div className="grid cols-2">
          {ev.levels.map((l) => (
            <div className="card stack" key={l.level}>
              <EvidenceTag level={l.level} />
              <strong>{l.label}</strong>
              <div className="muted small">{l.definition}</div>
            </div>
          ))}
        </div>
      </section>

      <section className="stack" id="attribution">
        <h2>6. Builder attribution</h2>
        <p className="muted small">The engine distinguishes who is speaking before a lead is trusted.</p>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Relation</th><th>Meaning</th></tr></thead>
            <tbody>
              {ev.builder_relations.map((r) => (
                <tr key={r.key}><td className="mono">{r.key}</td><td className="muted">{r.definition}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="stack" id="verification">
        <h2>7. Artifact verification</h2>
        <ul className="muted" style={{ maxWidth: "74ch" }}>
          <li>URLs are extracted from each Post and expanded from shortened links.</li>
          <li>Links are canonicalized and X-domain links are excluded, since a link back to X is not an external artifact.</li>
          <li>Artifact type is recorded (repository, documentation, product website, live demo, API endpoint).</li>
          <li>The engine checks the relationship between the author and the artifact organization.</li>
          <li>{ev.ownership_note}</li>
        </ul>
      </section>

      <section className="stack" id="dedup">
        <h2>8. Deduplication and consolidation</h2>
        <ul className="muted" style={{ maxWidth: "74ch" }}>
          <li>Within-run duplicate records are removed, and cross-run duplicates against the pilot are removed.</li>
          <li>Posts that match more than one query are noted, so per-query counts are not double counted at the run level.</li>
          <li>Authors are deduplicated, and project names are normalized before company consolidation.</li>
          <li>A Post is not a project, and a project is not an incorporated startup. The engine keeps these distinct.</li>
        </ul>
      </section>

      <section className="stack" id="enrichment">
        <h2>9. Profile enrichment</h2>
        <div className="grid cols-2">
          <div className="card stack">
            <strong>Why only shortlisted profiles</strong>
            <div className="muted small">{m.enrichment.why_selective}</div>
          </div>
          <div className="card stack">
            <strong>What enrichment examined</strong>
            <div className="tags">{m.enrichment.what_it_examined.map((x) => <Tag key={x}>{x}</Tag>)}</div>
            <strong style={{ marginTop: "0.5rem" }}>What it ignored</strong>
            <div className="tags">{m.enrichment.what_it_ignored.map((x) => <Tag key={x} variant="d">{x}</Tag>)}</div>
          </div>
        </div>
      </section>

      <section className="stack" id="human">
        <h2>10. Human decision</h2>
        <div className="callout"><p style={{ margin: 0 }}>{m.human_decision}</p></div>
        <ul className="muted small">
          {m.deterministic_rules.map((r) => <li key={r}>{r}</li>)}
        </ul>
      </section>
    </div>
  );
}
