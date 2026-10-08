"""
FinGraph-AI FastAPI Main Application Server
Integrates User Expense Tracking, Admin Intelligence Graph, SMOTE+XGBoost Engine,
and SHAP Explainability APIs.
"""

import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import Optional, List, Dict, Any

from backend.models import (
    TransactionCreate,
    TransactionRecord,
    AccountInfo,
    ExpenseSummaryResponse,
    GraphResponse,
    AnomalyCluster,
    SystemLog,
    ModelMetricsResponse
)
from backend.database import db
from backend.graph_engine import graph_engine
from backend.ml_pipeline import ml_pipeline


app = FastAPI(
    title="FinGraph-AI Platform",
    description="Multi-Account Transaction Graph Anomaly Detection with SHAP Explainability & User Expense Tracking",
    version="1.0.0"
)

# Enable CORS for hackathon development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STATIC_DIR = os.path.join(BASE_DIR, "static")

# Mount static files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
def serve_index():
    """Serves the primary FinGraph-AI Single Page Application."""
    index_file = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "FinGraph-AI Backend is running. Frontend index.html not found."}


# =====================================================================
# Auth & Account Endpoints
# =====================================================================

@app.get("/api/auth/profiles")
def get_available_profiles():
    """Returns available accounts for instant demo login switching (Customer, Merchant, Admin)."""
    profiles = []
    for acc in db.accounts.values():
        if "SMURF" not in acc.account_id and "SYNDICATE" not in acc.account_id and "LIVE" not in acc.account_id and "BOT" not in acc.account_id:
            profiles.append({
                "account_id": acc.account_id,
                "owner_name": acc.owner_name,
                "role": acc.role,
                "balance": acc.balance,
                "status": acc.status,
                "device_id": acc.device_id
            })
    return {"profiles": profiles}


@app.get("/api/accounts/balance/{account_id}", response_model=AccountInfo)
def get_account_balance(account_id: str):
    """Retrieves account status, role, and current balance."""
    acc = db.accounts.get(account_id)
    if not acc:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found.")
    return acc


# =====================================================================
# User Expense Tracking & Transaction Creation
# =====================================================================

@app.post("/api/transactions/create", response_model=TransactionRecord)
def create_transaction(req: TransactionCreate):
    """
    Records a user transaction with category dropdown, custom description,
    and predicted_frequency. Re-evaluates graph anomaly status in real time.
    """
    try:
        tx = db.record_user_transaction(req)
        # Invalidate cached graph clusters to trigger re-scan on next read
        graph_engine.cached_clusters.clear()
        return tx
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transaction processing error: {str(e)}")


@app.get("/api/analytics/expenses/{account_id}", response_model=ExpenseSummaryResponse)
def get_user_expenses(account_id: str):
    """
    Returns category breakdown vs amount for dynamic user pie charts,
    plus recent transaction history for this account.
    """
    if account_id not in db.accounts:
        raise HTTPException(status_code=404, detail=f"Account {account_id} not found.")
    return db.get_user_expenses(account_id)


# =====================================================================
# Admin Graph Visualization & Anomaly Detection
# =====================================================================

@app.get("/api/graph/data", response_model=GraphResponse)
def get_graph_data():
    """
    Returns the multi-dimensional NetworkX graph converted to Cytoscape.js format.
    Includes nodes (Customer, Account, Device, Merchant, Location) and edges
    (Transfers, Payments, Logins, Purchases) with red-ring anomaly outlines.
    """
    return graph_engine.get_cytoscape_graph()


@app.get("/api/anomalies", response_model=List[AnomalyCluster])
def get_anomalies():
    """Returns all detected anomalous clusters flagged with red rings."""
    clusters = graph_engine.detect_anomalous_clusters()
    return list(clusters.values())


@app.get("/api/anomalies/{cluster_id}/explain")
def get_anomaly_explanation(cluster_id: str):
    """
    Explainable AI (SHAP) endpoint:
    Returns local Shapley feature attribution values, base value, and a human-readable
    explanation when an investigator clicks on any suspicious red ring.
    """
    explanation = graph_engine.get_cluster_explanation(cluster_id)
    if not explanation:
        # Fallback: re-detect and check
        clusters = graph_engine.detect_anomalous_clusters()
        explanation = clusters.get(cluster_id)

    if not explanation:
        raise HTTPException(status_code=404, detail=f"Anomaly cluster {cluster_id} not found.")

    return explanation


# =====================================================================
# Attack Simulations & Controls
# =====================================================================

@app.post("/api/simulation/smurfing")
def trigger_smurfing_attack():
    """Simulates a live multi-mule Smurfing Ring attack into the transaction graph."""
    ring_id = db.trigger_dynamic_smurfing_simulation()
    graph_engine.cached_clusters.clear()
    return {
        "status": "SUCCESS",
        "message": f"Smurfing attack simulation injected. Flagged as {ring_id} with red-ring outline.",
        "ring_id": ring_id
    }


@app.post("/api/simulation/syndicate")
def trigger_syndicate_attack():
    """Simulates a live high-velocity Shared-Device Fraud Syndicate into the graph."""
    ring_id = db.trigger_dynamic_syndicate_simulation()
    graph_engine.cached_clusters.clear()
    return {
        "status": "SUCCESS",
        "message": f"Fraud Syndicate attack simulation injected. Flagged as {ring_id} with red-ring outline.",
        "ring_id": ring_id
    }


@app.post("/api/simulation/reset")
def reset_simulation():
    """Resets datastore and graph back to baseline state."""
    db.reset()
    graph_engine.cached_clusters.clear()
    return {"status": "SUCCESS", "message": "System state successfully reset to initial baseline."}


# =====================================================================
# Machine Learning Management (SMOTE & XGBoost)
# =====================================================================

@app.post("/api/model/retrain", response_model=ModelMetricsResponse)
def retrain_model():
    """Retrains the XGBoost classifier using SMOTE oversampled synthetic data."""
    try:
        metrics = ml_pipeline.train_pipeline(n_samples=2000)
        db._add_log(
            "INFO", "ML_INFERENCE",
            f"XGBoost model retrained with SMOTE. Macro F1: {metrics.f1_macro * 100:.1f}%, Accuracy: {metrics.accuracy * 100:.1f}%.",
            {"accuracy": metrics.accuracy, "f1": metrics.f1_macro}
        )
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Model retraining failed: {str(e)}")


@app.get("/api/model/metrics")
def get_model_metrics():
    """Returns current ML model performance metrics."""
    if not ml_pipeline.metrics:
        ml_pipeline.train_pipeline()
    return ml_pipeline.metrics


# =====================================================================
# System Logs Monitor
# =====================================================================

@app.get("/api/logs", response_model=List[SystemLog])
def get_system_logs(
    level: Optional[str] = Query(None, description="Filter by level: INFO, WARN, FRAUD_ALERT"),
    category: Optional[str] = Query(None, description="Filter by category: AUTH, TRANSACTION, GRAPH_SCAN, ML_INFERENCE, SECURITY")
):
    """Fetches real-time system audit logs for the admin monitoring console."""
    logs = db.logs
    if level:
        logs = [l for l in logs if l.level.upper() == level.upper()]
    if category:
        logs = [l for l in logs if l.category.upper() == category.upper()]
    return logs[:100]


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.app:app", host="127.0.0.1", port=8020, reload=True)
