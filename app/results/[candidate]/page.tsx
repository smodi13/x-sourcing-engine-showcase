import type { Metadata } from "next";
import Link from "next/link";
import { notFound } from "next/navigation";
import ReplayNotice from "@/components/ReplayNotice";
import { EvidenceTag, Tag } from "@/components/EvidenceTag";
import {
  getCandidatesFile,
  getCandidateBySlug,
  isFeatured,
  type Candidate,
  type FeaturedCandidate,
} from "@/lib/data";

export function generateStaticParams() {
  const file = getCandidatesFile();
  return [
    ...file.candidates.map((c) => ({ candidate: c.slug })),
    ...file.featured.map((c) => ({ candidate: c.slug })),
  ];
}

export async function generateMetadata({
  params,
}: {
  params: Promise<{ candidate: string }>;
}): Promise<Metadata> {
  const { candidate } = await params;
  const c = getCandidateBySlug(candidate);
  if (!c) return { title: "Candidate not found" };
  return {
    title: c.name,
    description: `Engine classification, evidence, and disposition for ${c.name} from the completed sourcing run.`,
  };
}

function ArtifactLinks({ urls, types }: { urls: string[]; types: string[] }) {
  if (!urls.length) return <span className="faint">No external artifact link recorded.</span>;
  return (
    <ul className="stack" style={{ margin: 0, paddingLeft: "1.1rem" }}>
      {urls.map((u, i) => (
        <li key={u}>
          <a href={u} target="_blank" rel="noopener noreferrer" className="mono small">{u}</a>
          {types[i] ? <span className="muted small"> ({types[i]})</span> : null}
        </li>
      ))}
    </ul>
  );
}

function FeaturedView({ c }: { c: FeaturedCandidate }) {
  return (
    <div className="container section stack-lg">
      <div className="stack">
        <Link href="/results" className="small">Back to results</Link>
        <div className="tags">
          <Tag variant="accent">Featured analysis</Tag>
          <Tag>{c.sector_bucket}</Tag>
          <Tag>{c.company_status}</Tag>
        </div>
        <h1>{c.name}</h1>
        <p className="lede">{c.summary}</p>
        <p className="muted small">
          This is a public featured investment-analysis page, sourced from the earlier pilot and
          targeted-enrichment comparison. It is separate from the sanitized broad-run project records
          on the results page. The complete investment memo remains private.
        </p>
        <ReplayNotice />
      </div>

      <section className="stack">
        <h2>Public facts and evidence class</h2>
        <p className="muted small">
          These are public claims only. Company-reported items are not treated as verified.
        </p>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Public claim</th><th>Evidence class</th></tr></thead>
            <tbody>
              {c.public_facts.map((f) => (
                <tr key={f.claim}><td>{f.claim}</td><td><Tag>{f.evidence_class}</Tag></td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="grid cols-2">
        <div className="card stack">
          <h3>Public artifacts</h3>
          <ArtifactLinks urls={c.artifact_urls} types={c.artifact_types} />
        </div>
        <div className="card stack">
          <h3>Evidence levels present</h3>
          <div className="tags">{c.evidence_levels.map((l) => <EvidenceTag key={l} level={l} />)}</div>
          <h3 style={{ marginTop: "0.6rem" }}>Selection basis</h3>
          <p className="muted small" style={{ margin: 0 }}>{c.disposition_note}</p>
        </div>
      </section>

      <section className="stack">
        <h2>Investment case</h2>
        <div className="callout">
          <strong>Public featured analysis.</strong> The summary, public facts, evidence, and
          diligence questions on this page are the public investment case. {c.thesis_note}
        </div>
      </section>

      <section className="stack">
        <h2>Unresolved diligence questions</h2>
        <ul className="muted">{c.unresolved_questions.map((q) => <li key={q}>{q}</li>)}</ul>
      </section>
    </div>
  );
}

function StandardView({ c }: { c: Candidate }) {
  return (
    <div className="container section stack-lg">
      <div className="stack">
        <Link href="/results" className="small">Back to results</Link>
        <div className="tags">
          <Tag>{c.sector_bucket}</Tag>
          {c.candidate_rank ? <Tag variant="accent">rank {c.candidate_rank}</Tag> : null}
          <Tag>{c.company_status}</Tag>
        </div>
        <h1>{c.name}</h1>
        <ReplayNotice />
      </div>

      <section className="grid cols-2">
        <div className="card stack">
          <h3>Engine classification</h3>
          <div className="dl">
            <dt>Announcement attribution</dt><dd>{c.announcement_attribution ?? "n/a"}</dd>
            <dt>Actor and project relation</dt><dd>{c.actor_project_relation ?? "n/a"}</dd>
            <dt>Artifact owner scope</dt><dd>{c.artifact_owner_scope ?? "n/a"}</dd>
            <dt>Mandate fit</dt><dd>{c.headline_mandate_fit ?? "n/a"}</dd>
            <dt>Venture attractiveness</dt><dd>{c.general_venture_attractiveness ?? "n/a"}</dd>
            <dt>Organizing score</dt><dd>{c.research_score ?? "n/a"} of 100</dd>
            <dt>Disposition</dt><dd><Tag>{c.lead_disposition}</Tag></dd>
          </div>
        </div>
        <div className="card stack">
          <h3>Evidence and artifacts</h3>
          <div className="tags">{c.evidence_levels.map((l) => <EvidenceTag key={l} level={l} />)}</div>
          <div style={{ marginTop: "0.5rem" }}>
            <ArtifactLinks urls={c.artifact_urls} types={c.artifact_types} />
          </div>
          <h3 style={{ marginTop: "0.6rem" }}>Original source</h3>
          {c.post_url ? (
            <a href={c.post_url} target="_blank" rel="noopener noreferrer" className="mono small">
              {c.post_url}
            </a>
          ) : (
            <span className="faint">No permalink recorded.</span>
          )}
        </div>
      </section>

      <section className="grid cols-2">
        <div className="card stack">
          <h3>Query families matched</h3>
          <div className="tags">{c.source_queries.map((q) => <Tag key={q}>{q}</Tag>)}</div>
        </div>
        <div className="card stack">
          <h3>Reason codes</h3>
          <div className="tags">{c.reason_codes.map((r) => <Tag key={r} variant="accent">{r}</Tag>)}</div>
        </div>
      </section>

      <section className="stack">
        <h3>Unresolved questions</h3>
        {c.unresolved_questions.length ? (
          <ul className="muted">{c.unresolved_questions.map((q) => <li key={q}>{q}</li>)}</ul>
        ) : (
          <p className="faint">No unresolved questions were recorded for this lead.</p>
        )}
      </section>

      <div className="callout small">
        This page shows engine-derived classifications plus a public permalink and public artifact
        links. Raw Post text and author identity are intentionally excluded. Engine classifications
        are clearly separated from the original X content, which remains at the linked Post.
      </div>
    </div>
  );
}

export default async function CandidatePage({
  params,
}: {
  params: Promise<{ candidate: string }>;
}) {
  const { candidate } = await params;
  const c = getCandidateBySlug(candidate);
  if (!c) notFound();
  return isFeatured(c) ? <FeaturedView c={c} /> : <StandardView c={c} />;
}
