const BASE_URL = "https://ksp-datathon-50043488989.development.catalystappsail.in";

export async function login(username, password, role) {
  const res = await fetch(`${BASE_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ username, password, role }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Login failed");
  return data;
}

export async function askQuestion(question, sessionId, token) {
  const res = await fetch(`${BASE_URL}/ask`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${token}`,
    },
    body: JSON.stringify({ message: message, session_id: sessionId, token }),
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Request failed");
  return data;
}
const data = await askQuestion(userMsg.text, sessionId, auth.token);
console.log("API response:", data); // ← add this
const replyText = data.answer || data.reply || data.message || data.text || "No response received.";