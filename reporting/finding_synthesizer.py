from typing import Any, Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


def _safe_lower(value: Any) -> str:
    if value is None:
        return ""
    return str(value).lower().strip()


def _convert_abnormalities_to_findings(abnormalities: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Convert abnormality dicts to findings."""
    findings = []
    for abnorm in abnormalities:
        test_name = abnorm.get('test_name', abnorm.get('parameter', 'unknown'))
        value = abnorm.get('value', 'N/A')
        unit = abnorm.get('unit', '')
        risk = abnorm.get('risk_level', 'unknown')
        description = abnorm.get('description', '')
        
        finding_text = f"{test_name}: {value} {unit} ({risk})"
        if description:
            finding_text += f" - {description}"
        
        findings.append({
            'description': finding_text,
            'test_name': test_name,
            'value': value,
            'unit': unit,
            'risk_level': risk,
        })
    return findings


def synthesize_findings(
    model1_output: Optional[Dict[str, Any]],
    model3_output: Optional[Dict[str, Any]],
) -> Dict[str, Any]:
    """
    Extract abnormalities and elevated risks into a compact structure.
    
    Enhanced to integrate reference range abnormalities from the extraction phase.
    Falls back to model outputs if no direct abnormalities provided.
    """
    key_abnormalities: List[Dict[str, Any]] = []

    # Try to get abnormalities from model1 output (which may now include reference range abnormalities)
    if isinstance(model1_output, dict):
        # First try to get reference range abnormalities
        ref_abnormalities = model1_output.get("key_abnormalities", [])
        if ref_abnormalities and isinstance(ref_abnormalities, list):
            key_abnormalities = ref_abnormalities.copy()
            logger.info(f"Found {len(key_abnormalities)} abnormalities from reference ranges")
        
        # If no abnormalities from reference ranges, try traditional model1 output
        if not key_abnormalities:
            for param, details in model1_output.items():
                if not isinstance(details, dict):
                    continue
                status = _safe_lower(details.get("status"))
                if not status or status == "normal":
                    continue

                item: Dict[str, Any] = {
                    "parameter": param,
                    "status": details.get("status"),
                }
                for field in ("value", "unit", "reference_range", "explanation"):
                    value = details.get(field)
                    if value not in (None, ""):
                        item[field] = value
                key_abnormalities.append(item)

    adjusted_risks: Dict[str, Any] = {}
    if isinstance(model3_output, dict):
        adjusted_risks = model3_output.get("adjusted_risks") or {}

    risk_summary: List[Dict[str, Any]] = []
    for domain, risk in adjusted_risks.items():
        if not isinstance(risk, dict):
            continue
        risk_level = _safe_lower(risk.get("risk_level"))
        # Include all risk levels, not just high/moderate
        # (to provide comprehensive information)
        
        entry: Dict[str, Any] = {
            "domain": domain,
            "risk_level": risk.get("risk_level"),
        }
        if "severity_score" in risk:
            entry["severity_score"] = risk.get("severity_score")
        if "confidence" in risk:
            entry["confidence"] = risk.get("confidence")
        if risk.get("matched_patterns") is not None:
            entry["matched_patterns"] = risk.get("matched_patterns")
        risk_summary.append(entry)

    risk_weight = {"high": 2, "moderate": 1, "low": 0}

    def _risk_sort_key(item: Dict[str, Any]) -> tuple:
        level = _safe_lower(item.get("risk_level"))
        severity = item.get("severity_score")
        severity_value = severity if isinstance(severity, (int, float)) else 0.0
        return (risk_weight.get(level, 0), severity_value)

    risk_summary.sort(key=_risk_sort_key, reverse=True)

    # Create key findings from abnormalities
    key_findings = _convert_abnormalities_to_findings(key_abnormalities)

    parts: List[str] = []
    if risk_summary:
        top_domain = risk_summary[0].get("domain", "unknown")
        high_risks = [r for r in risk_summary if _safe_lower(r.get("risk_level")) == "high"]
        if high_risks:
            parts.append(
                f"High-risk signals in {len(high_risks)} domain(s), led by {top_domain}."
            )
        elif len(risk_summary) > 0:
            parts.append(
                f"Elevated risk signals in {len(risk_summary)} domain(s), led by {top_domain}."
            )
    
    if key_abnormalities:
        parts.append(f"{len(key_abnormalities)} abnormal parameter(s) detected.")
    
    if not parts:
        parts.append("No significant abnormalities or elevated risks detected.")

    overall_assessment = " ".join(parts)

    return {
        "key_findings": key_findings,
        "key_abnormalities": key_abnormalities,
        "risk_summary": risk_summary,
        "overall_assessment": overall_assessment,
    }
