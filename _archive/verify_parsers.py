import asyncio
import io
import os
from fastapi import UploadFile
from src.input_parser.pdf_parser import extract_text_from_pdf
from src.input_parser.json_parser import parse_json
from src.input_parser.image_parser import extract_text_from_image
from src.extraction.parameter_extractor import extract_parameters_from_text, extract_parameters_from_json

# Mock UploadFile
class MockUploadFile:
    def __init__(self, filename, content):
        self.filename = filename
        self.file = io.BytesIO(content)
    
    async def read(self):
        self.file.seek(0)
        return self.file.read()
    
    async def seek(self, offset):
        self.file.seek(offset)

async def main():
    base_path = r"c:\Users\rakes\Downloads\blood report ai\test_samples"
    
    # 1. Test JSON Parser
    print("\n--- Testing JSON Parser ---")
    json_path = os.path.join(base_path, "normal.json")
    if os.path.exists(json_path):
        with open(json_path, "rb") as f:
            content = f.read()
        
        mock_file = MockUploadFile("normal.json", content)
        # Using the async parser
        try:
            data = await parse_json(mock_file)
            print("Parsed JSON Data:", data)
            extracted = extract_parameters_from_json(data)
            print("Extracted Parameters:", extracted)
        except Exception as e:
            print(f"JSON Parsing failed: {e}")
    else:
        print(f"File not found: {json_path}")

    # 2. Test PDF Parser
    print("\n--- Testing PDF Parser ---")
    pdf_path = os.path.join(base_path, "standard_report.pdf")
    if os.path.exists(pdf_path):
        with open(pdf_path, "rb") as f:
            content = f.read()
        
        mock_file = MockUploadFile("standard_report.pdf", content)
        # The existing pdf parser uses synchronous read on .file
        try:
            text = extract_text_from_pdf(mock_file)
            print(f"Parsed PDF Text (first 100 chars): {text[:100]}...")
            extracted = extract_parameters_from_text(text)
            print("Extracted Parameters:", extracted)
        except Exception as e:
            print(f"PDF Parsing failed: {e}")
            import traceback
            traceback.print_exc()
    else:
        print(f"File not found: {pdf_path}")

    # 3. Test Image Parser
    print("\n--- Testing Image Parser ---")
    img_path = os.path.join(base_path, "critical_image.png")
    if os.path.exists(img_path):
        with open(img_path, "rb") as f:
            content = f.read()
        
        mock_file = MockUploadFile("critical_image.png", content)
        try:
            # The existing image parser also uses .file.read()
            text = extract_text_from_image(mock_file)
            print(f"Parsed Image Text (first 100 chars): {text[:100]}...")
            extracted = extract_parameters_from_text(text)
            print("Extracted Parameters:", extracted)
        except Exception as e:
            print(f"Image Parsing failed: {e}")
    else:
        print(f"File not found: {img_path}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except ImportError:
         # simple fallback if asyncio.run not available (unlikely in python 3.7+)
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        loop.run_until_complete(main())
