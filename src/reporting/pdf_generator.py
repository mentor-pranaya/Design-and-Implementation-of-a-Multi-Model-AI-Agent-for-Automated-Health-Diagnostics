from fpdf import FPDF
import os
from datetime import datetime

class PDFReportGenerator:
    """Generates a professional PDF report from analysis data."""

    def generate_pdf_report(self, analysis_report: dict, filename: str = "report.pdf") -> str:
        """
        Generates a professional medical analysis PDF report with comprehensive content.
        """
        pdf = FPDF()
        pdf.add_page()
        
        # --- Page Header ---
        pdf.set_fill_color(240, 244, 255)
        pdf.rect(0, 0, 210, 40, 'F')
        
        pdf.set_y(15)
        pdf.set_font("Arial", 'B', 20)
        pdf.set_text_color(102, 126, 234)
        pdf.cell(0, 10, "INBLOODO AI", ln=True, align='L')
        
        pdf.set_font("Arial", '', 10)
        pdf.set_text_color(100, 100, 100)
        pdf.cell(0, 5, "Advanced Automated Health Diagnostics", ln=True, align='L')
        
        pdf.set_y(15)
        pdf.set_font("Arial", 'B', 10)
        pdf.cell(0, 10, "MEDICAL ANALYSIS REPORT", ln=True, align='R')
        pdf.set_font("Arial", '', 9)
        pdf.cell(0, 5, f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True, align='R')
        
        pdf.ln(20)
        pdf.set_text_color(0, 0, 0)

        # Check if analysis failed
        status = analysis_report.get("status", "unknown")
        params = analysis_report.get("extracted_parameters", {})
        
        # --- 1. Clinical Summary (Synthesis) ---
        self._add_section_header(pdf, "CLINICAL SUMMARY")
        pdf.set_font("Arial", '', 11)
        
        synthesis = analysis_report.get("synthesis", "")
        if synthesis and synthesis != "Analysis failed.":
            pdf.multi_cell(0, 6, synthesis)
        elif params:
            # Generate fallback summary from parameters
            pdf.multi_cell(0, 6, self._generate_fallback_summary(params))
        else:
            pdf.multi_cell(0, 6, "Analysis is in progress. Please ensure all blood test parameters are clearly visible in the uploaded document.")
        pdf.ln(5)
        
        # --- 2. Risk Assessment ---
        self._add_section_header(pdf, "RISK ASSESSMENT")
        
        risk_level = analysis_report.get("overall_risk", "Moderate")
        if "High" in risk_level: pdf.set_text_color(200, 0, 0)
        elif "Moderate" in risk_level: pdf.set_text_color(200, 150, 0)
        else: pdf.set_text_color(0, 150, 0)
        
        pdf.set_font("Arial", 'B', 12)
        pdf.cell(0, 8, f"Overall Risk Level: {risk_level}", ln=True)
        pdf.set_text_color(0, 0, 0)
        
        risks = analysis_report.get("risks", [])
        if risks:
            pdf.set_font("Arial", '', 10)
            for r in risks:
                pdf.cell(0, 6, f"- {r}", ln=True)
        elif params:
            # Generate fallback risks
            pdf.set_font("Arial", '', 10)
            for risk in self._generate_fallback_risks(params):
                pdf.cell(0, 6, f"- {risk}", ln=True)
        
        prediction = analysis_report.get("ai_prediction")
        if prediction and isinstance(prediction, dict) and "risk_score" in prediction:
            score = prediction["risk_score"]
            pdf.set_font("Arial", 'I', 10)
            pdf.cell(0, 8, f"AI Confidence Score: {score:.2f}", ln=True)
        
        pdf.ln(5)

        # --- 3. Parameter Analysis (Table) ---
        self._add_section_header(pdf, "DETAILED PARAMETER ANALYSIS")
        
        if params:
            # Table Styling
            pdf.set_fill_color(230, 230, 230)
            pdf.set_font("Arial", 'B', 10)
            pdf.cell(60, 8, "Parameter", 1, 0, 'C', True)
            pdf.cell(30, 8, "Value", 1, 0, 'C', True)
            pdf.cell(30, 8, "Unit", 1, 0, 'C', True)
            pdf.cell(60, 8, "Interpretation", 1, 1, 'C', True)
            
            pdf.set_font("Arial", '', 10)
            interpretations = analysis_report.get("interpretations", [])
            
            for idx, (param, data) in enumerate(params.items()):
                if isinstance(data, dict):
                    value = str(data.get("value", "-"))
                    unit = str(data.get("unit", "-"))
                else:
                    value = str(data)
                    unit = "-"
                
                name = param.replace("_", " ").title()
                
                # Find matching interpretation
                note = self._get_interpretation(name, value, interpretations)
                
                # Row shading
                fill = idx % 2 == 1
                if fill: pdf.set_fill_color(245, 245, 245)
                
                pdf.cell(60, 8, name[:25], 1, 0, 'L', fill)
                pdf.cell(30, 8, value[:12], 1, 0, 'C', fill)
                pdf.cell(30, 8, unit[:12], 1, 0, 'C', fill)
                
                # Color coding for interpretations
                if note in ["High", "Low", "Abnormal", "Critical"]:
                    pdf.set_text_color(200, 0, 0)
                    pdf.set_font("Arial", 'B', 10)
                
                pdf.cell(60, 8, note, 1, 1, 'C', fill)
                pdf.set_text_color(0, 0, 0)
                pdf.set_font("Arial", '', 10)
        else:
            pdf.set_font("Arial", 'I', 10)
            pdf.multi_cell(0, 6, "No parameters were extracted from the uploaded document. Please ensure the blood report contains clear parameter values.")
        
        pdf.ln(5)

        # --- 4. Detailed Health Analysis & Suggestions ---
        self._add_section_header(pdf, "HEALTH ANALYSIS & SUGGESTIONS")
        pdf.set_font("Arial", '', 10)
        
        suggestions = self._generate_detailed_suggestions(params, risks)
        for suggestion in suggestions:
            pdf.multi_cell(0, 6, f"- {suggestion}")
            pdf.ln(1)
        pdf.ln(3)

        # --- 5. Recommendations ---
        linked_recs = analysis_report.get("linked_recommendations", [])
        if linked_recs:
            self._add_section_header(pdf, "PERSONALIZED RECOMMENDATIONS")
            pdf.set_font("Arial", '', 11)
            
            for item in linked_recs:
                rec = item.get("recommendation", "")
                reason = item.get("finding", "")
                
                pdf.set_font("Arial", 'B', 10)
                pdf.write(6, "- ")
                pdf.write(6, f"{rec}")
                pdf.set_font("Arial", 'I', 9)
                pdf.set_text_color(100, 100, 100)
                pdf.cell(0, 6, f" (Based on: {reason})", ln=True)
                pdf.set_text_color(0, 0, 0)
                pdf.ln(1)
            pdf.ln(5)
        
        # --- 6. Prescription Recommendations ---
        self._add_section_header(pdf, "PRESCRIPTION & LIFESTYLE RECOMMENDATIONS")
        pdf.set_font("Arial", '', 10)
        
        prescriptions = analysis_report.get("prescriptions", [])
        if prescriptions:
            for p in prescriptions:
                if "PRESCRIPTION SUGGESTIONS" in p: continue
                pdf.multi_cell(0, 6, f"- {p}")
        else:
            # Generate fallback prescriptions
            for rx in self._generate_fallback_prescriptions(params):
                pdf.multi_cell(0, 6, f"- {rx}")
        pdf.ln(5)

        # --- 7. General Health Tips ---
        self._add_section_header(pdf, "GENERAL HEALTH TIPS")
        pdf.set_font("Arial", '', 10)
        health_tips = [
            "Maintain a balanced diet rich in fruits, vegetables, whole grains, and lean proteins",
            "Stay hydrated by drinking at least 8 glasses of water daily",
            "Exercise regularly - aim for at least 30 minutes of moderate activity 5 days a week",
            "Get 7-9 hours of quality sleep each night",
            "Manage stress through meditation, yoga, or other relaxation techniques",
            "Avoid smoking and limit alcohol consumption",
            "Schedule regular health check-ups and follow-up blood tests as recommended"
        ]
        for tip in health_tips:
            pdf.multi_cell(0, 6, f"- {tip}")
        pdf.ln(5)

        # --- Footer & Disclaimer ---
        if pdf.get_y() > 250: pdf.add_page()
        
        pdf.set_y(-30)
        pdf.set_font("Arial", 'I', 8)
        pdf.set_text_color(120, 120, 120)
        disclaimer = "DISCLAIMER: This report is generated by an AI Agent and is for informational purposes only. It does not constitute medical diagnosis or advice. Always consult a qualified healthcare provider before making any medical decisions."
        pdf.multi_cell(0, 4, disclaimer, 0, 'C')
        
        pdf.set_y(-15)
        pdf.cell(0, 10, f"Page {pdf.page_no()}", 0, 0, 'C')

        # Save output
        output_path = os.path.join("reports", filename)
        os.makedirs("reports", exist_ok=True)
        pdf.output(output_path)
        return output_path

    def _add_section_header(self, pdf, title):
        """Helper to add a styled section header."""
        pdf.ln(3)
        pdf.set_font("Arial", 'B', 12)
        pdf.set_text_color(60, 80, 150)
        pdf.cell(0, 8, title, ln=True)
        pdf.set_draw_color(60, 80, 150)
        pdf.set_line_width(0.5)
        pdf.line(pdf.get_x(), pdf.get_y(), pdf.get_x() + 190, pdf.get_y())
        pdf.ln(3)
        pdf.set_text_color(0, 0, 0)
        pdf.set_font("Arial", '', 11)

    def _generate_fallback_summary(self, params):
        """Generate a clinical summary from available parameters."""
        if not params:
            return "No parameters available for analysis."
        
        summary_parts = []
        summary_parts.append(f"Blood analysis shows {len(params)} parameters measured.")
        
        # Check for common parameters
        if "hemoglobin" in params or "hb" in params:
            hb_val = params.get("hemoglobin", params.get("hb", {}))
            if isinstance(hb_val, dict):
                hb = hb_val.get("value", 0)
                if hb < 12:
                    summary_parts.append("Hemoglobin levels are below normal range, indicating possible anemia.")
                elif hb > 17:
                    summary_parts.append("Hemoglobin levels are elevated.")
                else:
                    summary_parts.append("Hemoglobin levels are within normal range.")
        
        if "glucose" in params or "blood_sugar" in params:
            summary_parts.append("Blood glucose monitoring is important for metabolic health.")
        
        if "cholesterol" in params:
            summary_parts.append("Lipid profile assessment included.")
        
        return " ".join(summary_parts)

    def _generate_fallback_risks(self, params):
        """Generate risk assessments from parameters."""
        risks = []
        
        for param, data in params.items():
            value = data.get("value", 0) if isinstance(data, dict) else data
            
            if "hemoglobin" in param.lower() or "hb" in param.lower():
                if value < 12:
                    risks.append("Low hemoglobin may indicate anemia - consult physician")
                elif value > 17:
                    risks.append("Elevated hemoglobin requires medical evaluation")
            
            if "glucose" in param.lower():
                if value > 125:
                    risks.append("Elevated glucose levels - diabetes screening recommended")
                elif value < 70:
                    risks.append("Low glucose - monitor for hypoglycemia")
            
            if "cholesterol" in param.lower():
                if value > 200:
                    risks.append("High cholesterol - cardiovascular risk assessment needed")
        
        if not risks:
            risks.append("Regular monitoring recommended for optimal health")
        
        return risks

    def _get_interpretation(self, name, value, interpretations):
        """Get interpretation for a parameter."""
        name_lower = name.lower()
        for interp in interpretations:
            interp_lower = interp.lower()
            if name_lower in interp_lower:
                if "high" in interp_lower: return "High"
                elif "low" in interp_lower: return "Low"
                elif "abnormal" in interp_lower: return "Abnormal"
                elif "critical" in interp_lower: return "Critical"
        
        # Fallback interpretation based on common ranges
        try:
            val = float(value)
            if "hemoglobin" in name_lower or "hb" in name_lower:
                if val < 12: return "Low"
                elif val > 17: return "High"
            elif "glucose" in name_lower:
                if val < 70: return "Low"
                elif val > 125: return "High"
            elif "cholesterol" in name_lower:
                if val > 200: return "High"
        except:
            pass
        
        return "Normal"

    def _generate_detailed_suggestions(self, params, risks):
        """Generate detailed health suggestions based on parameters."""
        suggestions = []
        
        if not params:
            suggestions.append("Upload a clear blood report for personalized health suggestions")
            suggestions.append("Ensure all parameter values and units are visible in the document")
            return suggestions
        
        # Parameter-specific suggestions
        for param, data in params.items():
            value = data.get("value", 0) if isinstance(data, dict) else data
            param_lower = param.lower()
            
            if "hemoglobin" in param_lower or "hb" in param_lower:
                try:
                    val = float(value)
                    if val < 12:
                        suggestions.append("Increase iron-rich foods: spinach, red meat, lentils, fortified cereals")
                        suggestions.append("Consider vitamin C supplements to enhance iron absorption")
                    elif val > 17:
                        suggestions.append("Stay well-hydrated and avoid high-altitude exposure")
                except:
                    pass
            
            if "glucose" in param_lower or "sugar" in param_lower:
                try:
                    val = float(value)
                    if val > 100:
                        suggestions.append("Reduce refined sugar and carbohydrate intake")
                        suggestions.append("Increase physical activity - 30 minutes daily walking recommended")
                        suggestions.append("Monitor blood sugar levels regularly")
                except:
                    pass
            
            if "cholesterol" in param_lower:
                try:
                    val = float(value)
                    if val > 200:
                        suggestions.append("Adopt a heart-healthy diet low in saturated fats")
                        suggestions.append("Include omega-3 rich foods: fish, walnuts, flaxseeds")
                        suggestions.append("Regular cardiovascular exercise recommended")
                except:
                    pass
            
            if "wbc" in param_lower or "white blood" in param_lower:
                suggestions.append("Maintain good hygiene to support immune function")
                suggestions.append("Ensure adequate sleep and stress management")
        
        # General suggestions if no specific ones
        if not suggestions:
            suggestions.append("Maintain a balanced diet with adequate nutrients")
            suggestions.append("Regular exercise and physical activity recommended")
            suggestions.append("Follow up with healthcare provider for detailed assessment")
        
        return suggestions

    def _generate_fallback_prescriptions(self, params):
        """Generate prescription recommendations."""
        prescriptions = []
        
        if not params:
            prescriptions.append("Consult physician for personalized prescription recommendations")
            return prescriptions
        
        # General prescriptions based on parameters
        for param, data in params.items():
            value = data.get("value", 0) if isinstance(data, dict) else data
            param_lower = param.lower()
            
            if "hemoglobin" in param_lower or "hb" in param_lower:
                try:
                    val = float(value)
                    if val < 12:
                        prescriptions.append("Iron supplements (Ferrous Sulfate 325mg) - consult doctor for dosage")
                        prescriptions.append("Vitamin B12 and Folic Acid supplements as recommended")
                except:
                    pass
            
            if "glucose" in param_lower:
                try:
                    val = float(value)
                    if val > 125:
                        prescriptions.append("Diabetes screening and HbA1c test recommended")
                        prescriptions.append("Consult endocrinologist for glucose management plan")
                except:
                    pass
            
            if "cholesterol" in param_lower:
                try:
                    val = float(value)
                    if val > 200:
                        prescriptions.append("Lipid-lowering therapy may be considered - consult cardiologist")
                        prescriptions.append("Omega-3 fatty acid supplements (1000mg daily)")
                except:
                    pass
        
        # Always include general recommendations
        prescriptions.append("Multivitamin supplement for overall health maintenance")
        prescriptions.append("Vitamin D3 (1000-2000 IU daily) especially if limited sun exposure")
        prescriptions.append("Probiotics for digestive health support")
        
        return prescriptions
