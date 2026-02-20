from typing import Dict, Any, List


def analyze_patterns(model1_output: Dict[str, Any], patterns: List[Dict[str, Any]], total_reports: int) -> Dict[str, Any]:
    """Analyze historical patterns and produce domain-level risk summaries.

    - Uses only Model 1 `status` flags (ignores raw values/units).
    - Matches dataset patterns (each pattern has `params` set like 'ldl:high')
      and optional `tags` (domains such as 'cardiac', 'diabetes').
    - Aggregates matched pattern counts by tag/domain and computes
      relative frequencies and confidence.

    Returns a summary containing:
      - matched_patterns: list of matched pattern entries
      - domains: mapping domain -> {count, relative_freq, risk, confidence, matched_patterns}
      - matched_params: list of matched param:status
    """
    # Build observed tags like 'glucose_fasting:high'
    observed = set()
    for p, v in model1_output.items():
        if not isinstance(v, dict):
            continue
        status = v.get("status")
        if status and status not in ("normal", "invalid", "unknown", "unclassified"):
            observed.add(f"{p}:{status}")

    matched_patterns = []
    domain_counts: Dict[str, int] = {}
    matched_param_set = set()
    total_pattern_counts = sum(p.get("count", 0) for p in patterns) or 1

    for pat in patterns:
        pat_set = pat.get("_param_set") or set(pat.get("params", []))
        if pat_set and pat_set.issubset(observed):
            matched_patterns.append(pat)
            matched_param_set.update(pat_set)
            cnt = pat.get("count", 0)
            tags = pat.get("tags", []) or []
            if not tags:
                # place under generic domain if no tags provided
                domain_counts.setdefault("general", 0)
                domain_counts["general"] += cnt
            else:
                for t in tags:
                    domain_counts.setdefault(t, 0)
                    domain_counts[t] += cnt

    # Compute domain relative frequencies and assign risk category
    domains_summary: Dict[str, Any] = {}
    if total_reports and total_reports > 0:
        base_divisor = total_reports
    else:
        base_divisor = total_pattern_counts

    # Determine max domain freq for proportional risk assignment
    max_rel = 0.0
    domain_rel: Dict[str, float] = {}
    for dom, cnt in domain_counts.items():
        rel = cnt / float(base_divisor)
        domain_rel[dom] = rel
        if rel > max_rel:
            max_rel = rel

    # Assign risk levels proportionally to the strongest domain frequency
    for dom, rel in domain_rel.items():
        # confidence is dataset-driven: scaled relative frequency
        confidence = min(0.99, rel * 1.5)

        # Risk assignment is proportional to max_rel to avoid hardcoded medical cutoffs
        risk = "low"
        if max_rel > 0:
            frac = rel / max_rel
            if frac >= 0.75:
                risk = "high"
            elif frac >= 0.33:
                risk = "moderate"
            else:
                risk = "low"

        domains_summary[dom] = {
            "count": domain_counts.get(dom, 0),
            "relative_freq": rel,
            "risk": risk,
            "confidence": confidence,
            "matched_patterns": [p for p in matched_patterns if dom in (p.get("tags") or []) or (not p.get("tags"))]
        }

    return {
        "matched_patterns": matched_patterns,
        "matched_params": list(matched_param_set),
        "domains": domains_summary,
        "total_matched_count": sum(domain_counts.values())
    }
