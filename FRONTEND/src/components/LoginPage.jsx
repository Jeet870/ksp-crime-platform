import { useState } from "react";
import { login } from "../utils/api";
import KSPLogo from "./KSPLogo";

export default function LoginPage({ onLogin }) {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleLogin = async () => {
    setError("");
    if (!username || !password) { setError("Please fill in all fields."); return; }
    setLoading(true);
    try {
      const data = await login(username, password);
      onLogin(data);
    } catch (e) {
      setError(e.message || "Cannot connect to server. Is FastAPI running?");
    } finally { setLoading(false); }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter") handleLogin();
  };

  return (
    <div className="login-page">
      <div className="login-grid-bg" />
      <div className="login-glow" />
      <div className="login-card">
        <div className="login-logo">
          <KSPLogo size={80} />
          <div className="login-org-name">Karnataka State Police</div>
          <div className="login-title">Intelligence Platform</div>
          <div className="login-sub">Secure Officer Access Portal · "ಸೇವೆಯೇ ಸಾಧನ"</div>
        </div>

        {error && <div className="error-box">⚠️ {error}</div>}

        <div className="form-group">
          <label className="form-label">Officer ID / Username</label>
          <input
            className="form-input"
            type="text"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="e.g. KSP-CON-001"
            autoCapitalize="none"
          />
        </div>

        <div className="form-group">
          <label className="form-label">Password</label>
          <input
            className="form-input"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Enter your password"
          />
        </div>

        <button className="login-btn" onClick={handleLogin} disabled={loading}>
          {loading ? "Verifying credentials..." : "🔐 Sign In to Platform"}
        </button>

        <div className="creds-box">
          <div className="creds-title">Test Credentials</div>
          <div>👮 <strong>KSP-CON-001</strong> / ksp1234 — Constable</div>
          <div style={{marginTop:'4px'}}>🕵️ <strong>KSP-IO-001</strong> / ksp1234 — IO</div>
          <div style={{marginTop:'4px'}}>🎖️ <strong>KSP-SP-001</strong> / ksp1234 — SP</div>
          <div style={{marginTop:'4px'}}>📊 <strong>KSP-ANA-001</strong> / ksp1234 — Analyst</div>
          <div style={{marginTop:'4px'}}>⭐ <strong>KSP-DIR-001</strong> / ksp1234 — Director</div>
        </div>
      </div>
    </div>
  );
}
