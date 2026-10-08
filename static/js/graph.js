/**
 * FinGraph-AI Cinematic Interactive Simulation Graph (Crypto Dashboard Edition)
 * Inspired by Emote Agency's Crypto Payments Dashboard Dribbble shot.
 */

let cy = null;
let graphDataCache = null;

// Particle Simulation State
let particleCanvas = null;
let particleCtx = null;
let particleList = [];
let isSimulationRunning = true;
let simulationSpeed = 1;
let animationFrameId = null;
let lastFrameTime = performance.now();
let fpsSmoothed = 60;

async function initGraphVisualization() {
  const container = document.getElementById("cy-container");
  if (!container) return;

  await loadAndRenderGraph();
}

async function loadAndRenderGraph() {
  try {
    const res = await fetch("/api/graph/data");
    if (!res.ok) throw new Error("Failed to load graph data");
    const data = await res.json();
    graphDataCache = data;

    updateGraphStats(data.stats);
    renderCytoscape(data);
    initParticleSimulation();
  } catch (err) {
    console.error("Error loading graph:", err);
  }
}

function updateGraphStats(stats) {
  if (!stats) return;
  const nodesEl = document.getElementById("stat-total-nodes");
  const edgesEl = document.getElementById("stat-total-edges");
  const ringsEl = document.getElementById("stat-red-rings");
  const riskEl = document.getElementById("stat-risk-clusters");

  if (nodesEl) nodesEl.innerText = stats.total_nodes || 0;
  if (edgesEl) edgesEl.innerText = stats.total_edges || 0;
  if (ringsEl) ringsEl.innerText = stats.anomalous_clusters_count || 0;
  if (riskEl) riskEl.innerText = `${stats.smurfing_clusters || 0} Smurf / ${stats.syndicate_clusters || 0} Syndicate`;
}

function renderCytoscape(data) {
  const container = document.getElementById("cy-container");
  if (!container) return;

  if (cy) {
    cy.destroy();
  }

  cy = cytoscape({
    container: container,
    elements: {
      nodes: data.nodes,
      edges: data.edges
    },
    style: [
      // Base Node Style - Clean Light Minimalist Banking Node
      {
        selector: "node",
        style: {
          "label": "data(label)",
          "color": "#0F172A",
          "font-family": "'Inter', 'Plus Jakarta Sans', sans-serif",
          "font-size": "9px",
          "font-weight": "600",
          "text-valign": "bottom",
          "text-margin-y": 7,
          "text-background-color": "rgba(255, 255, 255, 0.95)",
          "text-background-opacity": 0.95,
          "text-background-padding": "3px",
          "text-background-shape": "roundrectangle",
          "width": 30,
          "height": 30,
          "background-color": "#FFFFFF",
          "border-width": 2,
          "border-color": "#CBD5E1",
          "transition-property": "border-width, border-color, background-color, transform, shadow-blur",
          "transition-duration": "0.2s"
        }
      },

      // Customer Nodes (Light Blue Hexagon)
      {
        selector: "node[type = 'customer']",
        style: {
          "shape": "hexagon",
          "background-color": "#EFF6FF",
          "border-color": "#3B82F6",
          "border-width": 2.5
        }
      },

      // Account Nodes (Light Emerald Circle)
      {
        selector: "node[type = 'account']",
        style: {
          "shape": "ellipse",
          "background-color": "#ECFDF5",
          "border-color": "#10B981",
          "border-width": 2.5
        }
      },

      // Device Nodes (Light Amber Rounded Rectangle)
      {
        selector: "node[type = 'device']",
        style: {
          "shape": "round-rectangle",
          "background-color": "#FFFBEB",
          "border-color": "#F59E0B",
          "border-width": 2.5,
          "width": 32,
          "height": 26
        }
      },

      // Merchant Nodes (Light Indigo Diamond)
      {
        selector: "node[type = 'merchant']",
        style: {
          "shape": "diamond",
          "background-color": "#EEF2FF",
          "border-color": "#6366F1",
          "border-width": 2.5,
          "width": 34,
          "height": 34
        }
      },

      // Location Nodes (Light Slate Star)
      {
        selector: "node[type = 'location']",
        style: {
          "shape": "star",
          "background-color": "#F8FAFC",
          "border-color": "#64748B",
          "border-width": 2.5,
          "width": 26,
          "height": 26
        }
      },

      // =========================================================
      // CRISP RED RINGS AROUND ANOMALIES (LIGHT MODE)
      // =========================================================
      {
        selector: "node[?is_anomalous]",
        style: {
          "border-color": "#EF4444",
          "border-width": 3.5,
          "border-style": "solid",
          "background-color": "#FEF2F2",
          "color": "#991B1B",
          "text-background-color": "rgba(254, 242, 242, 0.95)",
          "shadow-blur": 14,
          "shadow-color": "#EF4444",
          "shadow-opacity": 0.55,
          "width": 34,
          "height": 34
        }
      },

      // Hover on Nodes
      {
        selector: "node:hover",
        style: {
          "border-width": 4,
          "cursor": "pointer",
          "shadow-blur": 16,
          "shadow-color": "#3B82F6",
          "shadow-opacity": 0.5
        }
      },

      // Base Edges - Clean subtle slate lines
      {
        selector: "edge",
        style: {
          "width": 1.4,
          "line-color": "#CBD5E1",
          "target-arrow-color": "#CBD5E1",
          "target-arrow-shape": "triangle",
          "curve-style": "bezier",
          "opacity": 0.65,
          "transition-property": "width, opacity, line-color",
          "transition-duration": "0.15s"
        }
      },

      // Transfers (Royal Blue Route)
      {
        selector: "edge[type = 'TRANSFERRED_TO']",
        style: {
          "line-color": "#2563EB",
          "target-arrow-color": "#2563EB",
          "opacity": 0.8
        }
      },

      // Payments & Purchases (Emerald Route)
      {
        selector: "edge[type = 'PAID_TO'], edge[type = 'PURCHASED_FROM']",
        style: {
          "line-color": "#10B981",
          "target-arrow-color": "#10B981",
          "opacity": 0.8
        }
      },

      // Device & Location links (Dashed subtle slate)
      {
        selector: "edge[type = 'LOGGED_IN_FROM'], edge[type = 'LOCATED_AT']",
        style: {
          "line-style": "dashed",
          "line-color": "#94A3B8",
          "target-arrow-shape": "none",
          "width": 1.0,
          "opacity": 0.45
        }
      },

      // Anomalous Red Ring Edges (Crisp Crimson)
      {
        selector: "edge[?is_anomalous]",
        style: {
          "line-color": "#EF4444",
          "target-arrow-color": "#EF4444",
          "width": 2.6,
          "opacity": 0.95
        }
      },

      // Clean Edge Label only on hover/selected
      {
        selector: "edge:hover, edge:selected",
        style: {
          "width": 3.5,
          "opacity": 1.0,
          "label": "data(label)",
          "color": "#0F172A",
          "font-size": "9px",
          "font-family": "'JetBrains Mono', monospace",
          "font-weight": "bold",
          "text-background-color": "rgba(255, 255, 255, 0.95)",
          "text-background-opacity": 0.95,
          "text-background-padding": "3px",
          "text-background-shape": "roundrectangle"
        }
      }
    ],

    layout: getSmartLayoutConfig()
  });

  attachCytoscapeInteractions();
}

function getSmartLayoutConfig() {
  return {
    name: "cose",
    animate: true,
    animationDuration: 750,
    randomize: false,
    fit: true,
    padding: 60,
    nodeRepulsion: 1500000,
    idealEdgeLength: 160,
    edgeElasticity: 45,
    nestingFactor: 0.1,
    gravity: 0.15,
    numIter: 1000,
    nodeOverlap: 0,
    componentSpacing: 180
  };
}

function attachCytoscapeInteractions() {
  if (!cy) return;

  cy.on("tap", "node", function (evt) {
    const node = evt.target;
    const isAnomalous = node.data("is_anomalous");
    const clusterId = node.data("cluster_id");

    if (isAnomalous && clusterId) {
      openShapModal(clusterId);
    }
    
    showNodeInspection(node.data());
    highlightNeighborhood(node);
  });

  cy.on("tap", "edge", function (evt) {
    const edge = evt.target;
    showEdgeInspection(edge.data());
  });

  cy.on("tap", function (evt) {
    if (evt.target === cy) {
      clearHighlights();
    }
  });

  cy.on("mouseover", "node", function (evt) {
    const node = evt.target;
    node.connectedEdges().animate({
      style: { "width": 3.5, "opacity": 1.0 }
    }, { duration: 120 });
  });

  cy.on("mouseout", "node", function (evt) {
    const node = evt.target;
    node.connectedEdges().animate({
      style: { "width": node.data("is_anomalous") ? 2.6 : 1.4, "opacity": 0.6 }
    }, { duration: 120 });
  });
}

function highlightNeighborhood(node) {
  if (!cy) return;
  cy.elements().removeClass("faded");
  const neighborhood = node.closedNeighborhood();
  cy.elements().not(neighborhood).addClass("faded");
}

function clearHighlights() {
  if (!cy) return;
  cy.elements().removeClass("faded");
}

function showNodeInspection(data) {
  const infoEl = document.getElementById("node-inspection-card");
  if (!infoEl) return;

  infoEl.classList.remove("hidden");
  document.getElementById("inspect-node-id").innerText = data.id;
  document.getElementById("inspect-node-type").innerText = data.type.toUpperCase();
  document.getElementById("inspect-node-label").innerText = data.label;

  const riskEl = document.getElementById("inspect-node-risk");
  riskEl.innerText = data.risk_level || "LOW";
  riskEl.className = data.is_anomalous ? "font-bold text-red-600" : "font-bold text-emerald-600";

  const detailsEl = document.getElementById("inspect-node-details");
  let detailsText = "";
  if (data.balance !== null && data.balance !== undefined) {
    detailsText += `Balance: $${Number(data.balance).toLocaleString()}\n`;
  }
  if (data.metadata) {
    for (const [k, v] of Object.entries(data.metadata)) {
      if (v) detailsText += `${k}: ${v}\n`;
    }
  }
  if (data.is_anomalous) {
    detailsText += `\n⚠️ FLAG: Cluster ${data.cluster_id}\nClick node to open SHAP Feature Attributions.`;
  }
  detailsEl.innerText = detailsText || "Standard behavioral pattern";
}

function showEdgeInspection(data) {
  const infoEl = document.getElementById("node-inspection-card");
  if (!infoEl) return;

  infoEl.classList.remove("hidden");
  document.getElementById("inspect-node-id").innerText = data.id;
  document.getElementById("inspect-node-type").innerText = data.type;
  document.getElementById("inspect-node-label").innerText = `${data.source} → ${data.target}`;

  const riskEl = document.getElementById("inspect-node-risk");
  riskEl.innerText = data.is_anomalous ? "SUSPICIOUS" : "NORMAL";
  riskEl.className = data.is_anomalous ? "font-bold text-red-600" : "font-bold text-emerald-600";

  let detailsText = `Transaction Type: ${data.type}\n`;
  if (data.amount) detailsText += `Amount: $${Number(data.amount).toLocaleString()}\n`;
  if (data.category) detailsText += `Category: ${data.category}\n`;
  if (data.frequency) detailsText += `Frequency: ${data.frequency}\n`;

  document.getElementById("inspect-node-details").innerText = detailsText;
}

function closeNodeInspection() {
  const infoEl = document.getElementById("node-inspection-card");
  if (!infoEl) return;
  infoEl.classList.add("hidden");
  clearHighlights();
}

function setGraphLayout(layoutName) {
  if (!cy) return;

  if (layoutName === "smart" || layoutName === "cose") {
    cy.layout(getSmartLayoutConfig()).run();
  } else if (layoutName === "breadthfirst") {
    cy.layout({
      name: "breadthfirst",
      directed: true,
      spacingFactor: 1.5,
      animate: true,
      fit: true,
      padding: 50
    }).run();
  } else if (layoutName === "circle") {
    cy.layout({
      name: "circle",
      spacingFactor: 1.6,
      animate: true,
      fit: true,
      padding: 50
    }).run();
  } else if (layoutName === "concentric") {
    cy.layout({
      name: "concentric",
      spacingFactor: 1.8,
      minNodeSpacing: 60,
      animate: true,
      fit: true,
      padding: 50
    }).run();
  }
}

function untangleGraph() {
  if (!cy) return;
  cy.layout(getSmartLayoutConfig()).run();
}

function filterGraphNodes(filterType) {
  if (!cy) return;
  cy.nodes().show();
  cy.edges().show();

  if (filterType === "all") return;

  if (filterType === "red_rings") {
    cy.nodes().forEach(n => {
      if (!n.data("is_anomalous")) {
        n.hide();
      }
    });
  } else {
    cy.nodes().forEach(n => {
      if (n.data("type") !== filterType) {
        n.hide();
      }
    });
  }
}

function zoomFitGraph() {
  if (cy) cy.fit(undefined, 50);
}

function zoomInGraph() {
  if (cy) cy.zoom(cy.zoom() * 1.3);
}

function zoomOutGraph() {
  if (cy) cy.zoom(cy.zoom() * 0.75);
}

// =====================================================================
// LIVE ANIMATED GLOWING PARTICLE SIMULATION (CYBER TOKENS)
// =====================================================================

function initParticleSimulation() {
  particleCanvas = document.getElementById("particle-canvas");
  if (!particleCanvas || !cy) return;

  particleCtx = particleCanvas.getContext("2d");

  resizeParticleCanvas();
  window.addEventListener("resize", resizeParticleCanvas);

  createParticlesFromEdges();

  if (animationFrameId) {
    cancelAnimationFrame(animationFrameId);
  }

  lastFrameTime = performance.now();
  renderParticleLoop();
}

function resizeParticleCanvas() {
  if (!particleCanvas) return;
  const rect = particleCanvas.parentElement.getBoundingClientRect();
  particleCanvas.width = rect.width;
  particleCanvas.height = rect.height;
}

function createParticlesFromEdges() {
  if (!cy) return;
  particleList = [];

  const edges = cy.edges();
  edges.forEach((edge) => {
    const isAnomalous = edge.data("is_anomalous");
    const edgeType = edge.data("type");
    
    if (edgeType === "OWNS") return;

    const count = isAnomalous ? 3 : 2;
    for (let i = 0; i < count; i++) {
      particleList.push({
        edge: edge,
        source: edge.source(),
        target: edge.target(),
        progress: (i / count) + (Math.random() * 0.2),
        speed: (0.007 + Math.random() * 0.006) * (isAnomalous ? 1.5 : 1.0),
        isAnomalous: isAnomalous,
        color: isAnomalous ? "#EF4444" : (edgeType === "TRANSFERRED_TO" ? "#2563EB" : "#10B981"),
        size: isAnomalous ? 3.5 : 2.8
      });
    }
  });
}

function renderParticleLoop() {
  const now = performance.now();
  const delta = now - lastFrameTime;
  lastFrameTime = now;

  if (delta > 0) {
    const currentFps = 1000 / delta;
    fpsSmoothed = (fpsSmoothed * 0.9) + (currentFps * 0.1);
    const fpsCounter = document.getElementById("sim-fps-counter");
    if (fpsCounter && Math.random() < 0.1) {
      fpsCounter.innerText = `${Math.round(fpsSmoothed)} FPS`;
    }
  }

  if (particleCtx && particleCanvas) {
    particleCtx.clearRect(0, 0, particleCanvas.width, particleCanvas.height);

    if (isSimulationRunning && cy) {
      const pulsePhase = Math.sin(now / 220);
      const blurAmount = 14 + pulsePhase * 6;
      cy.nodes("[?is_anomalous]").style("shadow-blur", blurAmount);

      particleList.forEach(p => {
        p.progress += p.speed * simulationSpeed;
        if (p.progress > 1.0) {
          p.progress = 0.0;
        }

        if (!p.source.visible() || !p.target.visible()) return;

        const p1 = p.source.renderedPosition();
        const p2 = p.target.renderedPosition();

        if (!p1 || !p2) return;

        const curX = p1.x + (p2.x - p1.x) * p.progress;
        const curY = p1.y + (p2.y - p1.y) * p.progress;

        const haloRadius = p.size * 2.8;
        const grad = particleCtx.createRadialGradient(curX, curY, 0, curX, curY, haloRadius);
        grad.addColorStop(0, p.color);
        grad.addColorStop(0.35, p.color);
        grad.addColorStop(1, "transparent");

        particleCtx.fillStyle = grad;
        particleCtx.beginPath();
        particleCtx.arc(curX, curY, haloRadius, 0, Math.PI * 2);
        particleCtx.fill();

        particleCtx.fillStyle = "#FFFFFF";
        particleCtx.beginPath();
        particleCtx.arc(curX, curY, p.size * 0.65, 0, Math.PI * 2);
        particleCtx.fill();
      });
    }
  }

  animationFrameId = requestAnimationFrame(renderParticleLoop);
}

// =====================================================================
// VIDEO-PLAYER CONTROL DOCK HANDLERS
// =====================================================================

function toggleSimulationPlayback() {
  isSimulationRunning = !isSimulationRunning;
  const btn = document.getElementById("sim-play-btn");
  const icon = document.getElementById("sim-play-icon");

  if (isSimulationRunning) {
    icon.className = "fas fa-pause text-xs";
    btn.className = "w-7 h-7 rounded-full bg-blue-600 hover:bg-blue-700 text-white flex items-center justify-center transition-all shadow-sm";
  } else {
    icon.className = "fas fa-play text-xs pl-0.5";
    btn.className = "w-7 h-7 rounded-full bg-slate-200 hover:bg-slate-300 text-slate-700 flex items-center justify-center transition-all shadow-sm";
  }
}

function setSimulationSpeed(speed) {
  simulationSpeed = speed;

  [1, 2, 5].forEach(s => {
    const btn = document.getElementById(`sim-speed-${s}`);
    if (btn) {
      if (s === speed) {
        btn.className = "px-2.5 py-0.5 rounded-full bg-blue-600 text-white font-medium transition-all";
      } else {
        btn.className = "px-2.5 py-0.5 rounded-full text-slate-600 hover:text-slate-900 transition-all";
      }
    }
  });
}
