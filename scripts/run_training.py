"""
Standalone ML Pipeline Training & Evaluation Script
Tests synthetic data generation, SMOTE oversampling, XGBoost model training,
and SHAP TreeExplainer feature attributions.
"""

import sys
import os

# Ensure UTF-8 output on Windows terminal
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Add parent directory to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from backend.ml_pipeline import FraudMLPipeline, CLASS_NAMES


def main():
    print("=" * 70)
    print(" FinGraph-AI: Machine Learning Pipeline Verification")
    print("=" * 70)

    pipeline = FraudMLPipeline()
    print("\n[1] Training XGBoost model with SMOTE class balancing...")
    metrics = pipeline.train_pipeline(n_samples=2000)

    print(f"    - Accuracy:        {metrics.accuracy * 100:.2f}%")
    print(f"    - Precision Macro: {metrics.precision_macro * 100:.2f}%")
    print(f"    - Recall Macro:    {metrics.recall_macro * 100:.2f}%")
    print(f"    - F1 Score Macro:  {metrics.f1_macro * 100:.2f}%")
    print(f"    - SMOTE Balanced Sample Counts:")
    for cls_name, count in metrics.smote_sample_counts.items():
        print(f"        * {cls_name}: {count} samples")

    # Test Sample 1: Normal Consumer
    print("\n[2] Testing Inference & SHAP on Normal Profile:")
    normal_features = {
        "degree_centrality": 0.08,
        "pagerank_score": 0.012,
        "ip_velocity_count": 2,
        "shared_device_account_count": 1,
        "in_out_ratio": 0.45,
        "tx_amount_mean": 85.0,
        "rapid_tx_velocity": 0
    }
    exp_normal = pipeline.explain_instance(normal_features)
    print(f"    Result: {exp_normal['predicted_class']} (Confidence: {exp_normal['confidence']*100:.1f}%)")
    print(f"    Analyst Narrative: {exp_normal['human_explanation'][:120]}...")

    # Test Sample 2: Smurfing Ring
    print("\n[3] Testing Inference & SHAP on Smurfing Ring Profile:")
    smurf_features = {
        "degree_centrality": 0.52,
        "pagerank_score": 0.065,
        "ip_velocity_count": 5,
        "shared_device_account_count": 2,
        "in_out_ratio": 0.99,
        "tx_amount_mean": 6800.0,
        "rapid_tx_velocity": 8
    }
    exp_smurf = pipeline.explain_instance(smurf_features)
    print(f"    Result: {exp_smurf['predicted_class']} (Confidence: {exp_smurf['confidence']*100:.1f}%)")
    print("    Top SHAP Feature Attributions:")
    for attr in exp_smurf["attributions"][:3]:
        print(f"      * {attr.feature_name}: {attr.feature_value} -> SHAP: {attr.shap_value:+.4f} ({attr.impact_direction})")
    print(f"    Human Explanation:\n    {exp_smurf['human_explanation']}")

    # Test Sample 3: Fraud Syndicate
    print("\n[4] Testing Inference & SHAP on Fraud Syndicate Profile:")
    synd_features = {
        "degree_centrality": 0.38,
        "pagerank_score": 0.045,
        "ip_velocity_count": 14,
        "shared_device_account_count": 6,
        "in_out_ratio": 1.45,
        "tx_amount_mean": 3200.0,
        "rapid_tx_velocity": 11
    }
    exp_synd = pipeline.explain_instance(synd_features)
    print(f"    Result: {exp_synd['predicted_class']} (Confidence: {exp_synd['confidence']*100:.1f}%)")
    print("    Top SHAP Feature Attributions:")
    for attr in exp_synd["attributions"][:3]:
        print(f"      * {attr.feature_name}: {attr.feature_value} -> SHAP: {attr.shap_value:+.4f} ({attr.impact_direction})")
    print(f"    Human Explanation:\n    {exp_synd['human_explanation']}")
    print(f"    Action: {exp_synd['recommended_action']}")

    print("\n" + "=" * 70)
    print(" Machine Learning & SHAP Pipeline Verification Completed Successfully!")
    print("=" * 70)


if __name__ == "__main__":
    main()
