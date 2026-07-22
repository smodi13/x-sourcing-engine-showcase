"use client";

import { useId, useState } from "react";

const DEFAULT_TEXT =
  "This demo uses saved outputs from the completed sourcing run and does not initiate new X API requests.";

const EXPANDED_TEXT =
  "Replay mode uses sanitized saved outputs from the completed sourcing run. It does not initiate new X API requests, no API credential is deployed, and no additional API spending can occur. This keeps the demonstration stable and reproducible.";

export default function ReplayNotice({
  text,
  expandable = false,
}: {
  text?: string;
  expandable?: boolean;
}) {
  const [open, setOpen] = useState(false);
  const contentId = useId();
  const body = text ?? DEFAULT_TEXT;

  // Non-home usages keep the static, non-interactive banner unchanged.
  if (!expandable) {
    return (
      <div className="replay" role="note">
        <span className="badge">Replay mode</span>
        <span>{body}</span>
      </div>
    );
  }

  return (
    <div className="replay" role="note">
      <button
        type="button"
        className="badge badge-button"
        aria-expanded={open}
        aria-controls={contentId}
        onClick={() => setOpen((v) => !v)}
      >
        Replay mode
        <span className={`chevron${open ? " up" : ""}`} aria-hidden="true">
          &#9662;
        </span>
      </button>
      <div className="replay-body">
        <span>{body}</span>
        <div id={contentId} className="replay-expanded" hidden={!open}>
          {EXPANDED_TEXT}
        </div>
      </div>
    </div>
  );
}
