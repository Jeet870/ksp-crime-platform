import { useEffect, useRef, useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import cytoscape from "cytoscape";

// ── Hardcoded test data (Day 15-16) ──────────────────────────────────────────
const TEST_NODES = [
  { data: { id: "a1", label: "Ravi Kumar",    type: "accused", district: "Bengaluru" } },
  { data: { id: "a2", label: "Suresh Naik",   type: "accused", district: "Mysuru"    } },
  { data: { id: "f1", label: "FIR-2024-001",  type: "FIR",     district: "Bengaluru" } },
  { data: { id: "v1", label: "KA-01-AB-1234", type: "vehicle", district: "Bengaluru" } },
  { data: { id: "a3", label: "Mohan Das",     type: "accused", district: "Hubli"     } },
];

const TEST_EDGES = [
  { data: { id: "e1", source: "a1", target: "f1", relationship: "co-accused"  } },
  { data: { id: "e2", source: "a2", target: "f1", relationship: "co-accused"  } },
  { data: { id: "e3", source: "a1", target: "v1", relationship: "financial"   } },
  { data: { id: "e4", source: "a2", target: "a3", relationship: "phone_calls" } },
];

// ── Node & Edge styles (Day 19-21) ───────────────────────────────────────────
const STYLESHEET = [
  {
    selector: "node",
    style: {
      label: "data(label)",
      "text-valign": "bottom",
      "text-halign": "center",
      "font-size": "11px",
      "text-margin-y": "6px",
      width: 45,
      height: 45,
      "border-width": 2,
      "border-color": "#fff",
      color: "#1f2937",
    },
  },
  // accused = red
  {
    selector: "node[type='accused']",
    style: { "background-color": "#ef4444" },
  },
  // FIR = orange
  {
    selector: "node[type='FIR']",
    style: {
      "background-color": "#f97316",
      shape: "rectangle",
      width: 60,
      height: 35,
      "font-size": "10px",
    },
  },
  // vehicle = blue
  {
    selector: "node[type='vehicle']",
    style: {
      "background-color": "#3b82f6",
      shape: "diamond",
    },
  },
  // phone calls = dashed grey
  {
    selector: "edge[relationship='phone_calls']",
    style: {
      "line-style": "dashed",
      "line-color": "#9ca3af",
      width: 2,
      "target-arrow-shape": "triangle",
      "target-arrow-color": "#9ca3af",
      "curve-style": "bezier",
      label: "call",
      "font-size": "9px",
      color: "#6b7280",
    },
  },
  // financial = green solid
  {
    selector: "edge[relationship='financial']",
    style: {
      "line-style": "solid",
      "line-color": "#22c55e",
      width: 2,
      "target-arrow-shape": "triangle",
      "target-arrow-color": "#22c55e",
      "curve-style": "bezier",
      label: "financial",
      "font-size": "9px",
      color: "#16a34a",
    },
  },
  // co-accused = grey solid
  {
    selector: "edge[relationship='co-accused']",
    style: {
      "line-style": "solid",
      "line-color": "#6b7280",
      width: 2,
      "target-arrow-shape": "triangle",
      "target-arrow-color": "#6b7280",
      "curve-style": "bezier",
      label: "co-accused",
      "font-size": "9px",
      color: "#4b5563",
    },
  },
  // selected node highlight
  {
    selector: "node:selected",
    style: {
      "border-color": "#6366f1",
      "border-width": 3,
    },
  },
];

// ── Legend data (Day 19-21) ───────────────────────────────────────────────────
const LEGEND = [
  { label: "Accused",    color: "#ef4444", shape: "circle"  },
  { label: "FIR",        color: "#f97316", shape: "square"  },
  { label: "Vehicle",    color: "#3b82f6", shape: "diamond" },
  { label: "Phone call", color: "#9ca3af", dash: true       },
  { label: "Financial",  color: "#22c55e", dash: false      },
  { label: "Co-accused", color: "#6b7280", dash: false      },
];

export default function CrimeNetworkGraph({ auth }) {
  const cyRef    = useRef(null);
  const [firId,  setFirId]  = useState("");
  const [elements, setElements] = useState([...TEST_NODES, ...TEST_EDGES]);
  const [loading,  setLoading]  = useState(false);
  const [error,    setError]    = useState("");
  const [tooltip,  setTooltip]  = useState(null); // { x, y, label, type, district }
  const [useTest,  setUseTest]  = useState(true);

  // ── Tooltip on node hover (Day 15-16) ──────────────────────────────────────
  useEffect(() => {
    const cy = cyRef.current;
    if (!cy) return;

    cy.on("mouseover", "node", (e) => {
      const node     = e.target;
      const pos      = node.renderedPosition();
      const container = cy.container().getBoundingClientRect();
      setTooltip({
        x:        container.left + pos.x + 10,
        y:        container.top  + pos.y - 40,
        label:    node.data("label"),
        type:     node.data("type"),
        district: node.data("district"),
      });
    });

    cy.on("mouseout", "node", () => setTooltip(null));

    return () => {
      cy.removeListener("mouseover");
      cy.removeListener("mouseout");
    };
  }, [elements]);

  // ── Fetch live data from API (Day 17-18) ───────────────────────────────────
  const fetchGraph = async () => {
    if (!firId.trim()) {
      setError("Please enter a FIR ID.");
      return;
    }
    setLoading(true);
    setError("");
    setTooltip(null);

    try {
      const res = await fetch(
        `http://localhost:8000/graph?fir_id=${encodeURIComponent(firId)}`,
        {
          headers: { Authorization: `Bearer ${auth?.token || ""}` },
        }
      );

      if (!res.ok) throw new Error(`Server error: ${res.status}`);

      const data = await res.json();

      if (!data.nodes || data.nodes.length === 0) {
        setError("No graph data found for this FIR ID.");
        setElements([]);
        setUseTest(false);
        return;
      }

      // Map API response to Cytoscape elements
      const nodes = data.nodes.map((n) => ({
        data: {
          id:       n.id,
          label:    n.label   || n.id,
          type:     n.type    || "accused",
          district: n.district || "N/A",
        },
      }));

      const edges = (data.edges || []).map((e, i) => ({
        data: {
          id:           `e${i}`,
          source:       e.source,
          target:       e.target,
          relationship: e.relationship || "co-accused",
        },
      }));

      setElements([...nodes, ...edges]);
      setUseTest(false);
    } catch (err) {
      setError(`⚠️ ${err.message}`);
    } finally {
      setLoading(false);
    }
  };

  // ── Export as PNG (Day 19-21) ───────────────────────────────────────────────
  const exportPNG = () => {
    const cy = cyRef.current;
    if (!cy) return;
    const png = cy.png({ scale: 2, full: true, bg: "#ffffff" });
    const a   = document.createElement("a");
    a.href     = png;
    a.download = `crime-network-${firId || "test"}.png`;
    a.click();
  };

  // ── Reset to test data ──────────────────────────────────────────────────────
  const resetToTest = () => {
    setElements([...TEST_NODES, ...TEST_EDGES]);
    setUseTest(true);
    setFirId("");
    setError("");
  };

  return (
    <div className="flex flex-col h-full bg-gray-50">

      {/* ── Top Bar ── */}
      <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center gap-3 flex-wrap shadow-sm">
        <h1 className="text-base font-bold text-gray-800 mr-2">🕸️ Crime Network Graph</h1>

        <input
          type="text"
          value={firId}
          onChange={(e) => setFirId(e.target.value)}
          onKeyDown={(e) => e.key === "Enter" && fetchGraph()}
          placeholder="Enter FIR ID e.g. FIR-2024-001"
          className="flex-1 min-w-48 px-4 py-2 rounded-xl border border-gray-200 text-sm focus:outline-none focus:ring-2 focus:ring-blue-500"
        />

        <button
          onClick={fetchGraph}
          disabled={loading}
          className="bg-blue-600 hover:bg-blue-700 disabled:opacity-50 text-white px-4 py-2 rounded-xl text-sm font-medium transition"
        >
          {loading ? "Loading..." : "Load Graph"}
        </button>

        <button
          onClick={resetToTest}
          className="bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-xl text-sm font-medium transition"
        >
          Reset Test Data
        </button>

        <button
          onClick={exportPNG}
          className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-xl text-sm font-medium transition"
        >
          Export PNG
        </button>
      </div>

      {/* ── Error Message ── */}
      {error && (
        <div className="mx-6 mt-3 bg-red-50 border border-red-200 text-red-600 text-sm px-4 py-2 rounded-xl">
          {error}
        </div>
      )}

      {/* ── Test data badge ── */}
      {useTest && (
        <div className="mx-6 mt-3 bg-yellow-50 border border-yellow-200 text-yellow-700 text-xs px-4 py-2 rounded-xl">
          Showing hardcoded test data. Enter a FIR ID above to load live data.
        </div>
      )}

      {/* ── Graph Area ── */}
      <div className="flex-1 relative overflow-hidden m-4 bg-white rounded-2xl border border-gray-100 shadow-sm">

        {/* Loading Spinner */}
        {loading && (
          <div className="absolute inset-0 bg-white bg-opacity-80 flex items-center justify-center z-10 rounded-2xl">
            <div className="flex flex-col items-center gap-3">
              <div className="w-10 h-10 border-4 border-blue-500 border-t-transparent rounded-full animate-spin" />
              <p className="text-sm text-gray-500 font-medium">Loading graph...</p>
            </div>
          </div>
        )}

        {/* Empty State */}
        {!loading && elements.length === 0 && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center text-gray-400">
              <p className="text-4xl mb-3">🔍</p>
              <p className="font-medium">No graph data found</p>
              <p className="text-sm mt-1">Try a different FIR ID or reset to test data</p>
            </div>
          </div>
        )}

        {/* Cytoscape Graph */}
        {elements.length > 0 && (
          <CytoscapeComponent
            elements={elements}
            stylesheet={STYLESHEET}
            layout={{ name: "cose", animate: true, padding: 40 }}
            style={{ width: "100%", height: "100%" }}
            cy={(cy) => { cyRef.current = cy; }}
            userZoomingEnabled={true}
            userPanningEnabled={true}
          />
        )}

        {/* ── Color Legend (bottom-left) ── */}
        <div className="absolute bottom-4 left-4 bg-white border border-gray-100 rounded-xl shadow-sm px-4 py-3 text-xs space-y-1.5">
          <p className="font-semibold text-gray-700 mb-2">Legend</p>
          {LEGEND.map((item) => (
            <div key={item.label} className="flex items-center gap-2">
              {item.shape ? (
                <div
                  className="w-3 h-3 rounded-sm flex-shrink-0"
                  style={{
                    backgroundColor: item.color,
                    borderRadius: item.shape === "circle" ? "50%" : item.shape === "diamond" ? "2px" : "2px",
                    transform: item.shape === "diamond" ? "rotate(45deg)" : "none",
                  }}
                />
              ) : (
                <div
                  className="w-5 h-0.5 flex-shrink-0"
                  style={{
                    backgroundColor: item.color,
                    borderTop: item.dash ? `2px dashed ${item.color}` : `2px solid ${item.color}`,
                    background: "none",
                  }}
                />
              )}
              <span className="text-gray-600">{item.label}</span>
            </div>
          ))}
        </div>

        {/* ── Tooltip ── */}
        {tooltip && (
          <div
            className="fixed z-50 bg-gray-900 text-white text-xs px-3 py-2 rounded-lg shadow-lg pointer-events-none"
            style={{ left: tooltip.x, top: tooltip.y }}
          >
            <p className="font-semibold">{tooltip.label}</p>
            <p className="text-gray-300">Type: {tooltip.type}</p>
            <p className="text-gray-300">District: {tooltip.district}</p>
          </div>
        )}
      </div>
    </div>
  );
}
