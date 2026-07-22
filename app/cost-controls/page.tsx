import type { Metadata } from "next";
import ReplayNotice from "@/components/ReplayNotice";
import MetricCard from "@/components/MetricCard";
import { getCostLedger, getTestSummary } from "@/lib/data";

export const metadata: Metadata = {
  title: "Cost controls",
  description:
    "API cost ledger, budget visualization, approval fingerprints, execution locks, and Decimal budget arithmetic.",
};

export default function CostControlsPage() {
  const ledger = getCostLedger();
  const tests = getTestSummary();

  const allowance = Number(ledger.allowance_usd);
  const used = Number(ledger.estimated_activity_usd);
  const remaining = Number(ledger.estimated_remaining_usd);
  const pctUsed = (used / allowance) * 100;
  const pctRemaining = 100 - pctUsed;

  return (
    <div className="container section stack-lg">
      <div className="stack">
        <div className="eyebrow">Cost controls</div>
        <h1>Budget, approval, and execution governance</h1>
        <p className="lede">
          Every paid call was estimated first, gated by an explicit approval bound to a request
          fingerprint, and protected by an execution lock. Spending is tracked in exact decimal
          arithmetic against a fixed allowance.
        </p>
        <ReplayNotice />
      </div>

      <section className="stack">
        <h2>1. API cost ledger</h2>
        <div className="table-wrap">
          <table>
            <thead>
              <tr><th>Phase</th><th>Detail</th><th>Unit price</th><th>Units</th><th>Estimated USD</th></tr>
            </thead>
            <tbody>
              {ledger.lines.map((l) => (
                <tr key={l.phase}>
                  <td><strong>{l.phase}</strong></td>
                  <td className="muted small">{l.detail}</td>
                  <td className="mono">{l.unit_price_usd ?? "n/a"}</td>
                  <td className="mono">{l.units?.toLocaleString("en-US") ?? "n/a"}</td>
                  <td className="mono">{l.estimated_usd}</td>
                </tr>
              ))}
              <tr>
                <td colSpan={4}><strong>Cumulative estimated activity</strong></td>
                <td className="mono"><strong>{ledger.estimated_activity_usd}</strong></td>
              </tr>
              <tr>
                <td colSpan={4}><strong>Estimated remaining allowance</strong></td>
                <td className="mono"><strong>{ledger.estimated_remaining_usd}</strong></td>
              </tr>
            </tbody>
          </table>
        </div>
        <div className="callout small">{ledger.reconciliation_note}</div>
      </section>

      <section className="stack">
        <h2>2. Budget visualization</h2>
        <div className="grid cols-4">
          <MetricCard value={`USD ${ledger.allowance_usd}`} label="Total allowance" />
          <MetricCard value={`USD ${ledger.estimated_activity_usd}`} label="Estimated activity" />
          <MetricCard value={`USD ${ledger.estimated_remaining_usd}`} label="Estimated remaining" />
          <MetricCard value={`${pctUsed.toFixed(1)}%`} label="Allowance used" note={`${pctRemaining.toFixed(1)}% remaining`} />
        </div>
        <div>
          <div
            className="bar-track"
            role="img"
            aria-label={`Estimated ${pctUsed.toFixed(1)} percent of the USD ${ledger.allowance_usd} allowance used, ${pctRemaining.toFixed(1)} percent remaining`}
          >
            <div className="bar-used" style={{ width: `${pctUsed}%` }} />
          </div>
          <div className="bar-legend">
            <span><span className="legend-swatch" style={{ background: "var(--accent)" }} />Used: USD {ledger.estimated_activity_usd} ({pctUsed.toFixed(1)}%)</span>
            <span><span className="legend-swatch" style={{ background: "var(--surface-2)", border: "1px solid var(--border-strong)" }} />Remaining: USD {ledger.estimated_remaining_usd} ({pctRemaining.toFixed(1)}%)</span>
          </div>
          <p className="faint small">Percentages are computed in code from the ledger JSON values.</p>
        </div>
      </section>

      <section className="grid cols-2">
        <div className="card stack">
          <h2 style={{ fontSize: "1.2rem" }}>3. Approval process</h2>
          <ul className="muted small">
            <li>Paid requests required explicit approval before execution.</li>
            <li>Approvals were configuration specific, not blanket approvals.</li>
            <li>Approval expiration was {ledger.governance.approval_expiration_minutes} minutes.</li>
            <li>The exact configuration was fingerprinted, and the run was locked against accidental re-execution.</li>
          </ul>
        </div>
        <div className="card stack">
          <h2 style={{ fontSize: "1.2rem" }}>4. Request fingerprints</h2>
          <ul className="muted small">
            <li>Each request was reduced to a canonical representation.</li>
            <li>The canonical request was hashed with {String(ledger.governance.fingerprint_algorithm)}.</li>
            <li>The fingerprint bound the approval to that exact configuration.</li>
            <li>Changing any field changed the fingerprint, so an approval could not be reused for a different request.</li>
          </ul>
        </div>
      </section>

      <section className="grid cols-2">
        <div className="card stack">
          <h2 style={{ fontSize: "1.2rem" }}>5. Execution locks</h2>
          <ul className="muted small">
            <li>A run lock prevented duplicate paid execution.</li>
            <li>Raw responses were stored before any derived output was written.</li>
            <li>The system failed closed if a control could not be verified.</li>
            <li>Historical outputs were never altered by a later run.</li>
          </ul>
        </div>
        <div className="card stack">
          <h2 style={{ fontSize: "1.2rem" }}>6. Decimal budget controls</h2>
          <p className="muted small" style={{ margin: 0 }}>
            Budget math used exact decimal arithmetic rather than floating-point estimates, so unit
            prices, per-phase totals, and the remaining allowance are exact to the listed precision.
          </p>
        </div>
      </section>

      <section className="stack">
        <h2>7. Official endpoints used</h2>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Method</th><th>Endpoint</th><th>Purpose</th></tr></thead>
            <tbody>
              {ledger.official_endpoints.map((e) => (
                <tr key={e.url}><td className="mono">{e.method}</td><td className="mono">{e.url}</td><td className="muted">{e.purpose}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section className="stack">
        <h2>8. Test coverage</h2>
        <div className="grid cols-2">
          <MetricCard value={tests.original_engine_tests} label="Original engine tests" note="Passing tests in the original private engine repository." />
          <div className="card stack">
            <strong>Public showcase suite</strong>
            <p className="muted small" style={{ margin: 0 }}>{tests.showcase_note}</p>
          </div>
        </div>
        <div className="table-wrap">
          <table>
            <thead><tr><th>Category</th><th>What it checks</th></tr></thead>
            <tbody>
              {tests.categories.map((c) => (
                <tr key={c.category}><td className="mono">{c.category}</td><td className="muted">{c.description}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
