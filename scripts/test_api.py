"""
Comprehensive API & Pipeline Verification Test
Uses Starlette/FastAPI TestClient to verify all FinGraph-AI REST endpoints,
models, SMOTE+XGBoost inference, and SHAP explainability.
"""

import sys
import os

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastapi.testclient import TestClient
from backend.app import app


def run_tests():
    print("=" * 70)
    print(" FinGraph-AI: End-to-End API & Integration Tests")
    print("=" * 70)

    client = TestClient(app)

    # 1. Test Static Index File
    print("\n[1] Testing GET / (Static Index Serving)...")
    res = client.get("/")
    assert res.status_code == 200, f"Expected 200, got {res.status_code}"
    assert "FinGraph" in res.text, "Index should contain FinGraph branding"
    print("    ✓ Index HTML served successfully.")

    # 2. Test Auth Profiles
    print("\n[2] Testing GET /api/auth/profiles...")
    res = client.get("/api/auth/profiles")
    assert res.status_code == 200
    data = res.json()
    assert "profiles" in data and len(data["profiles"]) > 0
    print(f"    ✓ Retrieved {len(data['profiles'])} user/merchant profiles.")

    # 3. Test Account Balance
    print("\n[3] Testing GET /api/accounts/balance/ACC-ALICE-101...")
    res = client.get("/api/accounts/balance/ACC-ALICE-101")
    assert res.status_code == 200
    acc = res.json()
    assert acc["owner_name"] == "Alice Smith"
    print(f"    ✓ Account verified: {acc['owner_name']} (${acc['balance']:,.2f}).")

    # 4. Test Transaction Creation (User Portal Requirement)
    print("\n[4] Testing POST /api/transactions/create...")
    tx_payload = {
        "sender_account": "ACC-ALICE-101",
        "recipient_account": "ACC-GOURMET-501",
        "amount": 42.50,
        "type": "Payment",
        "category": "Food",
        "description": "Lunch meeting at Gourmet Bistro",
        "predicted_frequency": "Weekly",
        "device_id": "DEV-IPHONE-ALICE",
        "ip_address": "192.168.1.105",
        "location": "New York, USA"
    }
    res = client.post("/api/transactions/create", json=tx_payload)
    assert res.status_code == 200, f"Error creating tx: {res.text}"
    tx = res.json()
    assert tx["amount"] == 42.50
    assert tx["category"] == "Food"
    assert tx["predicted_frequency"] == "Weekly"
    print(f"    ✓ Transaction recorded: {tx['tx_id']} - ${tx['amount']} [{tx['category']}: {tx['description']}].")

    # 5. Test Expense Analytics for Pie Chart
    print("\n[5] Testing GET /api/analytics/expenses/ACC-ALICE-101...")
    res = client.get("/api/analytics/expenses/ACC-ALICE-101")
    assert res.status_code == 200
    exp = res.json()
    assert "categories" in exp and len(exp["categories"]) > 0
    food_cat = next((c for c in exp["categories"] if c["category"] == "Food"), None)
    assert food_cat is not None
    print(f"    ✓ Expenses calculated: Total spent = ${exp['total_spent']:,.2f}")
    for c in exp["categories"]:
        if c["total_amount"] > 0:
            print(f"        * {c['category']}: ${c['total_amount']:,.2f} ({c['percentage']}%)")

    # 6. Test Multi-Dimensional Graph Data (Admin Portal)
    print("\n[6] Testing GET /api/graph/data (Cytoscape Graph & Red Rings)...")
    res = client.get("/api/graph/data")
    assert res.status_code == 200
    graph = res.json()
    assert len(graph["nodes"]) > 0
    assert len(graph["edges"]) > 0
    red_ring_nodes = [n for n in graph["nodes"] if n["data"].get("is_anomalous")]
    assert len(red_ring_nodes) > 0, "Graph must contain red-ring flagged anomalous nodes"
    print(f"    ✓ Graph structure generated: {len(graph['nodes'])} nodes, {len(graph['edges'])} edges.")
    print(f"    ✓ Detected {len(red_ring_nodes)} red-ring anomalous nodes/clusters.")

    # 7. Test Anomaly Clusters & SHAP Explainability
    print("\n[7] Testing GET /api/anomalies and SHAP explanation...")
    res = client.get("/api/anomalies")
    assert res.status_code == 200
    anomalies = res.json()
    assert len(anomalies) > 0
    cid = anomalies[0]["cluster_id"]
    print(f"    ✓ Found {len(anomalies)} flagged anomaly clusters. Inspecting {cid}...")

    res_exp = client.get(f"/api/anomalies/{cid}/explain")
    assert res_exp.status_code == 200
    exp_data = res_exp.json()
    assert "shap_attributions" in exp_data and len(exp_data["shap_attributions"]) > 0
    assert "human_explanation" in exp_data and len(exp_data["human_explanation"]) > 20
    print(f"    ✓ SHAP explanation retrieved:")
    print(f"        - Flagged Type: {exp_data['anomaly_type']} ({exp_data['confidence_score']*100:.1f}%)")
    print(f"        - Top Feature: {exp_data['shap_attributions'][0]['feature_name']} (SHAP: {exp_data['shap_attributions'][0]['shap_value']:+.4f})")
    print(f"        - Human Narrative: {exp_data['human_explanation'][:100]}...")

    # 8. Test Dynamic Attack Simulation (Smurfing Ring)
    print("\n[8] Testing POST /api/simulation/smurfing...")
    res = client.post("/api/simulation/smurfing")
    assert res.status_code == 200
    sim_data = res.json()
    assert sim_data["status"] == "SUCCESS"
    print(f"    ✓ Dynamic Smurfing Ring injected: {sim_data['ring_id']}")

    # 9. Test Dynamic Attack Simulation (Device Syndicate)
    print("\n[9] Testing POST /api/simulation/syndicate...")
    res = client.post("/api/simulation/syndicate")
    assert res.status_code == 200
    sim_syn = res.json()
    assert sim_syn["status"] == "SUCCESS"
    print(f"    ✓ Dynamic Fraud Syndicate injected: {sim_syn['ring_id']}")

    # 10. Test Model Retraining (SMOTE + XGBoost)
    print("\n[10] Testing POST /api/model/retrain...")
    res = client.post("/api/model/retrain")
    assert res.status_code == 200
    metrics = res.json()
    assert metrics["accuracy"] >= 0.90
    print(f"    ✓ Retrained model: Accuracy = {metrics['accuracy']*100:.2f}%, Macro F1 = {metrics['f1_macro']*100:.2f}%.")

    # 11. Test System Logs Feed
    print("\n[11] Testing GET /api/logs...")
    res = client.get("/api/logs")
    assert res.status_code == 200
    logs = res.json()
    assert len(logs) > 0
    print(f"    ✓ Retrieved {len(logs)} audit logs.")

    print("\n" + "=" * 70)
    print(" ALL 11 TEST SUITES PASSED FLAWLESSLY! FIN-GRAPH AI IS PRODUCTION READY.")
    print("=" * 70)


if __name__ == "__main__":
    run_tests()
