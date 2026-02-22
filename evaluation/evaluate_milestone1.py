"""
Milestone 1 Evaluation: Data Ingestion & Parameter Interpretation

Organization Requirements:
- Extraction Accuracy: >95%
- Classification Accuracy: >98%
- Test Set: 15-20 diverse blood reports

This script evaluates the performance of:
1. Data Extraction Engine (Phase 1)
2. Data Validation Module (Phase 1)
3. Model 1 - Parameter Interpretation (Phase 3)
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class Milestone1Evaluator:
    """
    Evaluator for Milestone 1: Data Ingestion & Parameter Interpretation.
    
    Measures:
    1. Extraction accuracy (target >95%)
    2. Classification accuracy (target >98%)
    """
    
    def __init__(self, test_dataset_path: str = "evaluation/test_dataset"):
        """
        Initialize evaluator.
        
        Args:
            test_dataset_path: Path to test dataset directory
        """
        self.test_dataset_path = Path(test_dataset_path)
        self.reports_path = self.test_dataset_path / "reports"
        self.ground_truth_path = self.test_dataset_path / "ground_truth"
        
        # Results storage
        self.extraction_results = []
        self.classification_results = []
        
        print("="*70)
        print("MILESTONE 1 EVALUATION")
        print("Data Ingestion & Parameter Interpretation")
        print("="*70)
    
    def load_ground_truth(self, report_id: str) -> Dict:
        """
        Load ground truth annotations for a report.
        
        Args:
            report_id: Report identifier
        
        Returns:
            Ground truth data
        """
        gt_file = self.ground_truth_path / f"{report_id}.json"
        
        if not gt_file.exists():
            raise FileNotFoundError(f"Ground truth not found: {gt_file}")
        
        with open(gt_file, 'r') as f:
            return json.load(f)
    
    def evaluate_extraction(
        self,
        extracted: Dict,
        ground_truth: Dict
    ) -> Tuple[int, int, List[str]]:
        """
        Evaluate extraction accuracy.
        
        Args:
            extracted: Extracted parameters from system
            ground_truth: Manual ground truth annotations
        
        Returns:
            Tuple of (correct_count, total_count, errors)
        """
        correct = 0
        total = 0
        errors = []
        
        gt_params = ground_truth.get("parameters", {})
        
        for param_name, gt_data in gt_params.items():
            total += 1
            
            if param_name not in extracted:
                errors.append(f"Missing parameter: {param_name}")
                continue
            
            extracted_value = extracted[param_name].get("value")
            gt_value = gt_data.get("value")
            
            # Allow small tolerance for floating point
            if isinstance(gt_value, (int, float)) and isinstance(extracted_value, (int, float)):
                if abs(extracted_value - gt_value) < 0.01:
                    correct += 1
                else:
                    errors.append(
                        f"{param_name}: Expected {gt_value}, got {extracted_value}"
                    )
            elif extracted_value == gt_value:
                correct += 1
            else:
                errors.append(
                    f"{param_name}: Expected {gt_value}, got {extracted_value}"
                )
        
        # Check for extra parameters (false positives)
        for param_name in extracted:
            if param_name not in gt_params:
                errors.append(f"Extra parameter extracted: {param_name}")
        
        return correct, total, errors
    
    def evaluate_classification(
        self,
        classified: Dict,
        ground_truth: Dict
    ) -> Tuple[int, int, List[str]]:
        """
        Evaluate classification accuracy.
        
        Args:
            classified: Classified parameters from Model 1
            ground_truth: Manual ground truth classifications
        
        Returns:
            Tuple of (correct_count, total_count, errors)
        """
        correct = 0
        total = 0
        errors = []
        
        gt_classifications = ground_truth.get("classifications", {})
        
        for param_name, gt_class in gt_classifications.items():
            total += 1
            
            if param_name not in classified:
                errors.append(f"Missing classification: {param_name}")
                continue
            
            system_class = classified[param_name].get("status")
            
            if system_class == gt_class:
                correct += 1
            else:
                errors.append(
                    f"{param_name}: Expected '{gt_class}', got '{system_class}'"
                )
        
        return correct, total, errors
    
    def evaluate_report(self, report_id: str) -> Dict:
        """
        Evaluate a single report.
        
        Args:
            report_id: Report identifier
        
        Returns:
            Evaluation results for this report
        """
        print(f"\nEvaluating report: {report_id}")
        
        # Load ground truth
        ground_truth = self.load_ground_truth(report_id)
        
        # TODO: Run actual extraction and classification
        # For now, use placeholder
        # from core_phase1.ocr import extract_from_pdf
        # from core_phase1.validation.validator import validate_parameters
        # from core_phase3.knowledge_base.reference_manager import ReferenceRangeManager
        
        # Placeholder extracted and classified data
        extracted = {}
        classified = {}
        
        # Evaluate extraction
        ext_correct, ext_total, ext_errors = self.evaluate_extraction(
            extracted, ground_truth
        )
        
        # Evaluate classification
        cls_correct, cls_total, cls_errors = self.evaluate_classification(
            classified, ground_truth
        )
        
        result = {
            "report_id": report_id,
            "extraction": {
                "correct": ext_correct,
                "total": ext_total,
                "accuracy": (ext_correct / ext_total * 100) if ext_total > 0 else 0,
                "errors": ext_errors
            },
            "classification": {
                "correct": cls_correct,
                "total": cls_total,
                "accuracy": (cls_correct / cls_total * 100) if cls_total > 0 else 0,
                "errors": cls_errors
            }
        }
        
        print(f"  Extraction: {ext_correct}/{ext_total} ({result['extraction']['accuracy']:.1f}%)")
        print(f"  Classification: {cls_correct}/{cls_total} ({result['classification']['accuracy']:.1f}%)")
        
        return result
    
    def evaluate_all(self) -> Dict:
        """
        Evaluate all reports in test dataset.
        
        Returns:
            Complete evaluation results
        """
        print("\nStarting evaluation of all reports...")
        
        # Get list of ground truth files
        gt_files = list(self.ground_truth_path.glob("*.json"))
        
        if not gt_files:
            print("⚠ WARNING: No ground truth files found!")
            print(f"  Expected location: {self.ground_truth_path}")
            print("  Please create ground truth annotations first.")
            return {
                "status": "error",
                "message": "No ground truth files found"
            }
        
        print(f"Found {len(gt_files)} reports to evaluate")
        
        all_results = []
        
        for gt_file in gt_files:
            report_id = gt_file.stem
            try:
                result = self.evaluate_report(report_id)
                all_results.append(result)
            except Exception as e:
                print(f"  ERROR: {str(e)}")
                all_results.append({
                    "report_id": report_id,
                    "error": str(e)
                })
        
        # Calculate aggregate metrics
        total_ext_correct = sum(r["extraction"]["correct"] for r in all_results if "extraction" in r)
        total_ext_total = sum(r["extraction"]["total"] for r in all_results if "extraction" in r)
        total_cls_correct = sum(r["classification"]["correct"] for r in all_results if "classification" in r)
        total_cls_total = sum(r["classification"]["total"] for r in all_results if "classification" in r)
        
        extraction_accuracy = (total_ext_correct / total_ext_total * 100) if total_ext_total > 0 else 0
        classification_accuracy = (total_cls_correct / total_cls_total * 100) if total_cls_total > 0 else 0
        
        # Determine pass/fail
        extraction_pass = extraction_accuracy >= 95.0
        classification_pass = classification_accuracy >= 98.0
        
        results = {
            "milestone": "Milestone 1: Data Ingestion & Parameter Interpretation",
            "evaluation_date": datetime.now().isoformat(),
            "test_set_size": len(all_results),
            "aggregate_metrics": {
                "extraction_accuracy": {
                    "value": extraction_accuracy,
                    "target": 95.0,
                    "pass": extraction_pass,
                    "correct": total_ext_correct,
                    "total": total_ext_total
                },
                "classification_accuracy": {
                    "value": classification_accuracy,
                    "target": 98.0,
                    "pass": classification_pass,
                    "correct": total_cls_correct,
                    "total": total_cls_total
                }
            },
            "overall_pass": extraction_pass and classification_pass,
            "individual_results": all_results
        }
        
        # Print summary
        print("\n" + "="*70)
        print("MILESTONE 1 EVALUATION RESULTS")
        print("="*70)
        print(f"\nTest Set Size: {len(all_results)} reports")
        print(f"\nExtraction Accuracy: {extraction_accuracy:.2f}% (Target: >95%)")
        print(f"  Status: {'✓ PASS' if extraction_pass else '✗ FAIL'}")
        print(f"  Correct: {total_ext_correct}/{total_ext_total}")
        print(f"\nClassification Accuracy: {classification_accuracy:.2f}% (Target: >98%)")
        print(f"  Status: {'✓ PASS' if classification_pass else '✗ FAIL'}")
        print(f"  Correct: {total_cls_correct}/{total_cls_total}")
        print(f"\nOverall: {'✓ MILESTONE 1 PASSED' if results['overall_pass'] else '✗ MILESTONE 1 FAILED'}")
        print("="*70)
        
        return results
    
    def save_results(self, results: Dict, output_path: str = "evaluation/results/milestone1_results.json"):
        """
        Save evaluation results to file.
        
        Args:
            results: Evaluation results
            output_path: Output file path
        """
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)
        
        print(f"\n✓ Results saved to: {output_file}")


def main():
    """Main evaluation function."""
    evaluator = Milestone1Evaluator()
    results = evaluator.evaluate_all()
    evaluator.save_results(results)
    
    return results


if __name__ == "__main__":
    main()
