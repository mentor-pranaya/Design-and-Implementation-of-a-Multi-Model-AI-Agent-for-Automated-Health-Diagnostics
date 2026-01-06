import re

def extract_parameter(text, param_name, keywords):
    lines = text.split('\n')
    
    for i in range(len(lines)):
        line = lines[i].strip()

    
        
        if any(keyword.lower() in line.lower() for keyword in keywords):

            #Step 2 choose lines (same+next)
            candidate_lines = [line]
            if i + 1 <len(lines):
                candidate_lines.append(lines[i+1].strip())
            # step 3 search for candiditae lines
            for candidate in candidate_lines:
                numbers = re.findall(r"\d+\.\d+", candidate) # to find the all the decimal nos.
                range_match = re.search(r"\d+\.\d+\s*-\s*\d+\.\d+",candidate) # to find the refrence range
                if numbers:
                    value = float(numbers[0])
                    referencr_range = (
                        range_match.group() if range_match else None
                    )
                    
                    unit = None
                    for part in candidate.split():
                        if "/" in part:
                            unit = part
                            break
                    return {
                        param_name : {
                            "value": value,
                            "unit" : unit,
                            "reference_range": referencr_range
                        }
                    }
                    
    return {}
