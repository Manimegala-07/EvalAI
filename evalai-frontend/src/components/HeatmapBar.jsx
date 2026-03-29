export default function HeatmapBar({ label, value, color }) {
  const pct = Math.round((value || 0) * 100);
  const barColor = color || (pct >= 70 ? "var(--green)" : pct >= 40 ? "var(--amber)" : "var(--red)");
  return (
    <div className="heatmap-row">
      <div className="heatmap-label">{label}</div>
      <div className="heatmap-bar-track">
        <div className="heatmap-bar-fill" style={{ width: `${pct}%`, background: barColor }} />
      </div>
      <div className="heatmap-pct">{pct}%</div>
    </div>
  );
}
