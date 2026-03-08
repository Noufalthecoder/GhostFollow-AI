export default function ActivityFeed({ logs }) {
  return (
    <section className="panel rounded-2xl border border-white/10 bg-panel/70 p-5 shadow-panel">
      <header className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold">AI Agent Activity</h3>
        <span className="mono text-xs text-white/60">real-time logs</span>
      </header>

      <div className="max-h-[320px] space-y-3 overflow-auto pr-1">
        {logs.length === 0 && <p className="text-sm text-white/60">No activity yet.</p>}
        {logs.map((item) => (
          <article key={item.id} className="rounded-xl border border-white/10 bg-white/5 p-3">
            <p className="text-sm font-medium text-white">{item.step}</p>
            <p className="mt-1 text-sm text-white/70">{item.details}</p>
            <p className="mt-2 mono text-xs text-white/50">{new Date(item.created_at).toLocaleString()}</p>
          </article>
        ))}
      </div>
    </section>
  );
}
