# input_handlers/json_handler.py

import json
import os

def extract_text_from_json(json_path):
    if not os.path.exists(json_path):
        return ""

    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        return json.dumps(data)

    except Exception:
        return ""
