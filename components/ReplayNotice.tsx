export default function ReplayNotice({ text }: { text?: string }) {
  return (
    <div className="replay" role="note">
      <span className="badge">Replay mode</span>
      <span>
        {text ??
          "This demo uses saved outputs from the completed sourcing run and does not initiate new X API requests."}
      </span>
    </div>
  );
}
