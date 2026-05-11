export interface ExecutionTraceItem {
  node_name: string;
  status: string;
  duration_ms?: number;
  error?: string;
}

export interface UserInquiryResponse {
  answer: string;
  conversation_id: string;
}

export interface ChatMessage {
  role: "human" | "ai";
  content: string;
}

export interface OperatorInquiryResponse {
  category: string | null;
  confidence: number | null;
  selected_agent: string | null;
  selected_agents: string[] | null;
  agent_version: "v1" | "v2" | "v3";
  answer: string | null;
  fallback_used: boolean;
  routing_reason: string | null;
  execution_trace: ExecutionTraceItem[];
  latency_ms: number;
  mcp_connected?: boolean;
  faq_context?: string;
  faq_category?: string;
}

export interface ApiError {
  code: string;
  message: string;
}

export interface ApiErrorResponse {
  detail: ApiError;
}

export type InquiryMode = "user" | "operator";
export type AgentVersion = "v1" | "v2" | "v3";
