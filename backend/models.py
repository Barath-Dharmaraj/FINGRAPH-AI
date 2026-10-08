"""
FinGraph-AI Data Models & Pydantic Schemas
Defines request/response contracts for financial transactions, graph elements,
ML predictions, and explainable AI (SHAP) feature attributions.
"""

from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field
from datetime import datetime


class TransactionCreate(BaseModel):
    """Payload for submitting a new financial transaction from the User Portal."""
    sender_account: str = Field(..., example="ACC-ALICE-101")
    recipient_account: str = Field(..., example="ACC-BOB-202")
    amount: float = Field(..., gt=0, example=48.50)
    type: str = Field(default="Transfer", example="Transfer")  # Transfer, Payment, Purchase
    category: str = Field(..., example="Food")  # Food, Entertainment, Sports, Shopping, Bills
    description: str = Field(..., example="Team lunch at bistro")
    predicted_frequency: str = Field(default="Weekly", example="Weekly")  # Daily, Weekly, Monthly, Quarterly, Rare / One-off
    device_id: Optional[str] = Field(default="DEV-IPHONE-ALICE", example="DEV-IPHONE-ALICE")
    ip_address: Optional[str] = Field(default="192.168.1.105", example="192.168.1.105")
    location: Optional[str] = Field(default="New York, USA", example="New York, USA")


class TransactionRecord(BaseModel):
    """Historical or newly recorded transaction."""
    tx_id: str
    timestamp: str
    sender_account: str
    sender_name: str
    recipient_account: str
    recipient_name: str
    amount: float
    type: str
    category: str
    description: str
    predicted_frequency: str
    status: str = "COMPLETED"
    is_flagged: bool = False


class AccountInfo(BaseModel):
    """User and Merchant account status."""
    account_id: str
    customer_id: str
    owner_name: str
    role: str  # Customer, Merchant, Admin
    balance: float
    status: str  # Active, Monitored, Frozen
    device_id: str
    location: str


class ExpenseCategorySummary(BaseModel):
    """Category aggregated spend for pie chart rendering."""
    category: str
    total_amount: float
    percentage: float
    tx_count: int


class ExpenseSummaryResponse(BaseModel):
    """Full user expense breakdown response."""
    account_id: str
    total_spent: float
    total_inflow: float
    categories: List[ExpenseCategorySummary]
    recent_transactions: List[TransactionRecord]


class CytoscapeNodeData(BaseModel):
    """Data object inside Cytoscape.js node."""
    id: str
    label: str
    type: str  # customer, account, device, merchant, location, cluster_ring
    sublabel: Optional[str] = None
    balance: Optional[float] = None
    risk_level: Optional[str] = "LOW"
    is_anomalous: bool = False
    cluster_id: Optional[str] = None
    parent: Optional[str] = None  # for compound node clustering
    metadata: Optional[Dict[str, Any]] = None


class CytoscapeNode(BaseModel):
    data: CytoscapeNodeData


class CytoscapeEdgeData(BaseModel):
    """Data object inside Cytoscape.js edge."""
    id: str
    source: str
    target: str
    label: str
    type: str  # TRANSFERRED_TO, PAID_TO, LOGGED_IN_FROM, PURCHASED_FROM
    amount: Optional[float] = None
    category: Optional[str] = None
    frequency: Optional[str] = None
    is_anomalous: bool = False


class CytoscapeEdge(BaseModel):
    data: CytoscapeEdgeData


class GraphResponse(BaseModel):
    """Full graph structure returned to Cytoscape.js visualization."""
    nodes: List[CytoscapeNode]
    edges: List[CytoscapeEdge]
    stats: Dict[str, Any]


class SHAPFeatureAttribution(BaseModel):
    """Single feature contribution in SHAP explanation."""
    feature_name: str
    feature_value: float
    shap_value: float
    impact_direction: str  # "RISK_INCREASING" or "RISK_DECREASING"
    human_interpretation: str


class AnomalyCluster(BaseModel):
    """Detected anomalous cluster with SHAP attribution and red-ring outline metadata."""
    cluster_id: str
    anomaly_type: str  # "Smurfing", "Fraud Syndicate", "Normal"
    confidence_score: float
    risk_level: str  # CRITICAL, HIGH, MEDIUM, LOW
    node_ids: List[str]
    edge_ids: List[str]
    features: Dict[str, float]
    shap_attributions: List[SHAPFeatureAttribution]
    base_value: float
    prediction_value: float
    human_explanation: str
    recommended_action: str
    detected_at: str


class SystemLog(BaseModel):
    """Audit log entry for system log monitor."""
    id: str
    timestamp: str
    level: str  # INFO, WARN, FRAUD_ALERT
    category: str  # AUTH, TRANSACTION, GRAPH_SCAN, ML_INFERENCE, SECURITY
    message: str
    details: Optional[Dict[str, Any]] = None


class ModelMetricsResponse(BaseModel):
    """Metrics from XGBoost model training."""
    accuracy: float
    precision_macro: float
    recall_macro: float
    f1_macro: float
    classes: List[str]
    smote_sample_counts: Dict[str, int]
    trained_at: str
