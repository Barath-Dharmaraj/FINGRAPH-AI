"""
FinGraph-AI Machine Learning & Explainable AI (SHAP) Pipeline
Handles synthetic dataset generation, SMOTE class balancing, XGBoost training,
and SHAP TreeExplainer feature attributions for graph anomaly detection.
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Any, Optional
from datetime import datetime
import os
import pickle

from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, accuracy_score, precision_recall_fscore_support
from imblearn.over_sampling import SMOTE
import xgboost as xgb
import shap

from backend.models import SHAPFeatureAttribution, ModelMetricsResponse


FEATURE_NAMES = [
    "degree_centrality",
    "pagerank_score",
    "ip_velocity_count",
    "shared_device_account_count",
    "in_out_ratio",
    "tx_amount_mean",
    "rapid_tx_velocity"
]

FEATURE_DESCRIPTIONS = {
    "degree_centrality": "Graph Degree Centrality (fraction of total graph nodes directly connected)",
    "pagerank_score": "PageRank Flow Centrality (structural influence in money routing paths)",
    "ip_velocity_count": "IP Velocity Count (distinct network sessions / IP hops within observation window)",
    "shared_device_account_count": "Shared Device Account Count (number of distinct user profiles linked to identical hardware fingerprint)",
    "in_out_ratio": "Inflow vs Outflow Ratio (volume balance near 1.0 indicates rapid pass-through / layering)",
    "tx_amount_mean": "Mean Transaction Amount ($USD across recent activity)",
    "rapid_tx_velocity": "Rapid Burst Velocity (transactions conducted under 5 minutes)"
}

CLASS_NAMES = ["Normal", "Smurfing", "Fraud Syndicate"]


class FraudMLPipeline:
    """Manages synthetic graph feature data, SMOTE balancing, XGBoost training, and SHAP explainability."""

    def __init__(self):
        self.model: Optional[xgb.XGBClassifier] = None
        self.explainer: Optional[shap.TreeExplainer] = None
        self.feature_names = FEATURE_NAMES
        self.metrics: Optional[ModelMetricsResponse] = None
        self.is_trained = False
        self._initialize_pipeline()

    def generate_synthetic_dataset(self, n_samples: int = 1800, random_state: int = 42) -> pd.DataFrame:
        """
        Generates realistic synthetic multi-account transaction graph features.
        Distributions model financial baseline vs smurfing rings vs shared-device syndicates.
        Class distribution is realistically imbalanced:
          - 0: Normal (~82%)
          - 1: Smurfing (~10%)
          - 2: Fraud Syndicate (~8%)
        """
        np.random.seed(random_state)
        n_normal = int(n_samples * 0.82)
        n_smurf = int(n_samples * 0.10)
        n_syndicate = n_samples - n_normal - n_smurf

        # --- 0: Normal accounts (standard consumers & merchants) ---
        normal_deg = np.random.beta(a=1.5, b=15.0, size=n_normal) * 0.25
        normal_pr = np.random.exponential(scale=0.015, size=n_normal) + 0.002
        normal_ip_vel = np.random.poisson(lam=1.5, size=n_normal) + 1
        normal_dev_acc = np.random.choice([1, 2], size=n_normal, p=[0.92, 0.08])
        normal_in_out = np.random.normal(loc=0.55, scale=0.35, size=n_normal).clip(0.05, 3.5)
        normal_amt = np.random.lognormal(mean=4.2, sigma=1.1, size=n_normal).clip(5.0, 3500.0)
        normal_rapid = np.random.poisson(lam=0.4, size=n_normal)

        df_normal = pd.DataFrame({
            "degree_centrality": normal_deg,
            "pagerank_score": normal_pr,
            "ip_velocity_count": normal_ip_vel,
            "shared_device_account_count": normal_dev_acc,
            "in_out_ratio": normal_in_out,
            "tx_amount_mean": normal_amt,
            "rapid_tx_velocity": normal_rapid,
            "target": 0
        })

        # --- 1: Smurfing rings (structuring, fan-in/fan-out, pass-through ratio ~ 1.0) ---
        smurf_deg = np.random.beta(a=4.0, b=4.0, size=n_smurf) * 0.65 + 0.20
        smurf_pr = np.random.exponential(scale=0.05, size=n_smurf) + 0.04
        smurf_ip_vel = np.random.poisson(lam=4.2, size=n_smurf) + 2
        smurf_dev_acc = np.random.choice([1, 2, 3], size=n_smurf, p=[0.70, 0.25, 0.05])
        # In smurfing / layering, in_out ratio is tightly clustered around 0.90 to 1.10 (pass-through)
        smurf_in_out = np.random.normal(loc=0.98, scale=0.08, size=n_smurf).clip(0.80, 1.25)
        # Amounts structured just below reporting thresholds ($4,500 - $9,800)
        smurf_amt = np.random.uniform(low=4200.0, high=9700.0, size=n_smurf)
        smurf_rapid = np.random.poisson(lam=6.5, size=n_smurf) + 3

        df_smurf = pd.DataFrame({
            "degree_centrality": smurf_deg,
            "pagerank_score": smurf_pr,
            "ip_velocity_count": smurf_ip_vel,
            "shared_device_account_count": smurf_dev_acc,
            "in_out_ratio": smurf_in_out,
            "tx_amount_mean": smurf_amt,
            "rapid_tx_velocity": smurf_rapid,
            "target": 1
        })

        # --- 2: Fraud Syndicate (shared hardware fingerprints, high IP velocity, botnets) ---
        synd_deg = np.random.beta(a=3.0, b=5.0, size=n_syndicate) * 0.45 + 0.10
        synd_pr = np.random.exponential(scale=0.035, size=n_syndicate) + 0.02
        synd_ip_vel = np.random.poisson(lam=9.8, size=n_syndicate) + 5
        # High shared device account count (3 to 8 distinct profiles on same hardware)
        synd_dev_acc = np.random.choice([3, 4, 5, 6, 7, 8], size=n_syndicate, p=[0.25, 0.30, 0.20, 0.12, 0.08, 0.05])
        synd_in_out = np.random.normal(loc=1.4, scale=0.8, size=n_syndicate).clip(0.1, 4.0)
        synd_amt = np.random.lognormal(mean=6.5, sigma=1.4, size=n_syndicate).clip(200.0, 15000.0)
        synd_rapid = np.random.poisson(lam=8.2, size=n_syndicate) + 4

        df_syndicate = pd.DataFrame({
            "degree_centrality": synd_deg,
            "pagerank_score": synd_pr,
            "ip_velocity_count": synd_ip_vel,
            "shared_device_account_count": synd_dev_acc,
            "in_out_ratio": synd_in_out,
            "tx_amount_mean": synd_amt,
            "rapid_tx_velocity": synd_rapid,
            "target": 2
        })

        df = pd.concat([df_normal, df_smurf, df_syndicate], ignore_index=True)
        return df.sample(frac=1.0, random_state=random_state).reset_index(drop=True)

    def train_pipeline(self, n_samples: int = 1800) -> ModelMetricsResponse:
        """
        Executes full ML training pipeline:
          1. Generate synthetic dataset
          2. Train/Test split
          3. SMOTE class balancing on training set
          4. Train multi-class XGBoost Classifier
          5. Build SHAP TreeExplainer
          6. Compute validation metrics
        """
        df = self.generate_synthetic_dataset(n_samples=n_samples)
        X = df[self.feature_names]
        y = df["target"]

        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.25, random_state=42, stratify=y
        )

        # Apply SMOTE to handle class imbalance
        smote = SMOTE(random_state=42)
        X_train_res, y_train_res = smote.fit_resample(X_train, y_train)

        smote_counts = {
            CLASS_NAMES[k]: int(v) for k, v in pd.Series(y_train_res).value_counts().items()
        }

        # Train XGBoost Classifier
        self.model = xgb.XGBClassifier(
            n_estimators=120,
            max_depth=5,
            learning_rate=0.08,
            subsample=0.85,
            colsample_bytree=0.85,
            objective="multi:softprob",
            num_class=3,
            eval_metric="mlogloss",
            random_state=42
        )
        self.model.fit(X_train_res, y_train_res)

        # Initialize SHAP TreeExplainer
        self.explainer = shap.TreeExplainer(self.model)

        # Evaluate on un-resampled test set
        y_pred = self.model.predict(X_test)
        acc = float(accuracy_score(y_test, y_pred))
        prec, rec, f1, _ = precision_recall_fscore_support(y_test, y_pred, average="macro")

        self.metrics = ModelMetricsResponse(
            accuracy=round(acc, 4),
            precision_macro=round(float(prec), 4),
            recall_macro=round(float(rec), 4),
            f1_macro=round(float(f1), 4),
            classes=CLASS_NAMES,
            smote_sample_counts=smote_counts,
            trained_at=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%SZ")
        )

        self.is_trained = True
        return self.metrics

    def _initialize_pipeline(self):
        """Pre-trains model on initial load so the application is instantly ready."""
        try:
            self.train_pipeline(n_samples=1800)
        except Exception as e:
            print(f"Warning during ML pipeline init: {e}")

    def predict_features(self, feature_dict: Dict[str, float]) -> Tuple[int, str, float, np.ndarray]:
        """
        Given a dictionary of graph independent variables, returns:
          (class_idx, class_name, confidence_score, probabilities_array)
        """
        if not self.is_trained or self.model is None:
            self.train_pipeline()

        X_df = pd.DataFrame([[feature_dict.get(fn, 0.0) for fn in self.feature_names]], columns=self.feature_names)
        probs = self.model.predict_proba(X_df)[0]
        class_idx = int(np.argmax(probs))
        class_name = CLASS_NAMES[class_idx]
        confidence = float(probs[class_idx])
        return class_idx, class_name, confidence, probs

    def explain_instance(self, feature_dict: Dict[str, float], predicted_class_idx: Optional[int] = None) -> Dict[str, Any]:
        """
        Computes SHAP feature attributions for a given feature dictionary.
        Returns numerical Shapley values, base value, and an automated human-readable explanation narrative.
        """
        if not self.is_trained or self.explainer is None:
            self.train_pipeline()

        X_df = pd.DataFrame([[feature_dict.get(fn, 0.0) for fn in self.feature_names]], columns=self.feature_names)
        
        # Predict class if not provided
        probs = self.model.predict_proba(X_df)[0]
        if predicted_class_idx is None:
            predicted_class_idx = int(np.argmax(probs))

        # shap_values from TreeExplainer on multi-class returns shape (n_samples, n_features, n_classes) or list of arrays
        raw_shap = self.explainer.shap_values(X_df)
        
        # Format SHAP values for the predicted class
        if isinstance(raw_shap, list):
            class_shap = raw_shap[predicted_class_idx][0]
        elif len(np.shape(raw_shap)) == 3:
            class_shap = raw_shap[0, :, predicted_class_idx]
        else:
            class_shap = raw_shap[0]

        # Base value (expected value)
        expected_val = self.explainer.expected_value
        if isinstance(expected_val, (list, np.ndarray)):
            base_val = float(expected_val[predicted_class_idx])
        else:
            base_val = float(expected_val)

        # Build feature attribution records
        attributions: List[SHAPFeatureAttribution] = []
        for i, fname in enumerate(self.feature_names):
            val = float(X_df.iloc[0, i])
            shap_v = float(class_shap[i])
            impact = "RISK_INCREASING" if shap_v > 0 else "RISK_DECREASING"
            
            # Interpretive snippet
            if fname == "shared_device_account_count" and val >= 3:
                interp = f"{int(val)} distinct accounts routed via identical device fingerprint."
            elif fname == "ip_velocity_count" and val >= 5:
                interp = f"Abnormally high IP switching rate ({int(val)} distinct IP hops)."
            elif fname == "in_out_ratio" and 0.85 <= val <= 1.15:
                interp = f"Layering signature: Inflow tightly matches outflow (ratio={val:.2f})."
            elif fname == "rapid_tx_velocity" and val >= 4:
                interp = f"Rapid burst frequency ({int(val)} txns under 5 mins)."
            elif fname == "degree_centrality" and val >= 0.35:
                interp = f"Elevated network star topology (degree={val:.2f})."
            elif fname == "tx_amount_mean" and val >= 4000:
                interp = f"Transactions structured near threshold (${val:,.2f})."
            else:
                interp = f"{FEATURE_DESCRIPTIONS.get(fname, fname)} recorded at {val:.2f}."

            attributions.append(SHAPFeatureAttribution(
                feature_name=fname,
                feature_value=val,
                shap_value=round(shap_v, 4),
                impact_direction=impact,
                human_interpretation=interp
            ))

        # Sort attributions by absolute SHAP magnitude
        attributions.sort(key=lambda x: abs(x.shap_value), reverse=True)

        # Generate human-readable narrative explanation
        human_explanation, recommended_action = self._generate_analyst_narrative(
            CLASS_NAMES[predicted_class_idx],
            float(probs[predicted_class_idx]),
            attributions
        )

        return {
            "predicted_class": CLASS_NAMES[predicted_class_idx],
            "confidence": round(float(probs[predicted_class_idx]), 4),
            "base_value": round(base_val, 4),
            "prediction_value": round(float(probs[predicted_class_idx]), 4),
            "attributions": attributions,
            "human_explanation": human_explanation,
            "recommended_action": recommended_action
        }

    def _generate_analyst_narrative(
        self,
        predicted_class: str,
        confidence: float,
        attributions: List[SHAPFeatureAttribution]
    ) -> Tuple[str, str]:
        """Synthesizes human-readable AML intelligence narrative from top SHAP feature drivers."""
        top_positive = [a for a in attributions if a.shap_value > 0][:3]
        
        if predicted_class == "Normal":
            narrative = (
                f"Classification: Normal legitimate activity (Confidence: {confidence*100:.1f}%). "
                f"Metrics align with baseline consumer behavior: single primary device access, "
                f"moderate transaction velocity, and typical disperse spending ratios."
            )
            action = "No immediate restriction needed. Maintain standard behavioral monitoring."
            return narrative, action

        if predicted_class == "Smurfing":
            drivers = []
            for a in top_positive:
                if a.feature_name == "in_out_ratio":
                    drivers.append(f"pass-through inflow/outflow balance (ratio={a.feature_value:.2f}, +{a.shap_value:.2f} SHAP)")
                elif a.feature_name == "rapid_tx_velocity":
                    drivers.append(f"rapid burst transaction rate ({int(a.feature_value)} txns in short interval, +{a.shap_value:.2f} SHAP)")
                elif a.feature_name == "degree_centrality":
                    drivers.append(f"high fan-in/fan-out hub connectivity (centrality={a.feature_value:.2f}, +{a.shap_value:.2f} SHAP)")
                elif a.feature_name == "tx_amount_mean":
                    drivers.append(f"structured transaction amounts (${a.feature_value:,.2f}, +{a.shap_value:.2f} SHAP)")
                else:
                    drivers.append(f"{a.feature_name} (+{a.shap_value:.2f} SHAP)")

            driver_str = "; ".join(drivers) if drivers else "graph topology anomalies"
            narrative = (
                f"🚨 RED-RING ALERT: Smurfing / Structuring Pattern Flagged ({confidence*100:.1f}% Confidence). "
                f"The cluster exhibits classic money mule distribution characteristics. "
                f"Key drivers identified by SHAP: {driver_str}. "
                f"This pattern indicates automated fund layering designed to avoid single-transaction regulatory thresholds."
            )
            action = (
                "IMMEDIATE ACTION RECOMMENDED: Temporarily freeze outbound wire/ACH transfers on aggregator and mule accounts. "
                "Initiate FinCEN Form 111 / SAR (Suspicious Activity Report) drafting."
            )
            return narrative, action

        # Fraud Syndicate
        drivers = []
        for a in top_positive:
            if a.feature_name == "shared_device_account_count":
                drivers.append(f"multiple accounts multiplexed on identical hardware ({int(a.feature_value)} accounts, +{a.shap_value:.2f} SHAP)")
            elif a.feature_name == "ip_velocity_count":
                drivers.append(f"elevated IP address hopping ({int(a.feature_value)} proxy IPs, +{a.shap_value:.2f} SHAP)")
            elif a.feature_name == "rapid_tx_velocity":
                drivers.append(f"coordinated script velocity ({int(a.feature_value)} rapid actions, +{a.shap_value:.2f} SHAP)")
            else:
                drivers.append(f"{a.feature_name} (+{a.shap_value:.2f} SHAP)")

        driver_str = "; ".join(drivers) if drivers else "coordinated device telemetry"
        narrative = (
            f"🚨 RED-RING ALERT: Coordinated Fraud Syndicate Detected ({confidence*100:.1f}% Confidence). "
            f"The network cluster represents an organized synthetic identity or account-takeover ring. "
            f"Primary SHAP attribution factors: {driver_str}. "
            f"Shared hardware signatures combined with proxy velocity confirm coordinated syndicate access."
        )
        action = (
            "CRITICAL SECURITY ACTION: Blacklist hardware device fingerprint, revoke all active OAuth/JWT tokens, "
            "force biometric step-up verification for affected user credentials, and isolate involved merchant settlement channels."
        )
        return narrative, action


# Global singleton pipeline instance
ml_pipeline = FraudMLPipeline()
