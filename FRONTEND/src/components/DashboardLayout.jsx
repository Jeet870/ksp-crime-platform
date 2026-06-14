import { NavLink, Outlet } from "react-router-dom";

const ROLE_NAV = {
  Constable: [
    { label: "Chat", path: "/chat", icon: "💬" },
    { label: "My Cases", path: "/my-cases", icon: "📁" },
    { label: "Search", path: "/search", icon: "🔍" },
  ],
  SP: [
    { label: "Chat", path: "/chat", icon: "💬" },
    { label: "District Overview", path: "/district-overview", icon: "🗺️" },
    { label: "Analytics", path: "/analytics", icon: "📊" },
    { label: "Forecast", path: "/forecast", icon: "🔮" },
    { label: "Map", path: "/map", icon: "🗾" },
    { label: "Search", path: "/search", icon: "🔍" },
  ],
};

export default function DashboardLayout({ auth, onLogout }) {
  const navItems = ROLE_NAV[auth.role] || ROLE_NAV["Constable"];

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="w-56 bg-white border-r border-gray-200 flex flex-col">
        {/* Logo */}
        <div className="px-5 py-5 border-b border-gray-100">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
              <span className="text-white font-bold text-sm">KS</span>
            </div>
            <span className="font-bold text-gray-800">KSP Platform</span>
          </div>
          <div className="mt-3 text-xs text-gray-500">
            <p className="font-medium text-gray-700">{auth.name}</p>
            <p className="text-blue-600 font-semibold">{auth.role}</p>
          </div>
        </div>

        {/* Nav Items */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium transition-all ${
                  isActive
                    ? "bg-blue-50 text-blue-700"
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-800"
                }`
              }
            >
              <span>{item.icon}</span>
              <span>{item.label}</span>
            </NavLink>
          ))}
        </nav>

        {/* Logout */}
        <div className="px-3 py-4 border-t border-gray-100">
          <button
            onClick={onLogout}
            className="w-full flex items-center gap-3 px-3 py-2.5 rounded-xl text-sm font-medium text-red-500 hover:bg-red-50 transition-all"
          >
            <span>🚪</span>
            <span>Logout</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="flex-1 overflow-hidden">
        <Outlet />
      </div>
    </div>
  );
}
