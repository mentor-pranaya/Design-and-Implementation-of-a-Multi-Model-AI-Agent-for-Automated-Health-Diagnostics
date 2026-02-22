"""
Pattern Detection Diagnostic Tool

Analyzes Model 2 pattern detection errors with clinical precision:
- Pattern confusion matrix (TP, FP, FN, TN)
- Case-by-case audit with triggering parameters
- False positive analysis with root cause identification
- Pattern definition compliance check
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Set
from collections import defaultdict

# Add parent directory to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / 'core_phase3'))

from core_phase3.main import Phase3RecommendationPipeline
from pattern_registry import normalize_pattern_name, VALID_PATTERN_NAMES


class PatternDiagnostics:
    """Diagnose Model 2 pattern detection issues."""
    
    def __init__(self, validation_dir: Path, project_root: Path):
        self.validation_dir = validation_dir
        self.project_root = project_root
        self.pipeline = Phase3RecommendationPipeline()
        
        # Tracking
        self.true_positives = []  # Correctly detected patterns
        self.false_positives = []  # Incorrectly detected patterns
        self.false_negatives = []  # Missed patterns
        self.true_negatives = []  # Correctly not detected
        
        self.case_results = []
    
    def run_diagnostics(self):
        """Run comprehensive pattern diagnostics."""
        print("\n" + "="*80)
        print("PATTERN DETECTION DIAGNOSTICS - Model 2")
        print("="*80)
        
        # Load all test cases
        case_dirs = sorted([d for d in self.validation_dir.iterdir() if d.is_dir()])
        
        for case_dir in case_dirs:
            ground_truth_file = case_dir / "ground_truth.json"
            if not ground_truth_file.exists():
                continue
            
            # Load ground truth
            with open(ground_truth_file, 'r') as f:
                ground_truth = json.load(f)
            
            # Load source report
            source_rel_path = ground_truth["source_report"]
            source_path = self.project_root / source_rel_path.replace("../../", "")
            with open(source_path, 'r') as f:
                report_data = json.load(f)
            
            # Process report
            params_data = report_data.get("parameters", [])
            if isinstance(params_data, list):
                extracted_params = [
                    {"parameter": p["name"], "value": p["value"], "unit": p.get("unit", "")}
                    for p in params_data
                ]
            elif isinstance(params_data, dict):
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
            except Exception as e:
                print(f"\n⚠ Error processing {ground_truth['case_id']}: {e}")
                continue
            
            # Analyze case
            self._analyze_case(ground_truth, predicted, extracted_params)
        
        # Print results
        self._print_confusion_matrix()
        self._print_false_positive_analysis()
        self._print_false_negative_analysis()
        self._print_case_by_case_audit()
    
    def _analyze_case(self, ground_truth: Dict, predicted: Dict, extracted_params: List[Dict]):
        """Analyze single case for pattern detection."""
        case_id = ground_truth["case_id"]
        
        # Normalize pattern names
        expected_patterns = set()
        for pattern in ground_truth.get("true_patterns", []):
            try:
                expected_patterns.add(normalize_pattern_name(pattern))
            except ValueError as e:
                print(f"⚠ Warning: {e}")
        
        detected_patterns = set()
        # Patterns are in phase_3b_patterns list with key "pattern"
        for pattern in predicted.get("phase_3b_patterns", []):
            pattern_name = pattern.get("pattern", "")
            try:
                detected_patterns.add(normalize_pattern_name(pattern_name))
            except ValueError:
                # Unknown pattern detected
                detected_patterns.add(pattern_name)
        
        # Calculate matches
        tp = expected_patterns & detected_patterns
        fp = detected_patterns - expected_patterns
        fn = expected_patterns - detected_patterns
        
        # Store results
        case_result = {
            "case_id": case_id,
            "description": ground_truth["description"],
            "expected_patterns": sorted(list(expected_patterns)),
            "detected_patterns": sorted(list(detected_patterns)),
            "true_positives": sorted(list(tp)),
            "false_positives": sorted(list(fp)),
            "false_negatives": sorted(list(fn)),
            "parameters": extracted_params,
            "parameter_classifications": predicted.get("phase_3a_evaluation", {}).get("parameter_evaluations", [])
        }
        
        self.case_results.append(case_result)
        
        # Update global tracking
        for pattern in tp:
            self.true_positives.append((case_id, pattern))
        for pattern in fp:
            self.false_positives.append((case_id, pattern))
        for pattern in fn:
            self.false_negatives.append((case_id, pattern))
    
    def _print_confusion_matrix(self):
        """Print pattern detection confusion matrix."""
        print("\n" + "="*80)
        print("PATTERN CONFUSION MATRIX")
        print("="*80)
        
        tp_count = len(self.true_positives)
        fp_count = len(self.false_positives)
        fn_count = len(self.false_negatives)
        
        total_expected = tp_count + fn_count
        total_detected = tp_count + fp_count
        
        print(f"\nTrue Positives  (TP): {tp_count:2} - Correctly detected patterns")
        print(f"False Positives (FP): {fp_count:2} - Incorrectly triggered patterns")
        print(f"False Negatives (FN): {fn_count:2} - Missed patterns")
        
        print(f"\n{'Metric':<25} {'Value':<10} {'Formula'}")
        print("-" * 80)
        
        accuracy = (tp_count / total_expected * 100) if total_expected > 0 else 0
        precision = (tp_count / total_detected * 100) if total_detected > 0 else 0
        recall = (tp_count / total_expected * 100) if total_expected > 0 else 0
        fpr = (fp_count / total_detected * 100) if total_detected > 0 else 0
        
        print(f"{'Accuracy (Recall)':<25} {accuracy:>5.1f}%     TP / (TP + FN)")
        print(f"{'Precision':<25} {precision:>5.1f}%     TP / (TP + FP)")
        print(f"{'False Positive Rate':<25} {fpr:>5.1f}%     FP / (TP + FP)")
        
        print(f"\nTotal Expected Patterns:  {total_expected}")
        print(f"Total Detected Patterns:  {total_detected}")
    
    def _print_false_positive_analysis(self):
        """Analyze false positives with root cause."""
        print("\n" + "="*80)
        print("FALSE POSITIVE ANALYSIS - Why were these patterns incorrectly triggered?")
        print("="*80)
        
        if not self.false_positives:
            print("\n✓ No false positives detected")
            return
        
        # Group by pattern
        fp_by_pattern = defaultdict(list)
        for case_id, pattern in self.false_positives:
            fp_by_pattern[pattern].append(case_id)
        
        for pattern, case_ids in sorted(fp_by_pattern.items()):
            print(f"\n🔴 Pattern: '{pattern}' (False Positive in {len(case_ids)} case(s))")
            
            for case_id in case_ids:
                # Find case result
                case_result = next(r for r in self.case_results if r["case_id"] == case_id)
                
                print(f"\n  Case: {case_id} - {case_result['description']}")
                print(f"  Why was '{pattern}' triggered?")
                print(f"  Abnormal parameters in this case:")
                
                # Show abnormal parameters
                abnormal_params = []
                for eval_result in case_result["parameter_classifications"]:
                    status = eval_result.get("status", "").lower()
                    if status in ["high", "low"]:
                        param_name = eval_result.get("parameter", "")
                        value = eval_result.get("value", "")
                        ref_range = eval_result.get("reference_range", {})
                        abnormal_params.append(f"    - {param_name}: {value} ({status.upper()}, ref: {ref_range})")
                
                if abnormal_params:
                    for line in abnormal_params:
                        print(line)
                else:
                    print("    - No abnormal parameters found")
                
                print(f"  ⚠️ DIAGNOSIS: Pattern '{pattern}' should NOT have been triggered.")
                print(f"     Likely cause: Over-permissive rule definition")
    
    def _print_false_negative_analysis(self):
        """Analyze false negatives - missed patterns."""
        print("\n" + "="*80)
        print("FALSE NEGATIVE ANALYSIS - Why were these patterns missed?")
        print("="*80)
        
        if not self.false_negatives:
            print("\n✓ No false negatives detected")
            return
        
        # Group by pattern
        fn_by_pattern = defaultdict(list)
        for case_id, pattern in self.false_negatives:
            fn_by_pattern[pattern].append(case_id)
        
        for pattern, case_ids in sorted(fn_by_pattern.items()):
            print(f"\n🟡 Pattern: '{pattern}' (False Negative in {len(case_ids)} case(s))")
            
            for case_id in case_ids:
                case_result = next(r for r in self.case_results if r["case_id"] == case_id)
                
                print(f"\n  Case: {case_id} - {case_result['description']}")
                print(f"  Expected pattern '{pattern}' but it was NOT detected")
                print(f"  Supporting evidence that should have triggered it:")
                
                # Show abnormal parameters
                for eval_result in case_result["parameter_classifications"]:
                    status = eval_result.get("status", "").lower()
                    if status in ["high", "low"]:
                        param_name = eval_result.get("parameter", "")
                        value = eval_result.get("value", "")
                        print(f"    - {param_name}: {value} ({status.upper()})")
                
                print(f"  ⚠️ DIAGNOSIS: Pattern '{pattern}' SHOULD have been triggered.")
                print(f"     Likely cause: Missing rule definition or name mismatch")
    
    def _print_case_by_case_audit(self):
        """Print detailed case-by-case audit."""
        print("\n" + "="*80)
        print("CASE-BY-CASE PATTERN AUDIT")
        print("="*80)
        
        for case_result in self.case_results:
            print(f"\n{'='*80}")
            print(f"Case: {case_result['case_id']} - {case_result['description']}")
            print(f"{'='*80}")
            
            print(f"\nExpected Patterns: {', '.join(case_result['expected_patterns']) if case_result['expected_patterns'] else 'None'}")
            print(f"Detected Patterns: {', '.join(case_result['detected_patterns']) if case_result['detected_patterns'] else 'None'}")
            
            if case_result['true_positives']:
                print(f"\n✅ Correct: {', '.join(case_result['true_positives'])}")
            
            if case_result['false_positives']:
                print(f"\n❌ False Positives: {', '.join(case_result['false_positives'])}")
            
            if case_result['false_negatives']:
                print(f"\n⚠️  False Negatives (Missed): {', '.join(case_result['false_negatives'])}")
            
            # Show parameter summary
            print(f"\nParameter Summary:")
            normal_count = 0
            abnormal_count = 0
            
            for eval_result in case_result["parameter_classifications"]:
                status = eval_result.get("status", "").lower()
                param_name = eval_result.get("parameter", "")
                value = eval_result.get("value", "")
                
                if status in ["high", "low"]:
                    severity = eval_result.get("severity", "")
                    print(f"  🔴 {param_name}: {value} ({status.upper()}{', ' + severity if severity else ''})")
                    abnormal_count += 1
                else:
                    normal_count += 1
            
            print(f"\n  Total: {normal_count} Normal, {abnormal_count} Abnormal")


def main():
    """Run pattern diagnostics."""
    project_root = Path(__file__).parent
    validation_dir = project_root / "validation_dataset"
    
    if not validation_dir.exists():
        print(f"❌ Validation dataset not found at {validation_dir}")
        return
    
    diagnostics = PatternDiagnostics(validation_dir, project_root)
    diagnostics.run_diagnostics()
    
    print("\n" + "="*80)
    print("✅ Pattern diagnostics complete")
    print("="*80)


if __name__ == "__main__":
    main()
