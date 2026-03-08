export default function ThinkingPanel({ steps }) {
  return (
    <section className="panel rounded-2xl border border-glow/30 bg-gradient-to-br from-[#112546] to-[#0a1a33] p-5 shadow-neon">
      <h3 className="text-lg font-semibold">AI Thinking Panel</h3>
      <p className="mt-1 text-sm text-white/65">Autonomous reasoning trace used for hackathon demo.</p>

      <div className="mt-4 space-y-2">
        {steps.length === 0 && <p className="text-sm text-white/60">Run scan or generate follow-up to see reasoning steps.</p>}
        {steps.map((step, idx) => (
          <div key={`${step}-${idx}`} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2 text-sm">
            <span className="mono text-glow">{`Step ${idx + 1}`}</span>
            <span className="ml-2 text-white/85">{step.replace(/^Step\s+\d+:\s*/i, "")}</span>
          </div>
        ))}
      </div>
    </section>
  );
}
