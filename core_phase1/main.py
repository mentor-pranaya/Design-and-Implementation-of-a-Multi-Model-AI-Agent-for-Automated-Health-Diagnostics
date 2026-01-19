# core_phase1/main.py

import sys
from ingestion.loader import load_input, DataIngestionError
from extraction.parser import extract_parameters
from validation.validator import validate_parameters
from interpretation.interpreter import interpret_parameters


def main():
    if len(sys.argv) != 2:
        print("Usage: python main.py <path_to_input_file>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        raw_data = load_input(input_file)
    except DataIngestionError as e:
        print(f"[ERROR] {e}")
        sys.exit(1)

    extracted_data = extract_parameters(raw_data)
    validated_data = validate_parameters(extracted_data)
    interpreted_data = interpret_parameters(validated_data)

    print("=== PHASE-1 INTERPRETATION RESULTS ===")
    for param, details in interpreted_data.items():
        print(f"{param}: {details}")


if __name__ == "__main__":
    main()
