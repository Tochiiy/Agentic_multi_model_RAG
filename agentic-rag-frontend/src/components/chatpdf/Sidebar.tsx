import { useState, useRef } from "react";
import { MessageSquare, FileText, Image, Settings, Upload, Link } from "lucide-react";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

interface Props {
  open: boolean;
}

function SidebarItem({
  icon: Icon,
  label,
  active,
}: {
  icon: any;
  label: string;
  active?: boolean;
}) {
  return (
    <button
      className={`flex w-full items-center gap-2.5 rounded-lg px-3 py-2 text-sm transition-colors ${
        active
          ? "bg-white/10 text-white font-medium"
          : "text-slate-400 hover:bg-white/5 hover:text-slate-200"
      }`}
    >
      <Icon size={15} />
      <span>{label}</span>
    </button>
  );
}

// ── Upload + URL + Image Section ──────────────────────────────────
function UploadSection() {
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState("");
  const [loading, setLoading] = useState(false);
  const fileRef = useRef<HTMLInputElement>(null);
  const imageRef = useRef<HTMLInputElement>(null);

  // ── Upload document ───────────────────────────────────────────
  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setStatus(`⏳ Uploading ${file.name}...`);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(`${API_BASE}/api/agent/upload`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setStatus(data.message);
    } catch {
      setStatus("❌ Upload failed");
    } finally {
      setLoading(false);
      if (fileRef.current) fileRef.current.value = "";
    }
  };

  // ── Upload image file ────────────────────────────────────────
  const handleImageUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setLoading(true);
    setStatus(`⏳ Analyzing ${file.name}...`);
    const formData = new FormData();
    formData.append("file", file);
    try {
      const res = await fetch(`${API_BASE}/api/agent/upload-image`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setStatus(data.message);
    } catch {
      setStatus("❌ Image upload failed");
    } finally {
      setLoading(false);
      if (imageRef.current) imageRef.current.value = "";
    }
  };

  // ── Embed URL ─────────────────────────────────────────────────
  const handleUrlEmbed = async () => {
    if (!url.trim()) return;
    setLoading(true);
    setStatus(`⏳ Embedding URL...`);
    const formData = new FormData();
    formData.append("url", url.trim());
    try {
      const res = await fetch(`${API_BASE}/api/agent/embed-url`, {
        method: "POST",
        body: formData,
      });
      const data = await res.json();
      setStatus(data.message);
      setUrl("");
    } catch {
      setStatus("❌ Failed to embed URL");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="px-3 py-3 border-t border-white/10 space-y-2">
      <p className="text-[10px] text-slate-500 uppercase tracking-wider px-1">
        Add Knowledge
      </p>

      {/* Hidden file inputs */}
      <input
        ref={fileRef}
        type="file"
        accept=".pdf,.docx,.csv,.xlsx,.pptx,.txt,.mp3,.wav"
        onChange={handleFileUpload}
        className="hidden"
      />
      <input
        ref={imageRef}
        type="file"
        accept=".png,.jpg,.jpeg,.webp,.gif"
        onChange={handleImageUpload}
        className="hidden"
      />

      {/* Upload Document button */}
      <button
        onClick={() => fileRef.current?.click()}
        disabled={loading}
        className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs text-slate-300 hover:bg-white/5 transition-colors border border-white/10 disabled:opacity-50"
      >
        <Upload size={12} />
        <span>{loading ? "Processing..." : "Upload Document"}</span>
      </button>

      {/* Upload Image button */}
      <button
        onClick={() => imageRef.current?.click()}
        disabled={loading}
        className="flex w-full items-center gap-2 rounded-lg px-3 py-2 text-xs text-slate-300 hover:bg-white/5 transition-colors border border-purple-500/30 disabled:opacity-50"
      >
        <Image size={12} className="text-purple-400" />
        <span className="text-purple-300">
          {loading ? "Processing..." : "Upload Image"}
        </span>
      </button>

      {/* URL embed input */}
      <div className="flex gap-1">
        <input
          type="text"
          value={url}
          onChange={(e) => setUrl(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && handleUrlEmbed()}
          placeholder="Paste URL to embed..."
          disabled={loading}
          className="flex-1 bg-white/5 border border-white/10 rounded-lg px-2 py-1.5 text-xs text-white placeholder:text-slate-600 outline-none focus:border-blue-500/50 disabled:opacity-50"
        />
        <button
          onClick={handleUrlEmbed}
          disabled={loading || !url.trim()}
          className="px-2 py-1.5 rounded-lg bg-blue-600 hover:bg-blue-500 text-white text-xs transition-colors disabled:opacity-40"
        >
          <Link size={12} />
        </button>
      </div>

      {/* Status message */}
      {status && (
        <p className="text-[10px] text-slate-400 px-1 leading-relaxed">
          {status}
        </p>
      )}
    </div>
  );
}

// ── Main Sidebar ──────────────────────────────────────────────────
export default function Sidebar({ open }: Props) {
  return (
    <aside
      className={`flex flex-col h-full border-r border-white/10 bg-black/20 backdrop-blur-sm transition-all duration-300 overflow-hidden flex-shrink-0 ${
        open ? "w-60" : "w-0"
      }`}
    >
      <div className={`flex flex-col h-full ${!open && "hidden"}`}>
        {/* Logo */}
        <div className="px-5 py-5 border-b border-white/10">
          <div className="flex items-center gap-2.5">
            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-blue-500 to-indigo-600 flex items-center justify-center shadow-lg">
              <span className="text-xs font-bold text-white">AI</span>
            </div>
            <div>
              <p className="text-sm font-bold text-white tracking-tight">
                Max-AI
              </p>
              <p className="text-[10px] text-slate-400">Multi-Modal AI</p>
            </div>
          </div>
        </div>

        {/* Nav */}
        <nav className="flex-1 px-3 py-4 space-y-3">
          {/* AI Knowledge Card */}
          <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-gradient-to-b from-white/10 to-white/5 p-4 shadow-xl backdrop-blur-xl transition-all duration-300 hover:border-white/20 hover:bg-white/10">
            <div className="absolute inset-0 bg-[radial-gradient(circle_at_top,rgba(99,102,241,0.15),transparent_70%)]" />
            <div className="relative z-10">
              <div className="flex items-center gap-2 mb-3">
                <div className="h-2 w-2 rounded-full bg-green-400 animate-pulse" />
                <p className="text-xs uppercase tracking-wider text-gray-400 font-medium">
                  AI Knowledge
                </p>
              </div>
              <p className="text-sm leading-6 text-gray-300">
                I can process and generate responses using provided context,
                documents, images, internal knowledge, and external web
                information. I also support reasoning and critical thinking.
              </p>
            </div>
          </div>

          {/* Navigation */}
          <div className="space-y-1 pt-2">
            <SidebarItem icon={MessageSquare} label="Chat" active />
            <SidebarItem icon={FileText} label="Documents" />
            <SidebarItem icon={Image} label="Images" />
            <SidebarItem icon={Settings} label="Settings" />
          </div>
        </nav>

        {/* Upload + URL + Image section */}
        <UploadSection />

        {/* Footer */}
        <div className="px-4 py-4 border-t border-white/10 space-y-1">
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <p className="text-[10px] text-emerald-400">Made by Tochukwu ❤️</p>
          </div>
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <p className="text-[10px] text-emerald-400">Full Stack AI Engineer</p>
          </div>
        </div>
      </div>
    </aside>
  );
}