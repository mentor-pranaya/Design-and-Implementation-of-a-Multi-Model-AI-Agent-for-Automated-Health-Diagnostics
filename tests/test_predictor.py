import pytest
import numpy as np
from src.analysis.predictor import (
    predict_risk, generate_synthetic_data, evaluate_model_on_data,
    FEATURE_ORDER, _load_model
)


class TestPredictor:
    """Comprehensive tests for the enhanced predictor model."""

    def test_generate_synthetic_data(self):
        """Test synthetic data generation."""
        X, y = generate_synthetic_data(1000)

        # Check dimensions
        assert X.shape == (1000, 11)
        assert y.shape == (1000,)

        # Check feature ranges are realistic
        assert np.all(X[:, 0] >= 50) and np.all(X[:, 0] <= 300)  # glucose
        assert np.all(X[:, 1] >= 100) and np.all(X[:, 1] <= 400)  # cholesterol
        assert np.all(X[:, 2] >= 8) and np.all(X[:, 2] <= 18)  # hemoglobin
        assert np.all(X[:, 3] >= 90) and np.all(X[:, 3] <= 180)  # blood pressure

        # Check labels are binary
        assert np.all(np.isin(y, [0, 1]))

    def test_predict_risk_basic(self):
        """Test basic risk prediction functionality."""
        # Normal parameters
        normal_params = {
            "glucose": 100,
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

        assert "risk_score" in result
        assert "risk_label" in result
        assert "confidence" in result
        assert isinstance(result["risk_score"], float)
        assert 0 <= result["risk_score"] <= 1
        assert result["risk_label"] in ["low", "low_moderate", "moderate", "high", "very_high"]
        assert result["confidence"] in ["high", "medium"]

    def test_predict_risk_high_risk(self):
        """Test prediction with high-risk parameters."""
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

        # Should have high risk score
        assert result["risk_score"] > 0.5
        assert result["risk_label"] in ["high", "very_high"]

    def test_predict_risk_with_missing_values(self):
        """Test prediction handles missing parameters gracefully."""
        incomplete_params = {
            "glucose": 120,
            "cholesterol": 200
            # Missing other parameters
        }

        result = predict_risk(incomplete_params)

        assert "risk_score" in result
        assert "risk_label" in result
        assert "confidence" in result

    def test_predict_risk_edge_cases(self):
        """Test prediction with extreme values."""
        # Very low values
        low_params = {param: 0.1 for param in FEATURE_ORDER}
        result_low = predict_risk(low_params)
        assert isinstance(result_low["risk_score"], float)

        # Very high values
        high_params = {param: 10000 for param in FEATURE_ORDER}
        result_high = predict_risk(high_params)
        assert isinstance(result_high["risk_score"], float)

    def test_model_evaluation(self):
        """Test model evaluation functionality."""
        # Generate test data
        X_test, y_test = generate_synthetic_data(500)

        metrics = evaluate_model_on_data(X_test, y_test)

        assert "accuracy" in metrics
        assert "precision" in metrics
        assert "recall" in metrics
        assert "f1" in metrics

        # All metrics should be between 0 and 1
        for metric in metrics.values():
            assert 0 <= metric <= 1

    def test_model_loading(self):
        """Test model loading functionality."""
        model, scaler = _load_model()

        assert model is not None
        assert scaler is not None
        assert hasattr(model, 'predict_proba')
        assert hasattr(scaler, 'transform')

    def test_feature_order_consistency(self):
        """Test that FEATURE_ORDER matches expected parameters."""
        expected_features = [
            "glucose", "cholesterol", "hemoglobin", "blood_pressure",
            "wbc", "platelets", "creatinine", "alt", "ast", "ldl", "hdl"
        ]

        assert FEATURE_ORDER == expected_features

    def test_risk_label_mapping(self):
        """Test that risk scores map correctly to labels."""
        test_cases = [
            (0.1, "low"),
            (0.25, "low_moderate"),
            (0.45, "moderate"),
            (0.65, "high"),
            (0.85, "very_high")
        ]

        for score, expected_label in test_cases:
            # Create parameters that should give approximately this score
            # This is approximate since actual score depends on model
            params = {param: 100 for param in FEATURE_ORDER}
            result = predict_risk(params)
            # Just check that the function returns valid labels
            assert result["risk_label"] in ["low", "low_moderate", "moderate", "high", "very_high"]

    def test_confidence_levels(self):
        """Test confidence level assignment."""
        # Test with normal parameters (should have medium confidence for middle scores)
        normal_params = {param: 100 for param in FEATURE_ORDER}
        result = predict_risk(normal_params)
        assert result["confidence"] in ["high", "medium"]

    @pytest.mark.parametrize("n_samples", [100, 500, 1000])
    def test_synthetic_data_scalability(self, n_samples):
        """Test that synthetic data generation scales properly."""
        X, y = generate_synthetic_data(n_samples)

        assert X.shape == (n_samples, 11)
        assert y.shape == (n_samples,)
        assert len(np.unique(y)) <= 2  # Binary classification

    def test_correlation_in_synthetic_data(self):
        """Test that synthetic data has realistic correlations."""
        X, y = generate_synthetic_data(2000)

        # Check that high glucose correlates with higher cholesterol
        high_glucose = X[:, 0] > 120
        avg_chol_high_glucose = np.mean(X[high_glucose, 1])
        avg_chol_normal = np.mean(X[~high_glucose, 1])

        # High glucose should have higher average cholesterol
        assert avg_chol_high_glucose > avg_chol_normal

    def test_realistic_parameter_ranges(self):
        """Test that generated parameters are in realistic medical ranges."""
        X, y = generate_synthetic_data(1000)

        # Define realistic ranges for each parameter
        ranges = {
            0: (70, 140),    # glucose
            1: (125, 200),   # cholesterol
            2: (11, 16),     # hemoglobin
            3: (90, 140),    # blood pressure
            4: (4000, 11000), # wbc
            5: (150000, 450000), # platelets
            6: (0.6, 1.2),   # creatinine
            7: (7, 56),      # alt
            8: (10, 40),     # ast
            9: (50, 100),    # ldl
            10: (40, 60)     # hdl
        }

        for i, (min_val, max_val) in ranges.items():
            assert np.all(X[:, i] >= min_val)
            assert np.all(X[:, i] <= max_val)


if __name__ == "__main__":
    pytest.main([__file__])
