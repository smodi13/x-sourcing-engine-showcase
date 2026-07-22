"use client";

export default function Error({ error, reset }: { error: Error; reset: () => void }) {
  return (
    <div className="container section">
      <div className="error-box stack">
        <h1>Something went wrong loading the demo data</h1>
        <p className="muted">
          The page could not render because a local demo data file was missing or malformed.
          The demo reads only static JSON and never contacts the X API.
        </p>
        <p className="mono small">{error.message}</p>
        <div><button className="btn" onClick={() => reset()}>Try again</button></div>
      </div>
    </div>
  );
}
