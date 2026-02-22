"""
Report Generator (Milestone 3)
Formats the synthesized findings and personalized recommendations into a clear,
professional, user-friendly report for the end user.
"""

import json
from datetime import datetime


def generate_report(synthesis_findings, recommendations, parameters, interpretation, 
                   risk_assessment, contextual_risk, age=None, gender=None, 
                   filename=None, output_format="text"):
    """
    Generate a comprehensive, formatted report combining all findings and recommendations.
    
    Args:
        synthesis_findings: dict - Output from synthesis_engine
        recommendations: dict - Output from recommendation_generator
        parameters: dict - Raw extracted blood parameters
        interpretation: dict - Model 1 output
        risk_assessment: dict - Model 2 output
        contextual_risk: dict - Model 3 output
        age: int - User age (optional)
        gender: str - User gender (optional)
        filename: str - Optional filename for saving report
        output_format: str - Format type: "text", "html", "json", or "markdown"
    
    Returns:
        str - Filename of the saved report (if filename provided) or the report content
    """
    
    report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    if output_format == "json":
        content = _generate_json_report(synthesis_findings, recommendations, parameters, 
                                     interpretation, risk_assessment, contextual_risk, 
                                     age, gender, report_date)
    
    elif output_format == "html":
        content = _generate_html_report(synthesis_findings, recommendations, parameters,
                                     interpretation, risk_assessment, contextual_risk,
                                     age, gender, report_date)
    
    elif output_format == "markdown":
        content = _generate_markdown_report(synthesis_findings, recommendations, parameters,
                                         interpretation, risk_assessment, contextual_risk,
                                         age, gender, report_date)
    
    else:  # Default to text format
        content = _generate_text_report(synthesis_findings, recommendations, parameters,
                                     interpretation, risk_assessment, contextual_risk,
                                     age, gender, report_date)
        
    if filename:
        save_report(content, filename, output_format)
        # Determine final extension used by save_report
        if output_format == "html" and not filename.endswith(".html"):
            filename = f"{filename}.html"
        elif output_format == "json" and not filename.endswith(".json"):
            filename = f"{filename}.json"
        elif output_format == "markdown" and not filename.endswith(".md"):
            filename = f"{filename}.md"
        elif not filename.endswith(".txt"):
            filename = f"{filename}.txt"
        return filename
        
    return content


def _generate_text_report(synthesis_findings, recommendations, parameters, interpretation,
                         risk_assessment, contextual_risk, age=None, gender=None, report_date=None):
    """Generate a plain text format report."""
    
    report = []
    report.append("=" * 80)
    report.append(" " * 20 + "HEALTH DIAGNOSTIC REPORT")
    report.append("=" * 80)
    report.append("")
    
    # Header Information
    report.append("REPORT INFORMATION")
    report.append("-" * 80)
    report.append(f"Generated: {report_date}")
    if age:
        report.append(f"Age: {age} years")
    if gender:
        report.append(f"Gender: {gender}")
    report.append("")
    
    # Executive Summary
    report.append("EXECUTIVE SUMMARY")
    report.append("-" * 80)
    report.append(synthesis_findings.get("summary", "No summary available"))
    report.append("")
    report.append(f"Overall Health Status: {synthesis_findings.get('overall_health_status', 'N/A')}")
    report.append("")
    
    # Key Findings
    report.append("KEY FINDINGS")
    report.append("-" * 80)
    
    if synthesis_findings.get("critical_findings"):
        report.append("CRITICAL FINDINGS:")
        for i, finding in enumerate(synthesis_findings["critical_findings"], 1):
            report.append(f"  {i}. {finding}")
        report.append("")
    
    # Abnormal Parameters
    report.append("ABNORMAL PARAMETERS:")
    if synthesis_findings.get("abnormal_parameters"):
        for param_info in synthesis_findings["abnormal_parameters"]:
            status = param_info.get("status", "")
            value = param_info.get("value", "N/A")
            ref_range = param_info.get("reference_range", "")
            report.append(f"  • {param_info['parameter']}: {value} ({status})")
            report.append(f"    Reference Range: {ref_range}")
        report.append("")
    else:
        report.append("  No abnormal parameters detected.")
        report.append("")
    
    # Normal Parameters Summary
    report.append(f"NORMAL PARAMETERS: {len(synthesis_findings.get('normal_parameters', []))} parameter(s)")
    report.append("")
    
    # Risk Assessment
    report.append("RISK ASSESSMENT")
    report.append("-" * 80)
    for risk_pattern in synthesis_findings.get("risk_patterns", []):
        category = risk_pattern.get("category", "Unknown")
        level = risk_pattern.get("level", "N/A")
        report.append(f"{category}: {level}")
        
        factors = risk_pattern.get("contributing_factors", [])
        if factors:
            report.append("  Contributing Factors:")
            for factor in factors:
                report.append(f"    - {factor}")
        
        significance = risk_pattern.get("clinical_significance", "")
        if significance:
            report.append(f"  Significance: {significance}")
        report.append("")
    
    # Contextual Insights
    if synthesis_findings.get("contextual_insights"):
        report.append("CONTEXTUAL INSIGHTS (Age/Gender-Adjusted)")
        report.append("-" * 80)
        for insight in synthesis_findings["contextual_insights"]:
            report.append(f"Risk Area: {insight.get('risk_area', 'N/A')}")
            report.append(f"  Adjustment Factor: {insight.get('adjustment_reason', 'N/A')}")
            report.append(f"  Original Level: {insight.get('original_level', 'N/A')}")
            report.append(f"  Adjusted Level: {insight.get('adjusted_level', 'N/A')}")
            report.append("")
    
    # Priority Areas
    report.append("PRIORITY AREAS FOR ATTENTION")
    report.append("-" * 80)
    for i, priority in enumerate(synthesis_findings.get("priority_areas", []), 1):
        report.append(f"{i}. {priority.get('area', 'N/A')} (Priority Level {priority.get('priority', 'N/A')})")
        report.append(f"   Risk Level: {priority.get('risk_level', 'N/A')}")
        report.append(f"   Action: {priority.get('action_needed', 'N/A')}")
        report.append("")
    
    # Recommendations Section
    report.append("PERSONALIZED RECOMMENDATIONS")
    report.append("=" * 80)
    report.append("")
    
    # Dietary Recommendations
    if recommendations.get("dietary_recommendations"):
        report.append("DIETARY RECOMMENDATIONS")
        report.append("-" * 80)
        for diet_rec in recommendations["dietary_recommendations"]:
            report.append(f"Category: {diet_rec.get('category', 'N/A')}")
            report.append(f"Finding: {diet_rec.get('finding', 'N/A')}")
            report.append(f"Priority: {diet_rec.get('priority', 'N/A')}")
            report.append("Recommendations:")
            for rec in diet_rec.get("recommendations", []):
                report.append(f"  • {rec}")
            
            report.append("Foods to Include:")
            for food in diet_rec.get("foods_to_include", []):
                report.append(f"  ✓ {food}")
            
            report.append("Foods to Avoid:")
            for food in diet_rec.get("foods_to_avoid", []):
                report.append(f"  ✗ {food}")
            report.append("")
    
    # Lifestyle Recommendations
    if recommendations.get("lifestyle_recommendations"):
        report.append("LIFESTYLE RECOMMENDATIONS")
        report.append("-" * 80)
        for lifestyle in recommendations["lifestyle_recommendations"]:
            report.append(f"Category: {lifestyle.get('category', 'N/A')}")
            report.append(f"Finding: {lifestyle.get('finding', 'N/A')}")
            report.append(f"Priority: {lifestyle.get('priority', 'N/A')}")
            report.append("Recommendations:")
            for rec in lifestyle.get("recommendations", []):
                report.append(f"  • {rec}")
            report.append("")
    
    # Medical Follow-up
    report.append("MEDICAL FOLLOW-UP")
    report.append("-" * 80)
    for followup in recommendations.get("medical_follow_up", []):
        report.append(f"Urgency: {followup.get('urgency', 'N/A')}")
        report.append(f"Recommendation: {followup.get('recommendation', 'N/A')}")
        
        specialists = followup.get("specialists_to_consider", [])
        if specialists:
            report.append("Specialists to Consider:")
            for specialist in specialists:
                report.append(f"  • {specialist}")
        
        tests = followup.get("tests_to_request", [])
        if tests:
            report.append("Recommended Tests:")
            for test in tests:
                report.append(f"  • {test}")
        report.append("")
    
    # Monitoring Schedule
    if recommendations.get("monitoring_schedule"):
        report.append("MONITORING SCHEDULE")
        report.append("-" * 80)
        for schedule in recommendations["monitoring_schedule"]:
            report.append(f"Frequency: {schedule.get('frequency', 'N/A')}")
            report.append(f"Focus Areas: {', '.join(schedule.get('focus_areas', []))}")
            report.append(f"Method: {schedule.get('method', 'N/A')}")
            report.append("")
    
    # Supplementation Advice
    if recommendations.get("supplementation_advice"):
        report.append("SUPPLEMENTATION ADVICE")
        report.append("-" * 80)
        for supplement in recommendations["supplementation_advice"]:
            report.append(f"Supplement: {supplement.get('supplement', 'N/A')}")
            report.append(f"Reason: {supplement.get('reason', 'N/A')}")
            report.append(f"Dosage: {supplement.get('dosage', 'N/A')}")
            report.append(f"Note: {supplement.get('note', 'N/A')}")
            report.append("")
    
    # Activity Recommendations
    if recommendations.get("activity_recommendations"):
        report.append("EXERCISE & PHYSICAL ACTIVITY PLAN")
        report.append("-" * 80)
        for activity in recommendations["activity_recommendations"]:
            report.append(f"Category: {activity.get('category', 'N/A')}")
            plan = activity.get("plan", {})
            report.append(f"Weekly Goal: {plan.get('weekly_goal_minutes', 'N/A')} minutes")
            report.append(f"Intensity: {plan.get('intensity', 'N/A')}")
            report.append(f"Frequency: {plan.get('frequency', 'N/A')}")
            report.append("Recommended Activities:")
            for act in plan.get("activities", []):
                report.append(f"  • {act}")
            
            precautions = plan.get("precautions", [])
            if precautions:
                report.append("Precautions:")
                for precaution in precautions:
                    report.append(f"  ⚠ {precaution}")
            report.append("")
    
    # Risk Reduction Strategies
    if recommendations.get("risk_reduction_strategies"):
        report.append("RISK REDUCTION STRATEGIES")
        report.append("-" * 80)
        for strategy in recommendations["risk_reduction_strategies"]:
            report.append(f"Risk Area: {strategy.get('risk_area', 'N/A')}")
            report.append("Strategies:")
            for strat in strategy.get("strategies", []):
                report.append(f"  • {strat}")
            report.append(f"Timeline: {strategy.get('timeline', 'N/A')}")
            report.append("")
    
    # Disclaimers
    report.append("=" * 80)
    report.append("IMPORTANT MEDICAL DISCLAIMER")
    report.append("=" * 80)
    if recommendations.get("disclaimers"):
        for disclaimer in recommendations["disclaimers"]:
            content = disclaimer.get("content", [])
            for line in content:
                report.append(line)
            report.append("")
    
    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)
    
    return "\n".join(report)


def _generate_markdown_report(synthesis_findings, recommendations, parameters, interpretation,
                             risk_assessment, contextual_risk, age=None, gender=None, report_date=None):
    """Generate a Markdown format report."""
    
    report = []
    report.append("# HEALTH DIAGNOSTIC REPORT")
    report.append("")
    report.append(f"**Generated:** {report_date}")
    if age:
        report.append(f"**Age:** {age} years")
    if gender:
        report.append(f"**Gender:** {gender}")
    report.append("")
    
    # Executive Summary
    report.append("## Executive Summary")
    report.append(synthesis_findings.get("summary", "No summary available"))
    report.append("")
    report.append(f"**Overall Health Status:** {synthesis_findings.get('overall_health_status', 'N/A')}")
    report.append("")
    
    # Key Findings
    report.append("## Key Findings")
    
    if synthesis_findings.get("critical_findings"):
        report.append("### Critical Findings")
        for finding in synthesis_findings["critical_findings"]:
            report.append(f"- {finding}")
        report.append("")
    
    if synthesis_findings.get("abnormal_parameters"):
        report.append("### Abnormal Parameters")
        for param_info in synthesis_findings["abnormal_parameters"]:
            report.append(f"- **{param_info['parameter']}**: {param_info.get('value', 'N/A')} ({param_info.get('status', '')})")
            report.append(f"  - Reference Range: {param_info.get('reference_range', '')}")
        report.append("")
    
    # Risk Assessment
    report.append("## Risk Assessment")
    for risk_pattern in synthesis_findings.get("risk_patterns", []):
        category = risk_pattern.get("category", "Unknown")
        level = risk_pattern.get("level", "N/A")
        report.append(f"### {category}: **{level}**")
        
        factors = risk_pattern.get("contributing_factors", [])
        if factors:
            report.append("**Contributing Factors:**")
            for factor in factors:
                report.append(f"- {factor}")
        report.append("")
    
    # Recommendations
    report.append("## Recommendations")
    
    if recommendations.get("dietary_recommendations"):
        report.append("### Dietary Recommendations")
        for diet_rec in recommendations["dietary_recommendations"]:
            report.append(f"#### {diet_rec.get('category', 'N/A')}")
            report.append(f"**Priority:** {diet_rec.get('priority', 'N/A')}")
            report.append("**Recommendations:**")
            for rec in diet_rec.get("recommendations", []):
                report.append(f"- {rec}")
            report.append("")
    
    if recommendations.get("lifestyle_recommendations"):
        report.append("### Lifestyle Recommendations")
        for lifestyle in recommendations["lifestyle_recommendations"]:
            report.append(f"#### {lifestyle.get('category', 'N/A')}")
            for rec in lifestyle.get("recommendations", []):
                report.append(f"- {rec}")
            report.append("")
    
    if recommendations.get("medical_follow_up"):
        report.append("### Medical Follow-up")
        for followup in recommendations["medical_follow_up"]:
            report.append(f"**Urgency:** {followup.get('urgency', 'N/A')}")
            report.append(f"{followup.get('recommendation', 'N/A')}")
            report.append("")
    
    # Disclaimers
    report.append("## ⚠️ Important Medical Disclaimer")
    if recommendations.get("disclaimers"):
        for disclaimer in recommendations["disclaimers"]:
            for line in disclaimer.get("content", []):
                report.append(f"- {line}")
    report.append("")
    
    return "\n".join(report)


def _generate_html_report(synthesis_findings, recommendations, parameters, interpretation,
                         risk_assessment, contextual_risk, age=None, gender=None, report_date=None):
    """Generate an HTML format report."""
    
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html lang='en'>")
    html.append("<head>")
    html.append("    <meta charset='UTF-8'>")
    html.append("    <meta name='viewport' content='width=device-width, initial-scale=1.0'>")
    html.append("    <title>Health Diagnostic Report</title>")
    html.append("    <style>")
    html.append("        body { font-family: Arial, sans-serif; margin: 20px; line-height: 1.6; }")
    html.append("        .header { background-color: #2c3e50; color: white; padding: 20px; border-radius: 5px; }")
    html.append("        h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }")
    html.append("        h2 { color: #34495e; margin-top: 30px; }")
    html.append("        .status-healthy { color: #27ae60; font-weight: bold; }")
    html.append("        .status-warning { color: #f39c12; font-weight: bold; }")
    html.append("        .status-critical { color: #e74c3c; font-weight: bold; }")
    html.append("        .finding { background-color: #ecf0f1; padding: 10px; margin: 10px 0; border-left: 4px solid #3498db; }")
    html.append("        .critical-finding { border-left-color: #e74c3c; }")
    html.append("        .recommendation { background-color: #e8f8f5; padding: 15px; margin: 10px 0; border-radius: 5px; }")
    html.append("        .disclaimer { background-color: #fff3cd; padding: 15px; margin: 20px 0; border-radius: 5px; border-left: 4px solid #ff9800; }")
    html.append("        table { width: 100%; border-collapse: collapse; margin: 15px 0; }")
    html.append("        th, td { border: 1px solid #ddd; padding: 12px; text-align: left; }")
    html.append("        th { background-color: #3498db; color: white; }")
    html.append("        tr:nth-child(even) { background-color: #f2f2f2; }")
    html.append("    </style>")
    html.append("</head>")
    html.append("<body>")
    
    # Header
    html.append("<div class='header'>")
    html.append("    <h1>Health Diagnostic Report</h1>")
    html.append(f"    <p>Generated: {report_date}</p>")
    if age or gender:
        demo_info = []
        if age:
            demo_info.append(f"Age: {age} years")
        if gender:
            demo_info.append(f"Gender: {gender}")
        html.append(f"    <p>{' | '.join(demo_info)}</p>")
    html.append("</div>")
    
    # Executive Summary
    html.append("<h2>Executive Summary</h2>")
    html.append(f"<p>{synthesis_findings.get('summary', 'No summary available')}</p>")
    
    status = synthesis_findings.get('overall_health_status', 'N/A')
    if 'Healthy' in status:
        html.append(f"<p class='status-healthy'>Status: {status}</p>")
    elif 'CONCERNING' in status:
        html.append(f"<p class='status-critical'>Status: {status}</p>")
    else:
        html.append(f"<p class='status-warning'>Status: {status}</p>")
    
    # Key Findings
    html.append("<h2>Key Findings</h2>")
    
    if synthesis_findings.get("critical_findings"):
        html.append("<h3>Critical Findings</h3>")
        for finding in synthesis_findings["critical_findings"]:
            html.append(f"<div class='finding critical-finding'>{finding}</div>")
    
    if synthesis_findings.get("abnormal_parameters"):
        html.append("<h3>Abnormal Parameters</h3>")
        html.append("<table>")
        html.append("<tr><th>Parameter</th><th>Value</th><th>Status</th><th>Reference Range</th></tr>")
        for param_info in synthesis_findings["abnormal_parameters"]:
            html.append(f"<tr>")
            html.append(f"<td>{param_info['parameter']}</td>")
            html.append(f"<td>{param_info.get('value', 'N/A')}</td>")
            html.append(f"<td>{param_info.get('status', '')}</td>")
            html.append(f"<td>{param_info.get('reference_range', '')}</td>")
            html.append(f"</tr>")
        html.append("</table>")
    
    # Recommendations
    html.append("<h2>Personalized Recommendations</h2>")
    
    if recommendations.get("dietary_recommendations"):
        html.append("<h3>Dietary Recommendations</h3>")
        for diet_rec in recommendations["dietary_recommendations"]:
            html.append(f"<div class='recommendation'>")
            html.append(f"<h4>{diet_rec.get('category', 'N/A')}</h4>")
            html.append(f"<p><strong>Priority:</strong> {diet_rec.get('priority', 'N/A')}</p>")
            html.append("<ul>")
            for rec in diet_rec.get("recommendations", []):
                html.append(f"<li>{rec}</li>")
            html.append("</ul>")
            html.append("</div>")
    
    # Disclaimer
    html.append("<div class='disclaimer'>")
    html.append("<h3>⚠️ Important Medical Disclaimer</h3>")
    if recommendations.get("disclaimers"):
        html.append("<ul>")
        for disclaimer in recommendations["disclaimers"]:
            for line in disclaimer.get("content", []):
                html.append(f"<li>{line}</li>")
        html.append("</ul>")
    html.append("</div>")
    
    html.append("</body>")
    html.append("</html>")
    
    return "\n".join(html)


def _generate_json_report(synthesis_findings, recommendations, parameters, interpretation,
                         risk_assessment, contextual_risk, age=None, gender=None, report_date=None):
    """Generate a JSON format report."""
    
    report_data = {
        "metadata": {
            "generated_date": report_date,
            "age": age,
            "gender": gender,
            "report_format": "JSON"
        },
        "synthesis": synthesis_findings,
        "recommendations": recommendations,
        "raw_data": {
            "parameters": parameters,
            "interpretation": interpretation,
            "risk_assessment": risk_assessment,
            "contextual_risk": contextual_risk
        }
    }
    
    return json.dumps(report_data, indent=2)


def save_report(report_content, filename, format_type="text"):
    """
    Save report to file.
    
    Args:
        report_content: str - The report content to save
        filename: str - Output filename
        format_type: str - File format extension
    
    Returns:
        bool - Success status
    """
    try:
        # Add appropriate extension if not present
        if format_type == "html" and not filename.endswith(".html"):
            filename = f"{filename}.html"
        elif format_type == "json" and not filename.endswith(".json"):
            filename = f"{filename}.json"
        elif format_type == "markdown" and not filename.endswith(".md"):
            filename = f"{filename}.md"
        elif not filename.endswith(".txt"):
            filename = f"{filename}.txt"
        
        with open(filename, "w", encoding="utf-8") as f:
            f.write(report_content)
        
        return True
    except Exception as e:
        print(f"Error saving report: {str(e)}")
        return False
