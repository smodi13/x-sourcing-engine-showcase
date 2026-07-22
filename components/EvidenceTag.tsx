export function EvidenceTag({ level }: { level: string }) {
  const cls = ["A", "B", "C", "D"].includes(level) ? level.toLowerCase() : "d";
  return <span className={`tag ${cls}`} title={`Evidence level ${level}`}>Level {level}</span>;
}

export function Tag({ children, variant }: { children: React.ReactNode; variant?: string }) {
  return <span className={`tag ${variant ?? ""}`}>{children}</span>;
}
