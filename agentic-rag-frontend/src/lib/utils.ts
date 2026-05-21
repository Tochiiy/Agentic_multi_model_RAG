import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

// ── Tailwind class merger ─────────────────────────────────────────

// Combines clsx + tailwind-merge to handle conflicting classes
export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

// ── Truncate long titles ──────────────────────────────────────────
export function truncateTitle(title: string, maxLength = 30): string {
  if (title.length <= maxLength) return title;
  return title.slice(0, maxLength) + "...";
}

// ── Format date ───────────────────────────────────────────────────
export function formatDate(date: Date): string {
  return new Intl.DateTimeFormat("en-US", {
    month: "short",
    day: "numeric",
    hour: "2-digit",
    minute: "2-digit",
  }).format(date);
}

// ── Environment variables ─────────────────────────────────────────
export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";
export const MCP_API_KEY = import.meta.env.VITE_MCP_API_KEY || "";