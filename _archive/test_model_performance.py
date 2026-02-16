#!/usr/bin/env python3
"""
Simple test script to validate the enhanced AI model performance.
Tests the predictor model with various scenarios.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.analysis.predictor import predict_risk, generate_synthetic_data, evaluate_model_on_data

def test_normal_parameters():
    """Test with normal blood parameters."""
    print("Testing Normal Parameters...")
    normal_params = {
        "glucose": 95,
        "cholesterol": 180,
        "hemoglobin": 14,
        "blood_pressure": 120,
        "wbc": 7500,
        "platelets": 250000,
        "creatinine": 0.9,
        "alt": 25,
        "ast": 25,
        "ldl": 100,
        "hdl": 50
    }

    result = predict_risk(normal_params)
    print(f"   Risk Score: {result['risk_score']:.4f}")
    print(f"   Risk Label: {result['risk_label']}")
    print(f"   Confidence: {result['confidence']}")

    # Normal parameters should have low risk
    assert result['risk_label'] in ['low', 'low_moderate'], f"Expected low risk, got {result['risk_label']}"
    print("   [PASS] Normal parameters test passed")

def test_high_risk_parameters():
    """Test with high-risk blood parameters."""
    print("Testing High-Risk Parameters...")
    high_risk_params = {
        "glucose": 200,  # Very high
        "cholesterol": 300,  # High
        "hemoglobin": 10,  # Low
        "blood_pressure": 160,  # High
        "wbc": 15000,  # High
        "platelets": 100000,  # Low
        "creatinine": 2.0,  # High
        "alt": 80,  # High
        "ast": 70,  # High
        "ldl": 200,  # High
        "hdl": 30  # Low
    }

    result = predict_risk(high_risk_params)
    print(f"   Risk Score: {result['risk_score']:.4f}")
    print(f"   Risk Label: {result['risk_label']}")
    print(f"   Confidence: {result['confidence']}")

    # High-risk parameters should have high risk
    assert result['risk_score'] > 0.5, f"Expected high risk score, got {result['risk_score']}"
    assert result['risk_label'] in ['high', 'very_high'], f"Expected high risk, got {result['risk_label']}"
    print("   [PASS] High-risk parameters test passed")

def test_missing_parameters():
    """Test with missing parameters."""
    print("Testing Missing Parameters...")
    incomplete_params = {
        "glucose": 120,
        "cholesterol": 200
        # Missing other parameters
    }

    result = predict_risk(incomplete_params)
    print(f"   Risk Score: {result['risk_score']:.4f}")
    print(f"   Risk Label: {result['risk_label']}")
    print(f"   Confidence: {result['confidence']}")

    # Should still work with defaults
    assert isinstance(result['risk_score'], float), "Risk score should be a float"
    assert result['risk_label'] in ['low', 'low_moderate', 'moderate', 'high', 'very_high'], "Invalid risk label"
    print("   [PASS] Missing parameters test passed")

def test_model_evaluation():
    """Test model evaluation on synthetic data."""
    print("Testing Model Evaluation...")
    X_test, y_test = generate_synthetic_data(1000)

    metrics = evaluate_model_on_data(X_test, y_test)
    print(f"   Accuracy: {metrics['accuracy']:.4f}")
    print(f"   Precision: {metrics['precision']:.4f}")
    print(f"   Recall: {metrics['recall']:.4f}")
    print(f"   F1-Score: {metrics['f1']:.4f}")

    # Model should perform reasonably well
    assert metrics['accuracy'] > 0.7, f"Accuracy too low: {metrics['accuracy']}"
    assert metrics['f1'] > 0.7, f"F1-score too low: {metrics['f1']}"
    print("   [PASS] Model evaluation test passed")

def test_edge_cases():
    """Test edge cases."""
    print("Testing Edge Cases...")

    # Very low values
    low_params = {param: 0.1 for param in ["glucose", "cholesterol", "hemoglobin", "blood_pressure", "wbc", "platelets", "creatinine", "alt", "ast", "ldl", "hdl"]}
    result_low = predict_risk(low_params)
    assert isinstance(result_low['risk_score'], float), "Should handle very low values"

    # Very high values
    high_params = {param: 10000 for param in ["glucose", "cholesterol", "hemoglobin", "blood_pressure", "wbc", "platelets", "creatinine", "alt", "ast", "ldl", "hdl"]}
    result_high = predict_risk(high_params)
    assert isinstance(result_high['risk_score'], float), "Should handle very high values"

    print("   [PASS] Edge cases test passed")

def main():
    """Run all tests."""
    print("ENHANCED AI MODEL PERFORMANCE TESTING")
    print("=" * 50)

    try:
        test_normal_parameters()
        test_high_risk_parameters()
        test_missing_parameters()
        test_model_evaluation()
        test_edge_cases()

        print("\n" + "=" * 50)
        print("ALL TESTS PASSED!")
        print("Enhanced AI Model is working correctly")
        print("\nModel Features:")
        print("   - Random Forest classifier with hyperparameter tuning")
        print("   - Feature scaling and cross-validation")
        print("   - Comprehensive evaluation metrics")
        print("   - Realistic synthetic data generation")
        print("   - Robust handling of missing parameters")

    except Exception as e:
        print(f"\nTEST FAILED: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
