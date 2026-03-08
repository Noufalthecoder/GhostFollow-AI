export default function StatCard({ title, value, hint, tone = "default" }) {
  const toneStyles = {
    default: "border-white/10",
    danger: "border-ember/50",
    accent: "border-glow/50",
    success: "border-mint/50"
  };

  return (
    <section className={`panel rounded-2xl border bg-panel/75 p-5 shadow-panel ${toneStyles[tone] || toneStyles.default}`}>
      <p className="text-xs uppercase tracking-[0.18em] text-white/65">{title}</p>
      <p className="mt-3 text-3xl font-bold text-white">{value}</p>
      <p className="mt-2 text-sm text-white/70">{hint}</p>
    </section>
  );
}
