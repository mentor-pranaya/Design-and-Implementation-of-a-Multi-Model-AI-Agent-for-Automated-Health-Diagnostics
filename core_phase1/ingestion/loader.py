import json
import csv
from pathlib import Path
from ocr.pdf_ocr import extract_text_from_pdf



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
    raw_text = extract_text_from_pdf(str(path))
    return {"RAW_OCR_TEXT": raw_text}


    else:
        raise DataIngestionError(
            f"Unsupported file format: {path.suffix}. Use JSON or CSV."
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
