"""Aggregate matched patterns into graded risks with severity and confidence.

This module takes mined/matched patterns and combines them per domain/tag to
produce a numeric severity score and an overall confidence.
"""
from typing import List, Dict, Any
import math


def aggregate_risks(matched_patterns: List[Dict[str, Any]], total_reports: int = 0) -> Dict[str, Any]:
    """Aggregate a list of matched pattern dicts into domain-level risks.

    Each pattern is expected to have: `params`, `count`, `tags`, and optionally `confidence`.

    Returns a mapping domain-> {risk_level, severity_score, confidence, matched_patterns, reason}
    """
    domain_counts = {}
    domain_patterns = {}
    total = total_reports or sum(p.get('count', 0) for p in matched_patterns) or 1

    # accumulate weighted evidence per domain
    for p in matched_patterns:
        cnt = p.get('count', 0)
        conf = p.get('confidence') if p.get('confidence') is not None else (cnt / float(total))
        tags = p.get('tags') or ['general']
        for t in tags:
            domain_counts.setdefault(t, 0.0)
            domain_counts[t] += conf
            domain_patterns.setdefault(t, []).append({**p, 'pattern_confidence': conf})

    # normalize and compute scores
    domains_out = {}
    if domain_counts:
        max_evidence = max(domain_counts.values())
    else:
        max_evidence = 1.0

    for dom, evidence in domain_counts.items():
        # severity_score: scaled 0-1 proportional to evidence relative to max
        severity_score = min(1.0, evidence / max_evidence if max_evidence > 0 else 0.0)

        # confidence: combine pattern confidences using noisy-or
        pats = domain_patterns.get(dom, [])
        prod = 1.0
        for pp in pats:
            pc = pp.get('pattern_confidence', 0.0)
            prod *= (1.0 - min(0.99, max(0.0, pc)))
        confidence = 1.0 - prod

        # map severity_score to qualitative risk level
        if severity_score >= 0.75:
            risk_level = 'high'
        elif severity_score >= 0.4:
            risk_level = 'moderate'
        elif severity_score > 0:
            risk_level = 'low'
        else:
            risk_level = 'normal'

        # build reason string
        top_patterns = sorted(pats, key=lambda x: -x.get('pattern_confidence', 0.0))[:3]
        reasons = []
        for tp in top_patterns:
            reasons.append(f"Pattern [{', '.join(tp.get('params',[]))}] (conf={tp.get('pattern_confidence'):.2f})")

        domains_out[dom] = {
            'risk_level': risk_level,
            'severity_score': round(float(severity_score), 3),
            'confidence': round(float(confidence), 3),
            # return simplified matched patterns for frontend consumption
            'matched_patterns': [
                {
                    'params': pp.get('params'),
                    'count': pp.get('count'),
                    'pattern_confidence': round(float(pp.get('pattern_confidence', 0.0)), 3)
                }
                for pp in pats
            ],
            # provide list of reason strings
            'reasons': reasons or ['No strong matched patterns.']
        }

    return domains_out


if __name__ == '__main__':
    # small smoke test
    sample = [
        {"params": ["ldl:high", "hdl:low"], "count": 50, "tags": ["cardiac"]},
        {"params": ["glucose_fasting:high"], "count": 30, "tags": ["diabetes"]},
        {"params": ["ldl:high"], "count": 20, "tags": ["cardiac"]},
    ]
    # compute confidences
    total = 200
    for s in sample:
        s['confidence'] = float(s['count']) / float(total)
    print(aggregate_risks(sample, total_reports=total))
