import { useState } from "react";
import { Provider } from "react-redux";
import { store } from "@/stores";
import { useAppDispatch } from "@/stores";
import { clearMessages } from "@/stores/chatSlice";
import Sidebar from "@/components/chatpdf/Sidebar";
import ChatPanel from "@/components/chatpdf/ChatPanel";
import { Menu, X, Trash2 } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

// ── Header ────────────────────────────────────────────────────────
function Header({
  sidebarOpen,
  onToggle,
}: {
  sidebarOpen: boolean;
  onToggle: () => void;
}) {
  const dispatch = useAppDispatch();

  const handleClear = async () => {
    // Intercept with a quick confirmation alert box to protect user state
    if (!window.confirm("Are you sure you want to clear your conversation history?")) {
      return;
    }

    try {
      dispatch(clearMessages());
      await fetch(`${API_BASE}/api/agent/chat-history`, {
        method: "DELETE",
      });
    } catch (e) {
      console.error("Failed to clear chat history:", e);
    }
  };

  return (
    <header className="flex items-center justify-between px-6 py-4 border-b border-white/10 bg-black/20 backdrop-blur-sm flex-shrink-0 z-10">
      <div className="flex items-center gap-3">
        <button
          onClick={onToggle}
          className="w-8 h-8 rounded-lg bg-white/5 hover:bg-white/10 transition-colors flex items-center justify-center text-slate-400 hover:text-white"
        >
          {sidebarOpen ? <X size={15} /> : <Menu size={15} />}
        </button>
        <div>
          <h1 className="text-sm font-bold text-white tracking-tight">
            Agentic RAG
          </h1>
          <p className="text-[10px] text-slate-500">
            Multi-Modal · MCP · Vector Search
          </p>
        </div>
      </div>

      {/* Clear chat button */}
      <button
        onClick={handleClear}
        className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-red-400 border border-transparent hover:border-red-500/20 transition-all px-3 py-1.5 rounded-lg hover:bg-red-500/10 shadow-sm"
      >
        <Trash2 size={13} />
        <span>Clear Thread</span>
      </button>
    </header>
  );
}

// ── Inner Layout ──────────────────────────────────────────────────
function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(true);

  return (
    <div className="flex h-screen w-full overflow-hidden bg-[#0a0f1e] text-white">
      {/* Ambient background shadows */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-blue-500/5 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-indigo-500/5 rounded-full blur-3xl" />
      </div>

      {/* Sidebar navigation context drawer */}
      <Sidebar open={sidebarOpen} />

      {/* Main Container */}
      <main className="flex flex-1 flex-col overflow-hidden relative">
        <Header
          sidebarOpen={sidebarOpen}
          onToggle={() => setSidebarOpen((v) => !v)}
        />

        {/* Core Workspace Output Panel */}
        <ChatPanel />
      </main>
    </div>
  );
}

// ── Root App ──────────────────────────────────────────────────────
export default function App() {
  return (
    <Provider store={store}>
      <Layout />
    </Provider>
  );
}