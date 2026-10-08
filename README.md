# FinGraph-AI: Financial Fraud Intelligence Platform

**FinGraph-AI** is a full-stack, production-ready fintech cybersecurity and fraud intelligence platform. It combines **multi-account transaction graph anomaly detection**, **user expense tracking**, and **Explainable AI (SHAP)** to detect, isolate, and explain sophisticated financial fraud rings like smurfing networks and shared-device syndicates.

---

## 🌟 Key Capabilities

### 1. Dual-Role Experience
- **User Portal (Customer & Merchant)**:
  - Account balance check, monthly inflow & outflow analytics.
  - Transaction initiation: Transfers, Merchant Payments, Online Purchases.
  - Inputs include:
    - **Category**: Dropdown (`Food`, `Entertainment`, `Sports`, `Shopping`, `Bills`)
    - **Custom Description**: e.g., `"snacks"`, `"movie tickets"`
    - **Predicted Frequency**: `Daily`, `Weekly`, `Monthly`, `Quarterly`, `Rare / One-off`
  - **Dynamic Expense Pie Chart**: Real-time Chart.js doughnut chart comparing Amount ($) vs Category with dynamic legends and percentages.
  - Live Transaction History Ledger.

- **Admin Intelligence Portal**:
  - **Multi-Dimensional Network Graph**: Visualizes Customers, Accounts, Devices, Merchants, and Locations connected by Transfers, Payments, Logins, and Purchases.
  - **Red-Ring Anomaly Outlines**: Prominently highlights suspicious subgraphs and compound clusters in glowing crimson borders (`#ef4444`).
  - **One-Click Attack Simulators**:
    - `⚡ Simulate Smurfing Ring`: Injects fan-out/fan-in money mule structuring.
    - `🚨 Simulate Device Syndicate`: Injects coordinated multi-account botnets sharing hardware fingerprints and proxy IPs.
  - **Real-Time System Log Feed**: Live audit stream of transaction logs, graph scans, and ML alerts.

### 2. Machine Learning & Explainable AI (SHAP)
- **Synthetic Graph Dataset Pipeline**: Synthesizes multi-account graph topological metrics:
  - `degree_centrality`, `pagerank_score`, `ip_velocity_count`, `shared_device_account_count`, `in_out_ratio`, `tx_amount_mean`, `rapid_tx_velocity`.
- **SMOTE Class Balancing**: Uses `imbalanced-learn` SMOTE to counteract extreme class imbalance (82% Normal, 10% Smurfing, 8% Syndicate).
- **XGBoost Classifier**: Multi-class gradient boosting model achieving high precision & recall across fraud classes.
- **SHAP TreeExplainer Attribution**:
  - When clicking any red-ring node or cluster, an interactive modal displays:
    - Shapley values (horizontal bar chart showing positive vs negative feature contributions).
    - Base expected value vs prediction probability.
    - **Human-Readable AML Analyst Narrative**: Synthesized plain-English explanation of why the cluster was flagged (e.g. structuring pass-through ratios, hardware multiplexing).
    - Recommended mitigation actions (account freezes, biometric step-up, SAR filing).

---

## 🗂️ Project Directory Structure

```
fingraph_ai/
├── backend/
│   ├── __init__.py
│   ├── app.py                 # FastAPI application & REST endpoints
│   ├── models.py              # Pydantic schemas (Transactions, Cytoscape, SHAP, Logs)
│   ├── database.py            # In-memory financial datastore & seed entities
│   ├── graph_engine.py        # NetworkX multi-dimensional graph & red-ring clustering
│   └── ml_pipeline.py         # Synthetic data, SMOTE, XGBoost classifier & SHAP TreeExplainer
├── static/
│   ├── index.html             # Tailwind CSS single-page responsive application
│   ├── css/
│   │   └── style.css          # Cyber-fintech styling, red-ring pulse animations
│   └── js/
│       ├── app.js             # Dual portal logic, transaction handling & Chart.js pie chart
│       ├── graph.js           # Cytoscape.js interactive graph engine with red rings
│       └── shap_modal.js      # SHAP feature attribution modal & narrative renderer
├── scripts/
│   └── run_training.py        # Standalone ML training and evaluation script
├── main.py                    # Application launcher
├── requirements.txt           # Project dependencies
└── README.md                  # Complete documentation
```

---

## 🚀 Quickstart Guide

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Standalone ML Training Verification
```bash
python scripts/run_training.py
```

### 3. Launch the Web Application
```bash
python main.py
```
Or with Uvicorn directly:
```bash
uvicorn backend.app:app --host 127.0.0.1 --port 8020 --reload
```

### 4. Access the Application
Open your web browser and navigate to:
```
http://localhost:8020
```
(or `http://127.0.0.1:8020`)

---

## 🔬 Interactive Demo Walkthrough

1. **User Portal**:
   - Select profile `Alice Smith (Customer)` or `TechMart Global (Merchant)`.
   - Submit a new transaction: Recipient = `Gourmet Bistro`, Amount = `$45.00`, Category = `Food`, Description = `"team pizza lunch"`, Frequency = `Weekly`.
   - Watch the **Dynamic Expense Pie Chart** update immediately, reflecting the new amount distribution across categories!

2. **Admin Portal**:
   - Switch to the **Admin Intelligence Portal** tab.
   - Explore the force-directed **Cytoscape.js Graph**: observe Customers (blue hexagons), Accounts (green circles), Devices (amber rectangles), and Merchants (purple diamonds).
   - Locate the **glowing red-ring outlines** around `CLUSTER-SMURF-01` and `CLUSTER-SYN-RIG-99`.
   - Click on the red ring or click any flagged cluster card on the right panel.

3. **Explainable AI (SHAP) Modal**:
   - Notice the exact SHAP feature attributions on the horizontal bar chart (e.g. `shared_device_account_count: +3.03 SHAP`, `in_out_ratio: +0.98 SHAP`).
   - Read the synthesized **AML Analyst Narrative** clearly detailing the topological indicators.
   - Test investigator mitigation triggers: "Freeze Ring Accounts" or "Request Biometric 2FA".

4. **Live Attack Simulations**:
   - Click **⚡ Simulate Smurfing Ring**: A new multi-mule structuring chain is injected into the graph in real-time, receiving an immediate red ring!
   - Click **🚨 Simulate Device Syndicate**: A 5-account proxy botnet is spawned and flagged
