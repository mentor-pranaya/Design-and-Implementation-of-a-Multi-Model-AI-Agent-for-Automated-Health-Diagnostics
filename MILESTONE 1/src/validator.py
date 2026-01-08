def standardize_data(data):
    # Example: Standardize Glucose to mg/dL
    for item in data:
        if "Glucose" in item['parameter'] and item['unit'] == "mmol/L":
            item['value'] = round(item['value'] * 18.01, 2)
            item['unit'] = "mg/dL"
            item['range'] = "70 - 99"
    return data
  
