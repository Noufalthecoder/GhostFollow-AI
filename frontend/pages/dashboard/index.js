import { useCallback, useEffect, useMemo, useState } from "react";

import ActivityFeed from "../../components/ActivityFeed";
import ConversationsTable from "../../components/ConversationsTable";
import FollowupLog from "../../components/FollowupLog";
import StatCard from "../../components/StatCard";
import ThinkingPanel from "../../components/ThinkingPanel";
import { dashboardApi } from "../../dashboard/api";

const DEFAULT_STEPS = [
  "Step 1: Checking conversation inactivity",
  "Step 2: Last reply detected 3 days ago",
  "Step 3: Customer intent identified from context",
  "Step 4: Generating AI follow-up",
  "Step 5: Sending message via Gmail"
];

export default function DashboardPage() {
  const [conversations, setConversations] = useState([]);
  const [logs, setLogs] = useState([]);
  const [followups, setFollowups] = useState([]);
  const [steps, setSteps] = useState(DEFAULT_STEPS);
  const [status, setStatus] = useState("Idle");
  const [loading, setLoading] = useState(false);

  const loadData = useCallback(async () => {
    setLoading(true);
    try {
      const [convoData, activityData, followupData] = await Promise.all([
        dashboardApi.getConversations(),
        dashboardApi.getActivity(),
        dashboardApi.getFollowups()
      ]);
      setConversations(convoData.items || []);
      setLogs(activityData.items || []);
      setFollowups(followupData.items || []);

      const firstReasoning = (convoData.items || []).find((item) => item.ai_reasoning)?.ai_reasoning;
      if (firstReasoning) {
        setSteps(firstReasoning.split("\n").filter(Boolean));
      }
    } catch (error) {
      setStatus(`Error loading data: ${error.message}`);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadData();
    const timer = setInterval(loadData, 6000);
    return () => clearInterval(timer);
  }, [loadData]);

  const stats = useMemo(() => {
    const ghosted = conversations.filter((c) => c.ghosted_status).length;
    const sent = conversations.filter((c) => c.followup_sent).length;
    return {
      total: conversations.length,
      ghosted,
      sent,
      queue: Math.max(ghosted - sent, 0)
    };
  }, [conversations]);

  async function handleScan() {
    setStatus("Scanning conversations...");
    const result = await dashboardApi.scanConversations(48);
    setStatus(`Scan complete: ${result.ghosted} ghosted of ${result.total}`);
    await loadData();
  }

  async function handleGenerate(conversationId) {
    setStatus(`Generating follow-up for #${conversationId}...`);
    const result = await dashboardApi.generateFollowup(conversationId);
    if (result.reasoning) {
      setSteps(result.reasoning);
    }
    setStatus("AI follow-up generated.");
    await loadData();
  }

  async function handleSend(conversationId) {
    setStatus(`Sending follow-up for #${conversationId}...`);
    await dashboardApi.sendFollowup(conversationId, null, false);
    setStatus("Follow-up sent request executed.");
    await loadData();
  }

  return (
    <main className="relative min-h-screen overflow-hidden px-4 py-6 md:px-8 md:py-8">
      <div className="pointer-events-none absolute -left-16 top-24 h-52 w-52 animate-float rounded-full bg-glow/20 blur-3xl" />
      <div className="pointer-events-none absolute right-0 top-0 h-72 w-72 animate-pulseSoft rounded-full bg-ember/10 blur-3xl" />

      <section className="mx-auto max-w-7xl">
        <header className="mb-6 flex flex-wrap items-center justify-between gap-3">
          <div>
            <p className="mono text-xs uppercase tracking-[0.3em] text-glow">GhostFollow AI Console</p>
            <h1 className="mt-2 text-3xl font-bold md:text-4xl">Autonomous Customer Follow-Up Agent</h1>
          </div>
          <div className="flex gap-2">
            <button
              onClick={handleScan}
              className="rounded-xl border border-glow/50 px-4 py-2 text-sm font-semibold text-glow hover:bg-glow/10"
            >
              Scan Conversations
            </button>
            <button
              onClick={loadData}
              className="rounded-xl border border-white/20 px-4 py-2 text-sm font-semibold text-white/80 hover:border-white/40"
            >
              Refresh
            </button>
          </div>
        </header>

        <p className="mb-6 mono text-xs text-white/60">{loading ? "Syncing..." : status}</p>

        <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard title="Conversations" value={stats.total} hint="Total indexed threads" tone="default" />
          <StatCard title="Ghosted" value={stats.ghosted} hint="No reply in 48h" tone="danger" />
          <StatCard title="Follow-Ups Sent" value={stats.sent} hint="Messages delivered" tone="success" />
          <StatCard title="Queue" value={stats.queue} hint="Awaiting AI action" tone="accent" />
        </section>

        <section className="mt-6 grid gap-6 xl:grid-cols-[1.8fr_1fr]">
          <ConversationsTable
            rows={conversations.filter((item) => item.ghosted_status)}
            onGenerate={handleGenerate}
            onSend={handleSend}
          />
          <ThinkingPanel steps={steps} />
        </section>

        <section className="mt-6 grid gap-6 xl:grid-cols-2">
          <ActivityFeed logs={logs} />
          <FollowupLog items={followups} />
        </section>
      </section>
    </main>
  );
}
