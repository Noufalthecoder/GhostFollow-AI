import { useState } from "react";

export default function ConversationsTable({ rows, onGenerate, onSend }) {
  const [busyId, setBusyId] = useState(null);

  async function runAction(conversationId, action) {
    setBusyId(conversationId);
    try {
      await action();
    } finally {
      setBusyId(null);
    }
  }

  return (
    <section className="panel rounded-2xl border border-white/10 bg-panel/70 p-5 shadow-panel">
      <header className="mb-4 flex items-center justify-between gap-3">
        <h3 className="text-lg font-semibold">Ghosted Conversations</h3>
        <span className="mono rounded-full border border-white/20 px-3 py-1 text-xs text-white/70">Follow-Up Queue</span>
      </header>

      <div className="overflow-x-auto">
        <table className="min-w-full text-left text-sm">
          <thead className="text-white/60">
            <tr>
              <th className="pb-3 pr-4">Customer</th>
              <th className="pb-3 pr-4">Last Message</th>
              <th className="pb-3 pr-4">Last Reply Time</th>
              <th className="pb-3 pr-4">Status</th>
              <th className="pb-3">Actions</th>
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id} className="border-t border-white/10 align-top">
                <td className="py-4 pr-4">
                  <p className="font-medium">{row.customer_name}</p>
                  <p className="mono text-xs text-white/55">{row.customer_email || "N/A"}</p>
                </td>
                <td className="py-4 pr-4 text-white/80">{row.last_message}</td>
                <td className="py-4 pr-4 text-white/70">{new Date(row.last_message_time).toLocaleString()}</td>
                <td className="py-4 pr-4">
                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      row.followup_sent
                        ? "bg-mint/20 text-mint"
                        : row.ghosted_status
                          ? "bg-ember/20 text-ember"
                          : "bg-white/10 text-white/70"
                    }`}
                  >
                    {row.followup_sent ? "Followed Up" : row.ghosted_status ? "Ghosted" : "Active"}
                  </span>
                </td>
                <td className="py-4">
                  <div className="flex flex-wrap gap-2">
                    <button
                      onClick={() => runAction(row.id, () => onGenerate(row.id))}
                      disabled={busyId === row.id}
                      className="rounded-lg border border-glow/50 px-3 py-2 text-xs font-semibold text-glow hover:bg-glow/10 disabled:opacity-50"
                    >
                      AI Follow-up
                    </button>
                    <button
                      onClick={() => runAction(row.id, () => onSend(row.id))}
                      disabled={busyId === row.id}
                      className="rounded-lg bg-ember px-3 py-2 text-xs font-semibold text-black hover:brightness-110 disabled:opacity-50"
                    >
                      Send via Gmail
                    </button>
                  </div>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
        {rows.length === 0 && <p className="py-8 text-center text-white/55">No ghosted conversations yet.</p>}
      </div>
    </section>
  );
}
