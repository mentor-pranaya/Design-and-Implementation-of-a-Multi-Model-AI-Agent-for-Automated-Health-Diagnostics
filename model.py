def analyze_report(report_data):
    """
    report_data format:
    {
      "Glucose": {"value":145, "low":70, "high":99}
    }
    """

    analysis = {}

    for param, info in report_data.items():
        value = info["value"]
        low = info["low"]
        high = info["high"]

        if value < low:
            status = "Low"
        elif value > high:
            status = "High"
        else:
            status = "Normal"

        analysis[param] = {
            "value": value,
            "reference": f"{low} - {high}",
            "status": status
        }

    return analysis


def generate_summary(analysis):
    if not analysis:
        return "⚠️ No parameters were extracted from the uploaded report."

    problems = [
        f"{p} is {v['status']}"
        for p, v in analysis.items()
        if v["status"] != "Normal"
    ]

    if not problems:
        return "All parameters are within normal range."

    return " | ".join(problems)
