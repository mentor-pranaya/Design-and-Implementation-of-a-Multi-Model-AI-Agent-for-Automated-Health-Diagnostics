"""
Validation Pipeline Module

Compares system output against ground truth and calculates classification accuracy.
Validates Requirements 4.1, 4.2, 4.3 from milestone-1-validation spec.
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime

# Import existing system components
import sys
sys.path.append(str(Path(__file__).parent.parent))

from core_phase1.extraction.comprehensive_extractor import extract_parameters_comprehensive
from core_phase3.knowledge_base.unified_reference_manager import UnifiedReferenceManager
from core_phase1.ocr.pdf_ocr import extract_text_from_pdf
from core_phase1.ocr.image_ocr import extract_text_from_image


class ValidationPipeline:
    """Validates system classifications against ground truth."""
    
    def __init__(self, reference_manager: Optional[UnifiedReferenceManager] = None):
        """
        Initialize validation pipeline.
        
        Args:
            reference_manager: UnifiedReferenceManager instance (creates new if None)
        """
        self.reference_manager = reference_manager or UnifiedReferenceManager()
        self.ground_truth_data = {}
    
    def load_ground_truth(self, ground_truth_dir: str) -> Dict:
        """
        Load all ground truth files from directory.
        
        Args:
            ground_truth_dir: Directory containing ground truth JSON files
            
        Returns:
            Dictionary mapping report_id to ground truth data
        """
        ground_truth_dir = Path(ground_truth_dir)
        
        if not ground_truth_dir.exists():
            raise FileNotFoundError(f"Ground truth directory not found: {ground_truth_dir}")
        
        ground_truth = {}
        json_files = list(ground_truth_dir.glob("*.json"))
        
        # Filter out TEMPLATE.json and other non-report files
        json_files = [f for f in json_files if f.stem not in ['TEMPLATE', 'generation_summary']]
        
        for json_file in json_files:
            try:
                with open(json_file, 'r') as f:
                    data = json.load(f)
                    
                # Skip if it's a template or has instructions
                if '_instructions' in data:
                    continue
                    
                report_id = data.get('report_id')
                if report_id:
                    ground_truth[report_id] = data
                    
            except Exception as e:
                print(f"Warning: Failed to load {json_file.name}: {e}")
        
        self.ground_truth_data = ground_truth
        return ground_truth

    def _extract_text_from_report(self, report_path: str) -> str:
        """
        Extract text from PDF or PNG report.
        
        Args:
            report_path: Path to report file
            
        Returns:
            Extracted text content
        """
        path = Path(report_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Report not found: {report_path}")
        
        # For PDF files
        if path.suffix.lower() == '.pdf':
            return extract_text_from_pdf(str(path))
        
        # For PNG/image files
        elif path.suffix.lower() in ['.png', '.jpg', '.jpeg']:
            return extract_text_from_image(str(path))
        
        else:
            raise ValueError(f"Unsupported file format: {path.suffix}")
    
    def _normalize_parameter_name(self, param_name: str) -> str:
        """
        Normalize parameter name for comparison.
        
        Handles case differences and common variations.
        Maps to the exact names used by UnifiedReferenceManager.
        
        Args:
            param_name: Parameter name to normalize
            
        Returns:
            Normalized parameter name matching UnifiedReferenceManager format
        """
        # Convert to lowercase for lookup
        lower_name = param_name.lower().strip()
        
        # Map to UnifiedReferenceManager parameter names
        # These match the exact names in NHANES and ABIM data
        parameter_mapping = {
            'wbc': 'WBC',
            'white blood cell': 'WBC',
            'white blood cells': 'WBC',
            'rbc': 'RBC',
            'red blood cell': 'RBC',
            'red blood cells': 'RBC',
            'hemoglobin': 'Hemoglobin',
            'hb': 'Hemoglobin',
            'hgb': 'Hemoglobin',
            'hematocrit': 'Hematocrit',
            'hct': 'Hematocrit',
            'platelet': 'Platelet Count',
            'platelet count': 'Platelet Count',
            'platelets': 'Platelet Count',
            'glucose': 'Glucose',
            'blood glucose': 'Glucose',
            'fasting glucose': 'Glucose',
            'hba1c': 'HbA1c',
            'a1c': 'HbA1c',
            'cholesterol': 'Total Cholesterol',
            'total cholesterol': 'Total Cholesterol',
            'cholesterol total': 'Cholesterol Total',
            'hdl': 'HDL',
            'hdl cholesterol': 'HDL',
            'ldl': 'LDL',
            'ldl cholesterol': 'LDL',
            'triglycerides': 'Triglycerides',
            'trig': 'Triglycerides',
            'creatinine': 'Creatinine',
            'serum creatinine': 'Creatinine',
            'bun': 'BUN',
            'blood urea nitrogen': 'BUN',
            'sodium': 'Sodium',
            'na': 'Sodium',
            'potassium': 'Potassium',
            'k': 'Potassium',
            'calcium': 'Calcium',
            'ca': 'Calcium',
            'tsh': 'TSH',
            'thyroid stimulating hormone': 'TSH',
            'alt': 'ALT',
            'sgpt': 'ALT',
            'ast': 'AST',
            'sgot': 'AST',
            'alp': 'ALP',
            'alkaline phosphatase': 'ALP',
            'bilirubin': 'Bilirubin',
            'total bilirubin': 'Bilirubin',
            'albumin': 'Albumin',
            'protein': 'Protein',
            'total protein': 'Protein',
            'mcv': 'MCV',
            'mch': 'MCH',
            'mchc': 'MCHC',
            'rdw': 'RDW',
            'neutrophils': 'Neutrophils',
            'lymphocytes': 'Lymphocytes',
            'monocytes': 'Monocytes',
            'eosinophils': 'Eosinophils',
            'basophils': 'Basophils',
            'magnesium': 'Magnesium',
            'mg': 'Magnesium',
            'phosphorus': 'Phosphorus',
            'phosphate': 'Phosphorus',
        }
        
        return parameter_mapping.get(lower_name, param_name.capitalize())
    
    def process_report(self, report_path: str) -> Dict:
        """
        Process report with current system and extract parameters.
        
        Args:
            report_path: Path to report file
            
        Returns:
            Dictionary with extracted parameters and classifications
        """
        # Extract text from report
        text = self._extract_text_from_report(report_path)
        
        # Extract parameters using comprehensive extractor
        extracted_params = extract_parameters_comprehensive(text)
        
        # Classify each parameter
        classifications = {}
        parameters = {}
        
        for param_name, param_data in extracted_params.items():
            value = param_data['value']
            unit = param_data['unit']
            
            # Normalize parameter name for reference lookup
            normalized_name = self._normalize_parameter_name(param_name)
            
            # Get reference range
            ref_range = self.reference_manager.get_reference_range(
                parameter=normalized_name,
                age=None,  # Use default age
                sex=None   # Use default sex
            )
            
            # Classify parameter
            # Check if we have valid min/max values (not None)
            min_val = ref_range.get('min')
            max_val = ref_range.get('max')
            
            if min_val is not None and max_val is not None:
                if value < min_val:
                    classification = "Low"
                elif value > max_val:
                    classification = "High"
                else:
                    classification = "Normal"
            else:
                classification = "Unknown"
            
            parameters[param_name] = {
                "value": value,
                "unit": unit,
                "reference_range": {
                    "min": ref_range.get('min'),
                    "max": ref_range.get('max')
                }
            }
            classifications[param_name] = classification
        
        return {
            "parameters": parameters,
            "classifications": classifications
        }

    def compare_classifications(
        self,
        system_output: Dict,
        ground_truth: Dict
    ) -> Dict:
        """
        Compare system classifications against ground truth.
        
        Validates Requirement 4.1: Compare system classifications against ground truth
        Validates Requirement 4.2: Count matches as correct
        Validates Requirement 4.3: Count mismatches as incorrect and log them
        
        Args:
            system_output: System's parameter classifications
            ground_truth: Verified ground truth classifications
            
        Returns:
            Comparison results with matches and mismatches
        """
        system_params = system_output.get('parameters', {})
        system_classifications = system_output.get('classifications', {})
        
        gt_params = ground_truth.get('parameters', {})
        gt_classifications = ground_truth.get('classifications', {})
        
        # Normalize parameter names for comparison
        system_normalized = {
            self._normalize_parameter_name(k): (k, v) 
            for k, v in system_classifications.items()
        }
        gt_normalized = {
            self._normalize_parameter_name(k): (k, v) 
            for k, v in gt_classifications.items()
        }
        
        matches = []
        mismatches = []
        missing_in_system = []
        extra_in_system = []
        
        # Find all parameters in ground truth
        for norm_name, (gt_name, gt_classification) in gt_normalized.items():
            if norm_name in system_normalized:
                sys_name, sys_classification = system_normalized[norm_name]
                
                # Get parameter values for logging
                sys_value = system_params.get(sys_name, {}).get('value')
                gt_value = gt_params.get(gt_name, {}).get('value')
                
                # Get reference ranges
                sys_ref = system_params.get(sys_name, {}).get('reference_range', {})
                gt_ref = gt_params.get(gt_name, {}).get('reference_range', {})
                
                if sys_classification == gt_classification:
                    # Requirement 4.2: Count as correct
                    matches.append({
                        "parameter": gt_name,
                        "system_name": sys_name,
                        "classification": gt_classification,
                        "value": gt_value,
                        "reference_range": gt_ref
                    })
                else:
                    # Requirement 4.3: Count as incorrect and log
                    mismatches.append({
                        "parameter": gt_name,
                        "system_name": sys_name,
                        "system_classification": sys_classification,
                        "ground_truth_classification": gt_classification,
                        "system_value": sys_value,
                        "ground_truth_value": gt_value,
                        "reference_range": gt_ref
                    })
            else:
                # Parameter in ground truth but not in system output
                missing_in_system.append({
                    "parameter": gt_name,
                    "classification": gt_classification,
                    "value": gt_params.get(gt_name, {}).get('value')
                })
        
        # Find parameters in system output but not in ground truth
        for norm_name, (sys_name, sys_classification) in system_normalized.items():
            if norm_name not in gt_normalized:
                extra_in_system.append({
                    "parameter": sys_name,
                    "classification": sys_classification,
                    "value": system_params.get(sys_name, {}).get('value')
                })
        
        return {
            "matches": matches,
            "mismatches": mismatches,
            "missing_in_system": missing_in_system,
            "extra_in_system": extra_in_system,
            "total_ground_truth": len(gt_normalized),
            "total_system": len(system_normalized),
            "correct": len(matches),
            "incorrect": len(mismatches)
        }

    def calculate_accuracy(self, comparisons: List[Dict]) -> Dict:
        """
        Calculate overall accuracy metrics.
        
        Validates Requirement 4.4: Report total parameters, correct/incorrect counts, 
        and overall accuracy percentage
        
        Args:
            comparisons: List of comparison results from compare_classifications
            
        Returns:
            Accuracy metrics dictionary
        """
        total_parameters = 0
        correct_classifications = 0
        incorrect_classifications = 0
        
        all_mismatches = []
        all_missing = []
        all_extra = []
        
        # Aggregate results from all comparisons
        for comparison in comparisons:
            total_parameters += comparison['total_ground_truth']
            correct_classifications += comparison['correct']
            incorrect_classifications += comparison['incorrect']
            
            all_mismatches.extend(comparison['mismatches'])
            all_missing.extend(comparison['missing_in_system'])
            all_extra.extend(comparison['extra_in_system'])
        
        # Calculate accuracy percentage
        if total_parameters > 0:
            accuracy_percentage = (correct_classifications / total_parameters) * 100
        else:
            accuracy_percentage = 0.0
        
        # Requirement 4.4: Report all required metrics
        return {
            "total_parameters": total_parameters,
            "correct_classifications": correct_classifications,
            "incorrect_classifications": incorrect_classifications,
            "accuracy_percentage": round(accuracy_percentage, 2),
            "all_mismatches": all_mismatches,
            "all_missing": all_missing,
            "all_extra": all_extra
        }
    
    def _find_report_file(self, reports_dir: Path, report_id: str) -> Optional[Path]:
        """
        Find the report file corresponding to a report_id.
        
        Args:
            reports_dir: Directory containing reports
            report_id: Report ID (e.g., "report_001", "report_015_png")
            
        Returns:
            Path to report file or None if not found
        """
        # Extract number from report_id (e.g., "report_001" -> 1, "report_015_png" -> 15)
        import re
        match = re.search(r'(\d+)', report_id)
        if not match:
            return None
        
        number = int(match.group(1))
        
        # Check if it's a PNG report
        is_png = '_png' in report_id
        
        # Try different filename patterns
        patterns = [
            f"test report ({number}).pdf",
            f"test report ({number}).png",
            f"report_{number:03d}.pdf",
            f"report_{number:03d}.png",
            f"report{number}.pdf",
            f"report{number}.png",
        ]
        
        # If we know it's PNG, prioritize PNG patterns
        if is_png:
            patterns = [p for p in patterns if p.endswith('.png')] + [p for p in patterns if p.endswith('.pdf')]
        
        for pattern in patterns:
            report_path = reports_dir / pattern
            if report_path.exists():
                return report_path
        
        return None

    def run_validation(
        self,
        reports_dir: str,
        ground_truth_dir: str
    ) -> Dict:
        """
        Run complete validation pipeline.
        
        Args:
            reports_dir: Directory containing test reports
            ground_truth_dir: Directory containing ground truth files
            
        Returns:
            Complete validation results with accuracy metrics
        """
        reports_dir = Path(reports_dir)
        ground_truth_dir = Path(ground_truth_dir)
        
        print(f"\n{'='*70}")
        print(f"VALIDATION PIPELINE")
        print(f"{'='*70}")
        print(f"Reports directory: {reports_dir}")
        print(f"Ground truth directory: {ground_truth_dir}")
        print(f"{'='*70}\n")
        
        # Load ground truth files
        print("Loading ground truth files...")
        ground_truth = self.load_ground_truth(str(ground_truth_dir))
        print(f"Loaded {len(ground_truth)} ground truth files\n")
        
        if len(ground_truth) == 0:
            return {
                "error": "No ground truth files found",
                "reports_processed": 0,
                "accuracy": None
            }
        
        # Process each report and compare with ground truth
        comparisons = []
        per_report_results = []
        errors = []
        
        for i, (report_id, gt_data) in enumerate(sorted(ground_truth.items()), 1):
            print(f"[{i}/{len(ground_truth)}] Validating: {report_id}")
            
            try:
                # Find the report file
                report_path = self._find_report_file(reports_dir, report_id)
                
                if not report_path:
                    print(f"  ✗ Report file not found")
                    errors.append({
                        "report_id": report_id,
                        "error": "Report file not found"
                    })
                    continue
                
                # Process report with current system
                system_output = self.process_report(str(report_path))
                
                # Compare with ground truth
                comparison = self.compare_classifications(system_output, gt_data)
                comparisons.append(comparison)
                
                # Calculate per-report accuracy
                if comparison['total_ground_truth'] > 0:
                    report_accuracy = (comparison['correct'] / comparison['total_ground_truth']) * 100
                else:
                    report_accuracy = 0.0
                
                per_report_results.append({
                    "report_id": report_id,
                    "total_parameters": comparison['total_ground_truth'],
                    "correct": comparison['correct'],
                    "incorrect": comparison['incorrect'],
                    "accuracy": round(report_accuracy, 2)
                })
                
                print(f"  ✓ {comparison['correct']}/{comparison['total_ground_truth']} correct ({report_accuracy:.1f}%)")
                
                if comparison['incorrect'] > 0:
                    print(f"    Mismatches: {comparison['incorrect']}")
                if comparison['missing_in_system']:
                    print(f"    Missing in system: {len(comparison['missing_in_system'])}")
                if comparison['extra_in_system']:
                    print(f"    Extra in system: {len(comparison['extra_in_system'])}")
                
            except Exception as e:
                print(f"  ✗ Error: {str(e)}")
                errors.append({
                    "report_id": report_id,
                    "error": str(e)
                })
        
        # Calculate overall accuracy
        print(f"\n{'='*70}")
        print(f"CALCULATING OVERALL ACCURACY")
        print(f"{'='*70}\n")
        
        accuracy_metrics = self.calculate_accuracy(comparisons)
        
        print(f"Total parameters evaluated: {accuracy_metrics['total_parameters']}")
        print(f"Correct classifications: {accuracy_metrics['correct_classifications']}")
        print(f"Incorrect classifications: {accuracy_metrics['incorrect_classifications']}")
        print(f"Overall accuracy: {accuracy_metrics['accuracy_percentage']}%")
        
        # Check if target is met (>98%)
        target_met = accuracy_metrics['accuracy_percentage'] >= 98.0
        print(f"\nTarget (≥98%): {'✓ ACHIEVED' if target_met else '✗ NOT MET'}")
        
        print(f"\n{'='*70}")
        print(f"VALIDATION COMPLETE")
        print(f"{'='*70}\n")
        
        # Return complete results
        return {
            "timestamp": datetime.now().isoformat(),
            "reports_processed": len(ground_truth),
            "reports_with_errors": len(errors),
            "accuracy_metrics": accuracy_metrics,
            "per_report_results": per_report_results,
            "errors": errors,
            "target_met": target_met
        }


if __name__ == "__main__":
    # Test the validation pipeline
    pipeline = ValidationPipeline()
    
    # Run validation
    results = pipeline.run_validation(
        reports_dir="data/test_reports",
        ground_truth_dir="evaluation/test_dataset/ground_truth"
    )
    
    # Save results
    results_path = Path("evaluation/validation_results.json")
    with open(results_path, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"Results saved to: {results_path}")
