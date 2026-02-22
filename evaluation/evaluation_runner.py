"""
Evaluation Runner - Validation & Benchmarking for Multi-Model AI System

This module provides comprehensive validation infrastructure to measure:
1. Extraction Accuracy (%)
2. Classification Accuracy, Precision, Recall, F1
3. Pattern Detection Sensitivity/Specificity
4. Risk Scoring Directional Correctness

Transforms the system from "engineering maturity" to "scientific maturity"
by proving performance against ground truth data.

Success Criteria (from architecture document):
- 95% extraction accuracy
- 98% classification accuracy  
- 85% pattern detection accuracy
- 90% recommendation relevance
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict

# Add parent directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'core_phase3'))
sys.path.insert(0, str(Path(__file__).parent))

# Now import modules
from main import Phase3RecommendationPipeline
from gold_standard_dataset import GOLD_STANDARD_DATASET, get_dataset_statistics


class EvaluationMetrics:
    """Calculate standard ML evaluation metrics."""
    
    @staticmethod
    def calculate_accuracy(true_positives: int, true_negatives: int, 
                          false_positives: int, false_negatives: int) -> float:
        """Calculate accuracy: (TP + TN) / (TP + TN + FP + FN)"""
        total = true_positives + true_negatives + false_positives + false_negatives
        if total == 0:
            return 0.0
        return (true_positives + true_negatives) / total
    
    @staticmethod
    def calculate_precision(true_positives: int, false_positives: int) -> float:
        """Calculate precision: TP / (TP + FP)"""
        if true_positives + false_positives == 0:
            return 0.0
        return true_positives / (true_positives + false_positives)
    
    @staticmethod
    def calculate_recall(true_positives: int, false_negatives: int) -> float:
        """Calculate recall (sensitivity): TP / (TP + FN)"""
        if true_positives + false_negatives == 0:
            return 0.0
        return true_positives / (true_positives + false_negatives)
    
    @staticmethod
    def calculate_f1(precision: float, recall: float) -> float:
        """Calculate F1 score: 2 * (precision * recall) / (precision + recall)"""
        if precision + recall == 0:
            return 0.0
        return 2 * (precision * recall) / (precision + recall)
    
    @staticmethod
    def calculate_specificity(true_negatives: int, false_positives: int) -> float:
        """Calculate specificity: TN / (TN + FP)"""
        if true_negatives + false_positives == 0:
            return 0.0
        return true_negatives / (true_negatives + false_positives)


class Model1Evaluator:
    """Evaluate reference-based classification (Model 1)."""
    
    def __init__(self):
        """Initialize Model 1 evaluator."""
        self.results = defaultdict(lambda: {"tp": 0, "tn": 0, "fp": 0, "fn": 0})
        self.classification_errors = []
    
    def evaluate(self, predicted: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate classification performance.
        
        Args:
            predicted: System's classification output
            ground_truth: Gold standard classification
        
        Returns:
            Evaluation metrics
        """
        total_correct = 0
        total_parameters = len(ground_truth)
        
        for param_name, gt in ground_truth.items():
            # Find predicted classification
            pred = self._find_prediction(predicted, param_name)
            
            if pred is None:
                self.classification_errors.append({
                    "parameter": param_name,
                    "error": "Not found in predictions",
                    "expected": gt["status"]
                })
                self.results["overall"]["fn"] += 1
                continue
            
            # Normalize status strings
            pred_status = self._normalize_status(pred.get("status"))
            gt_status = self._normalize_status(gt["status"])
            
            # Check if classification matches
            if pred_status == gt_status:
                total_correct += 1
                self.results["overall"]["tp"] += 1
                self.results[param_name]["tp"] += 1
            else:
                self.classification_errors.append({
                    "parameter": param_name,
                    "predicted": pred_status,
                    "expected": gt_status,
                    "value": pred.get("value"),
                    "reference": pred.get("reference_range")
                })
                self.results["overall"]["fp"] += 1
                self.results[param_name]["fp"] += 1
        
        accuracy = (total_correct / total_parameters * 100) if total_parameters > 0 else 0
        
        return {
            "accuracy_percent": round(accuracy, 2),
            "correct": total_correct,
            "total": total_parameters,
            "errors": self.classification_errors
        }
    
    def _find_prediction(self, predicted: Dict[str, Any], param_name: str) -> Dict[str, Any]:
        """Find prediction for a specific parameter."""
        evaluations = predicted.get("phase_3a_evaluation", {}).get("evaluations", [])
        for eval in evaluations:
            if eval.get("parameter") == param_name:
                return eval
        return None
    
    def _normalize_status(self, status: str) -> str:
        """Normalize status string for comparison."""
        if hasattr(status, 'value'):
            status = status.value
        return str(status).lower().replace('_', ' ').strip()
    
    def get_confusion_matrix(self) -> Dict[str, Any]:
        """Generate confusion matrix for overall classification."""
        metrics = self.results["overall"]
        return {
            "true_positives": metrics["tp"],
            "true_negatives": metrics["tn"],
            "false_positives": metrics["fp"],
            "false_negatives": metrics["fn"],
            "precision": EvaluationMetrics.calculate_precision(metrics["tp"], metrics["fp"]),
            "recall": EvaluationMetrics.calculate_recall(metrics["tp"], metrics["fn"]),
            "f1_score": EvaluationMetrics.calculate_f1(
                EvaluationMetrics.calculate_precision(metrics["tp"], metrics["fp"]),
                EvaluationMetrics.calculate_recall(metrics["tp"], metrics["fn"])
            )
        }


class Model2Evaluator:
    """Evaluate pattern detection (Model 2)."""
    
    def __init__(self):
        """Initialize Model 2 evaluator."""
        self.pattern_results = {"tp": 0, "fp": 0, "fn": 0}
        self.pattern_errors = []
    
    def evaluate(self, predicted: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate pattern detection performance.
        
        Args:
            predicted: System's pattern detection output
            ground_truth: Gold standard patterns
        
        Returns:
            Evaluation metrics
        """
        expected_patterns = {p["pattern"] for p in ground_truth.get("expected_patterns", [])}
        absent_patterns = set(ground_truth.get("absent_patterns", []))
        
        # Get detected patterns
        detected_patterns = set()
        phase3b = predicted.get("phase_3b_patterns", [])
        for pattern in phase3b:
            pattern_name = pattern.get("pattern", "")
            detected_patterns.add(pattern_name)
        
        # Calculate true positives (correctly detected)
        true_positives = expected_patterns.intersection(detected_patterns)
        self.pattern_results["tp"] += len(true_positives)
        
        # Calculate false negatives (missed patterns)
        false_negatives = expected_patterns - detected_patterns
        self.pattern_results["fn"] += len(false_negatives)
        for fn in false_negatives:
            self.pattern_errors.append({
                "type": "False Negative",
                "pattern": fn,
                "error": "Expected but not detected"
            })
        
        # Calculate false positives (incorrectly detected)
        false_positives = detected_patterns - expected_patterns
        # Filter out patterns that should be absent
        false_positives = false_positives.intersection(absent_patterns)
        self.pattern_results["fp"] += len(false_positives)
        for fp in false_positives:
            self.pattern_errors.append({
                "type": "False Positive",
                "pattern": fp,
                "error": "Detected but should be absent"
            })
        
        # Calculate metrics
        precision = EvaluationMetrics.calculate_precision(
            self.pattern_results["tp"],
            self.pattern_results["fp"]
        )
        recall = EvaluationMetrics.calculate_recall(
            self.pattern_results["tp"],
            self.pattern_results["fn"]
        )
        f1 = EvaluationMetrics.calculate_f1(precision, recall)
        
        return {
            "detected": len(detected_patterns),
            "expected": len(expected_patterns),
            "true_positives": len(true_positives),
            "false_negatives": len(false_negatives),
            "false_positives": len(false_positives),
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
            "errors": self.pattern_errors
        }


class RiskScoringEvaluator:
    """Evaluate quantified risk scoring."""
    
    def __init__(self):
        """Initialize risk scoring evaluator."""
        self.risk_results = []
    
    def evaluate(self, predicted: Dict[str, Any], ground_truth: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate risk scoring directional correctness.
        
        Args:
            predicted: System's risk scoring output
            ground_truth: Gold standard risk assessment
        
        Returns:
            Evaluation metrics
        """
        cv_risk_pred = predicted.get("phase_3e_risk_scoring", {}).get("cardiovascular_risk")
        cv_risk_gt = ground_truth.get("cardiovascular", {})
        
        if not cv_risk_pred or "error" in cv_risk_pred:
            return {
                "status": "error",
                "message": "Risk scoring not available"
            }
        
        # Check category match
        pred_category = cv_risk_pred.get("risk_category")
        expected_category = cv_risk_gt.get("expected_category")
        category_match = pred_category == expected_category
        
        # Check if risk estimate is in expected range
        pred_risk = cv_risk_pred.get("estimated_10_year_risk_percent")
        expected_range = cv_risk_gt.get("expected_range", {})
        in_range = expected_range.get("min", 0) <= pred_risk <= expected_range.get("max", 100)
        
        # Check trigger overlap
        pred_triggers = set(cv_risk_pred.get("criteria_triggers", []))
        expected_triggers = set(cv_risk_gt.get("expected_triggers", []))
        trigger_overlap = len(pred_triggers.intersection(expected_triggers)) / len(expected_triggers) if expected_triggers else 0
        
        result = {
            "category_match": category_match,
            "predicted_category": pred_category,
            "expected_category": expected_category,
            "risk_in_range": in_range,
            "predicted_risk_percent": pred_risk,
            "expected_range": expected_range,
            "trigger_overlap_percent": round(trigger_overlap * 100, 1),
            "rationale": cv_risk_gt.get("rationale", "")
        }
        
        self.risk_results.append(result)
        return result


class EvaluationRunner:
    """Main evaluation orchestrator."""
    
    def __init__(self):
        """Initialize evaluation runner."""
        self.pipeline = Phase3RecommendationPipeline()
        self.model1_evaluator = Model1Evaluator()
        self.model2_evaluator = Model2Evaluator()
        self.risk_evaluator = RiskScoringEvaluator()
    
    def run_full_validation(self) -> Dict[str, Any]:
        """
        Run complete validation suite against gold standard dataset.
        
        Returns:
            Comprehensive evaluation report
        """
        print("\n" + "="*80)
        print("RUNNING VALIDATION SUITE")
        print("="*80)
        
        results = {
            "dataset_stats": get_dataset_statistics(),
            "model1_classification": {},
            "model2_pattern_detection": {},
            "risk_scoring": {},
            "test_case_results": []
        }
        
        # Process each test case
        for case_id, case_data in GOLD_STANDARD_DATASET.items():
            print(f"\n[{case_id}] {case_data['description']}")
            
            # Load source data
            source_file = Path(__file__).parent.parent / 'data' / 'sample_reports' / case_data['source_file']
            with open(source_file, 'r') as f:
                report_data = json.load(f)
            
            # Convert to phase 3 format
            extracted_params = [
                {"parameter": p["name"], "value": p["value"], "unit": p.get("unit", "")}
                for p in report_data["parameters"]
            ]
            patient_info = report_data["patient_info"].copy()
            if 'gender' in patient_info:
                patient_info['sex'] = patient_info['gender']
            
            # Run pipeline
            predicted = self.pipeline.process_extracted_parameters(extracted_params, patient_info)
            
            # Evaluate Model 1 (Classification)
            m1_result = self.model1_evaluator.evaluate(
                predicted,
                case_data["classification_ground_truth"]
            )
            
            # Evaluate Model 2 (Pattern Detection)
            m2_result = self.model2_evaluator.evaluate(
                predicted,
                case_data["pattern_ground_truth"]
            )
            
            # Evaluate Risk Scoring
            risk_result = self.risk_evaluator.evaluate(
                predicted,
                case_data["risk_scoring_ground_truth"]
            )
            
            # Store case results
            results["test_case_results"].append({
                "case_id": case_id,
                "classification": m1_result,
                "pattern_detection": m2_result,
                "risk_scoring": risk_result
            })
        
        # Calculate aggregate metrics
        results["model1_classification"] = self._aggregate_model1_results()
        results["model2_pattern_detection"] = self._aggregate_model2_results()
        results["risk_scoring"] = self._aggregate_risk_results()
        
        return results
    
    def _aggregate_model1_results(self) -> Dict[str, Any]:
        """Aggregate Model 1 classification results."""
        confusion_matrix = self.model1_evaluator.get_confusion_matrix()
        return {
            "confusion_matrix": confusion_matrix,
            "total_errors": len(self.model1_evaluator.classification_errors),
            "error_details": self.model1_evaluator.classification_errors[:10]  # First 10 errors
        }
    
    def _aggregate_model2_results(self) -> Dict[str, Any]:
        """Aggregate Model 2 pattern detection results."""
        metrics = self.model2_evaluator.pattern_results
        precision = EvaluationMetrics.calculate_precision(metrics["tp"], metrics["fp"])
        recall = EvaluationMetrics.calculate_recall(metrics["tp"], metrics["fn"])
        f1 = EvaluationMetrics.calculate_f1(precision, recall)
        
        return {
            "true_positives": metrics["tp"],
            "false_positives": metrics["fp"],
            "false_negatives": metrics["fn"],
            "precision": round(precision, 3),
            "recall": round(recall, 3),
            "f1_score": round(f1, 3),
            "error_details": self.model2_evaluator.pattern_errors
        }
    
    def _aggregate_risk_results(self) -> Dict[str, Any]:
        """Aggregate risk scoring results."""
        if not self.risk_evaluator.risk_results:
            return {"status": "no_results"}
        
        category_matches = sum(1 for r in self.risk_evaluator.risk_results if r["category_match"])
        range_matches = sum(1 for r in self.risk_evaluator.risk_results if r["risk_in_range"])
        total = len(self.risk_evaluator.risk_results)
        
        return {
            "category_accuracy": round(category_matches / total * 100, 1) if total > 0 else 0,
            "range_accuracy": round(range_matches / total * 100, 1) if total > 0 else 0,
            "total_cases": total,
            "results": self.risk_evaluator.risk_results
        }
    
    def generate_performance_report(self, results: Dict[str, Any], output_path: Path = None):
        """
        Generate comprehensive performance report.
        
        Args:
            results: Validation results
            output_path: Optional path to save report
        """
        report = []
        report.append("="*80)
        report.append("VALIDATION PERFORMANCE REPORT")
        report.append("="*80)
        
        # Dataset stats
        stats = results["dataset_stats"]
        report.append(f"\nDataset Statistics:")
        report.append(f"  Test Cases: {stats['total_test_cases']}")
        report.append(f"  Parameters: {stats['total_parameters']}")
        report.append(f"  Classifications: {stats['total_classifications']}")
        report.append(f"  Patterns: {stats['total_patterns']}")
        
        # Model 1 Results
        m1 = results["model1_classification"]
        cm = m1.get("confusion_matrix", {})
        report.append(f"\n[ MODEL 1: Reference-Based Classification ]")
        report.append(f"  Precision: {cm.get('precision', 0):.3f}")
        report.append(f"  Recall: {cm.get('recall', 0):.3f}")
        report.append(f"  F1 Score: {cm.get('f1_score', 0):.3f}")
        report.append(f"  Errors: {m1.get('total_errors', 0)}")
        
        # Model 2 Results
        m2 = results["model2_pattern_detection"]
        report.append(f"\n[ MODEL 2: Pattern Detection ]")
        report.append(f"  Precision: {m2.get('precision', 0):.3f}")
        report.append(f"  Recall (Sensitivity): {m2.get('recall', 0):.3f}")
        report.append(f"  F1 Score: {m2.get('f1_score', 0):.3f}")
        report.append(f"  True Positives: {m2.get('true_positives', 0)}")
        report.append(f"  False Positives: {m2.get('false_positives', 0)}")
        report.append(f"  False Negatives: {m2.get('false_negatives', 0)}")
        
        # Risk Scoring Results
        risk = results["risk_scoring"]
        if "status" not in risk:
            report.append(f"\n[ RISK SCORING: Cardiovascular ]")
            report.append(f"  Category Accuracy: {risk.get('category_accuracy', 0):.1f}%")
            report.append(f"  Range Accuracy: {risk.get('range_accuracy', 0):.1f}%")
        
        report.append("\n" + "="*80)
        
        report_text = "\n".join(report)
        print(report_text)
        
        if output_path:
            output_path.write_text(report_text)
            print(f"\n✓ Report saved to {output_path}")


def main():
    """Run validation suite."""
    runner = EvaluationRunner()
    results = runner.run_full_validation()
    
    # Generate report
    output_path = Path(__file__).parent / "validation_report.txt"
    runner.generate_performance_report(results, output_path)
    
    # Save detailed results as JSON
    json_path = Path(__file__).parent / "validation_results.json"
    with open(json_path, 'w') as f:
        # Convert enum values to strings for JSON serialization
        json.dump(results, f, indent=2, default=str)
    print(f"✓ Detailed results saved to {json_path}")


if __name__ == "__main__":
    main()
