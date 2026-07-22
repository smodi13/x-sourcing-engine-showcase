import Link from "next/link";
import { GITHUB_URL } from "@/lib/site";

export default function Footer() {
  return (
    <footer className="footer">
      <div className="container footer-inner">
        <div>
          <strong>Deterministic X Sourcing Engine</strong>
          <div className="faint small">
            Sanitized replay of a completed venture-sourcing run. No live X API credential is present.
          </div>
        </div>
        <div className="stack small" style={{ textAlign: "right" }}>
          <div><a href={GITHUB_URL} target="_blank" rel="noopener noreferrer">GitHub repository</a></div>
          <div><Link href="/">Back to overview</Link></div>
        </div>
      </div>
    </footer>
  );
}
