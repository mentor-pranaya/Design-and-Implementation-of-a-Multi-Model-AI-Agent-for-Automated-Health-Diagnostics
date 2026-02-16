
from datetime import datetime
import html
import json
import os

import fitz

try:
    from weasyprint import HTML, CSS
    WEASYPRINT_AVAILABLE = True
except Exception:
    WEASYPRINT_AVAILABLE = False


class ReportGenerator:
    """
    Generates formatted health diagnostic reports
    """
    
    def __init__(self, results):
        self.results = results
        self.report_id = datetime.now().strftime("%Y%m%d%H%M%S")
        self.generated_at = datetime.now()
        self.weasyprint_available = WEASYPRINT_AVAILABLE
    
    def generate_text_report(self):
        """
        Generate plain text report
        """
        lines = []
        
        # Header
        lines.append("=" * 70)
        lines.append("                    HEALTH DIAGNOSTIC REPORT")
        lines.append("=" * 70)
        lines.append(f"  Report ID: {self.report_id}")
        lines.append(f"  Generated: {self.generated_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
        # Patient Information
        lines.append("\n" + "-" * 70)
        lines.append("  PATIENT INFORMATION")
        lines.append("-" * 70)
        
        patient_info = self.results.get("patient_info", {})
        age = patient_info.get("age")
        gender = patient_info.get("gender")
        age_group = patient_info.get("age_group")
        
        lines.append(f"  Age      : {age if age else 'Not detected'} {'years' if age else ''}")
        lines.append(f"  Gender   : {gender.capitalize() if gender else 'Not detected'}")
        if age_group:
            lines.append(f"  Age Group: {age_group.capitalize()}")
        
        # Clinical Summary
        synthesis = self.results.get("synthesis", {})
        if synthesis:
            lines.append("\n" + "-" * 70)
            lines.append("  CLINICAL SUMMARY")
            lines.append("-" * 70)
            lines.append(f"  {synthesis.get('summary_text', 'No summary available')}")
        
        # Key Findings
        key_findings = synthesis.get("key_findings", []) if synthesis else []
        if key_findings:
            lines.append("\n" + "-" * 70)
            lines.append("  KEY FINDINGS")
            lines.append("-" * 70)
            for finding in key_findings:
                finding_type = finding.get("type", "info").upper()
                lines.append(f"  [{finding_type}] {finding.get('text', '')}")
        
        # Detailed Parameters
        parameters = self.results.get("parameters", {})
        if parameters:
            lines.append("\n" + "-" * 70)
            lines.append("  DETAILED PARAMETERS")
            lines.append("-" * 70)
            lines.append(f"  {'Parameter':<15} {'Value':<12} {'Range':<15} {'Status':<10}")
            lines.append("  " + "-" * 55)
            
            for param_name, param_data in parameters.items():
                if param_name in ["Age", "Gender"]:
                    continue
                
                if param_data:
                    value = param_data.get("value", "--")
                    unit = param_data.get("unit", "")
                    status = param_data.get("status", "UNKNOWN")
                    display_range = param_data.get("contextual_range") or param_data.get("reference_range", "--")
                    
                    value_str = f"{value} {unit}".strip() if value != "--" else "--"
                    lines.append(f"  {param_name:<15} {value_str:<12} {display_range:<15} {status:<10}")
        
        # Detected Patterns
        patterns = self.results.get("patterns", [])
        if patterns:
            lines.append("\n" + "-" * 70)
            lines.append("  DETECTED PATTERNS")
            lines.append("-" * 70)
            
            for i, pattern in enumerate(patterns, 1):
                lines.append(f"\n  Pattern {i}: {pattern.get('pattern', 'Unknown')}")
                lines.append(f"  Confidence: {pattern.get('confidence', 0)}%")
                lines.append(f"  Assessment: {pattern.get('description', '')}")
                lines.append("  Indicators:")
                for indicator in pattern.get("indicators", []):
                    lines.append(f"    - {indicator}")
        
        # Risk Assessment
        risk = self.results.get("risk_assessment", {})
        if risk:
            lines.append("\n" + "-" * 70)
            lines.append("  RISK ASSESSMENT")
            lines.append("-" * 70)
            lines.append(f"\n  Overall Risk Score: {risk.get('overall_score', 0)}/100")
            lines.append(f"  Risk Level: {risk.get('risk_level', 'UNKNOWN')}")
            
            lines.append("\n  Risk Breakdown:")
            for individual in risk.get("individual_risks", []):
                if individual.get("score", 0) > 0:
                    lines.append(f"    - {individual.get('category', '')}: {individual.get('score', 0)}/100")
                    for factor in individual.get("risk_factors", []):
                        lines.append(f"        {factor}")
        
        # Recommendations
        recommendations = self.results.get("recommendations", {})
        if recommendations:
            lines.append("\n" + "-" * 70)
            lines.append("  PERSONALIZED RECOMMENDATIONS")
            lines.append("-" * 70)
            lines.append(f"\n  Priority Level: {recommendations.get('overall_priority', 'MEDIUM')}")
            lines.append(f"  Summary: {recommendations.get('summary', '')}")
            
            for rec in recommendations.get("condition_recommendations", []):
                lines.append(f"\n  " + "=" * 60)
                lines.append(f"  CONDITION: {rec.get('linked_condition', '').upper()}")
                lines.append(f"  Timeline: {rec.get('timeline', 'As needed')}")
                lines.append("  " + "=" * 60)
                
                if rec.get("diet"):
                    lines.append("\n  DIETARY RECOMMENDATIONS:")
                    for i, item in enumerate(rec["diet"][:4], 1):
                        lines.append(f"    {i}. {item}")
                
                if rec.get("lifestyle"):
                    lines.append("\n  LIFESTYLE MODIFICATIONS:")
                    for i, item in enumerate(rec["lifestyle"][:4], 1):
                        lines.append(f"    {i}. {item}")
                
                if rec.get("followup"):
                    lines.append("\n  FOLLOW-UP ACTIONS:")
                    for i, item in enumerate(rec["followup"][:4], 1):
                        lines.append(f"    {i}. {item}")
                
                if rec.get("warnings"):
                    lines.append("\n  IMPORTANT WARNINGS:")
                    for i, item in enumerate(rec["warnings"], 1):
                        lines.append(f"    {i}. {item}")
        
        # Patient-Specific Notes
        age_advice = recommendations.get("age_specific_advice", {}) if recommendations else {}
        gender_advice = recommendations.get("gender_specific_advice", {}) if recommendations else {}
        
        if age_advice.get("notes") or gender_advice.get("notes"):
            lines.append("\n" + "-" * 70)
            lines.append("  PATIENT-SPECIFIC NOTES")
            lines.append("-" * 70)
            
            if age_advice.get("notes"):
                lines.append(f"\n  Age-Related Considerations:")
                lines.append(f"    {age_advice['notes']}")
            
            if age_advice.get("diet_modifier"):
                lines.append(f"    Dietary Note: {age_advice['diet_modifier']}")
            
            if gender_advice.get("notes"):
                lines.append(f"\n  Gender-Related Considerations:")
                lines.append(f"    {gender_advice['notes']}")
        
        # General Health Guidelines
        general = recommendations.get("general_advice", {}) if recommendations else {}
        if general:
            lines.append("\n" + "-" * 70)
            lines.append("  GENERAL HEALTH GUIDELINES")
            lines.append("-" * 70)
            lines.append(f"\n  1. Hydration: {general.get('hydration', 'Stay hydrated')}")
            lines.append(f"  2. Sleep: {general.get('sleep', 'Get adequate sleep')}")
            lines.append(f"  3. Exercise: {general.get('exercise', 'Exercise regularly')}")
            lines.append(f"  4. Stress Management: {general.get('stress', 'Manage stress')}")
            lines.append(f"  5. Regular Checkups: {general.get('checkups', 'Get regular health checkups')}")
        
        # Processing Information
        if self.results.get("processing_time_seconds"):
            lines.append("\n" + "-" * 70)
            lines.append("  PROCESSING INFORMATION")
            lines.append("-" * 70)
            lines.append(f"  Processing Time: {self.results['processing_time_seconds']:.2f} seconds")
            
            # Workflow status
            workflow = self.results.get("workflow_status", {})
            completed = sum(1 for v in workflow.values() if v == "completed")
            total = len(workflow)
            lines.append(f"  Workflow Status: {completed}/{total} steps completed")
        
        # Warnings/Errors
        warnings = self.results.get("warnings", [])
        if warnings:
            lines.append("\n" + "-" * 70)
            lines.append("  PROCESSING NOTES")
            lines.append("-" * 70)
            for warning in warnings:
                lines.append(f"  Note: {warning.get('message', '')}")
        
        # Disclaimer
        lines.append("\n" + "-" * 70)
        lines.append("  DISCLAIMER")
        lines.append("-" * 70)
        lines.append("""
  This report is generated by an AI-based health diagnostics system
  for informational purposes only. It is NOT a substitute for
  professional medical advice, diagnosis, or treatment.

  Always consult a qualified healthcare provider for:
    - Interpretation of these results
    - Medical advice and treatment decisions
    - Any health concerns or symptoms

  Do not disregard professional medical advice or delay seeking it
  based on information in this report.
""")
        
        lines.append("=" * 70)
        lines.append("                      END OF REPORT")
        lines.append("=" * 70)
        
        return "\n".join(lines)
    
    def generate_json_report(self):
        """
        Generate JSON report
        """
        return {
            "report_id": self.report_id,
            "generated_at": self.generated_at.isoformat(),
            "success": self.results.get("success", False),
            "processing_time_seconds": self.results.get("processing_time_seconds"),
            "patient_info": self.results.get("patient_info"),
            "summary": self.results.get("synthesis", {}).get("summary_text"),
            "key_findings": self.results.get("synthesis", {}).get("key_findings", []),
            "parameters": self._format_parameters_for_json(),
            "patterns": self.results.get("patterns", []),
            "risk_assessment": self.results.get("risk_assessment"),
            "recommendations": self.results.get("recommendations"),
            "warnings": self.results.get("warnings", []),
            "errors": self.results.get("errors", [])
        }

    def generate_pdf_report(self):
        """
        Generate PDF report as bytes
        """
        if WEASYPRINT_AVAILABLE:
            html_report, css_report = self._build_html_report()
            return HTML(string=html_report).write_pdf(stylesheets=[CSS(string=css_report)])

        return self._generate_plain_pdf()

    def _generate_plain_pdf(self):
        """Generate a plain PDF from the text report (fallback)."""
        text_report = self.generate_text_report()

        font_name = "courier"
        font_size = 10
        line_height = font_size * 1.2
        margin = 36

        def wrap_line_to_width(line, max_width):
            if not line:
                return [""]

            words = line.split(" ")
            wrapped = []
            current = ""

            for word in words:
                candidate = word if not current else f"{current} {word}"
                if fitz.get_text_length(candidate, fontname=font_name, fontsize=font_size) <= max_width:
                    current = candidate
                    continue

                if current:
                    wrapped.append(current)
                current = ""

                if fitz.get_text_length(word, fontname=font_name, fontsize=font_size) <= max_width:
                    current = word
                    continue

                # Split long words to avoid overflow
                chunk = ""
                for ch in word:
                    test_chunk = f"{chunk}{ch}"
                    if fitz.get_text_length(test_chunk, fontname=font_name, fontsize=font_size) <= max_width:
                        chunk = test_chunk
                    else:
                        if chunk:
                            wrapped.append(chunk)
                        chunk = ch
                current = chunk

            wrapped.append(current)
            return wrapped

        doc = fitz.open()
        page = doc.new_page()
        page_width = page.rect.width
        page_height = page.rect.height
        usable_width = page_width - (2 * margin)
        usable_height = page_height - (2 * margin)
        max_lines = int(usable_height // line_height)

        all_lines = []
        for raw_line in text_report.splitlines():
            all_lines.extend(wrap_line_to_width(raw_line, usable_width))

        line_index = 0
        total_lines = len(all_lines)

        while line_index < total_lines:
            if line_index > 0:
                page = doc.new_page()

            for i in range(max_lines):
                if line_index >= total_lines:
                    break
                y_pos = margin + (i * line_height)
                page.insert_text(
                    (margin, y_pos),
                    all_lines[line_index],
                    fontname=font_name,
                    fontsize=font_size,
                )
                line_index += 1

        return doc.tobytes()

    def _build_html_report(self):
        """Build a styled HTML report and CSS for PDF rendering."""
        def esc(value):
            return html.escape(str(value)) if value is not None else ""

        patient_info = self.results.get("patient_info", {})
        synthesis = self.results.get("synthesis", {})
        parameters = self.results.get("parameters", {})
        patterns = self.results.get("patterns", [])
        risk = self.results.get("risk_assessment", {})
        recommendations = self.results.get("recommendations", {})
        warnings = self.results.get("warnings", [])

        age = patient_info.get("age")
        gender = patient_info.get("gender")
        age_group = patient_info.get("age_group")

        summary_text = synthesis.get("summary_text", "No summary available")
        key_findings = synthesis.get("key_findings", [])

        overall_score = risk.get("overall_score", 0)
        risk_level = risk.get("risk_level", "UNKNOWN")

        def status_class(status):
            if not status:
                return "status-unknown"
            status = str(status).lower()
            if "normal" in status:
                return "status-normal"
            if "low" in status:
                return "status-low"
            if "high" in status:
                return "status-high"
            if "border" in status:
                return "status-borderline"
            return "status-unknown"

        def finding_class(finding_type):
            ftype = str(finding_type or "info").lower()
            if ftype == "critical":
                return "badge-critical"
            if ftype == "abnormal":
                return "badge-abnormal"
            if ftype == "borderline":
                return "badge-borderline"
            return "badge-info"

        param_cards = []
        for param_name, param_data in parameters.items():
            if param_name in ["Age", "Gender"]:
                continue
            if not param_data:
                continue
            value = param_data.get("value", "--")
            unit = param_data.get("unit", "")
            status = param_data.get("status", "UNKNOWN")
            value_str = f"{value} {unit}".strip() if value != "--" else "--"
            param_cards.append(
                "<div class='param-card'>"
                f"<div class='param-name'>{esc(param_name)}</div>"
                f"<div class='param-value'>{esc(value_str)}</div>"
                f"<span class='param-pill {status_class(status)}'>{esc(status)}</span>"
                "</div>"
            )

        key_finding_blocks = []
        for finding in key_findings:
            ftype = finding.get("type", "info")
            text = finding.get("text", "")
            key_finding_blocks.append(
                f"<div class='finding-row {finding_class(ftype)}'>"
                f"<span class='finding-tag'>{esc(ftype.upper())}</span>"
                f"<span class='finding-text'>{esc(text)}</span>"
                f"</div>"
            )

        pattern_blocks = []
        for pattern in patterns:
            indicators = pattern.get("indicators", [])
            indicator_list = "".join(f"<li>{esc(item)}</li>" for item in indicators)
            pattern_blocks.append(
                "<div class='card'>"
                f"<div class='card-title'>{esc(pattern.get('pattern', 'Unknown Pattern'))}</div>"
                f"<div class='muted'>Confidence: {esc(pattern.get('confidence', 0))}%</div>"
                f"<div class='paragraph'>{esc(pattern.get('description', ''))}</div>"
                f"<ul class='compact-list'>{indicator_list}</ul>"
                "</div>"
            )

        risk_breakdown = []
        for item in risk.get("individual_risks", []):
            if item.get("score", 0) <= 0:
                continue
            factors = item.get("risk_factors", [])
            factor_list = "".join(f"<li>{esc(f)}</li>" for f in factors)
            risk_breakdown.append(
                "<div class='card'>"
                f"<div class='card-title'>{esc(item.get('category', ''))} - {esc(item.get('score', 0))}/100</div>"
                f"<ul class='compact-list'>{factor_list}</ul>"
                "</div>"
            )

        condition_blocks = []
        for rec in recommendations.get("condition_recommendations", []):
            diet_list = "".join(f"<li>{esc(i)}</li>" for i in rec.get("diet", [])[:4])
            lifestyle_list = "".join(f"<li>{esc(i)}</li>" for i in rec.get("lifestyle", [])[:4])
            follow_list = "".join(f"<li>{esc(i)}</li>" for i in rec.get("followup", [])[:4])
            warn_list = "".join(f"<li>{esc(i)}</li>" for i in rec.get("warnings", []))

            condition_blocks.append(
                "<div class='card'>"
                f"<div class='card-title'>{esc(rec.get('linked_condition', '')).upper()}</div>"
                f"<div class='muted'>Timeline: {esc(rec.get('timeline', 'As needed'))}</div>"
                f"<div class='grid-2'>"
                f"<div><div class='section-label'>Dietary Recommendations</div><ul class='compact-list'>{diet_list}</ul></div>"
                f"<div><div class='section-label'>Lifestyle Modifications</div><ul class='compact-list'>{lifestyle_list}</ul></div>"
                f"</div>"
                f"<div class='grid-2'>"
                f"<div><div class='section-label'>Follow-up Actions</div><ul class='compact-list'>{follow_list}</ul></div>"
                f"<div><div class='section-label'>Important Warnings</div><ul class='compact-list'>{warn_list}</ul></div>"
                f"</div>"
                "</div>"
            )

        age_advice = recommendations.get("age_specific_advice", {})
        gender_advice = recommendations.get("gender_specific_advice", {})
        general = recommendations.get("general_advice", {})

        processing_time = self.results.get("processing_time_seconds")
        workflow = self.results.get("workflow_status", {})
        completed = sum(1 for v in workflow.values() if v == "completed")
        total = len(workflow)

        html_report = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <title>Health Diagnostic Report</title>
</head>
<body>
    <div class="header">
        <div class="header-title">HEALTH DIAGNOSTIC REPORT</div>
        <div class="header-subtitle">AI-Powered Blood Report Analysis</div>
        <div class="header-meta">Report ID: {esc(self.report_id)} | Generated: {esc(self.generated_at.strftime('%Y-%m-%d %H:%M:%S'))}</div>
    </div>

    <div class="section">
        <div class="section-title">Patient Information</div>
        <div class="card grid-3">
            <div>
                <div class="section-label">Age</div>
                <div class="metric">{esc(age) if age else 'Not detected'}</div>
            </div>
            <div>
                <div class="section-label">Gender</div>
                <div class="metric">{esc(gender.capitalize()) if gender else 'Not detected'}</div>
            </div>
            <div>
                <div class="section-label">Age Group</div>
                <div class="metric">{esc(age_group.capitalize()) if age_group else 'Not detected'}</div>
            </div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Clinical Summary</div>
        <div class="card paragraph">{esc(summary_text)}</div>
    </div>

    <div class="section">
        <div class="section-title">Parameter Overview</div>
        <div class="param-grid">{''.join(param_cards) if param_cards else '<div class="card muted">No parameters available.</div>'}</div>
    </div>

    <div class="section">
        <div class="section-title">Key Findings</div>
        <div class="finding-list">{''.join(key_finding_blocks) if key_finding_blocks else '<div class="card muted">No key findings available.</div>'}</div>
    </div>

    <div class="section">
        <div class="section-title">Detected Patterns</div>
        <div class="grid-2">{''.join(pattern_blocks) if pattern_blocks else '<div class="card muted">No patterns detected.</div>'}</div>
    </div>

    <div class="section">
        <div class="section-title">Risk Assessment</div>
        <div class="card">
            <div class="risk-grid">
                <div class="risk-score">{esc(overall_score)}</div>
                <div>
                    <div class="section-label">Overall Risk Score</div>
                    <div class="risk-level">{esc(risk_level)}</div>
                </div>
            </div>
        </div>
        <div class="grid-2">{''.join(risk_breakdown) if risk_breakdown else '<div class="card muted">No individual risks identified.</div>'}</div>
    </div>

    <div class="section">
        <div class="section-title">Personalized Recommendations</div>
        <div class="card">
            <div class="section-label">Priority Level</div>
            <div class="metric">{esc(recommendations.get('overall_priority', 'MEDIUM'))}</div>
            <div class="paragraph">{esc(recommendations.get('summary', ''))}</div>
        </div>
        {''.join(condition_blocks)}
    </div>

    <div class="section">
        <div class="section-title">Patient-Specific Notes</div>
        <div class="card">
            <div class="paragraph"><strong>Age-related:</strong> {esc(age_advice.get('notes', 'No specific notes'))}</div>
            <div class="paragraph"><strong>Dietary note:</strong> {esc(age_advice.get('diet_modifier', ''))}</div>
            <div class="paragraph"><strong>Gender-related:</strong> {esc(gender_advice.get('notes', 'No specific notes'))}</div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">General Health Guidelines</div>
        <div class="card">
            <div class="paragraph">1. Hydration: {esc(general.get('hydration', 'Stay hydrated'))}</div>
            <div class="paragraph">2. Sleep: {esc(general.get('sleep', 'Get adequate sleep'))}</div>
            <div class="paragraph">3. Exercise: {esc(general.get('exercise', 'Exercise regularly'))}</div>
            <div class="paragraph">4. Stress Management: {esc(general.get('stress', 'Manage stress'))}</div>
            <div class="paragraph">5. Regular Checkups: {esc(general.get('checkups', 'Get regular health checkups'))}</div>
        </div>
    </div>

    <div class="section">
        <div class="section-title">Processing Information</div>
        <div class="card">
            <div class="paragraph"><strong>Processing Time:</strong> {f"{processing_time:.2f}" if processing_time is not None else 'N/A'} seconds</div>
            <div class="paragraph"><strong>Workflow Status:</strong> {esc(completed)}/{esc(total)} steps completed</div>
        </div>
        {''.join([f"<div class='card warning'><strong>Note:</strong> {esc(w.get('message', ''))}</div>" for w in warnings])}
    </div>

    <div class="section">
        <div class="section-title">Disclaimer</div>
        <div class="card disclaimer">
            This report is generated by an AI-based health diagnostics system for informational purposes only.
            It is NOT a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified
            healthcare provider for interpretation of these results and any health concerns.
        </div>
    </div>
</body>
</html>
"""

        css_report = """
@page { size: A4; margin: 18mm; }
* { -webkit-print-color-adjust: exact; print-color-adjust: exact; }
body {
    font-family: "Segoe UI", Tahoma, Geneva, Verdana, sans-serif;
    color: #1E293B;
    background: #F8FAFC;
    font-size: 11px;
}
.header {
    text-align: center;
    padding: 18px 0 10px 0;
    border-bottom: 2px solid #E5E7EB;
}
.header-title {
    font-size: 20px;
    font-weight: 700;
    color: #1E293B;
}
.header-subtitle {
    font-size: 12px;
    color: #64748B;
}
.header-meta {
    margin-top: 6px;
    font-size: 10px;
    color: #94A3B8;
}
.section {
    margin-top: 16px;
}
.section-title {
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 8px;
    color: #1E293B;
}
.card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 12px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
    margin-bottom: 8px;
}
.card-title {
    font-size: 12px;
    font-weight: 700;
    margin-bottom: 4px;
}
.muted {
    color: #64748B;
}
.paragraph {
    margin-bottom: 6px;
}
.section-label {
    text-transform: uppercase;
    letter-spacing: 0.4px;
    color: #64748B;
    font-size: 9px;
    margin-bottom: 2px;
}
.metric {
    font-size: 14px;
    font-weight: 700;
}
.grid-2 {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 8px;
}
.grid-3 {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 8px;
}
.param-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 10px;
}
.param-card {
    background: #FFFFFF;
    border: 1px solid #E5E7EB;
    border-radius: 10px;
    padding: 12px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
}
.param-name {
    color: #64748B;
    font-size: 9px;
    text-transform: uppercase;
    letter-spacing: 0.3px;
    margin-bottom: 4px;
}
.param-value {
    font-size: 13px;
    font-weight: 700;
    margin-bottom: 6px;
}
.param-pill {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 999px;
    font-size: 9px;
    font-weight: 700;
}
.status-normal { background: #DCFCE7; color: #166534; }
.status-low { background: #FEE2E2; color: #991B1B; }
.status-high { background: #FEF3C7; color: #92400E; }
.status-borderline { background: #FEF9C3; color: #854D0E; }
.status-unknown { background: #F3F4F6; color: #6B7280; }
.finding-list {
    display: flex;
    flex-direction: column;
    gap: 6px;
}
.finding-row {
    display: flex;
    gap: 10px;
    padding: 8px 10px;
    border-radius: 8px;
    border: 1px solid #F1F5F9;
    background: #FFF7ED;
}
.finding-tag {
    font-size: 9px;
    font-weight: 700;
    padding: 3px 8px;
    border-radius: 6px;
    background: #FED7AA;
    color: #9A3412;
    white-space: nowrap;
}
.finding-text {
    font-size: 10.5px;
}
.badge-critical .finding-tag { background: #FEE2E2; color: #991B1B; }
.badge-abnormal .finding-tag { background: #FED7AA; color: #9A3412; }
.badge-borderline .finding-tag { background: #FEF9C3; color: #854D0E; }
.badge-info .finding-tag { background: #E2E8F0; color: #334155; }
.compact-list {
    margin: 6px 0 0 16px;
    padding: 0;
}
.risk-grid {
    display: grid;
    grid-template-columns: 80px 1fr;
    gap: 12px;
    align-items: center;
}
.risk-score {
    font-size: 28px;
    font-weight: 800;
    color: #16A34A;
}
.risk-level {
    font-size: 12px;
    font-weight: 700;
}
.warning {
    background: #FFFBEB;
    border-color: #FDE68A;
}
.disclaimer {
    background: #F1F5F9;
    color: #475569;
    font-size: 10px;
}
"""

        return html_report, css_report
    
    def _format_parameters_for_json(self):
        """Format parameters for JSON output"""
        formatted = []
        parameters = self.results.get("parameters", {})
        
        for param_name, param_data in parameters.items():
            if param_name in ["Age", "Gender"]:
                continue
            
            if param_data:
                formatted.append({
                    "name": param_name,
                    "value": param_data.get("value"),
                    "unit": param_data.get("unit", ""),
                    "status": param_data.get("status", "UNKNOWN"),
                    "reference_range": param_data.get("contextual_range") or param_data.get("reference_range")
                })
        
        return formatted
    
    def save_report(self, output_dir="reports", format="text"):
        """
        Save report to file
        """
        os.makedirs(output_dir, exist_ok=True)
        
        if format == "text":
            filename = f"report_{self.report_id}.txt"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                f.write(self.generate_text_report())
        
        elif format == "json":
            filename = f"report_{self.report_id}.json"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump(self.generate_json_report(), f, indent=2, ensure_ascii=False)

        elif format == "pdf":
            filename = f"report_{self.report_id}.pdf"
            filepath = os.path.join(output_dir, filename)
            with open(filepath, "wb") as f:
                f.write(self.generate_pdf_report())
        
        return filepath


def generate_report(results, format="text"):
    """
    Convenience function to generate report
    """
    generator = ReportGenerator(results)
    
    if format == "text":
        return generator.generate_text_report()
    elif format == "json":
        return generator.generate_json_report()
    elif format == "pdf":
        return generator.generate_pdf_report()
    else:
        return generator.generate_text_report()