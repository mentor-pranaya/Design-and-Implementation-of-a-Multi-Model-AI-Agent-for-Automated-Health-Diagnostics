def provide_precautions(params: dict) -> list[str]:
    precautions = []
    if 'glucose' in params:
        if params['glucose'] > 140:
            precautions.append("Monitor blood sugar levels and consult a doctor for diabetes management.")
        elif params['glucose'] < 70:
            precautions.append("Check for hypoglycemia; eat balanced meals.")
    if 'cholesterol' in params and params['cholesterol'] > 200:
        precautions.append("Reduce saturated fats in diet and exercise regularly.")
    # Add more rules
    return precautions