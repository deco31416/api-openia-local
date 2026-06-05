// ─── Tipos de la API del bridge ───

export interface ComponentStatus {
  name: string;
  status: "ok" | "degraded" | "error" | "unknown";
  detail: string;
}

export interface HealthResponse {
  status: "healthy" | "degraded" | "unhealthy";
  authenticated: boolean;
  bridge: string;
  version: string;
  components: ComponentStatus[];
  errors: string[];
  uptime_seconds: number;
}

export interface ModelInfo {
  id: string;
  object: string;
  created: number;
  owned_by: string;
}

export interface UsageTotals {
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
  cost_total_usd: number;
  calls: number;
}

export interface UsageByModel {
  [model: string]: {
    prompt_tokens: number;
    completion_tokens: number;
    total_tokens: number;
    cost_input_usd: number;
    cost_output_usd: number;
    cost_total_usd: number;
    calls: number;
  };
}

export interface UsageResponse {
  by_model: UsageByModel;
  totals: UsageTotals;
}

export interface ConversationInfo {
  conversation_id: string;
  model: string;
  url: string;
  last_used_at: number;
  summary: string;
  prompt_tokens: number;
  completion_tokens: number;
  total_tokens: number;
}

export interface ConversationsResponse {
  object: string;
  data: ConversationInfo[];
}

export interface QueueStats {
  pending: number;
  processed: number;
  rejected: number;
}
