import { useRef } from "react";

interface Props {
  value: string;
  onChange: (val: string) => void;
  onSend: () => void;
  loading: boolean;
}

export default function ChatInput({ value, onChange, onSend, loading }: Props) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      onSend();
    }
  };

  return (
    <div className="px-4 py-4 border-t border-white/10 bg-black/20 backdrop-blur-sm">
      <div className="max-w-4xl mx-auto">
        <div
          className={`rounded-2xl border transition-colors bg-white/5 backdrop-blur-sm ${
            loading
              ? "border-white/10"
              : "border-white/20 focus-within:border-blue-500/50"
          }`}
        >
          <textarea
            ref={textareaRef}
            rows={2}
            value={value}
            onChange={(e) => onChange(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about your documents..."
            disabled={loading}
            className="w-full resize-none bg-transparent px-4 pt-3 pb-1 text-sm text-white placeholder:text-slate-500 outline-none disabled:opacity-50"
          />

          <div className="flex items-center justify-between px-4 pb-3">
            <p className="text-[10px] text-slate-600">
              Enter to send · Shift+Enter for new line
            </p>

            <button
              onClick={onSend}
              disabled={!value.trim() || loading}
              className="flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white transition-colors disabled:opacity-40 disabled:cursor-not-allowed"
            >
              {loading ? (
                <>
                  <span className="w-3 h-3 border border-white border-t-transparent rounded-full animate-spin" />
                  <span>Thinking...</span>
                </>
              ) : (
                <>
                  <span>Send</span>
                  <span>↑</span>
                </>
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}