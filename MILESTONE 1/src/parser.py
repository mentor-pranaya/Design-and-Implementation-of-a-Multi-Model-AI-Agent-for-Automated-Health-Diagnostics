import json
import fitz  # PyMuPDF

def parse_input(uploaded_file):
    file_type = uploaded_file.type
    
    if file_type == "application/json":
        return json.load(uploaded_file), "json"
    
    elif file_type == "application/pdf":
        doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        return text, "text"
    
    else: # Images
        return uploaded_file.read(), "image"
      
