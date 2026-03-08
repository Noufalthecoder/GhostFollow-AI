import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen bg-ink text-white px-6 py-16">
      <div className="mx-auto max-w-4xl rounded-3xl border border-white/10 bg-gradient-to-br from-panel to-[#0c1d3d] p-10 shadow-panel">
        <p className="text-sm uppercase tracking-[0.3em] text-glow">TinyFish Hackathon MVP</p>
        <h1 className="mt-4 text-5xl font-bold leading-tight">GhostFollow AI</h1>
        <p className="mt-4 max-w-2xl text-white/75">
          Autonomous customer follow-up agent that scans ghosted conversations, generates contextual AI replies, and sends them via real browser automation.
        </p>

        <div className="mt-10 flex flex-wrap gap-4">
          <Link href="/dashboard" className="rounded-xl bg-glow px-6 py-3 font-semibold text-ink transition hover:brightness-110">
            Open Dashboard
          </Link>
          <a
            href="https://mail.google.com"
            target="_blank"
            rel="noreferrer"
            className="rounded-xl border border-white/20 px-6 py-3 font-semibold text-white/85 transition hover:border-white/50"
          >
            Gmail Web
          </a>
        </div>
      </div>
    </main>
  );
}
