"""
FastAPI Backend for Blood Report Analysis
Integrates with the complete processing pipeline (Phases 1-3)
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import uuid
import asyncio
from datetime import datetime
import os
import sys
import traceback

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import pipeline components
from core_phase1.ingestion.loader import load_input
from core_phase1.extraction.parser import extract_parameters
from core_phase3.evaluation.evaluator import ParameterEvaluator
from core_phase3.main import Phase3RecommendationPipeline

app = FastAPI(title="Blood Report Analysis API", version="1.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Storage
reports_db: Dict[str, Dict[str, Any]] = {}
processing_status: Dict[str, Dict[str, Any]] = {}

class UploadResponse(BaseModel):
    reportId: str
    status: str
    message: str

class ReportStatus(BaseModel):
    reportId: str
    status: str
    progress: int
    message: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    return {"message": "Blood Report Analysis API", "version": "1.0.0"}

@app.post("/api/reports/upload", response_model=UploadResponse)
async def upload_report(file: UploadFile = File(...)):
    report_id = str(uuid.uuid4())
    
    upload_dir = "uploads"
    os.makedirs(upload_dir, exist_ok=True)
    file_path = os.path.join(upload_dir, f"{report_id}_{file.filename}")
    
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)
    
    processing_status[report_id] = {
        "reportId": report_id,
        "status": "processing",
        "progress": 0,
        "message": "Processing started"
    }
    
    asyncio.create_task(process_report(report_id, file_path))
    
    return UploadResponse(
        reportId=report_id,
        status="processing",
        message="File uploaded successfully"
    )

async def process_report(report_id: str, file_path: str):
    """Process blood report through the complete pipeline (Phases 1-3)"""
    try:
        print(f"\n{'='*70}")
        print(f"Processing report: {report_id}")
        print(f"File: {file_path}")
        print(f"{'='*70}")
        
        # Phase 1: Ingestion & Extraction
        processing_status[report_id]["progress"] = 20
        processing_status[report_id]["message"] = "Loading file..."
        await asyncio.sleep(0.1)
        
        print("Phase 1: Loading file...")
        raw_data = load_input(file_path)
        print(f"✓ Loaded {len(raw_data)} parameters")
        
        # Try to extract patient info from metadata (for PDFs)
        patient_info = {"sex": "F", "age": 19}  # Default values
        
        if '_metadata' in raw_data:
            metadata = raw_data.pop('_metadata')  # Remove metadata from parameters
            extracted_info = metadata.get('patient_info', {})
            if 'sex' in extracted_info:
                patient_info['sex'] = extracted_info['sex']
            if 'age' in extracted_info:
                patient_info['age'] = int(extracted_info['age'])
            print(f"✓ Extracted patient info: {patient_info}")
        
        processing_status[report_id]["progress"] = 40
        processing_status[report_id]["message"] = "Extracting parameters..."
        await asyncio.sleep(0.1)
        
        print("Phase 1: Extracting parameters...")
        extracted_data = extract_parameters(raw_data)
        print(f"✓ Extracted {len(extracted_data)} parameters")
        
        # Convert to list format for Phase 3
        extracted_parameters = [
            {"parameter": param, "value": data["value"], "unit": data.get("unit", "")}
            for param, data in extracted_data.items()
        ]
        
        # Phase 3: Evaluation & Recommendations
        processing_status[report_id]["progress"] = 60
        processing_status[report_id]["message"] = "Evaluating parameters..."
        await asyncio.sleep(0.1)
        
        print("Phase 3: Running evaluation pipeline...")
        pipeline = Phase3RecommendationPipeline()
        
        phase3_report = pipeline.process_extracted_parameters(
            extracted_parameters, 
            patient_info
        )
        print("✓ Phase 3 pipeline complete")
        
        processing_status[report_id]["progress"] = 80
        processing_status[report_id]["message"] = "Generating report..."
        await asyncio.sleep(0.1)
        
        print("Converting to API format...")
        # Convert pipeline output to API format
        report_data = convert_pipeline_to_api_format(
            report_id, 
            file_path, 
            phase3_report, 
            patient_info
        )
        print(f"✓ Report data generated with {len(report_data.get('parameters', []))} parameters")
        
        reports_db[report_id] = report_data
        
        processing_status[report_id]["status"] = "completed"
        processing_status[report_id]["progress"] = 100
        processing_status[report_id]["message"] = "Completed"
        
        print(f"✓ Report {report_id} processing complete")
        print(f"{'='*70}\n")
        
    except Exception as e:
        print(f"\n{'='*70}")
        print(f"ERROR processing report {report_id}: {str(e)}")
        print(traceback.format_exc())
        print(f"{'='*70}\n")
        processing_status[report_id]["status"] = "failed"
        processing_status[report_id]["error"] = str(e)

def convert_pipeline_to_api_format(
    report_id: str,
    file_path: str,
    phase3_report: Dict[str, Any],
    patient_info: Dict[str, Any]
) -> Dict[str, Any]:
    """Convert Phase 3 pipeline output to API response format"""
    
    # Extract evaluation results
    evaluations = phase3_report.get("phase_3a_evaluation", {}).get("evaluations", [])
    
    # Convert parameters to API format
    parameters = []
    for idx, eval_data in enumerate(evaluations):
        param_id = f"param{idx + 1}"
        
        # Map evaluation status to classification
        status = eval_data.get("status")
        if hasattr(status, 'value'):
            status_str = status.value
        else:
            status_str = str(status)
        
        # Map status to classification
        if "NORMAL" in status_str.upper():
            classification = "Normal"
        elif "HIGH" in status_str.upper() or "CRITICAL_HIGH" in status_str.upper():
            classification = "High"
        elif "LOW" in status_str.upper() or "CRITICAL_LOW" in status_str.upper():
            classification = "Low"
        else:
            classification = "Unknown"
        
        # Get reference range
        ref_range_str = eval_data.get("reference_range", "")
        
        # Try to parse the reference range string (format: "min-max unit")
        # Example: "0.8-2.0 ng/dL" or "3.5-12.5 mIU/mL"
        min_val = 0
        max_val = 0
        unit = eval_data.get("unit", "")
        
        if isinstance(ref_range_str, str) and ref_range_str:
            # Try to extract min-max from string like "0.8-2.0 ng/dL"
            import re
            match = re.match(r'(\d+\.?\d*)-(\d+\.?\d*)\s*(.+)?', ref_range_str)
            if match:
                min_val = float(match.group(1))
                max_val = float(match.group(2))
                if match.group(3):
                    unit = match.group(3).strip()
        
        reference_range = {
            "min": min_val,
            "max": max_val,
            "unit": unit,
            "sex": "All"
        }
        
        parameters.append({
            "id": param_id,
            "name": eval_data.get("parameter", "Unknown"),
            "value": eval_data.get("value", 0),
            "unit": eval_data.get("extracted_unit", ""),
            "classification": classification,
            "referenceRange": reference_range,
            "category": eval_data.get("category", "General"),
            "description": eval_data.get("interpretation", "")
        })
    
    # Extract health risk score
    risk_scoring = phase3_report.get("phase_3e_risk_scoring", {})
    risk_category = risk_scoring.get("risk_category", "moderate")
    
    # Map risk category to valid schema values (low, moderate, high, critical)
    # Ensure lowercase and handle any variations
    if isinstance(risk_category, str):
        risk_category_lower = risk_category.lower().strip()
        # Map variations to valid values
        if risk_category_lower in ['low', 'minimal', 'minor']:
            risk_level = 'low'
        elif risk_category_lower in ['moderate', 'medium', 'average']:
            risk_level = 'moderate'
        elif risk_category_lower in ['high', 'elevated', 'significant']:
            risk_level = 'high'
        elif risk_category_lower in ['critical', 'severe', 'very high', 'extreme']:
            risk_level = 'critical'
        else:
            risk_level = 'moderate'  # Default fallback
    else:
        risk_level = 'moderate'  # Default if not a string
    
    health_risk_score = {
        "overall": risk_scoring.get("total_score", 50),
        "cardiovascular": risk_scoring.get("cardiovascular_risk", {}).get("score", 50),
        "metabolic": risk_scoring.get("diabetes_risk", {}).get("score", 50),
        "kidney": risk_scoring.get("ckd_risk", {}).get("score", 50),
        "liver": 50,  # Default
        "level": risk_level
    }
    
    # Extract recommendations
    recommendations_data = phase3_report.get("phase_3c_recommendations", {})
    recommendations = []
    
    # Get recommendations from the enhanced recommendations
    detailed_guidance = recommendations_data.get("detailed_guidance", {})
    for idx, (condition, guidance) in enumerate(detailed_guidance.items()):
        rec_id = f"rec{idx + 1}"
        
        # Get diet recommendations
        diet_recs = guidance.get("diet_details", {}).get("recommendations", [])
        if diet_recs:
            recommendations.append({
                "id": f"{rec_id}_diet",
                "priority": "high",
                "category": "Diet",
                "title": f"Dietary Guidance for {condition}",
                "description": "; ".join(diet_recs[:3]),  # First 3 recommendations
                "relatedParameters": [],
                "actionable": True
            })
        
        # Get exercise recommendations
        exercise_plan = guidance.get("exercise_plan", {})
        if exercise_plan.get("recommendations"):
            recommendations.append({
                "id": f"{rec_id}_exercise",
                "priority": "medium",
                "category": "Exercise",
                "title": f"Exercise Plan for {condition}",
                "description": exercise_plan.get("recommendations", ["Regular physical activity"])[0],
                "relatedParameters": [],
                "actionable": True
            })
        
        # Get lifestyle recommendations
        lifestyle_recs = guidance.get("lifestyle_guidance", {}).get("recommendations", [])
        if lifestyle_recs:
            recommendations.append({
                "id": f"{rec_id}_lifestyle",
                "priority": "medium",
                "category": "Lifestyle",
                "title": f"Lifestyle Changes for {condition}",
                "description": lifestyle_recs[0] if lifestyle_recs else "Maintain healthy lifestyle",
                "relatedParameters": [],
                "actionable": True
            })
    
    # If no recommendations were generated, add general health recommendations
    if len(recommendations) == 0:
        print("⚠ No condition-specific recommendations found, generating general health recommendations")
        
        # Get abnormal parameters to tailor recommendations
        abnormal_params = []
        for eval_data in evaluations:
            status = eval_data.get("status")
            if hasattr(status, 'value'):
                status_str = status.value
            else:
                status_str = str(status)
            
            if "HIGH" in status_str.upper() or "LOW" in status_str.upper():
                abnormal_params.append({
                    "name": eval_data.get("parameter", "Unknown"),
                    "status": status_str
                })
        
        # General Diet Recommendations
        diet_desc = "Maintain a balanced diet rich in whole grains, lean proteins, fruits, and vegetables. "
        if any("Prolactin" in p["name"] or "LH" in p["name"] for p in abnormal_params):
            diet_desc += "Include foods rich in vitamin B6 (bananas, chickpeas, salmon) and zinc (nuts, seeds, legumes) to support hormonal balance. Avoid excessive caffeine and alcohol."
        else:
            diet_desc += "Limit processed foods, added sugars, and saturated fats. Stay hydrated with 8-10 glasses of water daily."
        
        recommendations.append({
            "id": "rec_diet_general",
            "priority": "high",
            "category": "Diet",
            "title": "Balanced Nutrition Plan",
            "description": diet_desc,
            "relatedParameters": [p["name"] for p in abnormal_params],
            "actionable": True
        })
        
        # General Exercise Recommendations
        exercise_desc = "Engage in at least 150 minutes of moderate-intensity aerobic activity per week. "
        if any("Prolactin" in p["name"] or "LH" in p["name"] for p in abnormal_params):
            exercise_desc += "Include stress-reducing activities like yoga, walking, or swimming. Avoid excessive high-intensity exercise which may affect hormone levels."
        else:
            exercise_desc += "Include strength training exercises 2-3 times per week. Take regular breaks from sitting every hour."
        
        recommendations.append({
            "id": "rec_exercise_general",
            "priority": "medium",
            "category": "Exercise",
            "title": "Physical Activity Guidelines",
            "description": exercise_desc,
            "relatedParameters": [p["name"] for p in abnormal_params],
            "actionable": True
        })
        
        # Sleep Recommendations
        sleep_desc = "Aim for 7-9 hours of quality sleep each night. Maintain a consistent sleep schedule by going to bed and waking up at the same time daily. "
        if any("Prolactin" in p["name"] for p in abnormal_params):
            sleep_desc += "Elevated prolactin can be affected by sleep patterns. Create a dark, cool sleeping environment and avoid screens 1 hour before bedtime."
        else:
            sleep_desc += "Create a relaxing bedtime routine. Avoid caffeine 6 hours before sleep and heavy meals 3 hours before bedtime."
        
        recommendations.append({
            "id": "rec_sleep_general",
            "priority": "high",
            "category": "Lifestyle",
            "title": "Sleep Hygiene",
            "description": sleep_desc,
            "relatedParameters": [p["name"] for p in abnormal_params],
            "actionable": True
        })
        
        # Stress Management
        stress_desc = "Practice stress management techniques such as meditation, deep breathing exercises, or mindfulness for 10-15 minutes daily. "
        if any("Prolactin" in p["name"] or "LH" in p["name"] for p in abnormal_params):
            stress_desc += "Chronic stress can significantly impact hormone levels. Consider activities like journaling, spending time in nature, or engaging in hobbies you enjoy."
        else:
            stress_desc += "Maintain social connections and seek support when needed. Consider professional counseling if stress becomes overwhelming."
        
        recommendations.append({
            "id": "rec_stress_general",
            "priority": "medium",
            "category": "Lifestyle",
            "title": "Stress Management",
            "description": stress_desc,
            "relatedParameters": [p["name"] for p in abnormal_params],
            "actionable": True
        })
        
        # Medical Follow-up
        if len(abnormal_params) > 0:
            followup_desc = f"You have {len(abnormal_params)} parameter(s) outside the normal range: {', '.join([p['name'] for p in abnormal_params])}. "
            followup_desc += "Schedule a follow-up appointment with your healthcare provider to discuss these results and determine if further testing or treatment is needed. "
            if any("Prolactin" in p["name"] for p in abnormal_params):
                followup_desc += "Elevated prolactin may require evaluation by an endocrinologist to rule out underlying causes."
            
            recommendations.append({
                "id": "rec_followup",
                "priority": "high",
                "category": "Medical",
                "title": "Medical Follow-up Required",
                "description": followup_desc,
                "relatedParameters": [p["name"] for p in abnormal_params],
                "actionable": True
            })
        
        print(f"✓ Generated {len(recommendations)} general health recommendations")
    
    # Calculate summary
    summary_data = phase3_report.get("phase_3a_evaluation", {}).get("summary", {})
    status_counts = summary_data.get("status_counts", {})
    
    summary = {
        "totalParameters": len(parameters),
        "normalCount": status_counts.get("normal", 0),
        "highCount": status_counts.get("high", 0) + status_counts.get("critical", 0),
        "lowCount": status_counts.get("low", 0),
        "unknownCount": status_counts.get("unknown", 0)
    }
    
    # Create final report
    return {
        "id": report_id,
        "reportDate": datetime.now().strftime("%Y-%m-%d"),
        "uploadDate": datetime.now().isoformat(),
        "patientId": "P12345",
        "patientName": "Test Patient",
        "patientAge": patient_info.get("age", 35),
        "patientSex": patient_info.get("sex", "M"),
        "parameters": parameters,
        "healthRiskScore": health_risk_score,
        "recommendations": recommendations,
        "summary": summary
    }

@app.get("/api/reports/{report_id}/status", response_model=ReportStatus)
async def get_report_status(report_id: str):
    if report_id not in processing_status:
        raise HTTPException(status_code=404, detail="Report not found")
    
    status = processing_status[report_id]
    return ReportStatus(
        reportId=status["reportId"],
        status=status["status"],
        progress=status["progress"],
        message=status.get("message"),
        error=status.get("error")
    )

@app.get("/api/reports/{report_id}")
async def get_report_data(report_id: str):
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="Report not found")
    
    response_data = {"report": reports_db[report_id]}
    
    # Debug logging
    print(f"\n{'='*70}")
    print(f"DEBUG: Returning report data for {report_id}")
    print(f"DEBUG: Response structure:")
    print(f"  - Has 'report' key: {('report' in response_data)}")
    print(f"  - Report has 'id': {('id' in response_data['report'])}")
    print(f"  - Report has 'parameters': {('parameters' in response_data['report'])}")
    print(f"  - Number of parameters: {len(response_data['report'].get('parameters', []))}")
    print(f"  - Report has 'healthRiskScore': {('healthRiskScore' in response_data['report'])}")
    print(f"  - Report has 'recommendations': {('recommendations' in response_data['report'])}")
    print(f"  - Number of recommendations: {len(response_data['report'].get('recommendations', []))}")
    print(f"  - Report has 'summary': {('summary' in response_data['report'])}")
    
    # Print first parameter as sample
    if response_data['report'].get('parameters'):
        print(f"\nSample parameter:")
        import json
        print(json.dumps(response_data['report']['parameters'][0], indent=2))
    
    print(f"{'='*70}\n")
    
    return response_data

@app.get("/api/reports/history")
async def get_report_history(page: int = 1, pageSize: int = 10):
    all_reports = list(reports_db.values())
    total = len(all_reports)
    start = (page - 1) * pageSize
    end = start + pageSize
    
    return {
        "items": all_reports[start:end],
        "total": total,
        "page": page,
        "pageSize": pageSize,
        "totalPages": (total + pageSize - 1) // pageSize
    }

@app.post("/api/reports/{report_id}/export")
async def export_report(report_id: str):
    if report_id not in reports_db:
        raise HTTPException(status_code=404, detail="Report not found")
    
    return {
        "downloadUrl": f"/downloads/{report_id}.pdf",
        "fileName": f"report_{report_id}.pdf",
        "fileSize": 1024000,
        "expiresAt": datetime.now().isoformat()
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
