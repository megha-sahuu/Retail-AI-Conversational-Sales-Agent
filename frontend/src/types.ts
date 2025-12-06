export type Channel = "web_chat" | "kiosk" | "whatsapp";

export interface ChatRequest {
  session_id: string;
  customer_id: string;
  channel: Channel;
  message: string;
}

export interface ChatResponse {
  session_id: string;
  channel: Channel;
  agent_reply: string;
  state: Record<string, unknown>;
}
