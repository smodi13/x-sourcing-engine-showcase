"use client";

import { useMemo, useState } from "react";
import Link from "next/link";
import type { Candidate } from "@/lib/data";
import { EvidenceTag, Tag } from "@/components/EvidenceTag";

type SortKey = "name" | "sector_bucket" | "research_score" | "company_status";

const PAGE_SIZE = 25;

function bestLevel(levels: string[]): string {
  for (const l of ["A", "B", "C", "D"]) if (levels.includes(l)) return l;
  return "D";
}

function uniqueSorted(values: (string | null)[]): string[] {
  return Array.from(new Set(values.filter((v): v is string => !!v))).sort();
}

export default function ResultsTable({ candidates }: { candidates: Candidate[] }) {
  const [query, setQuery] = useState("");
  const [sector, setSector] = useState("");
  const [family, setFamily] = useState("");
  const [level, setLevel] = useState("");
  const [attribution, setAttribution] = useState("");
  const [disposition, setDisposition] = useState("");
  const [status, setStatus] = useState("");
  const [sortKey, setSortKey] = useState<SortKey>("research_score");
  const [sortDir, setSortDir] = useState<"asc" | "desc">("desc");
  const [page, setPage] = useState(0);

  const sectors = useMemo(() => uniqueSorted(candidates.map((c) => c.sector_bucket)), [candidates]);
  const families = useMemo(
    () => uniqueSorted(candidates.flatMap((c) => c.source_queries)),
    [candidates]
  );
  const attributions = useMemo(
    () => uniqueSorted(candidates.map((c) => c.announcement_attribution)),
    [candidates]
  );
  const dispositions = useMemo(() => uniqueSorted(candidates.map((c) => c.lead_disposition)), [candidates]);
  const statuses = useMemo(() => uniqueSorted(candidates.map((c) => c.company_status)), [candidates]);

  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase();
    const rows = candidates.filter((c) => {
      if (q && !c.name.toLowerCase().includes(q)) return false;
      if (sector && c.sector_bucket !== sector) return false;
      if (family && !c.source_queries.includes(family)) return false;
      if (level && !c.evidence_levels.includes(level)) return false;
      if (attribution && c.announcement_attribution !== attribution) return false;
      if (disposition && c.lead_disposition !== disposition) return false;
      if (status && c.company_status !== status) return false;
      return true;
    });
    rows.sort((a, b) => {
      let av: string | number = "";
      let bv: string | number = "";
      if (sortKey === "research_score") {
        av = a.research_score ?? -1;
        bv = b.research_score ?? -1;
      } else {
        av = (a[sortKey] ?? "") as string;
        bv = (b[sortKey] ?? "") as string;
      }
      if (av < bv) return sortDir === "asc" ? -1 : 1;
      if (av > bv) return sortDir === "asc" ? 1 : -1;
      return a.name.localeCompare(b.name);
    });
    return rows;
  }, [candidates, query, sector, family, level, attribution, disposition, status, sortKey, sortDir]);

  const pageCount = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const current = Math.min(page, pageCount - 1);
  const shown = filtered.slice(current * PAGE_SIZE, current * PAGE_SIZE + PAGE_SIZE);

  const setSort = (key: SortKey) => {
    if (sortKey === key) setSortDir(sortDir === "asc" ? "desc" : "asc");
    else {
      setSortKey(key);
      setSortDir(key === "research_score" ? "desc" : "asc");
    }
    setPage(0);
  };
  const arrow = (key: SortKey) => (sortKey === key ? <span className="arrow">{sortDir === "asc" ? " up" : " down"}</span> : null);

  const resetPage = <T,>(setter: (v: T) => void) => (v: T) => {
    setter(v);
    setPage(0);
  };

  return (
    <div className="stack">
      <div className="controls" role="search">
        <div className="field" style={{ flex: "1 1 220px" }}>
          <label htmlFor="q">Search project</label>
          <input
            id="q"
            className="input"
            type="search"
            placeholder="Search by project name"
            value={query}
            onChange={(e) => resetPage(setQuery)(e.target.value)}
          />
        </div>
        <div className="field">
          <label htmlFor="sector">Sector</label>
          <select id="sector" className="select" value={sector} onChange={(e) => resetPage(setSector)(e.target.value)}>
            <option value="">All sectors</option>
            {sectors.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor="family">Query family</label>
          <select id="family" className="select" value={family} onChange={(e) => resetPage(setFamily)(e.target.value)}>
            <option value="">All queries</option>
            {families.map((f) => <option key={f} value={f}>{f}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor="level">Evidence level</label>
          <select id="level" className="select" value={level} onChange={(e) => resetPage(setLevel)(e.target.value)}>
            <option value="">Any level</option>
            {["A", "B", "C", "D"].map((l) => <option key={l} value={l}>Level {l}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor="attr">Classification</label>
          <select id="attr" className="select" value={attribution} onChange={(e) => resetPage(setAttribution)(e.target.value)}>
            <option value="">Any classification</option>
            {attributions.map((a) => <option key={a} value={a}>{a}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor="disp">Disposition</label>
          <select id="disp" className="select" value={disposition} onChange={(e) => resetPage(setDisposition)(e.target.value)}>
            <option value="">Any disposition</option>
            {dispositions.map((d) => <option key={d} value={d}>{d}</option>)}
          </select>
        </div>
        <div className="field">
          <label htmlFor="status">Company status</label>
          <select id="status" className="select" value={status} onChange={(e) => resetPage(setStatus)(e.target.value)}>
            <option value="">Any status</option>
            {statuses.map((s) => <option key={s} value={s}>{s}</option>)}
          </select>
        </div>
      </div>

      <div className="muted small">
        Showing <strong>{filtered.length}</strong> of {candidates.length} consolidated projects
      </div>

      {filtered.length === 0 ? (
        <div className="empty">No projects match these filters. Clear a filter to see more.</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                <th className="sortable" onClick={() => setSort("name")}>Project{arrow("name")}</th>
                <th className="sortable" onClick={() => setSort("sector_bucket")}>Sector{arrow("sector_bucket")}</th>
                <th>Query family</th>
                <th>Evidence</th>
                <th>Artifact</th>
                <th>Classification</th>
                <th>Disposition</th>
                <th className="sortable" onClick={() => setSort("company_status")}>Status{arrow("company_status")}</th>
                <th className="sortable" onClick={() => setSort("research_score")}>Score{arrow("research_score")}</th>
                <th>Post</th>
              </tr>
            </thead>
            <tbody>
              {shown.map((c) => (
                <tr key={c.slug}>
                  <td><Link href={`/results/${c.slug}`}>{c.name}</Link></td>
                  <td className="muted">{c.sector_bucket}</td>
                  <td className="mono small">{c.source_queries.join(", ")}</td>
                  <td><EvidenceTag level={bestLevel(c.evidence_levels)} /></td>
                  <td className="muted small">{c.artifact_types.join(", ") || "none"}</td>
                  <td className="muted small">{c.announcement_attribution}</td>
                  <td><Tag>{c.lead_disposition}</Tag></td>
                  <td className="muted small">{c.company_status}</td>
                  <td>{c.research_score ?? "n/a"}</td>
                  <td>
                    {c.post_url ? (
                      <a href={c.post_url} target="_blank" rel="noopener noreferrer">View post</a>
                    ) : (
                      <span className="faint">n/a</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {pageCount > 1 && (
        <div className="btn-row" style={{ justifyContent: "space-between", alignItems: "center" }}>
          <button className="btn secondary" disabled={current === 0} onClick={() => setPage(current - 1)}>
            Previous
          </button>
          <span className="muted small">Page {current + 1} of {pageCount}</span>
          <button className="btn secondary" disabled={current >= pageCount - 1} onClick={() => setPage(current + 1)}>
            Next
          </button>
        </div>
      )}
    </div>
  );
}
