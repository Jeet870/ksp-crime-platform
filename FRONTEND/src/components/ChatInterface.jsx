import { useState } from "react";
import { askQuestion } from "../utils/api";

export default function ChatInterface({ auth }) {
  const [sessionId] = useState(() => crypto.randomUUID());
  const [messages, setMessages] = useState([
    {
      id: 1, role: "agent",
      text: `Namaskara ${auth.name}! I am the KSP Intelligence Assistant. How can I help you today?`,
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    },
  ]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSend = async () => {
    if (!input.trim()) return;
    const userMsg = {
      id: Date.now(), role: "user", text: input.trim(),
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
    };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    try {
      const data = await askQuestion(userMsg.text, sessionId, auth.token);
const replyText = data.answer || data.reply || data.message || data.text || "No response received.";
setMessages((prev) => [...prev, {
  id: Date.now()+1, role: "agent", text: replyText,
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      }]);
    } catch (e) {
      setMessages((prev) => [...prev, {
        id: Date.now()+1, role: "agent", text: `⚠️ ${e.message}`, time: "",
      }]);
    } finally { setLoading(false); }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) { e.preventDefault(); handleSend(); }
  };

  return (
    <div className="chat-container">
      <div className="chat-header">
        <div className="chat-avatar">KS</div>
        <div>
          <div className="chat-name">KSP Intelligence Assistant</div>
          <div className="chat-status">● Online · Secure Channel</div>
        </div>
      </div>

      <div className="chat-messages">
        {messages.map((msg) => (
          <div key={msg.id} className={`msg-row ${msg.role}`}>
            <div className={`msg-bubble ${msg.role}`}>
              <div>{msg.text}</div>
              {msg.time && <div className="msg-time">{msg.time}</div>}
            </div>
          </div>
        ))}
        {loading && (
          <div className="msg-row agent">
            <div className="msg-bubble agent" style={{color:'var(--text-muted)'}}>
              Analysing...
            </div>
          </div>
        )}
      </div>

      <div className="chat-input-area">
        <div className="chat-input-row">
          <button className="mic-btn" aria-label="Voice input">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.8}>
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 1a3 3 0 0 1 3 3v7a3 3 0 0 1-6 0V4a3 3 0 0 1 3-3z"/>
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 10a7 7 0 0 1-14 0M12 19v4M8 23h8"/>
            </svg>
          </button>
          <input
            className="chat-input"
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask about cases, FIRs, suspects..."
          />
          <button className="send-btn" onClick={handleSend} disabled={!input.trim() || loading}>
            Send
          </button>
        </div>
        <div className="session-id">Session: {sessionId.slice(0,8)} · Secure</div>
      </div>
    </div>
  );
}
