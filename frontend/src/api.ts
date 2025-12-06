import axios from "axios";
import type { ChatRequest, ChatResponse } from "./types";

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000/api/v1",
  timeout: 10000,
});

export async function sendChat(req: ChatRequest): Promise<ChatResponse> {
  const res = await api.post<ChatResponse>("/chat", req);
  return res.data;
}
