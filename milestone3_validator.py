"""
Milestone 3 Testing & Validation Module
Implements comprehensive evaluation criteria for Milestone 3
- Summary Coherence
- Recommendation Relevance & Actionability
- Clinical Expert Review Compatibility
"""

import json
from datetime import datetime


class Milestone3Validator:
    """Validates Milestone 3 outputs against success criteria"""
    
    def __init__(self):
        self.validation_results = {
            "summary_coherence": 0,
            "recommendation_relevance": 0,
            "recommendation_actionability": 0,
            "clinical_alignment": 0,
            "overall_score": 0,
            "issues": [],
            "recommendations": []
        }
    
    def validate_synthesis(self, synthesis_findings, interpretation, risk_assessment):
        """
        Validate synthesis coherence against model outputs
        Success Criteria: Synthesized summaries accurately reflect model findings in >95% of cases
        
        Args:
            synthesis_findings: dict - Output from synthesis_engine
            interpretation: dict - Model 1 output
            risk_assessment: dict - Model 2 output
        
        Returns:
            dict - Validation results
        """
        
        issues = []
        accuracy_score = 0
        
        # Check 1: Abnormal parameters are reflected in synthesis
        abnormal_from_model = sum(1 for status in interpretation.values() if status != "NORMAL")
        abnormal_in_synthesis = len(synthesis_findings.get("abnormal_parameters", []))
        
        if abnormal_in_synthesis == abnormal_from_model:
            accuracy_score += 20
        else:
            issues.append(f"Abnormal parameter count mismatch: Model={abnormal_from_model}, Synthesis={abnormal_in_synthesis}")
        
        # Check 2: Risk patterns are reflected in synthesis
        risk_categories_from_model = set(risk_assessment.keys())
        risk_categories_in_synthesis = set(rp.get("category") for rp in synthesis_findings.get("risk_patterns", []))
        
        if risk_categories_from_model == risk_categories_in_synthesis:
            accuracy_score += 20
        else:
            issues.append(f"Risk category mismatch")
        
        # Check 3: Critical findings are identified
        critical_findings = synthesis_findings.get("critical_findings", [])
        if len(critical_findings) > 0 and abnormal_from_model > 0:
            accuracy_score += 15
        elif abnormal_from_model == 0 and len(critical_findings) == 0:
            accuracy_score += 15
        else:
            issues.append("Critical findings not properly identified")
        
        # Check 4: Overall health status is determined
        overall_status = synthesis_findings.get("overall_health_status", "")
        if overall_status and any(status in overall_status for status in ["HEALTHY", "MONITOR", "ATTENTION", "CONCERNING"]):
            accuracy_score += 15
        else:
            issues.append("Overall health status not properly determined")
        
        # Check 5: Summary is generated
        summary = synthesis_findings.get("summary", "").strip()
        if len(summary) > 100:  # Minimum summary length
            accuracy_score += 15
        else:
            issues.append("Summary is too short or missing")
        
        # Check 6: Priority areas are identified
        priority_areas = synthesis_findings.get("priority_areas", [])
        if len(priority_areas) > 0 or abnormal_from_model == 0:
            accuracy_score += 15
        else:
            issues.append("Priority areas not identified despite abnormalities")
        
        self.validation_results["summary_coherence"] = min(100, accuracy_score)
        self.validation_results["issues"].extend(issues)
        
        return {
            "coherence_score": min(100, accuracy_score),
            "issues": issues,
            "passed": min(100, accuracy_score) >= 95
        }
    
    def validate_recommendations(self, recommendations, synthesis_findings, risk_assessment):
        """
        Validate recommendation relevance and actionability
        Success Criteria: Recommendations relevant and actionable for >90% of identified findings
        
        Args:
            recommendations: dict - Output from recommendation_generator
            synthesis_findings: dict - Output from synthesis_engine
            risk_assessment: dict - Model 2 output
        
        Returns:
            dict - Validation results
        """
        
        relevance_score = 0
        actionability_score = 0
        alignment_score = 0
        validation_issues = []
        
        # Check 1: Dietary recommendations match abnormalities
        dietary_recs = recommendations.get("dietary_recommendations", [])
        abnormal_params = synthesis_findings.get("abnormal_parameters", [])
        
        if dietary_recs and abnormal_params:
            diet_relevance = 0
            for param_info in abnormal_params:
                param = param_info.get("parameter", "")
                # Check if this parameter has corresponding recommendations
                for diet_rec in dietary_recs:
                    if param in str(diet_rec.get("finding", "")):
                        diet_relevance += 1
            
            if diet_relevance > 0:
                relevance_score += 15
            else:
                validation_issues.append("Dietary recommendations not linked to abnormal parameters")
        else:
            relevance_score += 15  # No abnormalities, no dietary recs needed
        
        # Check 2: Lifestyle recommendations match risk areas
        lifestyle_recs = recommendations.get("lifestyle_recommendations", [])
        high_risk_areas = [cat for cat, level in risk_assessment.items() if level == "HIGH"]
        
        if lifestyle_recs and high_risk_areas:
            lifestyle_relevance = 0
            for risk_area in high_risk_areas:
                for lifestyle_rec in lifestyle_recs:
                    if risk_area in str(lifestyle_rec.get("finding", "")):
                        lifestyle_relevance += 1
            
            if lifestyle_relevance > 0:
                relevance_score += 15
            else:
                validation_issues.append("Lifestyle recommendations not linked to high-risk areas")
        else:
            relevance_score += 15
        
        # Check 3: Medical follow-up is appropriate for risk level
        medical_followup = recommendations.get("medical_follow_up", [])
        
        if medical_followup:
            for followup in medical_followup:
                urgency = followup.get("urgency", "").upper()
                if high_risk_areas and urgency == "URGENT":
                    relevance_score += 15
                    break
                elif not high_risk_areas and urgency in ["ROUTINE", "RECOMMENDED"]:
                    relevance_score += 15
                    break
        else:
            validation_issues.append("No medical follow-up recommendations provided")
        
        # Check 4: Actionability - Recommendations have specific actions
        actionability_count = 0
        total_recommendations = 0
        
        for category in ["dietary_recommendations", "lifestyle_recommendations"]:
            for rec_item in recommendations.get(category, []):
                rec_list = rec_item.get("recommendations", [])
                for rec in rec_list:
                    total_recommendations += 1
                    # Check if recommendation is specific and actionable
                    if any(action in rec for action in ["eat", "increase", "reduce", "avoid", "exercise", "limit", "monitor"]):
                        actionability_count += 1
        
        if total_recommendations > 0:
            actionability_score = (actionability_count / total_recommendations) * 30
        else:
            actionability_score = 30  # No recommendations to check
        
        # Check 5: Monitoring schedule is appropriate
        monitoring = recommendations.get("monitoring_schedule", [])
        if monitoring:
            actionability_score += 10
        else:
            validation_issues.append("No monitoring schedule provided")
        
        # Check 6: Supplementation advice is evidence-based
        supplements = recommendations.get("supplementation_advice", [])
        if supplements:
            actionability_score += 10
        
        # Check 7: Disclaimers are present
        disclaimers = recommendations.get("disclaimers", [])
        if disclaimers:
            alignment_score += 15
        else:
            validation_issues.append("Critical: Medical disclaimers missing")
        
        # Check 8: Recommendations linked to specific findings
        priority_areas = synthesis_findings.get("priority_areas", [])
        if priority_areas:
            for priority in priority_areas:
                area = priority.get("area", "")
                # Check if this priority area has recommendations
                rec_found = False
                for dietary_rec in dietary_recs:
                    if area in str(dietary_rec):
                        rec_found = True
                        break
                for lifestyle_rec in lifestyle_recs:
                    if area in str(lifestyle_rec):
                        rec_found = True
                        break
                
                if rec_found:
                    alignment_score += 10
        
        self.validation_results["recommendation_relevance"] = min(100, relevance_score)
        self.validation_results["recommendation_actionability"] = min(100, actionability_score)
        self.validation_results["clinical_alignment"] = min(100, alignment_score)
        self.validation_results["issues"].extend(validation_issues)
        
        return {
            "relevance_score": min(100, relevance_score),
            "actionability_score": min(100, actionability_score),
            "alignment_score": min(100, alignment_score),
            "issues": validation_issues,
            "passed": min(100, relevance_score + actionability_score) / 2 >= 90
        }
    
    def validate_clinical_alignment(self, recommendations, synthesis_findings):
        """
        Validate that recommendations align with established medical guidelines
        """
        alignment_issues = []
        guideline_adherence = 0
        
        # Check cardiovascular recommendations
        diet_recs = recommendations.get("dietary_recommendations", [])
        for diet_rec in diet_recs:
            if "Cholesterol" in diet_rec.get("finding", ""):
                foods = diet_rec.get("foods_to_include", [])
                # Check for evidence-based foods
                evidence_based = ["fatty fish", "almonds", "olive oil", "avocado", "berries"]
                if any(food.lower() in [f.lower() for f in foods] for food in evidence_based):
                    guideline_adherence += 10
        
        # Check diabetes recommendations
        for diet_rec in diet_recs:
            if "Glucose" in diet_rec.get("finding", ""):
                recommendations_list = diet_rec.get("recommendations", [])
                if any("fiber" in rec.lower() or "complex carb" in rec.lower() for rec in recommendations_list):
                    guideline_adherence += 10
        
        return {
            "guideline_adherence": min(100, guideline_adherence),
            "issues": alignment_issues
        }
    
    def generate_validation_report(self):
        """Generate comprehensive validation report"""
        
        coherence = self.validation_results["summary_coherence"]
        relevance = self.validation_results["recommendation_relevance"]
        actionability = self.validation_results["recommendation_actionability"]
        alignment = self.validation_results["clinical_alignment"]
        
        overall_score = (coherence + relevance + actionability + alignment) / 4
        self.validation_results["overall_score"] = overall_score
        
        report = []
        report.append("=" * 70)
        report.append(" " * 15 + "MILESTONE 3 VALIDATION REPORT")
        report.append("=" * 70)
        report.append("")
        
        report.append("VALIDATION METRICS:")
        report.append(f"  Summary Coherence:           {coherence:>6.2f}%  {'✓ PASS' if coherence >= 95 else '✗ FAIL'}")
        report.append(f"  Recommendation Relevance:    {relevance:>6.2f}%  {'✓ PASS' if relevance >= 90 else '✗ FAIL'}")
        report.append(f"  Recommendation Actionability:{actionability:>6.2f}%  {'✓ PASS' if actionability >= 90 else '✗ FAIL'}")
        report.append(f"  Clinical Alignment:          {alignment:>6.2f}%  {'✓ PASS' if alignment >= 80 else '✗ FAIL'}")
        report.append("-" * 70)
        report.append(f"  OVERALL SCORE:               {overall_score:>6.2f}%")
        report.append("=" * 70)
        report.append("")
        
        # Success Criteria Check
        success_criteria_met = (
            coherence >= 95 and
            relevance >= 90 and
            actionability >= 90
        )
        
        report.append("SUCCESS CRITERIA CHECK:")
        report.append(f"  Summary Coherence >= 95%:    {'✓ PASS' if coherence >= 95 else '✗ FAIL'}")
        report.append(f"  Relevance >= 90%:            {'✓ PASS' if relevance >= 90 else '✗ FAIL'}")
        report.append(f"  Actionability >= 90%:        {'✓ PASS' if actionability >= 90 else '✗ FAIL'}")
        report.append("")
        
        if success_criteria_met:
            report.append("✓ MILESTONE 3 SUCCESS CRITERIA MET")
        else:
            report.append("✗ MILESTONE 3 SUCCESS CRITERIA NOT MET")
        report.append("")
        
        # Issues
        if self.validation_results["issues"]:
            report.append("IDENTIFIED ISSUES:")
            for i, issue in enumerate(self.validation_results["issues"], 1):
                report.append(f"  {i}. {issue}")
            report.append("")
        
        # Recommendations
        if self.validation_results["recommendations"]:
            report.append("IMPROVEMENT RECOMMENDATIONS:")
            for i, rec in enumerate(self.validation_results["recommendations"], 1):
                report.append(f"  {i}. {rec}")
        
        report.append("")
        report.append("=" * 70)
        
        return "\n".join(report)


def validate_milestone_3_output(synthesis_findings, recommendations, interpretation, 
                               risk_assessment):
    """
    Complete validation function for Milestone 3 outputs
    
    Returns:
        dict - Comprehensive validation results
    """
    
    validator = Milestone3Validator()
    
    # Validate synthesis
    synthesis_validation = validator.validate_synthesis(
        synthesis_findings, interpretation, risk_assessment
    )
    
    # Validate recommendations
    recommendations_validation = validator.validate_recommendations(
        recommendations, synthesis_findings, risk_assessment
    )
    
    # Validate clinical alignment
    clinical_validation = validator.validate_clinical_alignment(
        recommendations, synthesis_findings
    )
    
    # Generate report
    validation_report = validator.generate_validation_report()
    
    return {
        "synthesis_validation": synthesis_validation,
        "recommendations_validation": recommendations_validation,
        "clinical_validation": clinical_validation,
        "overall_results": validator.validation_results,
        "validation_report": validation_report,
        "timestamp": datetime.now().isoformat()
    }
