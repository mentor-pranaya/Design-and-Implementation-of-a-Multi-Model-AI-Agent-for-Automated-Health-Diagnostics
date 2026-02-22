"""
Ground Truth Generator Module

Automatically generates ground truth templates from system output for validation.
Integrates with comprehensive_extractor.py and unified_reference_manager.py.
"""

import json
import os
import re
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


class GroundTruthGenerator:
    """Generates ground truth templates for validation."""
    
    def __init__(self, reference_manager: Optional[UnifiedReferenceManager] = None):
        """
        Initialize ground truth generator.
        
        Args:
            reference_manager: UnifiedReferenceManager instance (creates new if None)
        """
        self.reference_manager = reference_manager or UnifiedReferenceManager()
        self.schema = self._load_template_schema()
    
    def _load_template_schema(self) -> Dict:
        """Load the template schema for validation."""
        template_path = Path(__file__).parent / "test_dataset" / "ground_truth" / "TEMPLATE.json"
        if template_path.exists():
            with open(template_path, 'r') as f:
                return json.load(f)
        return {}
    
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
    
    def _determine_report_format(self, report_path: str) -> str:
        """Determine report format (PDF/PNG)."""
        suffix = Path(report_path).suffix.lower()
        if suffix == '.pdf':
            return 'PDF'
        elif suffix in ['.png', '.jpg', '.jpeg']:
            return 'PNG'
        return 'Unknown'
    
    def _extract_report_metadata(self, text: str, report_path: str) -> Dict:
        """
        Extract metadata from report text.
        
        Args:
            text: OCR text from report
            report_path: Path to report file
            
        Returns:
            Metadata dictionary
        """
        metadata = {
            "laboratory": "Unknown",
            "format": self._determine_report_format(report_path),
            "date": datetime.now().strftime("%Y-%m-%d"),
            "completeness": "Complete",
            "abnormality_type": "Unknown",
            "verified": False,
            "verified_by": "",
            "verified_date": ""
        }
        
        # Try to extract lab name (common patterns)
        lab_patterns = [
            r'(?:laboratory|lab|diagnostics|pathology)[\s:]+([A-Z][A-Za-z\s&]+)',
            r'^([A-Z][A-Za-z\s&]+)(?:laboratory|lab|diagnostics)',
        ]
        
        for pattern in lab_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.MULTILINE)
            if match:
                metadata["laboratory"] = match.group(1).strip()
                break
        
        # Try to extract date
        date_patterns = [
            r'(?:date|collected|reported)[\s:]+(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
            r'(\d{1,2}[-/]\d{1,2}[-/]\d{2,4})',
        ]
        
        for pattern in date_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                metadata["date"] = match.group(1)
                break
        
        return metadata
    
    def _normalize_parameter_name(self, param_name: str) -> str:
        """
        Normalize parameter name to match UnifiedReferenceManager format.
        
        This uses the same mapping as the validation pipeline to ensure consistency.
        Maps lowercase parameter names from the extractor to the exact names
        used by UnifiedReferenceManager (from NHANES and ABIM data).
        
        Args:
            param_name: Parameter name from extractor (e.g., "hemoglobin", "wbc", "platelet")
            
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
    
    def _get_reference_range_for_parameter(
        self,
        parameter: str,
        age: Optional[int] = None,
        sex: Optional[str] = None
    ) -> Dict:
        """
        Get reference range for a parameter.
        
        Args:
            parameter: Parameter name
            age: Patient age (optional)
            sex: Patient sex (optional)
            
        Returns:
            Reference range dictionary with min/max
        """
        # Normalize parameter name to match reference manager format
        normalized_param = self._normalize_parameter_name(parameter)
        
        ref_range = self.reference_manager.get_reference_range(
            parameter=normalized_param,
            age=age,
            sex=sex
        )
        
        if ref_range.get('available', True):
            return {
                "min": ref_range['min'],
                "max": ref_range['max'],
                "unit": ref_range.get('unit', 'N/A'),
                "source": ref_range.get('source', 'unknown')
            }
        
        return {
            "min": None,
            "max": None,
            "unit": "N/A",
            "source": "unavailable"
        }
    
    def _classify_parameter(
        self,
        parameter: str,
        value: float,
        reference_range: Dict
    ) -> str:
        """
        Classify parameter as Normal/High/Low.
        
        Args:
            parameter: Parameter name
            value: Measured value
            reference_range: Reference range with min/max
            
        Returns:
            Classification string (Normal/High/Low/Unknown)
        """
        if reference_range['min'] is None or reference_range['max'] is None:
            return "Unknown"
        
        min_val = reference_range['min']
        max_val = reference_range['max']
        
        if value < min_val:
            return "Low"
        elif value > max_val:
            return "High"
        else:
            return "Normal"
    
    def generate_template(
        self,
        report_path: str,
        age: Optional[int] = None,
        sex: Optional[str] = None
    ) -> Dict:
        """
        Generate ground truth template for a single report.
        
        Args:
            report_path: Path to PDF or PNG report
            age: Patient age (optional, for age-specific ranges)
            sex: Patient sex (optional, for sex-specific ranges)
            
        Returns:
            Dictionary matching TEMPLATE.json format
        """
        # Extract text from report
        text = self._extract_text_from_report(report_path)
        
        # Extract parameters using comprehensive extractor
        extracted_params = extract_parameters_comprehensive(text)
        
        # Generate report ID from filename
        report_id = self._generate_report_id(report_path)
        
        # Extract metadata
        metadata = self._extract_report_metadata(text, report_path)
        
        # Build parameters dictionary
        parameters = {}
        classifications = {}
        
        for param_name, param_data in extracted_params.items():
            value = param_data['value']
            unit = param_data['unit']
            
            # Get reference range
            ref_range = self._get_reference_range_for_parameter(
                parameter=param_name,
                age=age,
                sex=sex
            )
            
            # Store parameter with reference range
            parameters[param_name] = {
                "value": value,
                "unit": unit,
                "reference_range": {
                    "min": ref_range['min'],
                    "max": ref_range['max']
                }
            }
            
            # Classify parameter
            classification = self._classify_parameter(param_name, value, ref_range)
            classifications[param_name] = classification
        
        # Build complete template
        template = {
            "report_id": report_id,
            "report_metadata": metadata,
            "parameters": parameters,
            "classifications": classifications,
            "notes": "Auto-generated template - requires manual verification"
        }
        
        return template
    
    def _generate_report_id(self, report_path: str) -> str:
        """
        Generate report ID from filename.
        
        Follows convention: report_001.json, report_015_png.json
        
        Args:
            report_path: Path to report file
            
        Returns:
            Report ID string
        """
        path = Path(report_path)
        filename = path.stem  # Get filename without extension
        
        # Extract number from filename (e.g., "test report (15)" -> "15")
        match = re.search(r'\((\d+)\)', filename)
        if match:
            number = int(match.group(1))
            # Format as report_XXX or report_XXX_png
            if path.suffix.lower() == '.png':
                return f"report_{number:03d}_png"
            else:
                return f"report_{number:03d}"
        
        # Fallback: use filename as-is
        return filename.replace(' ', '_').lower()
    
    def _generate_output_filename(self, report_id: str) -> str:
        """Generate output filename from report ID."""
        return f"{report_id}.json"
    
    def save_template(self, template: Dict, output_path: str):
        """
        Save template as formatted JSON.
        
        Args:
            template: Template dictionary
            output_path: Path to save JSON file
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(template, f, indent=2)
    
    def validate_template(self, template: Dict) -> tuple[bool, List[str]]:
        """
        Validate template against schema.
        
        Args:
            template: Template dictionary to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required top-level fields
        required_fields = ['report_id', 'report_metadata', 'parameters', 'classifications']
        for field in required_fields:
            if field not in template:
                errors.append(f"Missing required field: {field}")
        
        # Check report_metadata structure
        if 'report_metadata' in template:
            metadata = template['report_metadata']
            required_metadata = ['laboratory', 'format', 'date', 'completeness', 'abnormality_type']
            for field in required_metadata:
                if field not in metadata:
                    errors.append(f"Missing metadata field: {field}")
        
        # Check parameters structure
        if 'parameters' in template:
            for param_name, param_data in template['parameters'].items():
                if not isinstance(param_data, dict):
                    errors.append(f"Parameter {param_name} must be a dictionary")
                    continue
                
                required_param_fields = ['value', 'unit', 'reference_range']
                for field in required_param_fields:
                    if field not in param_data:
                        errors.append(f"Parameter {param_name} missing field: {field}")
                
                # Check reference_range structure
                if 'reference_range' in param_data:
                    ref_range = param_data['reference_range']
                    if 'min' not in ref_range or 'max' not in ref_range:
                        errors.append(f"Parameter {param_name} reference_range missing min/max")
        
        # Check classifications
        if 'classifications' in template and 'parameters' in template:
            params = set(template['parameters'].keys())
            classifications = set(template['classifications'].keys())
            
            # Every parameter should have a classification
            missing_classifications = params - classifications
            if missing_classifications:
                errors.append(f"Missing classifications for: {missing_classifications}")
        
        return (len(errors) == 0, errors)
    
    def generate_all_templates(
        self,
        reports_dir: str,
        output_dir: str,
        age: Optional[int] = None,
        sex: Optional[str] = None
    ) -> Dict:
        """
        Generate templates for all reports in directory.
        
        Args:
            reports_dir: Directory containing test reports
            output_dir: Directory to save ground truth files
            age: Patient age (optional)
            sex: Patient sex (optional)
            
        Returns:
            Summary with counts and status
        """
        reports_dir = Path(reports_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Find all PDF and PNG files
        report_files = []
        report_files.extend(reports_dir.glob("*.pdf"))
        report_files.extend(reports_dir.glob("*.png"))
        report_files = sorted(report_files)
        
        summary = {
            "total_reports": len(report_files),
            "successful": 0,
            "failed": 0,
            "reports": [],
            "errors": []
        }
        
        print(f"\n{'='*70}")
        print(f"GROUND TRUTH GENERATION")
        print(f"{'='*70}")
        print(f"Reports directory: {reports_dir}")
        print(f"Output directory: {output_dir}")
        print(f"Total reports found: {len(report_files)}")
        print(f"{'='*70}\n")
        
        for i, report_path in enumerate(report_files, 1):
            print(f"[{i}/{len(report_files)}] Processing: {report_path.name}")
            
            try:
                # Generate template
                template = self.generate_template(str(report_path), age=age, sex=sex)
                
                # Validate template
                is_valid, validation_errors = self.validate_template(template)
                if not is_valid:
                    print(f"  ⚠ Validation warnings: {len(validation_errors)}")
                    for error in validation_errors:
                        print(f"    - {error}")
                
                # Save template
                output_filename = self._generate_output_filename(template['report_id'])
                output_path = output_dir / output_filename
                self.save_template(template, str(output_path))
                
                param_count = len(template['parameters'])
                print(f"  ✓ Generated: {output_filename} ({param_count} parameters)")
                
                summary["successful"] += 1
                summary["reports"].append({
                    "report_id": template['report_id'],
                    "source_file": report_path.name,
                    "output_file": output_filename,
                    "parameter_count": param_count,
                    "status": "success"
                })
                
            except Exception as e:
                print(f"  ✗ Failed: {str(e)}")
                summary["failed"] += 1
                summary["errors"].append({
                    "report": report_path.name,
                    "error": str(e)
                })
                summary["reports"].append({
                    "report_id": report_path.stem,
                    "source_file": report_path.name,
                    "status": "failed",
                    "error": str(e)
                })
        
        print(f"\n{'='*70}")
        print(f"GENERATION COMPLETE")
        print(f"{'='*70}")
        print(f"Successful: {summary['successful']}/{summary['total_reports']}")
        print(f"Failed: {summary['failed']}/{summary['total_reports']}")
        print(f"{'='*70}\n")
        
        return summary


if __name__ == "__main__":
    # Test the generator
    generator = GroundTruthGenerator()
    
    # Generate templates for all test reports
    summary = generator.generate_all_templates(
        reports_dir="data/test_reports",
        output_dir="evaluation/test_dataset/ground_truth"
    )
    
    # Save summary
    summary_path = Path("evaluation/test_dataset/ground_truth/generation_summary.json")
    with open(summary_path, 'w') as f:
        json.dump(summary, f, indent=2)
    
    print(f"Summary saved to: {summary_path}")
