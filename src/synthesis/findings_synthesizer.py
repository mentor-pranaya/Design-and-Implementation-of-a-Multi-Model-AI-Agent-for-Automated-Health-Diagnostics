from typing import List, Dict, Any

def synthesize_findings(
    extracted_parameters: Dict[str, Any],
    interpretations: List[str],
    risks: List[str],
    recommendations: List[str],
    derived_metrics: Dict[str, Any] = {},
    context_adjustments: List[str] = []
) -> str:
    """
    Synthesize all analysis results into a coherent natural language summary.
    """
    summary_parts = []

    # 1. Overview
    param_count = len(extracted_parameters)
    summary_parts.append(f"Analysis of {param_count} clinical parameters completed.")

    # 2. Key Findings (interpretations)
    if interpretations:
        # Filter for non-normal if possible, but for now use all
        # Ideally, we prioritize "High", "Low", "Critical"
        significant_findings = [i for i in interpretations if "normal" not in i.lower()]
        if significant_findings:
             summary_parts.append(f"Key abnormal findings include: {'; '.join(significant_findings[:5])}.")
        else:
             summary_parts.append("All analyzed parameters appear within normal reference ranges.")

    # 3. Derived Metrics & Risks (Model 2)
    if risks:
        summary_parts.append(f"Risk assessment identified the following concerns: {'; '.join(risks)}.")
    
    if derived_metrics:
        # Mention specific high-value metrics if they are associated with risks
        # For now, just a general statement
        pass

    # 4. Context (Model 3)
    if context_adjustments:
        summary_parts.append(f"Contextual notes: {' '.join(context_adjustments)}")

    # 5. Conclusion
    if risks or [i for i in interpretations if "high" in i.lower() or "low" in i.lower()]:
        summary_parts.append("Medical consultation is recommended to address these findings.")
    else:
        summary_parts.append("Health status appears stable based on provided data.")

    return " ".join(summary_parts)
