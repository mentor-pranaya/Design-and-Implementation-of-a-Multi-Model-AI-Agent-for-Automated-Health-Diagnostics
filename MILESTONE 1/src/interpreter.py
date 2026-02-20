import re

def interpret_parameters(standardized_data):
    """
    Compares test values against reference ranges to determine health status.
    Normalizes different dash characters and handles malformed data.
    """
    for item in standardized_data:
        # Extract range and value safely
        range_str = item.get('range', '')
        val = item.get('value')

        # 1. Handle Missing Data
        if val is None or not range_str or range_str == "N/A":
            item['status'] = "Unknown Range"
            continue

        try:
            # 2. Normalize Range String
            # Replaces en-dash (–) and em-dash (—) commonly found in OCR with standard hyphen (-)
            clean_range = range_str.replace('–', '-').replace('—', '-').strip()
            
            # 3. Handle standard "Low - High" ranges
            if '-' in clean_range:
                parts = [p.strip() for p in clean_range.split('-')]
                if len(parts) == 2:
                    low = float(parts[0])
                    high = float(parts[1])
                    
                    if val < low:
                        item['status'] = "Low"
                    elif val > high:
                        item['status'] = "High"
                    else:
                        item['status'] = "Normal"
                else:
                    item['status'] = "Format Error"
            
            # 4. Handle "Less than" or "Greater than" ranges (e.g., < 30)
            elif '<' in clean_range:
                limit = float(clean_range.replace('<', '').strip())
                item['status'] = "Normal" if val < limit else "High"
            elif '>' in clean_range:
                limit = float(clean_range.replace('>', '').strip())
                item['status'] = "Normal" if val > limit else "Low"
            else:
                item['status'] = "Unknown Format"
                
        except (ValueError, IndexError, TypeError):
            # Handles cases where strings cannot be converted to floats
            item['status'] = "Interpretation Error"
            
    return standardized_data
