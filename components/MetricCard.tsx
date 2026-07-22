export default function MetricCard({
  value,
  label,
  note,
}: {
  value: number | string;
  label: string;
  note?: string;
}) {
  const display = typeof value === "number" ? value.toLocaleString("en-US") : value;
  return (
    <div className="card metric">
      <div className="value">{display}</div>
      <div className="label">{label}</div>
      {note ? <div className="note">{note}</div> : null}
    </div>
  );
}
