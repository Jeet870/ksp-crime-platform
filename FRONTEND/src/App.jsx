import { useState } from "react";
import LoginPage from "./components/LoginPage";
import ChatPage from "./components/ChatPage";
import Dashboard from "./components/Dashboard";

function App() {
  const [token, setToken] = useState(null);
  const [role, setRole] = useState(null);
  const [name, setName] = useState(null);
  const [page, setPage] = useState("chat");

  const handleLogin = (data) => {
    setToken(data.token);
    setRole(data.role);
    setName(data.name);
  };

  const handleLogout = () => {
    setToken(null);
    setRole(null);
    setName(null);
    setPage("chat");
  };

  if (!token) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <div className="flex flex-col h-screen">
      {/* Top Nav Bar */}
      <div className="bg-blue-700 text-white px-6 py-3 flex items-center justify-between">
        <div className="flex items-center gap-4">
          <span className="font-bold text-lg">KSP Platform</span>
          <button
            onClick={() => setPage("chat")}
            className={`text-sm px-3 py-1 rounded-lg transition ${page === "chat" ? "bg-white text-blue-700 font-semibold" : "hover:bg-blue-600"}`}
          >
            Chat
          </button>
          <button
            onClick={() => setPage("dashboard")}
            className={`text-sm px-3 py-1 rounded-lg transition ${page === "dashboard" ? "bg-white text-blue-700 font-semibold" : "hover:bg-blue-600"}`}
          >
            Dashboard
          </button>
        </div>
        <div className="flex items-center gap-3">
          <span className="text-sm opacity-80">{name} — <span className="font-semibold">{role}</span></span>
          <button
            onClick={handleLogout}
            className="text-sm bg-red-500 hover:bg-red-600 px-3 py-1 rounded-lg transition"
          >
            Logout
          </button>
        </div>
      </div>

      {/* Page Content */}
      <div className="flex-1 overflow-hidden">
        {page === "chat" ? (
          <ChatPage token={token} role={role} />
        ) : (
          <Dashboard role={role} name={name} />
        )}
      </div>
    </div>
  );
}

export default App;
