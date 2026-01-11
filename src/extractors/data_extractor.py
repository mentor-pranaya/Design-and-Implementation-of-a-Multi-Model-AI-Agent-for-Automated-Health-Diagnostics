"""
Data Extraction Engine
Extracts blood parameters, values, units, and reference ranges
"""

import re
from typing import List, Dict, Any, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ParameterExtractor:
    """Extract blood parameters from parsed report data"""
    
    # Common parameter name variations
    PARAMETER_ALIASES = {
        'hemoglobin': ['hemoglobin', 'hb', 'hgb'],
        'wbc': ['wbc', 'white blood cell', 'white blood cells', 'leukocytes'],
        'rbc': ['rbc', 'red blood cell', 'red blood cells', 'erythrocytes'],
        'platelets': ['platelets', 'platelet count', 'plt'],
        'glucose': ['glucose', 'blood sugar', 'blood glucose'],
        'cholesterol': ['total_cholesterol', 'cholesterol', 'total cholesterol'],
        'hdl': ['hdl', 'hdl cholesterol', 'high density lipoprotein'],
        'ldl': ['ldl', 'ldl cholesterol', 'low density lipoprotein'],
        'triglycerides': ['triglycerides', 'trig'],
        'creatinine': ['creatinine', 'creat'],
        'bun': ['bun', 'blood urea nitrogen', 'urea'],
        'alt': ['alt', 'sgpt', 'alanine aminotransferase'],
        'ast': ['ast', 'sgot', 'aspartate aminotransferase'],
        'tsh': ['tsh', 'thyroid stimulating hormone'],
        'hba1c': ['hba1c', 'hemoglobin a1c', 'glycated hemoglobin']
    }
    
    # Unit variations
    UNIT_STANDARDIZATION = {
        'g/dl': 'g/dL',
        'gm/dl': 'g/dL',
        'mg/dl': 'mg/dL',
        'mmol/l': 'mmol/L',
        'cells/μl': '10^3/μL',
        'k/μl': '10^3/μL',
        'k/ul': '10^3/μL',
        'thou/ul': '10^3/μL',
        'm/μl': '10^6/μL',
        'u/l': 'U/L',
        'iu/ml': 'mIU/L',
        'miu/l': 'mIU/L',
        '%': '%'
    }
    
    def __init__(self):
        self.extracted_parameters = []
    
    def extract(self, parsed_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Extract parameters from parsed report data
        
        Args:
            parsed_data: Dictionary from InputParser
            
        Returns:
            List of extracted parameters with standardized names
        """
        format_type = parsed_data.get('format', 'unknown')
        
        if format_type == 'json':
            return self._extract_from_json(parsed_data)
        elif format_type in ['pdf', 'text']:
            return self._extract_from_text(parsed_data)
        else:
            logger.warning(f"Unknown format: {format_type}")
            return []
    
    def _extract_from_json(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract from JSON structure"""
        parameters = data.get('parameters', [])
        extracted = []
        
        for param in parameters:
            # Standardize parameter name
            original_name = param.get('name', '').lower().replace(' ', '_')
            standard_name = self._standardize_parameter_name(original_name)
            
            # Standardize unit
            original_unit = param.get('unit', '')
            standard_unit = self._standardize_unit(original_unit)
            
            extracted_param = {
                'original_name': param.get('name', 'Unknown'),
                'standard_name': standard_name,
                'value': param.get('value'),
                'original_unit': original_unit,
                'standard_unit': standard_unit,
                'reference_min': param.get('reference_min'),
                'reference_max': param.get('reference_max'),
                'extraction_confidence': 1.0  # High confidence for structured data
            }
            
            extracted.append(extracted_param)
            
        self.extracted_parameters = extracted
        logger.info(f"Extracted {len(extracted)} parameters from JSON")
        return extracted
    
    def _extract_from_text(self, data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract from unstructured text (PDF/TXT)"""
        text = data.get('raw_text', '')
        extracted = []
        
        # Pattern to match: Parameter Name: Value Unit (Reference: Min - Max)
        # Example: "Hemoglobin: 14.5 g/dL (Reference: 13.0 - 17.0)"
        pattern = r'([A-Za-z0-9\s]+?):\s*(\d+\.?\d*)\s*([A-Za-z/^μ%]+)(?:\s*\((?:Reference|Ref|Normal):\s*(\d+\.?\d*)\s*-\s*(\d+\.?\d*)\))?'
        
        matches = re.finditer(pattern, text, re.IGNORECASE)
        
        for match in matches:
            param_name = match.group(1).strip()
            value = float(match.group(2))
            unit = match.group(3).strip()
            ref_min = float(match.group(4)) if match.group(4) else None
            ref_max = float(match.group(5)) if match.group(5) else None
            
            standard_name = self._standardize_parameter_name(param_name.lower().replace(' ', '_'))
            standard_unit = self._standardize_unit(unit.lower())
            
            # Only include if we recognize the parameter
            if standard_name != 'unknown':
                extracted_param = {
                    'original_name': param_name,
                    'standard_name': standard_name,
                    'value': value,
                    'original_unit': unit,
                    'standard_unit': standard_unit,
                    'reference_min': ref_min,
                    'reference_max': ref_max,
                    'extraction_confidence': 0.8  # Lower confidence for text extraction
                }
                extracted.append(extracted_param)
        
        self.extracted_parameters = extracted
        logger.info(f"Extracted {len(extracted)} parameters from text")
        return extracted
    
    def _standardize_parameter_name(self, name: str) -> str:
        """Standardize parameter name using aliases"""
        name = name.lower().strip().replace(' ', '_')
        
        for standard, aliases in self.PARAMETER_ALIASES.items():
            if name in aliases:
                return standard.upper()
        
        # Return cleaned name if not in aliases
        return name.upper() if name else 'UNKNOWN'
    
    def _standardize_unit(self, unit: str) -> str:
        """Standardize unit notation"""
        unit_lower = unit.lower().strip()
        return self.UNIT_STANDARDIZATION.get(unit_lower, unit)
    
    def get_parameter_count(self) -> int:
        """Get count of extracted parameters"""
        return len(self.extracted_parameters)
    
    def get_parameters_by_category(self) -> Dict[str, List[Dict]]:
        """Group parameters by medical category"""
        categories = {
            'Complete Blood Count': ['HEMOGLOBIN', 'WBC', 'RBC', 'PLATELETS'],
            'Metabolic Panel': ['GLUCOSE', 'CREATININE', 'BUN'],
            'Lipid Panel': ['CHOLESTEROL', 'HDL', 'LDL', 'TRIGLYCERIDES'],
            'Liver Function': ['ALT', 'AST'],
            'Thyroid': ['TSH'],
            'Diabetes Markers': ['HBA1C', 'GLUCOSE']
        }
        
        categorized = {cat: [] for cat in categories}
        categorized['Other'] = []
        
        for param in self.extracted_parameters:
            added = False
            for category, param_list in categories.items():
                if param['standard_name'] in param_list:
                    categorized[category].append(param)
                    added = True
                    break
            
            if not added:
                categorized['Other'].append(param)
        
        # Remove empty categories
        return {k: v for k, v in categorized.items() if v}