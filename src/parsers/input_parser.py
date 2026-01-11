"""
Input Interface & Parser
Handles PDF, JSON, and image inputs for blood reports
"""

import json
import PyPDF2
from pathlib import Path
from typing import Dict, Any, Union
import re

class InputParser:
    """Parse blood reports from various input formats"""
    
    SUPPORTED_FORMATS = ['.json', '.pdf', '.txt']
    
    def __init__(self):
        self.raw_content = None
        self.format = None
    
    def parse(self, file_path: Union[str, Path]) -> Dict[str, Any]:
        """
        Main parsing method that routes to appropriate parser based on file type
        
        Args:
            file_path: Path to the blood report file
            
        Returns:
            Dictionary containing parsed report data
        """
        file_path = Path(file_path)
        
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")
        
        self.format = file_path.suffix.lower()
        
        if self.format not in self.SUPPORTED_FORMATS:
            raise ValueError(f"Unsupported format: {self.format}. Supported: {self.SUPPORTED_FORMATS}")
        
        if self.format == '.json':
            return self._parse_json(file_path)
        elif self.format == '.pdf':
            return self._parse_pdf(file_path)
        elif self.format == '.txt':
            return self._parse_text(file_path)
    
    def _parse_json(self, file_path: Path) -> Dict[str, Any]:
        """Parse JSON format blood report"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            
            self.raw_content = data
            
            # Validate JSON structure
            required_fields = ['report_id', 'parameters']
            for field in required_fields:
                if field not in data:
                    raise ValueError(f"Missing required field: {field}")
            
            return {
                'format': 'json',
                'report_id': data.get('report_id', 'UNKNOWN'),
                'patient_id': data.get('patient_id', 'UNKNOWN'),
                'test_date': data.get('test_date', 'UNKNOWN'),
                'lab_name': data.get('lab_name', 'UNKNOWN'),
                'gender': data.get('gender', None),
                'age': data.get('age', None),
                'parameters': data.get('parameters', []),
                'raw_data': data
            }
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON format: {e}")
    
    def _parse_pdf(self, file_path: Path) -> Dict[str, Any]:
        """Parse PDF format blood report using PyPDF2"""
        try:
            with open(file_path, 'rb') as f:
                pdf_reader = PyPDF2.PdfReader(f)
                
                # Extract text from all pages
                text_content = ""
                for page in pdf_reader.pages:
                    text_content += page.extract_text() + "\n"
            
            self.raw_content = text_content
            
            # Extract structured data from text
            # This is a simplified extraction - in production, use more robust NLP/regex
            return {
                'format': 'pdf',
                'report_id': self._extract_field(text_content, r'Report\s*ID[:\s]+(\S+)', 'RPT_PDF'),
                'patient_id': self._extract_field(text_content, r'Patient\s*ID[:\s]+(\S+)', 'PAT_UNKNOWN'),
                'test_date': self._extract_field(text_content, r'Date[:\s]+(\d{4}-\d{2}-\d{2})', 'UNKNOWN'),
                'lab_name': self._extract_field(text_content, r'Laboratory[:\s]+([^\n]+)', 'UNKNOWN'),
                'gender': None,
                'age': None,
                'parameters': [],  # Will be extracted in next module
                'raw_text': text_content
            }
            
        except Exception as e:
            raise ValueError(f"Error parsing PDF: {e}")
    
    def _parse_text(self, file_path: Path) -> Dict[str, Any]:
        """Parse plain text format blood report"""
        try:
            with open(file_path, 'r') as f:
                text_content = f.read()
            
            self.raw_content = text_content
            
            return {
                'format': 'text',
                'report_id': self._extract_field(text_content, r'Report\s*ID[:\s]+(\S+)', 'RPT_TXT'),
                'patient_id': self._extract_field(text_content, r'Patient\s*ID[:\s]+(\S+)', 'PAT_UNKNOWN'),
                'test_date': self._extract_field(text_content, r'Date[:\s]+(\d{4}-\d{2}-\d{2})', 'UNKNOWN'),
                'lab_name': self._extract_field(text_content, r'Laboratory[:\s]+([^\n]+)', 'UNKNOWN'),
                'gender': None,
                'age': None,
                'parameters': [],
                'raw_text': text_content
            }
            
        except Exception as e:
            raise ValueError(f"Error parsing text file: {e}")
    
    def _extract_field(self, text: str, pattern: str, default: str = 'UNKNOWN') -> str:
        """Extract field using regex pattern"""
        match = re.search(pattern, text, re.IGNORECASE)
        return match.group(1).strip() if match else default

    def get_format(self) -> str:
        """Return the format of the last parsed file"""
        return self.format
    
    def get_raw_content(self) -> Any:
        """Return the raw content of the last parsed file"""
        return self.raw_content