"""
Data extraction engine
Extracts blood parameters from parsed content
"""

import re
import logging
from typing import Dict, List, Any, Optional, Tuple

logger = logging.getLogger(__name__)

class DataExtractor:
    """Extract blood parameters from various formats"""
    
    def __init__(self):
        # Common parameter patterns
        self.parameter_patterns = [
            # Pattern: "Parameter: Value Unit"
            r'([A-Za-z][A-Za-z0-9\s\-/]+):\s*([0-9.]+)\s*([A-Za-z/%μ]+)',
            # Pattern: "Parameter Value Unit"
            r'([A-Za-z][A-Za-z0-9\s\-/]+)\s+([0-9.]+)\s+([A-Za-z/%μ]+)',
            # Pattern with reference range: "Parameter: Value Unit (Range: X-Y)"
            r'([A-Za-z][A-Za-z0-9\s\-/]+):\s*([0-9.]+)\s*([A-Za-z/%μ]+)\s*\(.*?([0-9.]+)\s*-\s*([0-9.]+)',
        ]
    
    async def extract(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract parameters from parsed data
        Returns: Dict with extracted parameters list
        """
        file_format = parsed_data.get("format")
        raw_content = parsed_data.get("raw_content")
        
        if file_format == "json":
            return await self._extract_from_json(raw_content)
        elif file_format == "pdf":
            return await self._extract_from_pdf(raw_content)
        elif file_format == "image":
            return await self._extract_from_image(raw_content)
        else:
            raise ValueError(f"Unsupported format for extraction: {file_format}")
    
    async def _extract_from_json(self, content: Dict) -> Dict[str, Any]:
        """Extract from JSON structured data"""
        parameters = []
        
        # Expected JSON format:
        # {"parameters": [{"name": "...", "value": ..., "unit": "..."}]}
        if "parameters" in content and isinstance(content["parameters"], list):
            for param in content["parameters"]:
                if all(k in param for k in ["name", "value", "unit"]):
                    parameters.append({
                        "name": param["name"].strip(),
                        "value": float(param["value"]),
                        "unit": param["unit"].strip(),
                        "reference_min": param.get("reference_min"),
                        "reference_max": param.get("reference_max"),
                        "confidence": 1.0
                    })
        
        # Alternative flat format: {"hemoglobin": 15.5, "glucose": 95, ...}
        elif any(isinstance(v, (int, float)) for v in content.values()):
            for key, value in content.items():
                if isinstance(value, (int, float)):
                    parameters.append({
                        "name": key.strip(),
                        "value": float(value),
                        "unit": "unknown",  # Will be inferred in validation
                        "confidence": 0.8
                    })
        
        return {
            "parameters": parameters,
            "extraction_method": "json",
            "total_extracted": len(parameters)
        }
    
    async def _extract_from_pdf(self, content: Dict) -> Dict[str, Any]:
        """Extract from PDF text and tables"""
        parameters = []
        
        # Extract from tables first (more reliable)
        if "tables" in content and content["tables"]:
            table_params = self._extract_from_tables(content["tables"])
            parameters.extend(table_params)
        
        # Extract from text
        if "text" in content and content["text"]:
            text_params = self._extract_from_text(content["text"])
            parameters.extend(text_params)
        
        # Remove duplicates (keep higher confidence)
        parameters = self._deduplicate_parameters(parameters)
        
        return {
            "parameters": parameters,
            "extraction_method": "pdf",
            "total_extracted": len(parameters)
        }
    
    async def _extract_from_image(self, content: Dict) -> Dict[str, Any]:
        """Extract from OCR text"""
        parameters = []
        
        if "text" in content and content["text"]:
            parameters = self._extract_from_text(content["text"])
        
        return {
            "parameters": parameters,
            "extraction_method": "ocr",
            "total_extracted": len(parameters)
        }
    
    def _extract_from_tables(self, tables: List[List[List[str]]]) -> List[Dict]:
        """Extract parameters from table data"""
        parameters = []
        
        for table in tables:
            if not table or len(table) < 2:
                continue
            
            # Try to identify parameter column, value column, unit column
            for row in table[1:]:  # Skip header
                if len(row) >= 2:
                    param_name = str(row[0]).strip() if row[0] else ""
                    value_str = str(row[1]).strip() if row[1] else ""
                    unit = str(row[2]).strip() if len(row) > 2 and row[2] else ""
                    
                    # Extract numeric value
                    value = self._extract_numeric_value(value_str)
                    
                    if param_name and value is not None:
                        parameters.append({
                            "name": param_name,
                            "value": value,
                            "unit": unit,
                            "confidence": 0.95
                        })
        
        return parameters
    
    def _extract_from_text(self, text: str) -> List[Dict]:
        """Extract parameters from free text"""
        parameters = []
        
        for pattern in self.parameter_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                groups = match.groups()
                if len(groups) >= 3:
                    param_name = groups[0].strip()
                    value_str = groups[1].strip()
                    unit = groups[2].strip()
                    
                    value = self._extract_numeric_value(value_str)
                    
                    if value is not None:
                        param_dict = {
                            "name": param_name,
                            "value": value,
                            "unit": unit,
                            "confidence": 0.85
                        }
                        
                        # Add reference range if available
                        if len(groups) >= 5:
                            param_dict["reference_min"] = float(groups[3])
                            param_dict["reference_max"] = float(groups[4])
                        
                        parameters.append(param_dict)
        
        return parameters
    
    def _extract_numeric_value(self, value_str: str) -> Optional[float]:
        """Extract numeric value from string"""
        # Remove common non-numeric characters
        cleaned = re.sub(r'[^\d.]', '', value_str)
        
        try:
            return float(cleaned)
        except ValueError:
            return None
    
    def _deduplicate_parameters(self, parameters: List[Dict]) -> List[Dict]:
        """Remove duplicate parameters, keeping highest confidence"""
        seen = {}
        
        for param in parameters:
            name = param["name"].lower().strip()
            
            if name not in seen or param["confidence"] > seen[name]["confidence"]:
                seen[name] = param
        
        return list(seen.values())

# Global instance
data_extractor = DataExtractor()
