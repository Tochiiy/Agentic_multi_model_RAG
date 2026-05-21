import { useEffect, useRef, useState } from "react";
import { useAppDispatch, useAppSelector } from "@/stores";
import {
  addUserMessageWithAssistant,
  fetchChatHistory,
} from "@/stores/chatSlice";
import { streamChat } from "@/api/chat";
import ChatInput from "./chatbox/ChatInput";
import ConvertToMarkdown from "./chatbox/ConvertToMarkdown";

// ── Thinking toggle block ───────────────────────
function ThinkingBlock({
  thinking,
  loading,
  isLast,
}: {
  thinking: string;
  loading: boolean;
  isLast: boolean;
}) {
  const [open, setOpen] = useState(false);

  if (!thinking && !(loading && isLast)) return null;

  return (
    <div className="mb-3">
      <button
        onClick={() => setOpen((v) => !v)}
        className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-slate-200 transition-colors"
      >
        <span className="text-[10px]">{open ? "▼" : "▶"}</span>
        <span>Thinking</span>
        {loading && isLast && !thinking && (
          <span className="inline-block w-3 h-3 border border-slate-400 border-t-transparent rounded-full animate-spin ml-1" />
        )}
      </button>

      {open && thinking && (
        <div className="mt-2 rounded-lg bg-black/30 border border-white/10 px-3 py-2 text-xs text-slate-400 whitespace-pre-line font-mono max-h-48 overflow-y-auto">
          {thinking}
        </div>
      )}
    </div>
  );
}

// ── Single message bubble ─────────────────────────────────────────
function MessageBubble({
  role,
  text,
  thinking,
  loading,
  isLast,
}: {
  role: "user" | "assistant";
  text: string;
  thinking?: string;
  loading: boolean;
  isLast: boolean;
}) {
  const isUser = role === "user";

  return (
    <div className={`flex ${isUser ? "justify-end" : "justify-start"} mb-5`}>
      {/* AI avatar */}
      {!isUser && (
        <div className="w-7 h-7 rounded-full bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center mr-2.5 mt-1 flex-shrink-0 shadow-lg">
          <span className="text-[10px] font-bold text-white">AI</span>
        </div>
      )}

      <div className={`${isUser ? "max-w-[60%]" : "max-w-[75%]"}`}>
        {isUser ? (
          // User bubble
          <div className="bg-blue-600/80 backdrop-blur-sm text-white rounded-2xl rounded-tr-sm px-4 py-3 text-sm shadow-lg">
            <p className="whitespace-pre-line leading-relaxed">{text}</p>
          </div>
        ) : (
          // Assistant bubble
          <div className="bg-white/5 backdrop-blur-sm border border-white/10 rounded-2xl rounded-tl-sm px-4 py-3 text-sm text-slate-200 shadow-lg">
            {/* Thinking section */}
            <ThinkingBlock
              thinking={thinking || ""}
              loading={loading}
              isLast={isLast}
            />

            {/* Answer */}
            {text ? (
              <ConvertToMarkdown text={text} />
            ) : loading && isLast ? (
              // Loading dots
              <div className="flex gap-1 items-center py-1">
                <span
                  className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce"
                  style={{ animationDelay: "0ms" }}
                />
                <span
                  className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce"
                  style={{ animationDelay: "150ms" }}
                />
                <span
                  className="w-1.5 h-1.5 rounded-full bg-blue-400 animate-bounce"
                  style={{ animationDelay: "300ms" }}
                />
              </div>
            ) : null}
          </div>
        )}
      </div>

      {/* User avatar */}
      {isUser && (
        <div className="w-7 h-7 rounded-full bg-slate-600 flex items-center justify-center ml-2.5 mt-1 flex-shrink-0">
          <span className="text-[10px] font-bold text-white">U</span>
        </div>
      )}
    </div>
  );
}

// ── Main ChatPanel ────────────────────────────────────────────────
export default function ChatPanel() {
  const dispatch = useAppDispatch();
  const { messages, loading } = useAppSelector((state) => state.chat);
  const [input, setInput] = useState("");
  const bottomRef = useRef<HTMLDivElement>(null);

  // load chat history on mount
  useEffect(() => {
    dispatch(fetchChatHistory());
  }, [dispatch]);

  // auto scroll to bottom on new messages
  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  // send message
  const handleSend = () => {
    if (!input.trim() || loading) return;
    const message = input.trim();
    setInput("");
    dispatch(addUserMessageWithAssistant(message));
    streamChat(message);
  };

  return (
    <div className="flex flex-col h-full">
      {/* Messages area */}
      <div className="flex-1 overflow-y-auto px-6 py-6">
        {/* Empty state */}
        {messages.length === 0 && !loading && (
          <div className="flex flex-col items-center justify-center h-full gap-4 text-center">
            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-2xl">
              <span className="text-2xl">🤖</span>
            </div>
            <div>
              <h2 className="text-xl font-bold text-white mb-1">
                Agentic RAG Assistant
              </h2>
              <p className="text-sm text-slate-400 max-w-sm">
                Ask anything about your documents. I'll retrieve, analyze, and
                synthesize information for you.
              </p>
            </div>

            {/* Quick prompts */}
            <div className="flex flex-wrap gap-2 justify-center mt-2">
              {[
                "What is RAG?",
                "Types of agent memory",
                "How does MCP work?",
              ].map((q) => (
                <button
                  key={q}
                  onClick={() => setInput(q)}
                  className="text-xs px-3 py-1.5 rounded-full bg-white/5 border border-white/10 text-slate-300 hover:bg-white/10 hover:text-white transition-colors"
                >
                  {q}
                </button>
              ))}
            </div>
          </div>
        )}

        {/* Message list */}
        {messages.map((msg, i) => (
          <MessageBubble
            key={i}
            role={msg.role}
            text={msg.text}
            thinking={msg.thinking}
            loading={loading}
            isLast={i === messages.length - 1}
          />
        ))}

        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <ChatInput
        value={input}
        onChange={setInput}
        onSend={handleSend}
        loading={loading}
      />
    </div>
  );
}