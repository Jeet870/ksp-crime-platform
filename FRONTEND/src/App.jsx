import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import LoginPage from "./components/LoginPage";
import DashboardLayout from "./components/DashboardLayout";
import ChatInterface from "./components/ChatInterface";
import MyCases from "./components/pages/MyCases";
import Search from "./components/pages/Search";
import DistrictOverview from "./components/pages/DistrictOverview";
import Analytics from "./components/pages/Analytics";
import Forecast from "./components/pages/Forecast";
import MapView from "./components/pages/MapView";

function App() {
  const [auth, setAuth] = useState(null);
  // auth = { token, role, name, district }

  const handleLogin = (data) => {
    setAuth({
      token: data.token,
      role: data.role,
      name: data.name,
      district: data.district || "N/A",
    });
  };

  const handleLogout = () => setAuth(null);

  if (!auth) {
    return <LoginPage onLogin={handleLogin} />;
  }

  return (
    <BrowserRouter>
      <Routes>
        <Route
          path="/"
          element={<DashboardLayout auth={auth} onLogout={handleLogout} />}
        >
          <Route index element={<Navigate to="/chat" replace />} />
          <Route path="chat" element={<ChatInterface auth={auth} />} />
          <Route path="my-cases" element={<MyCases />} />
          <Route path="search" element={<Search />} />
          <Route path="district-overview" element={<DistrictOverview />} />
          <Route path="analytics" element={<Analytics />} />
          <Route path="forecast" element={<Forecast />} />
          <Route path="map" element={<MapView />} />
          <Route path="*" element={<Navigate to="/chat" replace />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

export default App;
