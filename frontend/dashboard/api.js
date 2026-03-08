const API_BASE = process.env.NEXT_PUBLIC_API_BASE || "http://localhost:8000";

async function request(path, options = {}) {
  const response = await fetch(`${API_BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options
  });

  if (!response.ok) {
    const text = await response.text();
    throw new Error(text || `API request failed: ${response.status}`);
  }

  return response.json();
}

export const dashboardApi = {
  getConversations: () => request("/conversations"),
  getActivity: () => request("/activity"),
  getFollowups: () => request("/followups"),
  scanConversations: (thresholdHours = 48) =>
    request("/scan-conversations", {
      method: "POST",
      body: JSON.stringify({ threshold_hours: thresholdHours })
    }),
  generateFollowup: (conversationId) =>
    request("/generate-followup", {
      method: "POST",
      body: JSON.stringify({ conversation_id: conversationId })
    }),
  sendFollowup: (conversationId, message, dryRun = false) =>
    request("/send-followup", {
      method: "POST",
      body: JSON.stringify({ conversation_id: conversationId, message, dry_run: dryRun })
    })
};
