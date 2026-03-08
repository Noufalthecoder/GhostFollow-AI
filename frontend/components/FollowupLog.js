export default function FollowupLog({ items }) {
  return (
    <section className="panel rounded-2xl border border-white/10 bg-panel/70 p-5 shadow-panel">
      <header className="mb-4 flex items-center justify-between">
        <h3 className="text-lg font-semibold">Success Logs</h3>
        <span className="mono text-xs text-white/60">Follow-up status log</span>
      </header>

      <div className="space-y-2">
        {items.length === 0 && <p className="text-sm text-white/60">No follow-up records yet.</p>}
        {items.slice(0, 8).map((entry) => (
          <article key={entry.id} className="rounded-xl border border-white/10 bg-black/20 px-3 py-2">
            <p className="text-sm text-white/85">{entry.generated_message}</p>
            <p className="mt-1 mono text-xs text-white/55">
              #{entry.conversation_id} | {entry.status} | {entry.sent_time ? new Date(entry.sent_time).toLocaleString() : "pending"}
            </p>
          </article>
        ))}
      </div>
    </section>
  );
}
