import json
import csv
from pathlib import Path
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from ocr.pdf_ocr import extract_text_from_pdf
    from extraction.pdf_parser import parse_pdf_text, extract_patient_info
    PDF_SUPPORT = True
except ImportError:
    PDF_SUPPORT = False



class DataIngestionError(Exception):
    """Custom exception for ingestion-related errors."""
    pass


def load_input(file_path: str) -> dict:
    """
    Load blood report data from JSON or CSV.

    Args:
        file_path (str): Path to input file

    Returns:
        dict: Raw parameter data {parameter_name: raw_value}

    Raises:
        DataIngestionError: If file cannot be loaded or parsed
    """
    
    path = Path(file_path)

    if not path.exists():
        raise DataIngestionError(f"File not found: {file_path}")

    if path.suffix.lower() == ".json":
        return _load_json(path)

    elif path.suffix.lower() == ".csv":
        return _load_csv(path)
    
    elif path.suffix.lower() == ".pdf":
        if not PDF_SUPPORT:
            raise DataIngestionError("PDF support not available. OCR module not found.")
        raw_text = extract_text_from_pdf(str(path))
        
        # Parse the OCR text to extract structured parameters
        parameters = parse_pdf_text(raw_text)
        
        print(f"\n{'='*70}")
        print("DEBUG: Raw parameters from PDF parser:")
        for param, val in parameters.items():
            print(f"  {param}: '{val}'")
        print(f"{'='*70}\n")
        
        # Also extract patient info
        patient_info = extract_patient_info(raw_text)
        
        # Return both parameters and metadata
        result = parameters.copy() if parameters else {}
        result['_metadata'] = {
            'raw_text': raw_text,
            'patient_info': patient_info,
            'source_type': 'pdf'
        }
        
        return result

    else:
        raise DataIngestionError(
            f"Unsupported file format: {path.suffix}. Use JSON, CSV, or PDF."
        )


def _load_json(path: Path) -> dict:
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise DataIngestionError("JSON root must be an object")

        return data

    except json.JSONDecodeError as e:
        raise DataIngestionError(f"Invalid JSON format: {e}")


def _load_csv(path: Path) -> dict:
    """
    Expected CSV format:
    Parameter,Value
    Hemoglobin,13.2 g/dL
    """
    data = {}

    try:
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)

            if "Parameter" not in reader.fieldnames or "Value" not in reader.fieldnames:
                raise DataIngestionError(
                    "CSV must contain 'Parameter' and 'Value' columns"
                )

            for row in reader:
                parameter = row["Parameter"].strip()
                value = row["Value"].strip()

                if parameter:
                    data[parameter] = value

        return data

    except Exception as e:
        raise DataIngestionError(f"Error reading CSV file: {e}")
