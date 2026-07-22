const ROLE_ITEMS = {
  Constable: [
    { label: "My Cases",  icon: "📁", desc: "View your assigned cases" },
    { label: "Search",    icon: "🔍", desc: "Search records and FIRs" },
  ],
  IO: [
    { label: "My Cases",  icon: "📁", desc: "View your assigned cases" },
    { label: "Search",    icon: "🔍", desc: "Search records and FIRs" },
  ],
  SP: [
    { label: "District Overview", icon: "🗺️", desc: "District-wide activity" },
    { label: "Analytics",         icon: "📊", desc: "Crime trends and stats" },
    { label: "Forecast",          icon: "🔮", desc: "Predictive crime data" },
    { label: "Crime Graph",       icon: "🕸️", desc: "Network visualization" },
    { label: "Map",               icon: "🗾", desc: "Geographic crime map" },
    { label: "Search",            icon: "🔍", desc: "Search all records" },
  ],
  Analyst: [
    { label: "Analytics", icon: "📊", desc: "Crime trends and stats" },
    { label: "Forecast",  icon: "🔮", desc: "Predictive crime data" },
    { label: "Search",    icon: "🔍", desc: "Search records" },
  ],
  Director: [
    { label: "District Overview", icon: "🗺️", desc: "District-wide activity" },
    { label: "Analytics",         icon: "📊", desc: "Crime trends and stats" },
    { label: "Forecast",          icon: "🔮", desc: "Predictive data" },
    { label: "Crime Graph",       icon: "🕸️", desc: "Network visualization" },
    { label: "Map",               icon: "🗾", desc: "Geographic map" },
    { label: "Search",            icon: "🔍", desc: "Search all records" },
  ],
};

const STATS = [
  { label: "Active Cases",  value: "142", accent: false },
  { label: "Solved Today",  value: "08",  accent: true  },
  { label: "Pending FIRs",  value: "23",  accent: false },
  { label: "Active Alerts", value: "05",  accent: false },
];

export default function Dashboard({ role, name }) {
  const items = ROLE_ITEMS[role] || ROLE_ITEMS["Constable"];

  return (
    <div>
      <div className="page-header">
        <div className="page-eyebrow">Karnataka State Police · Dashboard</div>
        <div className="page-title">Welcome, {name}</div>
        <div className="page-subtitle">
          {role} · {new Date().toLocaleDateString('en-IN', {
            weekday: 'long', day: 'numeric', month: 'long', year: 'numeric'
          })}
        </div>
      </div>

      <div className="stat-grid" style={{marginTop:'16px'}}>
        {STATS.map((s) => (
          <div className="stat-card" key={s.label}>
            <div className="stat-label">{s.label}</div>
            <div className={`stat-value${s.accent ? " stat-accent" : ""}`}>{s.value}</div>
          </div>
        ))}
      </div>

      <div style={{padding:'16px 24px 6px'}}>
        <div className="page-eyebrow">Quick Access</div>
      </div>

      <div className="card-grid">
        {items.map((item) => (
          <div className="card" key={item.label}>
            <div className="card-icon">{item.icon}</div>
            <div className="card-title">{item.label}</div>
            <div className="card-desc">{item.desc}</div>
            <div className="card-arrow">Open →</div>
          </div>
        ))}
      </div>
    </div>
  );
}
