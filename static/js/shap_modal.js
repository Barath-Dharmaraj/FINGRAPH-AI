/**
 * FinGraph-AI SHAP Explainability Command Dialog Controller (Crypto Dashboard Edition)
 * Inspired by Emote Agency's Crypto Payments Dashboard Dribbble shot.
 */

let shapChartInstance = null;

async function openShapModal(clusterId) {
  const modal = document.getElementById("shap-modal");
  if (!modal) return;

  modal.classList.remove("hidden");
  document.getElementById("modal-cluster-id").innerText = clusterId;
  document.getElementById("modal-human-narrative").innerHTML = `
    <div class="flex items-center space-x-2 text-blue-600 text-xs py-3">
      <i class="fas fa-spinner fa-spin"></i>
      <span>Executing SHAP TreeExplainer feature attribution for ${clusterId}...</span>
    </div>
  `;

  try {
    const res = await fetch(`/api/anomalies/${clusterId}/explain`);
    if (!res.ok) {
      throw new Error(`Failed to load explanation for ${clusterId}`);
    }
    const data = await res.json();
    renderShapModalContent(data);
  } catch (err) {
    document.getElementById("modal-human-narrative").innerHTML = `
      <div class="p-3 bg-red-50 border border-red-200 rounded-xl text-red-700 text-xs">
        <i class="fas fa-triangle-exclamation mr-1.5"></i> Error fetching SHAP data: ${err.message}
      </div>
    `;
  }
}

function closeShapModal() {
  const modal = document.getElementById("shap-modal");
  if (modal) {
    modal.classList.add("hidden");
  }
  if (shapChartInstance) {
    shapChartInstance.destroy();
    shapChartInstance = null;
  }
}

function renderShapModalContent(data) {
  document.getElementById("modal-cluster-id").innerText = data.cluster_id;
  
  // Anomaly Badge
  const badgeEl = document.getElementById("modal-anomaly-badge");
  badgeEl.innerText = `${data.anomaly_type.toUpperCase()} (${(data.confidence_score * 100).toFixed(1)}% CONF)`;

  // Base & Prediction stats
  document.getElementById("modal-base-val").innerText = (data.base_value || 0).toFixed(3);
  document.getElementById("modal-pred-val").innerText = `${(data.confidence_score * 100).toFixed(1)}%`;
  document.getElementById("modal-risk-level").innerText = data.risk_level;

  // Involved nodes badges
  const nodesContainer = document.getElementById("modal-involved-nodes");
  nodesContainer.innerHTML = "";
  (data.node_ids || []).forEach(nid => {
    const span = document.createElement("span");
    span.className = "px-2.5 py-1 text-[11px] rounded-lg bg-slate-100 border border-slate-200 text-slate-700 font-mono font-medium";
    span.innerText = nid;
    nodesContainer.appendChild(span);
  });

  // Human-Readable Analyst Narrative Briefing
  const narrativeEl = document.getElementById("modal-human-narrative");
  narrativeEl.innerHTML = `
    <div class="p-4 rounded-xl bg-slate-50 border border-slate-200 space-y-3 shadow-sm">
      <div class="flex items-start space-x-3">
        <div class="w-8 h-8 rounded-lg bg-red-50 border border-red-200 text-red-600 flex items-center justify-center shrink-0 mt-0.5 shadow-sm">
          <i class="fas fa-shield-virus text-xs"></i>
        </div>
        <div class="flex-1">
          <h4 class="text-xs font-bold text-slate-900 tracking-wider uppercase">Executive AML Narrative Briefing</h4>
          <p class="text-xs text-slate-600 mt-1 leading-relaxed">${data.human_explanation}</p>
        </div>
      </div>
      <div class="mt-3 pt-3 border-t border-slate-200 flex items-start space-x-2">
        <i class="fas fa-lightbulb text-amber-500 text-xs mt-0.5"></i>
        <div class="text-xs text-amber-900 leading-relaxed">
          <span class="font-bold text-amber-800">Action Plan:</span> ${data.recommended_action}
        </div>
      </div>
    </div>
  `;

  renderShapChart(data.shap_attributions);
}

function renderShapChart(attributions) {
  const canvas = document.getElementById("shap-chart-canvas");
  if (!canvas) return;

  if (shapChartInstance) {
    shapChartInstance.destroy();
  }

  const sorted = [...attributions].sort((a, b) => b.shap_value - a.shap_value);

  const labels = sorted.map(a => a.feature_name);
  const values = sorted.map(a => a.shap_value);
  const backgroundColors = sorted.map(a => a.shap_value >= 0 ? "#ef4444" : "#10b981");

  const ctx = canvas.getContext("2d");
  shapChartInstance = new Chart(ctx, {
    type: "bar",
    data: {
      labels: labels,
      datasets: [{
        data: values,
        backgroundColor: backgroundColors,
        borderWidth: 0,
        borderRadius: 4
      }]
    },
    options: {
      indexAxis: "y",
      responsive: true,
      maintainAspectRatio: false,
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          backgroundColor: "#FFFFFF",
          titleColor: "#0F172A",
          bodyColor: "#334155",
          borderColor: "#E2E8F0",
          borderWidth: 1,
          padding: 10,
          cornerRadius: 8,
          callbacks: {
            title: function(items) {
              const item = items[0];
              const attr = sorted[item.dataIndex];
              return `${attr.feature_name} = ${attr.feature_value}`;
            },
            label: function(item) {
              const attr = sorted[item.dataIndex];
              const dir = attr.impact_direction === "RISK_INCREASING" ? "Increases Anomaly Probability" : "Reduces Anomaly Probability";
              return [
                `SHAP Attribution: ${attr.shap_value > 0 ? "+" : ""}${attr.shap_value.toFixed(4)}`,
                `Direction: ${dir}`,
                `Context: ${attr.human_interpretation}`
              ];
            }
          }
        }
      },
      scales: {
        x: {
          grid: {
            color: "rgba(226, 232, 240, 0.8)",
            drawBorder: false
          },
          ticks: {
            color: "#64748B",
            font: { family: "'JetBrains Mono', monospace", size: 9 }
          },
          title: {
            display: true,
            text: "← Lowers Anomaly Risk | SHAP Feature Contribution | Raises Anomaly Risk →",
            color: "#64748B",
            font: { size: 9, weight: "bold" }
          }
        },
        y: {
          grid: {
            display: false
          },
          ticks: {
            color: "#0F172A",
            font: { family: "'Plus Jakarta Sans', sans-serif", size: 10, weight: "700" }
          }
        }
      }
    }
  });
}

function handleFreezeAccounts() {
  const clusterId = document.getElementById("modal-cluster-id").innerText;
  alert(`[CRITICAL ACTION EXECUTED]\nAll accounts associated with ${clusterId} have been placed under AML Restrictive Hold.`);
  closeShapModal();
}

function handleStepUpAuth() {
  const clusterId = document.getElementById("modal-cluster-id").innerText;
  alert(`[SECURITY POLICY APPLIED]\nMandatory WebAuthn biometric step-up requested for cluster ${clusterId}.`);
  closeShapModal();
}

function handleFalsePositive() {
  const clusterId = document.getElementById("modal-cluster-id").innerText;
  alert(`[FEEDBACK RECORDED]\nCluster ${clusterId} flagged for human AML supervisor review as potential False Positive.`);
  closeShapModal();
}
