export default function Dashboard({ role, name }) {
  const constableNav = [
    { label: "My Cases", icon: "📁", desc: "View and manage your assigned cases" },
    { label: "Search", icon: "🔍", desc: "Search records and case files" },
  ];

  const spNav = [
    { label: "District Overview", icon: "🗺️", desc: "View district-wide activity and reports" },
    { label: "Analytics", icon: "📊", desc: "Crime trends, stats and analytics" },
    { label: "Search", icon: "🔍", desc: "Search records and case files" },
  ];

  const navItems = role === "SP" ? spNav : constableNav;

  return (
    <div className="h-full bg-gray-50 p-8 overflow-y-auto">
      {/* Welcome Header */}
      <div className="mb-8">
        <h1 className="text-2xl font-bold text-gray-800">Welcome, {name} 👋</h1>
        <p className="text-gray-500 mt-1">Role: <span className="font-semibold text-blue-600">{role}</span> — Select a section below to get started.</p>
      </div>

      {/* Nav Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
        {navItems.map((item) => (
          <div
            key={item.label}
            className="bg-white border border-gray-100 rounded-2xl p-6 shadow-sm hover:shadow-md hover:border-blue-200 transition-all cursor-pointer group"
          >
            <div className="text-3xl mb-3">{item.icon}</div>
            <h2 className="text-base font-semibold text-gray-800 group-hover:text-blue-600 transition-colors">{item.label}</h2>
            <p className="text-sm text-gray-500 mt-1">{item.desc}</p>
            <div className="mt-4 text-xs text-blue-500 font-medium opacity-0 group-hover:opacity-100 transition-opacity">
              Coming soon →
            </div>
          </div>
        ))}
      </div>

      {/* Role Info Box */}
      <div className="mt-8 bg-blue-50 border border-blue-100 rounded-2xl p-5">
        <p className="text-sm text-blue-700 font-medium">
          {role === "SP"
            ? "🎖️ You have SP-level access: District Overview, Analytics and Search are available to you."
            : "👮 You have Constable-level access: My Cases and Search are available to you."}
        </p>
      </div>
    </div>
  );
}
