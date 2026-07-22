import Link from "next/link";

export default function NotFound() {
  return (
    <div className="container section">
      <div className="empty stack">
        <h1>Page not found</h1>
        <p className="muted">The page or candidate you requested does not exist in the saved run.</p>
        <div><Link className="btn" href="/">Back to overview</Link></div>
      </div>
    </div>
  );
}
