import os

from src.input_parser.json_reader import read_json
from src.input_parser.pdf_reader import read_pdf
from src.input_parser.image_reader import read_image

def read_input(filepath):
    extension = os.path.splitext(filepath)[1].lower()
    if extension == ".json":
        return read_json(filepath)
    elif extension == ".pdf":
        return read_pdf(filepath)
    elif extension in [".jpg", ".jpeg", ".png"]:
        return read_image(filepath)
    else:
        raise ValueError(f"Unsupported file format: {extension}")