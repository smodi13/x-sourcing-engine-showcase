import type { Metadata } from "next";
import ReplayNotice from "@/components/ReplayNotice";
import { getMethodology, getLimitations } from "@/lib/data";
import { GITHUB_URL } from "@/lib/site";

export const metadata: Metadata = {
  title: "About",
  description:
    "Assignment, technical stack, architecture, limitations, and version-two improvements for the sourcing engine.",
};

export default function AboutPage() {
  const m = getMethodology();
  const lim = getLimitations();

  return (
    <div className="container section stack-lg">
      <div className="stack">
        <div className="eyebrow">About</div>
        <h1>About this project</h1>
        <ReplayNotice />
      </div>

      <section className="stack">
        <h2>1. Assignment</h2>
        <p className="muted" style={{ maxWidth: "74ch" }}>
          The assignment was to build a lightweight X sourcing engine for early-stage venture
          discovery, stay within a USD 25 estimated API allowance, produce actionable leads, select
          one compelling company, and explain why it is an interesting investment. This showcase is a
          sanitized replay of that completed work.
        </p>
      </section>

      <section className="stack">
        <h2>2. Technical stack</h2>
        <div className="grid cols-2">
          <div className="card stack">
            <strong>Engine</strong>
            <p className="muted small" style={{ margin: 0 }}>
              Python command-line engine with deterministic scoring and classification, a query
              validator, phased least-privilege spending, request fingerprinting, execution locks,
              and a full test suite. The engine calls the official X API. No language model assigns a
              score or a disposition.
            </p>
          </div>
          <div className="card stack">
            <strong>This demo</strong>
            <p className="muted small" style={{ margin: 0 }}>
              Next.js with the App Router and TypeScript. Pages render from local sanitized static
              JSON. There is no database, no authentication, no external API dependency, and no
              client-side secret.
            </p>
          </div>
        </div>
      </section>

      <section className="stack">
        <h2>3. Architecture</h2>
        <p className="muted small">Data flows in one direction, from thesis to a human investment decision.</p>
        <div className="pipeline">
          {m.pipeline.map((step, i) => (
            <span key={step} style={{ display: "inline-flex", alignItems: "center", gap: "0.5rem" }}>
              <span className={`step${i === m.pipeline.length - 1 ? " terminal" : ""}`}>{step}</span>
              {i < m.pipeline.length - 1 ? <span className="arrow" aria-hidden="true">to</span> : null}
            </span>
          ))}
        </div>
      </section>

      <section className="stack">
        <h2>4. Limitations</h2>
        <ul className="muted" style={{ maxWidth: "78ch" }}>
          {lim.limitations.map((l) => <li key={l}>{l}</li>)}
        </ul>
      </section>

      <section className="stack">
        <h2>5. Version-two improvements</h2>
        <div className="grid cols-2">
          {lim.version_two.map((v) => (
            <div className="card small" key={v}>{v}</div>
          ))}
        </div>
      </section>

      <section className="stack">
        <h2>6. Metric provenance</h2>
        <p className="muted small">
          The public summary uses the final adjudicated metrics from the completed run. Intermediate
          pipeline stages recorded different counts, and the public results table is a sanitized
          subset. The full reconciliation of the final, intermediate, and public figures is
          documented in the metrics reconciliation.
        </p>
        <div className="btn-row">
          <a className="btn secondary" href={`${GITHUB_URL}/blob/main/docs/metrics-reconciliation.md`} target="_blank" rel="noopener noreferrer">
            Metrics reconciliation
          </a>
        </div>
      </section>

      <section className="stack">
        <h2>7. Source</h2>
        <p className="muted small">
          The sanitized code and this demo are published in the public showcase repository.
        </p>
        <div className="btn-row">
          <a className="btn" href={GITHUB_URL} target="_blank" rel="noopener noreferrer">
            GitHub repository
          </a>
        </div>
      </section>
    </div>
  );
}
