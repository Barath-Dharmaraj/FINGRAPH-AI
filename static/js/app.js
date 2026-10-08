/**
 * FinGraph-AI Main Application Controller (Crypto Payments Dashboard Edition)
 * Inspired by Emote Agency's Crypto Payments Dashboard Dribbble shot.
 */

// Global State
let currentPortal = "USER"; // "USER" or "ADMIN"
let currentAccountId = "ACC-ALICE-101";
let expenseChartInstance = null;

document.addEventListener("DOMContentLoaded", async () => {
  setupTransactionForm();
  await loadProfiles();
  await switchUserProfile(currentAccountId);

  // Poll system logs every 4 seconds when in Admin portal
  setInterval(() => {
    if (currentPortal === "ADMIN") {
      loadSystemLogs();
    }
  }, 4000);
});

// =====================================================================
// Portal Switching & Sidebar Navigation
// =====================================================================

function switchPortal(portal) {
  currentPortal = portal;
  const viewUser = document.getElementById("view-user-portal");
  const viewAdmin = document.getElementById("view-admin-portal");
  const breadcrumb = document.getElementById("header-breadcrumb");

  const sideUser = document.getElementById("sidebar-btn-user");
  const sideAdmin = document.getElementById("sidebar-btn-admin");
  const mobileUser = document.getElementById("mobile-tab-user");
  const mobileAdmin = document.getElementById("mobile-tab-admin");

  if (portal === "USER") {
    viewUser.classList.remove("hidden");
    viewAdmin.classList.add("hidden");
    if (breadcrumb) breadcrumb.innerText = "User Payment Portal";

    // Sidebar active styling
    if (sideUser) {
      sideUser.className = "w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold bg-blue-600 text-white shadow-sm transition-all group";
    }
    if (sideAdmin) {
      sideAdmin.className = "w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-all group";
    }
    if (mobileUser) {
      mobileUser.className = "px-3 py-1 rounded-full bg-blue-600 text-white font-semibold text-xs";
      mobileAdmin.className = "px-3 py-1 rounded-full text-slate-600 font-semibold text-xs";
    }

    loadUserExpenses(currentAccountId);
  } else {
    viewAdmin.classList.remove("hidden");
    viewUser.classList.add("hidden");
    if (breadcrumb) breadcrumb.innerText = "Admin Tactical Graph Intelligence";

    // Sidebar active styling
    if (sideAdmin) {
      sideAdmin.className = "w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold bg-blue-600 text-white shadow-sm transition-all group";
    }
    if (sideUser) {
      sideUser.className = "w-full flex items-center justify-between px-3.5 py-2.5 rounded-xl text-xs font-semibold text-slate-600 hover:text-slate-900 hover:bg-slate-100 transition-all group";
    }
    if (mobileAdmin) {
      mobileAdmin.className = "px-3 py-1 rounded-full bg-blue-600 text-white font-semibold text-xs";
      mobileUser.className = "px-3 py-1 rounded-full text-slate-600 font-semibold text-xs";
    }

    loadAndRenderGraph();
    loadSystemLogs();
    loadAnomalyClustersList();
  }
}

// =====================================================================
// User Profiles & Dual-Role Logins
// =====================================================================

async function loadProfiles() {
  try {
    const res = await fetch("/api/auth/profiles");
    const data = await res.json();
    const select = document.getElementById("profile-select");
    const recipientSelect = document.getElementById("tx-recipient");

    if (select) {
      select.innerHTML = "";
      data.profiles.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.account_id;
        opt.innerText = `${p.owner_name} (${p.role}) - ${p.account_id}`;
        select.appendChild(opt);
      });
      select.value = currentAccountId;
      select.addEventListener("change", (e) => switchUserProfile(e.target.value));
    }

    if (recipientSelect) {
      recipientSelect.innerHTML = "";
      data.profiles.forEach(p => {
        const opt = document.createElement("option");
        opt.value = p.account_id;
        opt.innerText = `${p.owner_name} (${p.account_id})`;
        recipientSelect.appendChild(opt);
      });
      recipientSelect.value = "ACC-GOURMET-501";
    }
  } catch (err) {
    console.error("Error loading profiles:", err);
  }
}

async function switchUserProfile(accountId) {
  currentAccountId = accountId;
  try {
    const res = await fetch(`/api/accounts/balance/${accountId}`);
    const acc = await res.json();

    // User Avatar Initials
    const initials = acc.owner_name.split(" ").map(w => w[0]).join("").toUpperCase().slice(0, 2);
    const initialsEl = document.getElementById("user-avatar-initials");
    if (initialsEl) initialsEl.innerText = initials;

    const roleBadge = document.getElementById("user-role-badge");
    if (roleBadge) {
      roleBadge.innerText = acc.role.toUpperCase();
      roleBadge.className = acc.role === "Merchant" ? "pill-badge badge-cyan" : "pill-badge badge-purple";
    }

    const accIdEl = document.getElementById("user-account-id");
    if (accIdEl) accIdEl.innerText = acc.account_id;

    const balEl = document.getElementById("stat-balance");
    if (balEl) balEl.innerText = `$${acc.balance.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

    await loadUserExpenses(accountId);
  } catch (err) {
    console.error("Error switching profile:", err);
  }
}

// =====================================================================
// User Expenses & Dynamic Doughnut Chart (Chart.js)
// =====================================================================

async function loadUserExpenses(accountId) {
  try {
    const res = await fetch(`/api/analytics/expenses/${accountId}`);
    const data = await res.json();

    const spentEl = document.getElementById("stat-spent");
    const inflowEl = document.getElementById("stat-inflow");
    if (spentEl) spentEl.innerText = `$${data.total_spent.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    if (inflowEl) inflowEl.innerText = `$${data.total_inflow.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;

    renderExpensePieChart(data.categories);
    renderTransactionTable(data.recent_transactions);
  } catch (err) {
    console.error("Error loading expenses:", err);
  }
}

function renderExpensePieChart(categories) {
  const canvas = document.getElementById("expense-pie-chart");
  if (!canvas) return;

  if (expenseChartInstance) {
    expenseChartInstance.destroy();
  }

  // Emote Agency Neon Crypto Palette
  const categoryColors = {
    "Food": "#F59E0B",          // Amber Gold
    "Entertainment": "#EC4899", // Neon Magenta
    "Sports": "#06B6D4",        // Bright Cyan
    "Shopping": "#8B5CF6",      // Electric Purple
    "Bills": "#3B82F6"          // Neon Blue
  };

  const labels = categories.map(c => c.category);
  const amounts = categories.map(c => c.total_amount);
  const bgColors = categories.map(c => categoryColors[c.category] || "#64748B");

  const ctx = canvas.getContext("2d");
  expenseChartInstance = new Chart(ctx, {
    type: "doughnut",
    data: {
      labels: labels,
      datasets: [{
        data: amounts,
        backgroundColor: bgColors,
        borderColor: "#FFFFFF",
        borderWidth: 4,
        hoverOffset: 10,
        borderRadius: 6
      }]
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      cutout: "75%",
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
          padding: 12,
          cornerRadius: 12,
          boxPadding: 4,
          callbacks: {
            label: function(item) {
              const cat = categories[item.dataIndex];
              return ` $${cat.total_amount.toLocaleString(undefined, { minimumFractionDigits: 2 })} (${cat.percentage}%) • ${cat.tx_count} txns`;
            }
          }
        }
      }
    }
  });

  renderCategoryList(categories);
}

function renderCategoryList(categories) {
  const container = document.getElementById("category-breakdown-list");
  if (!container) return;

  container.innerHTML = "";
  categories.forEach(cat => {
    const item = document.createElement("div");
    item.className = "flex items-center justify-between p-2.5 rounded-lg bg-slate-50 border border-slate-100 text-xs hover:border-slate-200 transition-all";
    
    const coinClass = getCategoryCoinClass(cat.category);
    const tokenSymbol = getCategoryTokenSymbol(cat.category);

    item.innerHTML = `
      <div class="flex items-center space-x-2.5">
        <span class="coin-badge ${coinClass} !w-6 !h-6 !text-[9px] font-bold">${tokenSymbol}</span>
        <span class="font-semibold text-slate-800">${cat.category}</span>
        <span class="text-[10px] text-slate-400">(${cat.tx_count} txns)</span>
      </div>
      <div class="flex items-center space-x-2">
        <span class="font-mono font-bold text-slate-900">$${cat.total_amount.toLocaleString()}</span>
        <span class="pill-badge ${getCategoryBadgePillClass(cat.category)}">${cat.percentage}%</span>
      </div>
    `;
    container.appendChild(item);
  });
}

function getCategoryCoinClass(cat) {
  switch (cat) {
    case "Food": return "coin-food";
    case "Entertainment": return "coin-entertainment";
    case "Sports": return "coin-sports";
    case "Shopping": return "coin-shopping";
    case "Bills": return "coin-bills";
    default: return "coin-shopping";
  }
}

function getCategoryTokenSymbol(cat) {
  switch (cat) {
    case "Food": return "FOD";
    case "Entertainment": return "ENT";
    case "Sports": return "SPT";
    case "Shopping": return "SHP";
    case "Bills": return "BIL";
    default: return "AST";
  }
}

function getCategoryBadgePillClass(cat) {
  switch (cat) {
    case "Food": return "badge-amber";
    case "Entertainment": return "badge-crimson";
    case "Sports": return "badge-cyan";
    case "Shopping": return "badge-purple";
    case "Bills": return "badge-purple";
    default: return "badge-purple";
  }
}

/**
 * Renders the transaction history table styled as a crypto wallet activity feed.
 */
function renderTransactionTable(transactions) {
  const tbody = document.getElementById("tx-history-tbody");
  if (!tbody) return;

  tbody.innerHTML = "";
  if (!transactions || transactions.length === 0) {
    tbody.innerHTML = `<tr><td colspan="7" class="text-center py-6 text-[#64748B] text-xs">No transaction records on ledger yet</td></tr>`;
    return;
  }

  transactions.forEach(t => {
    const tr = document.createElement("tr");
    tr.className = "border-b border-slate-100 hover:bg-slate-50/80 transition-colors";
    
    const coinClass = getCategoryCoinClass(t.category);
    const tokenSymbol = getCategoryTokenSymbol(t.category);
    const truncatedHash = `0x${t.tx_id.replace("TX-", "").toLowerCase()}...${t.tx_id.slice(-4).toLowerCase()}`;

    tr.innerHTML = `
      <td class="py-3 px-3">
        <div class="flex items-center space-x-2">
          <div class="coin-badge ${coinClass}">${tokenSymbol}</div>
          <div>
            <span class="text-xs font-semibold text-slate-900 block">${t.category}</span>
            <span class="text-[10px] text-slate-500">${t.type}</span>
          </div>
        </div>
      </td>
      <td class="py-3 px-3 text-xs font-semibold text-slate-900">${t.recipient_name}</td>
      <td class="py-3 px-3 text-xs font-mono text-blue-600 font-medium">${truncatedHash}</td>
      <td class="py-3 px-3 text-xs text-slate-600 max-w-xs truncate">${t.description}</td>
      <td class="py-3 px-3 text-xs text-slate-500 font-mono">${t.predicted_frequency}</td>
      <td class="py-3 px-3 text-xs font-bold text-right font-mono text-slate-900">-$${t.amount.toFixed(2)}</td>
      <td class="py-3 px-3 text-right">
        <div class="inline-flex items-center space-x-1 px-2 py-0.5 rounded-full bg-emerald-50 border border-emerald-200 text-emerald-700 text-[10px] font-semibold">
          <span class="w-1.5 h-1.5 rounded-full bg-emerald-500 status-dot-pulse"></span>
          <span>Settled</span>
        </div>
      </td>
    `;
    tbody.appendChild(tr);
  });
}

// =====================================================================
// Transaction Creation Form
// =====================================================================

function setupTransactionForm() {
  const form = document.getElementById("tx-form");
  if (!form) return;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const recipient = document.getElementById("tx-recipient").value;
    const amount = parseFloat(document.getElementById("tx-amount").value);
    const txType = document.getElementById("tx-type").value;
    const category = document.getElementById("tx-category").value;
    const description = document.getElementById("tx-description").value;
    const predictedFrequency = document.getElementById("tx-frequency").value;

    if (!recipient || isNaN(amount) || amount <= 0 || !description) {
      alert("Please fill out all required transaction fields with a valid amount.");
      return;
    }

    const payload = {
      sender_account: currentAccountId,
      recipient_account: recipient,
      amount: amount,
      type: txType,
      category: category,
      description: description,
      predicted_frequency: predictedFrequency,
      device_id: "DEV-IPHONE-ALICE",
      ip_address: "192.168.1.105",
      location: "New York, USA"
    };

    try {
      const res = await fetch("/api/transactions/create", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload)
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Transaction failed");
      }

      const tx = await res.json();
      showToast(`Payment of $${tx.amount.toFixed(2)} [${tx.category}: ${tx.description}] confirmed!`, "success");

      // Reset inputs
      document.getElementById("tx-amount").value = "";
      document.getElementById("tx-description").value = "";

      // Refresh balance & expenses
      await switchUserProfile(currentAccountId);

    } catch (err) {
      alert(`Transaction Error: ${err.message}`);
    }
  });
}

// =====================================================================
// Admin Portal & Live Attack Simulations
// =====================================================================

async function triggerSmurfingSim() {
  try {
    showToast("⚡ Injecting Smurfing Ring Attack Simulation...", "warn");
    const res = await fetch("/api/simulation/smurfing", { method: "POST" });
    const data = await res.json();
    showToast(data.message, "danger");

    await loadAndRenderGraph();
    await loadSystemLogs();
    await loadAnomalyClustersList();
  } catch (err) {
    console.error("Smurfing sim error:", err);
  }
}

async function triggerSyndicateSim() {
  try {
    showToast("🚨 Injecting Coordinated Device Syndicate Attack...", "warn");
    const res = await fetch("/api/simulation/syndicate", { method: "POST" });
    const data = await res.json();
    showToast(data.message, "danger");

    await loadAndRenderGraph();
    await loadSystemLogs();
    await loadAnomalyClustersList();
  } catch (err) {
    console.error("Syndicate sim error:", err);
  }
}

async function resetSystemState() {
  if (!confirm("Reset datastore and graph to clean baseline?")) return;
  try {
    const res = await fetch("/api/simulation/reset", { method: "POST" });
    const data = await res.json();
    showToast(data.message, "success");

    await switchUserProfile(currentAccountId);
    await loadAndRenderGraph();
    await loadSystemLogs();
    await loadAnomalyClustersList();
  } catch (err) {
    console.error("Reset error:", err);
  }
}

async function retrainMLModel() {
  const badge = document.getElementById("ml-metrics-badge");
  showToast("🧠 Retraining XGBoost with SMOTE balancing...", "info");

  try {
    const res = await fetch("/api/model/retrain", { method: "POST" });
    const metrics = await res.json();
    showToast(`XGBoost Model retrained with SMOTE. Macro F1: ${(metrics.f1_macro * 100).toFixed(1)}%`, "success");

    if (badge) {
      badge.innerHTML = `<i class="fas fa-bolt text-[10px]"></i><span>XGBoost + SMOTE: ${(metrics.accuracy * 100).toFixed(0)}% Acc</span>`;
    }
  } catch (err) {
    alert(`Retraining error: ${err.message}`);
  }
}

// =====================================================================
// System Logs Feed & Anomaly Clusters Card List (Block Explorer Style)
// =====================================================================

async function loadSystemLogs() {
  try {
    const res = await fetch("/api/logs");
    const logs = await res.json();
    const container = document.getElementById("system-logs-container");
    if (!container) return;

    container.innerHTML = "";
    logs.slice(0, 30).forEach(log => {
      const row = document.createElement("div");
      row.className = "flex items-start space-x-3 py-1.5 px-2 rounded hover:bg-white text-xs font-mono transition-colors";

      const badgeClass = log.level === "FRAUD_ALERT" ? "pill-badge badge-crimson"
        : (log.level === "WARN" ? "pill-badge badge-amber"
        : "pill-badge badge-indigo");

      row.innerHTML = `
        <span class="text-slate-400 text-[10px] whitespace-nowrap">${log.timestamp.split(" ")[1] || log.timestamp}</span>
        <span class="${badgeClass} text-[9px] py-0 px-1.5 font-semibold">${log.level}</span>
        <span class="text-blue-600 text-[10px] font-medium">[${log.category}]</span>
        <span class="text-slate-700 flex-1 truncate">${log.message}</span>
      `;
      container.appendChild(row);
    });
  } catch (err) {
    console.error("Error loading logs:", err);
  }
}

async function loadAnomalyClustersList() {
  try {
    const res = await fetch("/api/anomalies");
    const clusters = await res.json();
    const container = document.getElementById("flagged-clusters-list");
    if (!container) return;

    container.innerHTML = "";
    clusters.forEach(c => {
      const card = document.createElement("div");
      card.className = "p-3.5 rounded-xl bg-white border border-red-200 hover:border-red-400 hover:shadow-md transition-all cursor-pointer space-y-2 group";
      card.onclick = () => openShapModal(c.cluster_id);

      card.innerHTML = `
        <div class="flex items-center justify-between">
          <span class="text-xs font-bold text-red-600 group-hover:text-red-700 flex items-center">
            <i class="fas fa-radiation mr-1.5 text-red-500 animate-pulse"></i> ${c.cluster_id}
          </span>
          <span class="pill-badge badge-crimson font-bold">
            ${(c.confidence_score * 100).toFixed(0)}% CONF
          </span>
        </div>
        <div class="text-[11px] font-bold text-slate-900 tracking-wide">
          ${c.anomaly_type.toUpperCase()} FLAGGED
        </div>
        <div class="text-[10px] text-slate-500 line-clamp-2 leading-relaxed">
          ${c.human_explanation}
        </div>
        <div class="text-[10px] text-blue-600 font-semibold flex items-center justify-end group-hover:underline pt-0.5">
          Inspect SHAP Attributions <i class="fas fa-arrow-right ml-1 text-[9px]"></i>
        </div>
      `;
      container.appendChild(card);
    });
  } catch (err) {
    console.error("Error loading anomaly clusters:", err);
  }
}

// Toast Notifications
function showToast(message, type = "info") {
  const container = document.getElementById("toast-container");
  if (!container) return;

  const toast = document.createElement("div");
  const bg = type === "danger" ? "bg-white border-red-200 text-red-800"
    : (type === "warn" ? "bg-white border-amber-200 text-amber-800"
    : (type === "success" ? "bg-white border-emerald-200 text-emerald-800"
    : "bg-white border-blue-200 text-blue-800"));

  toast.className = `p-3 rounded-lg border shadow-lg flex items-center space-x-2.5 text-xs font-semibold backdrop-blur-xl transition-all duration-200 transform translate-y-1 ${bg}`;
  toast.innerHTML = `<i class="fas fa-circle-info text-xs"></i><span>${message}</span>`;

  container.appendChild(toast);
  setTimeout(() => toast.remove(), 4500);
}
