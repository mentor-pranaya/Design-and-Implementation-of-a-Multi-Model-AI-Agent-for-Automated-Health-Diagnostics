def compare_report_with_normals(report_data, normal_data):
    """
    Compares test values with normal ranges
    normal_data format:
    {
      "Glucose": [70, 99],
      "Hemoglobin": [13, 17]
    }
    """

    analysis = {}

    for param, value in report_data.items():
        if param not in normal_data:
            analysis[param] = {
                "value": value,
                "status": "No reference range"
            }
            continue

        low, high = normal_data[param]

        if value < low:
            status = "Low"
        elif value > high:
            status = "High"
        else:
            status = "Normal"

        analysis[param] = {
            "value": value,
            "normal_range": f"{low} - {high}",
            "status": status
        }

    return analysis


def generate_summary(analysis):
    issues = []

    for param, info in analysis.items():
        if info["status"] in ["High", "Low"]:
            issues.append(f"{param} is {info['status']}")

    if not issues:
        return "All parameters are within normal range."

    return " | ".join(issues)
