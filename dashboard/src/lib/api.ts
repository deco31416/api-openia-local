// ─── API Client centralizado ───

const API_BASE = process.env.NEXT_PUBLIC_API_URL || "http://localhost:9090";

async function fetchJSON<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`);
  if (!res.ok) {
    throw new Error(`API ${path}: ${res.status} ${res.statusText}`);
  }
  return res.json();
}

import type {
  HealthResponse,
  UsageResponse,
  ConversationsResponse,
} from "@/types/api";

export const api = {
  health: () => fetchJSON<HealthResponse>("/health"),
  usage: () => fetchJSON<UsageResponse>("/v1/usage"),
  conversations: () => fetchJSON<ConversationsResponse>("/v1/conversations"),
};
