"""
Input parser for blood reports
Handles PDF, Image, and JSON formats
"""

import json
import logging
from pathlib import Path
from typing import Dict, Optional, Any
from enum import Enum
import aiofiles

logger = logging.getLogger(__name__)

class FileFormat(str, Enum):
    PDF = "pdf"
    IMAGE = "image"
    JSON = "json"
    UNKNOWN = "unknown"

class InputParser:
    """Main input parser class"""
    
    def __init__(self):
        self.supported_extensions = {
            '.pdf': FileFormat.PDF,
            '.json': FileFormat.JSON,
            '.jpg': FileFormat.IMAGE,
            '.jpeg': FileFormat.IMAGE,
            '.png': FileFormat.IMAGE,
        }
    
    def detect_format(self, filename: str) -> FileFormat:
        """Detect file format from extension"""
        suffix = Path(filename).suffix.lower()
        return self.supported_extensions.get(suffix, FileFormat.UNKNOWN)
    
    async def parse_file(self, file_path: str) -> Dict[str, Any]:
        """
        Parse uploaded file and extract raw content
        Returns: Dict with format, raw_content, and metadata
        """
        file_format = self.detect_format(file_path)
        
        if file_format == FileFormat.UNKNOWN:
            raise ValueError(f"Unsupported file format: {file_path}")
        
        logger.info(f"Parsing file: {file_path} (format: {file_format})")
        
        if file_format == FileFormat.JSON:
            return await self._parse_json(file_path)
        elif file_format == FileFormat.PDF:
            return await self._parse_pdf(file_path)
        elif file_format == FileFormat.IMAGE:
            return await self._parse_image(file_path)
    
    async def _parse_json(self, file_path: str) -> Dict[str, Any]:
        """Parse JSON structured data"""
        try:
            async with aiofiles.open(file_path, 'r', encoding='utf-8') as f:
                content = await f.read()
                data = json.loads(content)
            
            return {
                "format": FileFormat.JSON,
                "raw_content": data,
                "metadata": {
                    "file_path": file_path,
                    "parsing_method": "json"
                }
            }
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing error: {e}")
            raise ValueError(f"Invalid JSON format: {e}")
    
    async def _parse_pdf(self, file_path: str) -> Dict[str, Any]:
        """Parse PDF file (text extraction)"""
        try:
            import pdfplumber
            
            text_content = []
            tables = []
            
            with pdfplumber.open(file_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    # Extract text
                    page_text = page.extract_text()
                    if page_text:
                        text_content.append(page_text)
                    
                    # Extract tables
                    page_tables = page.extract_tables()
                    if page_tables:
                        tables.extend(page_tables)
            
            return {
                "format": FileFormat.PDF,
                "raw_content": {
                    "text": "\n\n".join(text_content),
                    "tables": tables
                },
                "metadata": {
                    "file_path": file_path,
                    "parsing_method": "pdfplumber",
                    "num_pages": len(text_content)
                }
            }
        except ImportError:
            logger.warning("pdfplumber not installed, falling back to basic extraction")
            return {
                "format": FileFormat.PDF,
                "raw_content": {"text": "", "tables": []},
                "metadata": {
                    "file_path": file_path,
                    "parsing_method": "fallback",
                    "error": "pdfplumber not available"
                }
            }
        except Exception as e:
            logger.error(f"PDF parsing error: {e}")
            raise ValueError(f"Failed to parse PDF: {e}")
    
    async def _parse_image(self, file_path: str) -> Dict[str, Any]:
        """Parse image file using OCR"""
        # For now, return placeholder
        # OCR implementation can be added later with EasyOCR
        logger.info(f"Image parsing for {file_path} - OCR not yet implemented")
        return {
            "format": FileFormat.IMAGE,
            "raw_content": {"text": "", "ocr_pending": True},
            "metadata": {
                "file_path": file_path,
                "parsing_method": "pending_ocr_implementation"
            }
        }

# Global instance
input_parser = InputParser()
