def interpret_parameters(standardized_data):
    for item in standardized_data:
        try:
            low, high = map(float, item['range'].replace(' ', '').split('-'))
            val = item['value']
            
            if val < low:
                item['status'] = "Low"
            elif val > high:
                item['status'] = "High"
            else:
                item['status'] = "Normal"
        except:
            item['status'] = "Unknown Range"
    return standardized_data
