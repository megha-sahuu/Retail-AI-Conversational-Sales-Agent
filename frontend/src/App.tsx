import { useState } from "react";
import { v4 as uuidv4 } from "uuid";
import { sendChat } from "./api";
import type { Channel, ChatRequest } from "./types";
import "./index.css";

interface ChatMessage {
  id: string;
  role: "user" | "agent";
  text: string;
  channel: Channel;
}

const CHANNEL_LABELS: Record<Channel, string> = {
  web_chat: "🌐 Web Chat",
  kiosk: "🖥️ In-store Kiosk",
  whatsapp: "📱 WhatsApp",
};

function App() {
  const [sessionId] = useState<string>(() => `demo-${uuidv4()}`);
  const [customerId] = useState<string>("cust1");
  const [channel, setChannel] = useState<Channel>("web_chat");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState<string>("");
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  const handleSend = async () => {
    if (!input.trim() || loading) return;

    const userMsg: ChatMessage = {
      id: uuidv4(),
      role: "user",
      text: input.trim(),
      channel,
    };

    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setError(null);
    setLoading(true);

    const payload: ChatRequest = {
      session_id: sessionId,
      customer_id: customerId,
      channel,
      message: userMsg.text,
    };

    try {
      const res = await sendChat(payload);

      const agentMsg: ChatMessage = {
        id: uuidv4(),
        role: "agent",
        text: res.agent_reply,
        channel: res.channel as Channel,
      };

      setMessages((prev) => [...prev, agentMsg]);
    } catch (err: any) {
      console.error(err);
      setError("Backend error. Please check FastAPI server is running.");
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLInputElement>) => {
    if (e.key === "Enter") {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="app">
      <header className="app-header">
        <h1>Retail AI Conversational Sales Agent</h1>
      </header>

      <main className="app-main">
        <section className="sidebar">
          <h2>Channel</h2>
          <div className="channel-list">
            {(["web_chat", "kiosk", "whatsapp"] as Channel[]).map((ch) => (
              <button
                key={ch}
                className={`channel-btn ${channel === ch ? "active" : ""}`}
                onClick={() => setChannel(ch)}
              >
                {CHANNEL_LABELS[ch]}
              </button>
            ))}
          </div>

          <div className="session-info">
            <h3>Session</h3>
            <p>
              <strong>ID:</strong> {sessionId}
            </p>
            <p>
              <strong>Customer:</strong> {customerId}
            </p>
          </div>

          <div className="demo-hints">
            <h3>Suggested prompt</h3>
            <ol>
              <li>
                On <b>Web Chat</b>: “Suggest outfits for a beach vacation under 3000”
              </li>
              <li>
                Switch to <b>Kiosk</b>: “Check availability for the first one”
              </li>
              <li>
                Still Kiosk: “Reserve it in store”
              </li>
              <li>
                Switch to <b>WhatsApp</b>: “Proceed to payment”
              </li>
            </ol>
          </div>
        </section>

        <section className="chat-panel">
          <div className="chat-window">
            {messages.length === 0 && (
              <div className="empty-state">
                Start the conversation by sending a message on any channel.
              </div>
            )}
            {messages.map((msg) => (
              <div
                key={msg.id}
                className={`chat-row ${msg.role === "user" ? "user" : "agent"}`}
              >
                <div className="chat-meta">
                  <span className="chat-role">
                    {msg.role === "user" ? "You" : "Sales Agent"}
                  </span>
                  <span className="chat-channel">{CHANNEL_LABELS[msg.channel]}</span>
                </div>
                <div className="chat-bubble">{msg.text}</div>
              </div>
            ))}
          </div>

          {error && <div className="error-banner">{error}</div>}

          <div className="chat-input-row">
            <input
              type="text"
              placeholder="Type your message…"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
            />
            <button onClick={handleSend} disabled={loading}>
              {loading ? "Sending…" : "Send"}
            </button>
          </div>
        </section>
      </main>
    </div>
  );
}

export default App;
