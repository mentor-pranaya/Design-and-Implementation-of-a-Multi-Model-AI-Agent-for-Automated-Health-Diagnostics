"""
Summary Generator: Intelligent medical summary synthesis.

Generates conversational, AI-assisted medical summaries that synthesize
complex medical information into clear clinical narratives.

Production-grade medical summary generation with responsible tone.
"""

import logging
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from severity_engine import SeverityLevel, SeverityResult
from risk_aggregator import RiskAggregation, UrgencyLevel

logger = logging.getLogger(__name__)


@dataclass
class MedicalSummary:
    """Structured medical summary output."""
    summary_text: str
    key_insights: List[str]
    top_2_severe_findings: List[str]
    overall_urgency: str
    abnormal_parameter_count: int
    tone: str  # "low_concern", "moderate_concern", "high_concern", "critical_concern"
    guidance: str
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            "summary_text": self.summary_text,
            "key_insights": self.key_insights,
            "top_2_severe_findings": self.top_2_severe_findings,
            "overall_urgency": self.overall_urgency,
            "abnormal_parameter_count": self.abnormal_parameter_count,
            "tone": self.tone,
            "guidance": self.guidance
        }


class SummaryGenerator:
    """
    Generates intelligent medical summaries from structured analysis results.
    
    Combines findings, risks, and parameters into conversational narrative
    with responsible medical tone and clear communication of severity.
    """
    
    # Tone templates based on urgency
    TONE_TEMPLATES = {
        "low_concern": {
            "opening": "Your recent health report shows",
            "transition": "Good news —",
            "closing": "These results suggest you're in good health."
        },
        "moderate_concern": {
            "opening": "Your health report indicates",
            "transition": "We've identified",
            "closing": "These results warrant attention through routine follow-up care."
        },
        "high_concern": {
            "opening": "Your health report reveals",
            "transition": "Important findings show",
            "closing": "These results require prompt medical attention."
        },
        "critical_concern": {
            "opening": "⚠️ Your health report indicates",
            "transition": "Critical finding:",
            "closing": "These results require immediate medical evaluation."
        }
    }
    
    def __init__(self):
        """Initialize summary generator."""
        logger.info("Summary generator initialized")
    
    def generate_medical_summary(
        self,
        severity_results: Dict[str, SeverityResult],
        risk_aggregation: RiskAggregation,
        age: Optional[int] = None,
        gender: Optional[str] = None,
        test_name: Optional[str] = None
    ) -> MedicalSummary:
        """
        Generate intelligent medical summary from analysis results.
        
        Args:
            severity_results: Dict of severity assessment results
            risk_aggregation: Risk aggregation analysis
            age: Optional age for context
            gender: Optional gender for context
            test_name: Optional name of test/report
            
        Returns:
            MedicalSummary: Structured summary with narrative
            
        Example:
            >>> summary = generator.generate_medical_summary(
            ...     severity_results=severity_results,
            ...     risk_aggregation=risk_aggregation,
            ...     age=55
            ... )
            >>> print(summary.summary_text)
        """
        
        # Get tone based on urgency
        tone = self._get_tone(risk_aggregation.global_urgency)
        templates = self.TONE_TEMPLATES[tone]
        
        # Extract top 2 most severe findings
        top_2_findings = self._get_top_2_findings(
            severity_results,
            risk_aggregation
        )
        
        # Build key insights
        key_insights = self._build_key_insights(
            severity_results,
            risk_aggregation,
            top_2_findings
        )
        
        # Generate narrative summary
        summary_text = self._generate_narrative(
            risk_aggregation=risk_aggregation,
            top_2_findings=top_2_findings,
            abnormal_count=risk_aggregation.num_abnormal_parameters,
            templates=templates,
            age=age,
            gender=gender,
            test_name=test_name
        )
        
        # Generate guidance based on urgency
        guidance = self._generate_guidance(
            risk_aggregation.global_urgency,
            risk_aggregation.escalation_reasons,
            rank_domains=risk_aggregation.escalation_reasons
        )
        
        logger.info(
            f"Summary generated: urgency={risk_aggregation.global_urgency.value}, "
            f"abnormal_count={risk_aggregation.num_abnormal_parameters}"
        )
        
        return MedicalSummary(
            summary_text=summary_text,
            key_insights=key_insights,
            top_2_severe_findings=top_2_findings,
            overall_urgency=risk_aggregation.global_urgency.value,
            abnormal_parameter_count=risk_aggregation.num_abnormal_parameters,
            tone=tone,
            guidance=guidance
        )
    
    def _get_tone(self, urgency: UrgencyLevel) -> str:
        """Map urgency level to tone."""
        tone_map = {
            UrgencyLevel.LOW: "low_concern",
            UrgencyLevel.MODERATE: "moderate_concern",
            UrgencyLevel.HIGH: "high_concern",
            UrgencyLevel.CRITICAL: "critical_concern"
        }
        return tone_map.get(urgency, "low_concern")
    
    def _get_top_2_findings(
        self,
        severity_results: Dict[str, SeverityResult],
        risk_aggregation: RiskAggregation
    ) -> List[str]:
        """Extract top 2 most severe findings."""
        
        findings = []
        
        # Critical parameters first
        for param in risk_aggregation.critical_parameters:
            if param in severity_results:
                result = severity_results[param]
                findings.append(
                    f"{param.replace('_', ' ').title()}: {result.value} {result.unit} "
                    f"(Critical - {result.deviation_percent:.0f}% above normal)"
                )
        
        # Then high parameters
        for param in risk_aggregation.high_risk_parameters:
            if param in severity_results:
                result = severity_results[param]
                findings.append(
                    f"{param.replace('_', ' ').title()}: {result.value} {result.unit} "
                    f"(High - {result.deviation_percent:.0f}% above normal)"
                )
        
        # Return top 2
        return findings[:2]
    
    def _build_key_insights(
        self,
        severity_results: Dict[str, SeverityResult],
        risk_aggregation: RiskAggregation,
        top_2_findings: List[str]
    ) -> List[str]:
        """Build key clinical insights from results."""
        
        insights = []
        
        # Insight 1: Number of abnormalities
        if risk_aggregation.num_abnormal_parameters == 0:
            insights.append("All measured parameters are within normal ranges.")
        elif risk_aggregation.num_abnormal_parameters == 1:
            insights.append("One parameter shows abnormal values.")
        else:
            insights.append(
                f"Multiple parameters ({risk_aggregation.num_abnormal_parameters}) "
                f"show abnormal values."
            )
        
        # Insight 2: Severity distribution
        dist = risk_aggregation.severity_distribution
        if dist["critical"] > 0:
            insights.append(f"⚠️ {dist['critical']} critical abnormality found.")
        if dist["high"] > 0:
            insights.append(f"⚠️ {dist['high']} high-severity finding(s) detected.")
        if dist["moderate"] > 0:
            insights.append(f"📊 {dist['moderate']} moderate abnormality(ies) identified.")
        
        # Insight 3: Max deviation
        if risk_aggregation.max_deviation_percent > 0:
            insights.append(
                f"Maximum deviation from normal: {risk_aggregation.max_deviation_percent:.0f}%"
            )
        
        # Insight 4: Medical history consideration
        if risk_aggregation.medical_history_considered:
            insights.append("Assessment adjusted based on medical history.")
        
        return insights
    
    def _generate_narrative(
        self,
        risk_aggregation: RiskAggregation,
        top_2_findings: List[str],
        abnormal_count: int,
        templates: Dict[str, str],
        age: Optional[int] = None,
        gender: Optional[str] = None,
        test_name: Optional[str] = None
    ) -> str:
        """Generate conversational narrative summary."""
        
        parts = []
        
        # Opening
        test_ref = f"your {test_name}" if test_name else "your health report"
        parts.append(f"{templates['opening']} {test_ref}:")
        
        # Context
        if age or gender:
            context = []
            if age:
                context.append(f"age {age}")
            if gender:
                context.append(f"{gender.lower()}")
            parts.append(f"(Patient: {', '.join(context).title()})")
        
        # Main findings
        if abnormal_count == 0:
            parts.append(f"{templates['transition']} all key indicators are within normal ranges.")
        elif abnormal_count == 1:
            parts.append(f"{templates['transition']} {abnormal_count} parameter requires attention:")
            if top_2_findings:
                parts.append(f"• {top_2_findings[0]}")
        else:
            parts.append(
                f"{templates['transition']} {abnormal_count} key parameters show abnormal values:"
            )
            for finding in top_2_findings:
                parts.append(f"• {finding}")
        
        # Urgency statement
        urgency_statement = self._get_urgency_statement(risk_aggregation.global_urgency)
        parts.append(f"\n{urgency_statement}")
        
        # Closing
        parts.append(f"\n{templates['closing']}")
        
        return " ".join(parts)
    
    def _get_urgency_statement(self, urgency: UrgencyLevel) -> str:
        """Get statement based on urgency level."""
        
        statements = {
            UrgencyLevel.CRITICAL: (
                "⚠️ CRITICAL URGENCY: These findings require immediate medical evaluation. "
                "Seek emergency medical attention or visit an ER immediately."
            ),
            UrgencyLevel.HIGH: (
                "🟠 HIGH URGENCY: Prompt medical consultation is recommended within 1-3 days. "
                "These findings warrant professional evaluation."
            ),
            UrgencyLevel.MODERATE: (
                "🟡 MODERATE CONCERN: Schedule a healthcare appointment within 1-2 weeks "
                "to discuss these findings."
            ),
            UrgencyLevel.LOW: (
                "🟢 LOW URGENCY: These results are generally reassuring. "
                "Routine follow-up during regular checkups is recommended."
            )
        }
        
        return statements.get(urgency, "Please consult with a healthcare provider.")
    
    def _generate_guidance(
        self,
        urgency: UrgencyLevel,
        escalation_reasons: List[str],
        rank_domains: List[str]
    ) -> str:
        """Generate next-step guidance based on urgency."""
        
        guidance_map = {
            UrgencyLevel.CRITICAL: (
                "IMMEDIATE ACTION REQUIRED:\n"
                "1. Contact emergency services (911) or visit nearest ER\n"
                "2. Inform healthcare provider of critical findings\n"
                "3. Do not delay — seek immediate professional evaluation"
            ),
            UrgencyLevel.HIGH: (
                "PROMPT ACTION REQUIRED:\n"
                "1. Schedule urgent medical appointment (within 1-3 days)\n"
                "2. Contact your healthcare provider today if possible\n"
                "3. Monitor symptoms and report to physician"
            ),
            UrgencyLevel.MODERATE: (
                "ROUTINE ACTION:\n"
                "1. Schedule regular appointment (within 1-2 weeks)\n"
                "2. Discuss findings with healthcare provider\n"
                "3. Consider lifestyle modifications if recommended"
            ),
            UrgencyLevel.LOW: (
                "STANDARD CARE:\n"
                "1. No immediate action required\n"
                "2. Share results with your healthcare provider at next visit\n"
                "3. Continue regular health maintenance"
            )
        }
        
        return guidance_map.get(urgency, "Consult healthcare provider for guidance.")
    
    def generate_summary_html(self, summary: MedicalSummary) -> str:
        """
        Generate HTML representation of summary for UI display.
        
        Args:
            summary: MedicalSummary object
            
        Returns:
            str: HTML markup
        """
        
        # Color coding based on tone
        color_map = {
            "low_concern": "#4CAF50",        # Green
            "moderate_concern": "#FFC107",   # Yellow
            "high_concern": "#FF9800",       # Orange
            "critical_concern": "#F44336"     # Red
        }
        
        color = color_map.get(summary.tone, "#2196F3")
        
        html = f"""
        <div style="border-left: 5px solid {color}; padding: 20px; margin: 10px 0; background-color: #f9f9f9; border-radius: 4px;">
            <h3 style="margin-top: 0; color: {color};">Medical Summary</h3>
            <p style="font-size: 16px; line-height: 1.6;">{summary.summary_text}</p>
            
            <h4 style="color: {color};">Key Insights</h4>
            <ul style="padding-left: 20px;">
        """
        
        for insight in summary.key_insights:
            html += f"<li style='margin: 8px 0;'>{insight}</li>"
        
        html += """
            </ul>
            
            <h4 style="color: {color};">Top Findings</h4>
            <ul style="padding-left: 20px;">
        """.format(color=color)
        
        for finding in summary.top_2_severe_findings:
            html += f"<li style='margin: 8px 0;'><strong>{finding}</strong></li>"
        
        html += f"""
            </ul>
            
            <p style="color: {color}; font-weight: bold;">Overall Urgency: {summary.overall_urgency}</p>
            <p>{summary.guidance}</p>
        </div>
        """
        
        return html


def generate_medical_summary(
    severity_results: Dict[str, SeverityResult],
    risk_aggregation: RiskAggregation,
    age: Optional[int] = None,
    gender: Optional[str] = None,
    test_name: Optional[str] = None
) -> MedicalSummary:
    """Convenience function for quick summary generation."""
    generator = SummaryGenerator()
    return generator.generate_medical_summary(
        severity_results=severity_results,
        risk_aggregation=risk_aggregation,
        age=age,
        gender=gender,
        test_name=test_name
    )


if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    
    from severity_engine import SeverityEngine
    from risk_aggregator import RiskAggregator
    
    engine = SeverityEngine()
    
    # Simulate severity results
    severity_results = {
        "glucose": engine.calculate_severity(250, 70, 100, "mg/dL"),
        "hemoglobin": engine.calculate_severity(9.5, 12, 16, "g/dL"),
        "cholesterol": engine.calculate_severity(220, 0, 200, "mg/dL"),
        "hdl": engine.calculate_severity(30, 40, 999, "mg/dL"),
    }
    
    aggregator = RiskAggregator()
    risk = aggregator.aggregate_risks(
        severity_results=severity_results,
        age=58,
        medical_history=["Type 2 Diabetes", "Hypertension"]
    )
    
    generator = SummaryGenerator()
    summary = generator.generate_medical_summary(
        severity_results=severity_results,
        risk_aggregation=risk,
        age=58,
        gender="Male",
        test_name="Blood Work"
    )
    
    print("\n=== Medical Summary ===")
    print(summary.summary_text)
    print(f"\nUrgency: {summary.overall_urgency}")
    print(f"Tone: {summary.tone}")
    print(f"\nKey Insights:")
    for insight in summary.key_insights:
        print(f"  - {insight}")
    print(f"\nGuidance:\n{summary.guidance}")
