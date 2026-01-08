import json

def extract_from_json(json_file):
    data = json.load(json_file)
    return data
