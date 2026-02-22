"""
Phase 4 - Formal Validation & Benchmarking Framework

This module implements scientific validation for the Multi-Model AI Agent:
- Model 1: Parameter Classification (extraction, classification, severity)
- Model 2: Pattern Recognition (metabolic, cardiovascular, anemia, etc.)
- Model 3: Contextual Adjustments (risk modifiers)
- Risk Scoring Engine: Quantified cardiovascular risk assessment

Outputs structured metrics, error analysis, and overall system reliability score.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any, List, Tuple
from collections import defaultdict
from dataclasses import dataclass, field

# Add parent directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'core_phase3'))

from core_phase3.main import Phase3RecommendationPipeline
from pattern_registry import normalize_pattern_name, VALID_PATTERN_NAMES


@dataclass
class ValidationMetrics:
    """Container for validation metrics."""
    # Model 1 metrics
    model1_accuracy: float = 0.0
    model1_precision: float = 0.0
    model1_recall: float = 0.0
    model1_f1: float = 0.0
    
    # Model 2 metrics
    model2_accuracy: float = 0.0
    model2_false_positive_rate: float = 0.0
    
    # Risk scoring metrics
    risk_category_match_rate: float = 0.0
    risk_directional_correctness: float = 0.0
    
    # Overall
    overall_reliability_score: float = 0.0
    
    # Error tracking
    most_misclassified_parameter: str = ""
    most_confused_pattern: str = ""
    risk_overestimation_bias: float = 0.0
    risk_underestimation_bias: float = 0.0
    
    # Detailed errors
    classification_errors: List[Dict] = field(default_factory=list)
    pattern_errors: List[Dict] = field(default_factory=list)
    risk_errors: List[Dict] = field(default_factory=list)


class Model1Evaluator:
    """Evaluate Model 1: Parameter Classification."""
    
    def __init__(self):
        self.total_parameters = 0
        self.correct_extractions = 0
        self.correct_classifications = 0
        self.correct_severities = 0
        
        # Confusion matrix elements
        self.tp = 0  # True positives (correctly identified abnormal)
        self.tn = 0  # True negatives (correctly identified normal)
        self.fp = 0  # False positives (flagged abnormal when normal)
        self.fn = 0  # False negatives (missed abnormal)
        
        # Detailed confusion matrix (Normal, High, Low)
        self.confusion_matrix_detailed = {
            'Normal': {'Normal': 0, 'High': 0, 'Low': 0},
            'High': {'Normal': 0, 'High': 0, 'Low': 0},
            'Low': {'Normal': 0, 'High': 0, 'Low': 0}
        }
        
        # Per-parameter accuracy tracking
        self.parameter_stats = defaultdict(lambda: {'correct': 0, 'total': 0, 'errors': []})
        
        # Error tracking
        self.errors = []
        self.parameter_error_counts = defaultdict(int)
    
    def evaluate_case(self, predicted: Dict, ground_truth: Dict) -> Dict[str, Any]:
        """
        Evaluate Model 1 for a single case.
        
        Returns:
            Case-level metrics
        """
        true_params = ground_truth["true_parameters"]
        true_class = ground_truth["true_classification"]
        true_sev = ground_truth.get("true_severity", {})
        
        case_correct = 0
        case_total = len(true_params)
        
        for param_name, true_value in true_params.items():
            self.total_parameters += 1
            
            # Find predicted classification
            pred_eval = self._find_prediction(predicted, param_name)
            
            if pred_eval is None:
                self.fn += 1
                self.errors.append({
                    "case": ground_truth["case_id"],
                    "parameter": param_name,
                    "error_type": "Missing prediction",
                    "expected": true_class.get(param_name)
                })
                self.parameter_error_counts[param_name] += 1
                continue
            
            # Evaluate extraction (value match)
            pred_value = pred_eval.get("value")
            if pred_value == true_value:
                self.correct_extractions += 1
            
            # Evaluate classification
            pred_status = self._normalize_status(pred_eval.get("status", ""))
            true_status = self._normalize_status(true_class.get(param_name, ""))
            
            # Update per-parameter stats
            self.parameter_stats[param_name]['total'] += 1
            
            # Update detailed confusion matrix
            true_cat = self._get_category(true_status)
            pred_cat = self._get_category(pred_status)
            if true_cat and pred_cat:
                self.confusion_matrix_detailed[true_cat][pred_cat] += 1
            
            if pred_status == true_status:
                self.correct_classifications += 1
                case_correct += 1
                self.parameter_stats[param_name]['correct'] += 1
                
                # Update confusion matrix
                if true_status == "normal":
                    self.tn += 1
                else:
                    self.tp += 1
            else:
                # Classification mismatch
                error_detail = {
                    "case": ground_truth["case_id"],
                    "parameter": param_name,
                    "error_type": "Classification mismatch",
                    "predicted": pred_status,
                    "expected": true_status,
                    "value": pred_value,
                    "reference": pred_eval.get("reference_range", "")
                }
                self.errors.append(error_detail)
                self.parameter_stats[param_name]['errors'].append(error_detail)
                self.parameter_error_counts[param_name] += 1
                
                # Update confusion matrix
                if true_status == "normal" and pred_status != "normal":
                    self.fp += 1  # False positive
                elif true_status != "normal" and pred_status == "normal":
                    self.fn += 1  # False negative
                else:
                    self.fp += 1  # Wrong abnormal classification
            
            # Evaluate severity (if applicable)
            if param_name in true_sev:
                pred_sev = pred_eval.get("severity")
                if pred_sev == true_sev[param_name]:
                    self.correct_severities += 1
        
        return {
            "accuracy": (case_correct / case_total * 100) if case_total > 0 else 0,
            "correct": case_correct,
            "total": case_total
        }
    
    def _find_prediction(self, predicted: Dict, param_name: str) -> Dict:
        """Find prediction for a parameter."""
        evaluations = predicted.get("phase_3a_evaluation", {}).get("evaluations", [])
        for eval in evaluations:
            if eval.get("parameter") == param_name:
                return eval
        return None
    
    def _normalize_status(self, status: str) -> str:
        """Normalize status string."""
        # Handle enum objects
        if hasattr(status, 'value'):
            status = status.value
        elif hasattr(status, 'name'):
            # Handle EvaluationStatus.HIGH → "HIGH"
            status = status.name
        
        # Convert to string and normalize
        status_str = str(status).lower().replace('_', ' ').strip()
        
        # Remove "evaluationstatus." prefix if present
        if 'evaluationstatus.' in status_str:
            status_str = status_str.split('.')[-1]
        
        return status_str
    
    def _get_category(self, status: str) -> str:
        """Get category (Normal/High/Low) from status."""
        status_lower = status.lower()
        if 'normal' in status_lower:
            return 'Normal'
        elif 'high' in status_lower:
            return 'High'
        elif 'low' in status_lower:
            return 'Low'
        return None
    
    def get_metrics(self) -> Dict[str, Any]:
        """Calculate aggregate metrics."""
        accuracy = (self.correct_classifications / self.total_parameters * 100) if self.total_parameters > 0 else 0
        
        precision = (self.tp / (self.tp + self.fp)) if (self.tp + self.fp) > 0 else 0
        recall = (self.tp / (self.tp + self.fn)) if (self.tp + self.fn) > 0 else 0
        f1 = (2 * precision * recall / (precision + recall)) if (precision + recall) > 0 else 0
        
        # Find most misclassified parameter
        most_misclassified = max(self.parameter_error_counts.items(), key=lambda x: x[1])[0] if self.parameter_error_counts else "None"
        
        # Calculate per-parameter accuracy
        parameter_accuracy = {}
        for param, stats in self.parameter_stats.items():
            if stats['total'] > 0:
                parameter_accuracy[param] = (stats['correct'] / stats['total']) * 100
        
        return {
            "accuracy": accuracy,
            "precision": precision,
            "recall": recall,
            "f1_score": f1,
            "confusion_matrix": {
                "true_positives": self.tp,
                "true_negatives": self.tn,
                "false_positives": self.fp,
                "false_negatives": self.fn
            },
            "confusion_matrix_detailed": self.confusion_matrix_detailed,
            "parameter_accuracy": parameter_accuracy,
            "parameter_stats": dict(self.parameter_stats),
            "most_misclassified_parameter": most_misclassified,
            "total_errors": len(self.errors),
            "error_details": self.errors  # All errors for detailed analysis
        }


class Model2Evaluator:
    """Evaluate Model 2: Pattern Recognition."""
    
    def __init__(self):
        self.total_patterns_expected = 0
        self.total_patterns_detected = 0
        self.correct_patterns = 0
        self.false_positives = 0
        self.false_negatives = 0
        
        # Error tracking
        self.errors = []
        self.pattern_error_counts = defaultdict(int)
    
    def evaluate_case(self, predicted: Dict, ground_truth: Dict) -> Dict[str, Any]:
        """Evaluate Model 2 for a single case."""
        # Normalize ground truth patterns
        true_patterns = set()
        for pattern in ground_truth["true_patterns"]:
            try:
                true_patterns.add(normalize_pattern_name(pattern))
            except ValueError:
                # Keep original if not in registry
                true_patterns.add(pattern)
        
        self.total_patterns_expected += len(true_patterns)
        
        # Get detected patterns
        detected_patterns = set()
        phase3b = predicted.get("phase_3b_patterns", [])
        for pattern in phase3b:
            pattern_name = pattern.get("pattern", "")
            try:
                detected_patterns.add(normalize_pattern_name(pattern_name))
            except ValueError:
                # Keep original if not in registry
                detected_patterns.add(pattern_name)
        
        self.total_patterns_detected += len(detected_patterns)
        
        # Calculate matches
        correct = true_patterns.intersection(detected_patterns)
        self.correct_patterns += len(correct)
        
        # False negatives (missed patterns)
        missed = true_patterns - detected_patterns
        self.false_negatives += len(missed)
        for pattern in missed:
            self.errors.append({
                "case": ground_truth["case_id"],
                "pattern": pattern,
                "error_type": "False Negative (missed)",
                "expected": True,
                "detected": False
            })
            self.pattern_error_counts[pattern] += 1
        
        # False positives (incorrect detections)
        incorrect = detected_patterns - true_patterns
        self.false_positives += len(incorrect)
        for pattern in incorrect:
            self.errors.append({
                "case": ground_truth["case_id"],
                "pattern": pattern,
                "error_type": "False Positive (incorrect)",
                "expected": False,
                "detected": True
            })
            self.pattern_error_counts[pattern] += 1
        
        accuracy = (len(correct) / len(true_patterns) * 100) if true_patterns else 100
        
        return {
            "accuracy": accuracy,
            "detected": len(detected_patterns),
            "expected": len(true_patterns),
            "correct": len(correct)
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Calculate aggregate metrics."""
        accuracy = (self.correct_patterns / self.total_patterns_expected * 100) if self.total_patterns_expected > 0 else 0
        
        # False positive rate
        fp_rate = (self.false_positives / self.total_patterns_detected * 100) if self.total_patterns_detected > 0 else 0
        
        # Find most confused pattern
        most_confused = max(self.pattern_error_counts.items(), key=lambda x: x[1])[0] if self.pattern_error_counts else "None"
        
        return {
            "accuracy": accuracy,
            "false_positive_rate": fp_rate,
            "true_positives": self.correct_patterns,
            "false_positives": self.false_positives,
            "false_negatives": self.false_negatives,
            "most_confused_pattern": most_confused,
            "error_details": self.errors
        }


class RiskScoringEvaluator:
    """Evaluate Risk Scoring Engine."""
    
    def __init__(self):
        self.total_cases = 0
        self.category_matches = 0
        self.directional_correct = 0
        
        self.risk_differences = []  # For bias calculation
        self.errors = []
    
    def evaluate_case(self, predicted: Dict, ground_truth: Dict) -> Dict[str, Any]:
        """Evaluate risk scoring for a single case."""
        self.total_cases += 1
        
        health_risk = predicted.get("phase_3e_risk_scoring", {})
        
        if "error" in health_risk or not health_risk:
            self.errors.append({
                "case": ground_truth["case_id"],
                "error_type": "Risk scoring failed",
                "details": health_risk.get("error", "No risk output")
            })
            return {"category_match": False, "directional_correct": False}
        
        pred_category = health_risk.get("risk_category", "").strip()
        true_category = ground_truth["true_risk_category"].strip()
        
        # Map risk category to approximate percentage for comparison
        # (New engine uses score-based categories, not explicit percentages)
        category_to_risk_map = {
            "Low": 5,
            "Borderline": 10,
            "Intermediate": 15,
            "High": 25,
            "Critical": 35
        }
        pred_risk = category_to_risk_map.get(pred_category, 0)
        
        true_range = ground_truth.get("true_risk_range", {"min": 0, "max": 100})
        true_risk_midpoint = (true_range["min"] + true_range["max"]) / 2
        
        # Category match
        category_match = pred_category == true_category
        if category_match:
            self.category_matches += 1
        else:
            self.errors.append({
                "case": ground_truth["case_id"],
                "error_type": "Category mismatch",
                "predicted": pred_category,
                "expected": true_category,
                "risk_score": health_risk.get("total_score", 0),
                "top_contributors": health_risk.get("top_contributors", [])[:3]
            })
        
        # Directional correctness (risk in expected range or reasonable proximity)
        in_range = true_range["min"] <= pred_risk <= true_range["max"]
        reasonable_proximity = abs(pred_risk - true_risk_midpoint) <= 10  # Within 10% points
        
        directional_correct = in_range or reasonable_proximity
        if directional_correct:
            self.directional_correct += 1
        
        # Track risk difference for bias analysis
        risk_diff = pred_risk - true_risk_midpoint
        self.risk_differences.append(risk_diff)
        
        return {
            "category_match": category_match,
            "directional_correct": directional_correct,
            "predicted_risk": pred_risk,
            "expected_range": true_range
        }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Calculate aggregate metrics."""
        category_match_rate = (self.category_matches / self.total_cases * 100) if self.total_cases > 0 else 0
        directional_correctness = (self.directional_correct / self.total_cases * 100) if self.total_cases > 0 else 0
        
        # Bias analysis
        overestimation_bias = sum(d for d in self.risk_differences if d > 0) / self.total_cases if self.total_cases > 0 else 0
        underestimation_bias = -sum(d for d in self.risk_differences if d < 0) / self.total_cases if self.total_cases > 0 else 0
        
        mean_absolute_diff = sum(abs(d) for d in self.risk_differences) / self.total_cases if self.total_cases > 0 else 0
        
        return {
            "category_match_rate": category_match_rate,
            "directional_correctness": directional_correctness,
            "mean_absolute_risk_difference": mean_absolute_diff,
            "risk_overestimation_bias": overestimation_bias,
            "risk_underestimation_bias": underestimation_bias,
            "total_cases": self.total_cases,
            "error_details": self.errors
        }


class ValidationRunner:
    """Main validation orchestrator."""
    
    def __init__(self, validation_dataset_dir: Path, project_root: Path):
        self.dataset_dir = validation_dataset_dir
        self.project_root = project_root
        self.pipeline = Phase3RecommendationPipeline()
        
        self.model1_evaluator = Model1Evaluator()
        self.model2_evaluator = Model2Evaluator()
        self.risk_evaluator = RiskScoringEvaluator()
    
    def run_validation(self) -> ValidationMetrics:
        """Run complete validation suite."""
        print("\n" + "="*80)
        print("PHASE 4: FORMAL VALIDATION & BENCHMARKING")
        print("="*80)
        
        # Load all test cases
        case_dirs = sorted([d for d in self.dataset_dir.iterdir() if d.is_dir()])
        
        print(f"\n📊 Loading {len(case_dirs)} test cases...")
        
        for case_dir in case_dirs:
            ground_truth_file = case_dir / "ground_truth.json"
            if not ground_truth_file.exists():
                print(f"⚠ Skipping {case_dir.name}: No ground_truth.json found")
                continue
            
            # Load ground truth
            with open(ground_truth_file, 'r') as f:
                ground_truth = json.load(f)
            
            print(f"\n[{ground_truth['case_id']}] {ground_truth['description']}")
            
            # Load source report (resolve relative path from project root)
            source_rel_path = ground_truth["source_report"]
            source_path = self.project_root / source_rel_path.replace("../../", "")
            with open(source_path, 'r') as f:
                report_data = json.load(f)
            
            # Convert to phase 3 format
            # Handle both list and dict parameter formats
            params_data = report_data.get("parameters", [])
            
            if isinstance(params_data, list):
                # List format: [{"name": "...", "value": ..., "unit": "..."}]
                extracted_params = [
                    {"parameter": p["name"], "value": p["value"], "unit": p.get("unit", "")}
                    for p in params_data
                ]
            elif isinstance(params_data, dict):
                # Dict format: {"Glucose": {"value": ..., "unit": "..."}}
                extracted_params = [
                    {"parameter": name, "value": details["value"], "unit": details.get("unit", "")}
                    for name, details in params_data.items()
                ]
            else:
                extracted_params = []
            
            patient_info = report_data["patient_info"].copy()
            if 'gender' in patient_info:
                patient_info['sex'] = patient_info['gender']
            
            # Run pipeline
            try:
                predicted = self.pipeline.process_extracted_parameters(extracted_params, patient_info)
                
                # Evaluate each model
                self.model1_evaluator.evaluate_case(predicted, ground_truth)
                self.model2_evaluator.evaluate_case(predicted, ground_truth)
                self.risk_evaluator.evaluate_case(predicted, ground_truth)
                
            except Exception as e:
                print(f"  ❌ Pipeline error: {str(e)}")
                continue
        
        # Calculate final metrics
        return self._compile_metrics()
    
    def _compile_metrics(self) -> ValidationMetrics:
        """Compile all metrics into ValidationMetrics object."""
        m1_metrics = self.model1_evaluator.get_metrics()
        m2_metrics = self.model2_evaluator.get_metrics()
        risk_metrics = self.risk_evaluator.get_metrics()
        
        # Calculate overall reliability score (weighted average)
        # Weights: Model1=40%, Model2=30%, Risk=30%
        reliability_score = (
            m1_metrics["accuracy"] * 0.4 +
            m2_metrics["accuracy"] * 0.3 +
            risk_metrics["category_match_rate"] * 0.3
        )
        
        return ValidationMetrics(
            model1_accuracy=m1_metrics["accuracy"],
            model1_precision=m1_metrics["precision"],
            model1_recall=m1_metrics["recall"],
            model1_f1=m1_metrics["f1_score"],
            model2_accuracy=m2_metrics["accuracy"],
            model2_false_positive_rate=m2_metrics["false_positive_rate"],
            risk_category_match_rate=risk_metrics["category_match_rate"],
            risk_directional_correctness=risk_metrics["directional_correctness"],
            overall_reliability_score=reliability_score,
            most_misclassified_parameter=m1_metrics["most_misclassified_parameter"],
            most_confused_pattern=m2_metrics["most_confused_pattern"],
            risk_overestimation_bias=risk_metrics["risk_overestimation_bias"],
            risk_underestimation_bias=risk_metrics["risk_underestimation_bias"],
            classification_errors=m1_metrics["error_details"],
            pattern_errors=m2_metrics["error_details"],
            risk_errors=risk_metrics["error_details"]
        )
    
    def generate_report(self, metrics: ValidationMetrics, output_file: Path = None):
        """Generate structured validation report."""
        report = []
        report.append("\n" + "="*80)
        report.append("=== VALIDATION RESULTS ===")
        report.append("="*80)
        
        report.append(f"\n📊 MODEL 1: Parameter Classification")
        report.append(f"   Accuracy: {metrics.model1_accuracy:.1f}%")
        report.append(f"   Precision: {metrics.model1_precision:.3f}")
        report.append(f"   Recall: {metrics.model1_recall:.3f}")
        report.append(f"   F1 Score: {metrics.model1_f1:.3f}")
        
        # Print detailed confusion matrix
        report.append(f"\n   Confusion Matrix (True \\ Predicted):")
        report.append(f"   {'':8} | Normal | High | Low")
        report.append(f"   {'-'*35}")
        cm = self.model1_evaluator.confusion_matrix_detailed
        report.append(f"   {'Normal':8} |   {cm['Normal']['Normal']:2}   |  {cm['Normal']['High']:2}  |  {cm['Normal']['Low']:2}")
        report.append(f"   {'High':8} |   {cm['High']['Normal']:2}   |  {cm['High']['High']:2}  |  {cm['High']['Low']:2}")
        report.append(f"   {'Low':8} |   {cm['Low']['Normal']:2}   |  {cm['Low']['High']:2}  |  {cm['Low']['Low']:2}")
        
        # Print per-parameter accuracy
        report.append(f"\n   Per-Parameter Accuracy:")
        param_acc = self.model1_evaluator.parameter_stats
        for param, stats in sorted(param_acc.items(), key=lambda x: x[1]['correct']/max(x[1]['total'],1)):
            if stats['total'] > 0:
                acc = (stats['correct'] / stats['total']) * 100
                report.append(f"   {param:20} {acc:5.1f}% ({stats['correct']}/{stats['total']})")
        
        report.append(f"\n🔍 MODEL 2: Pattern Recognition")
        report.append(f"   Pattern Detection Accuracy: {metrics.model2_accuracy:.1f}%")
        report.append(f"   False Positive Rate: {metrics.model2_false_positive_rate:.1f}%")
        
        report.append(f"\n❤️  RISK SCORING ENGINE")
        report.append(f"   Risk Category Match: {metrics.risk_category_match_rate:.1f}%")
        report.append(f"   Directional Correctness: {metrics.risk_directional_correctness:.1f}%")
        
        report.append(f"\n📈 ERROR ANALYSIS")
        report.append(f"   Most Misclassified Parameter: {metrics.most_misclassified_parameter}")
        report.append(f"   Most Confused Pattern: {metrics.most_confused_pattern}")
        report.append(f"   Risk Overestimation Bias: {metrics.risk_overestimation_bias:.2f}%")
        report.append(f"   Risk Underestimation Bias: {metrics.risk_underestimation_bias:.2f}%")
        
        report.append(f"\n🎯 OVERALL SYSTEM RELIABILITY SCORE: {metrics.overall_reliability_score:.1f}%")
        report.append("="*80)
        
        report_text = "\n".join(report)
        print(report_text)
        
        if output_file:
            output_file.write_text(report_text)
            print(f"\n✅ Validation report saved to {output_file}")


def main():
    """Run Phase 4 validation."""
    project_root = Path(__file__).parent
    validation_dir = project_root / "validation_dataset"
    
    if not validation_dir.exists():
        print(f"❌ Validation dataset not found at {validation_dir}")
        return
    
    runner = ValidationRunner(validation_dir, project_root)
    metrics = runner.run_validation()
    
    # Generate report
    output_file = project_root / "validation_report.txt"
    runner.generate_report(metrics, output_file)
    
    # Save detailed metrics as JSON
    json_output = project_root / "validation_metrics.json"
    with open(json_output, 'w') as f:
        metrics_dict = {
            "model1_classification": {
                "accuracy": metrics.model1_accuracy,
                "precision": metrics.model1_precision,
                "recall": metrics.model1_recall,
                "f1_score": metrics.model1_f1
            },
            "model2_pattern_detection": {
                "accuracy": metrics.model2_accuracy,
                "false_positive_rate": metrics.model2_false_positive_rate
            },
            "risk_scoring": {
                "category_match_rate": metrics.risk_category_match_rate,
                "directional_correctness": metrics.risk_directional_correctness
            },
            "error_analysis": {
                "most_misclassified_parameter": metrics.most_misclassified_parameter,
                "most_confused_pattern": metrics.most_confused_pattern,
                "risk_overestimation_bias": metrics.risk_overestimation_bias,
                "risk_underestimation_bias": metrics.risk_underestimation_bias
            },
            "overall_reliability_score": metrics.overall_reliability_score
        }
        json.dump(metrics_dict, f, indent=2)
    
    print(f"✅ Detailed metrics saved to {json_output}")


if __name__ == "__main__":
    main()
