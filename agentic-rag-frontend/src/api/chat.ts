import { API_BASE, MCP_API_KEY } from "@/lib/utils";
import { store } from "@/stores";
import {
  appendToLastAssistant,
  appendToAssistantThinking,
  setLoading,
  setSessionId,
} from "@/stores/chatSlice";

// ── MCP Session management ────────────────────────────────────────
let mcpSessionId: string | null = null;

async function initMCPSession(): Promise<string | null> {
  try {
    const res = await fetch("http://localhost:3001/mcp", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "x-api-key": MCP_API_KEY,
      },
      body: JSON.stringify({
        jsonrpc: "2.0",
        id: 1,
        method: "initialize",
        params: {
          protocolVersion: "2024-11-05",
          capabilities: {},
          clientInfo: { name: "agentic-rag-frontend", version: "1.0.0" }
        }
      })
    });

    const sessionId = res.headers.get("mcp-session-id");
    if (sessionId) {
      mcpSessionId = sessionId;
      store.dispatch(setSessionId(sessionId));
      console.log("✅ MCP Session initialized:", sessionId);
    }
    return sessionId;
  } catch (e) {
    console.error("❌ MCP Session init failed:", e);
    return null;
  }
}

// ── Call MCP tool ─────────────────────────────────────────────────
export async function callMCPTool(toolName: string, args: Record<string, any>) {
  // initialize session if not already done
  if (!mcpSessionId) {
    await initMCPSession();
  }

  const res = await fetch("http://localhost:3001/mcp", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      "Accept": "application/json, text/event-stream",
      "x-api-key": MCP_API_KEY,
      ...(mcpSessionId ? { "mcp-session-id": mcpSessionId } : {}),
    },
    body: JSON.stringify({
      jsonrpc: "2.0",
      id: Date.now(),
      method: "tools/call",
      params: { name: toolName, arguments: args }
    })
  });

  const text = await res.text();

  // parse SSE or JSON response
  // MCP returns: event: message\ndata: {...}
  const dataLine = text.split("\n").find(line => line.startsWith("data:"));
  if (dataLine) {
    return JSON.parse(dataLine.replace("data:", "").trim());
  }
  return JSON.parse(text);
}

// ── Stream chat response from Python backend ──────────────────────
// This connects to FastAPI /api/agent/stream endpoint
// Python backend calls MCP tools and streams back the response
export function streamChat(message: string): void {
  const url = `${API_BASE}/api/agent/stream?message=${encodeURIComponent(message)}`;

  // typing queue for smooth typewriter effect
  const queue: string[] = [];
  const thinkingQueue: string[] = [];
  let typing = false;
  let thinkingTyping = false;

  // typewriter for answer
  function typeNext() {
    if (queue.length === 0) { typing = false; return; }
    typing = true;
    const char = queue.shift()!;
    store.dispatch(appendToLastAssistant(char));
    setTimeout(typeNext, 18);
  }

  // typewriter for thinking
  function typeNextThinking() {
    if (thinkingQueue.length === 0) { thinkingTyping = false; return; }
    thinkingTyping = true;
    const char = thinkingQueue.shift()!;
    store.dispatch(appendToAssistantThinking(char));
    setTimeout(typeNextThinking, 12);
  }

  const eventSource = new EventSource(url);

  // answer stream
  eventSource.addEventListener("message", (event) => {
    const data = JSON.parse(event.data);
    for (const char of (data.message || "")) {
      queue.push(char);
    }
    if (!typing) typeNext();
  });

  // thinking stream
  eventSource.addEventListener("thinking", (event) => {
    const data = JSON.parse(event.data);
    for (const char of (data.thinking || "")) {
      thinkingQueue.push(char);
    }
    if (!thinkingTyping) typeNextThinking();
  });

  // stream ended
  eventSource.addEventListener("end", () => {
    store.dispatch(setLoading(false));
    eventSource.close();
  });

  // error
  eventSource.onerror = () => {
    store.dispatch(setLoading(false));
    eventSource.close();
  };
}

// ── Fetch chat history from Python backend ────────────────────────
export async function fetchChatHistoryAPI() {
  try {
    const res = await fetch(`${API_BASE}/api/agent/chat-history`);
    if (!res.ok) return [];
    const data = await res.json();
    return (data.messages || []).map((msg: any) => ({
      role: msg.role === "ai" ? "assistant" : "user",
      text: msg.content,
      thinking: msg.thinking || "",
    }));
  } catch {
    return [];
  }
}