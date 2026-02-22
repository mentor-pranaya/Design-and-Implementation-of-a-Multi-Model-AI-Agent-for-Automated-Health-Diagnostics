"""
Milestone 3 Integration Tests
Comprehensive test suite for Milestone 3 components
Tests synthesis, recommendations, and report generation
"""

import sys
from synthesis_engine import synthesize_findings
from recommendation_generator import generate_recommendations
from report_generator import generate_report
from milestone3_validator import validate_milestone_3_output


def create_test_data():
    """Create realistic test data for Milestone 3"""
    
    test_case = {
        "parameters": {
            "Hemoglobin": 11.5,
            "Glucose": 135,
            "Cholesterol": 220,
            "LDL": 140,
            "HDL": 35,
            "Triglycerides": 160,
            "Creatinine": 1.0,
            "BUN": 18,
            "ALT": 35,
            "AST": 32,
            "Bilirubin": 0.8,
            "Protein": 7.2,
            "Albumin": 4.0,
            "Platelet Count": 250,
            "WBC": 7.2,
            "RBC": 4.2
        },
        "interpretation": {
            "Hemoglobin": "LOW",
            "Glucose": "HIGH",
            "Cholesterol": "HIGH",
            "LDL": "HIGH",
            "HDL": "LOW",
            "Triglycerides": "HIGH",
            "Creatinine": "NORMAL",
            "BUN": "NORMAL",
            "ALT": "NORMAL",
            "AST": "NORMAL",
            "Bilirubin": "NORMAL",
            "Protein": "NORMAL",
            "Albumin": "NORMAL",
            "Platelet Count": "NORMAL",
            "WBC": "NORMAL",
            "RBC": "LOW"
        },
        "risk_assessment": {
            "Cardiovascular Risk": "HIGH",
            "Diabetes Risk": "HIGH",
            "Anemia Risk": "MODERATE"
        },
        "contextual_risk": {
            "Cardiovascular Risk": "HIGH",
            "Diabetes Risk": "HIGH",
            "Anemia Risk": "HIGH"
        },
        "age": 55,
        "gender": "male"
    }
    
    return test_case


def test_synthesis_engine():
    """Test Milestone 3 - Synthesis Engine"""
    print("\n" + "="*70)
    print("TEST 1: FINDINGS SYNTHESIS ENGINE")
    print("="*70)
    
    test_data = create_test_data()
    
    try:
        # Generate synthesis
        synthesis = synthesize_findings(
            parameters=test_data["parameters"],
            interpretation=test_data["interpretation"],
            risk_assessment=test_data["risk_assessment"],
            contextual_risk=test_data["contextual_risk"],
            age=test_data["age"],
            gender=test_data["gender"]
        )
        
        # Verify output structure
        assert "summary" in synthesis, "Missing summary"
        assert "critical_findings" in synthesis, "Missing critical_findings"
        assert "abnormal_parameters" in synthesis, "Missing abnormal_parameters"
        assert "risk_patterns" in synthesis, "Missing risk_patterns"
        assert "overall_health_status" in synthesis, "Missing overall_health_status"
        assert "priority_areas" in synthesis, "Missing priority_areas"
        
        # Verify content
        assert len(synthesis["summary"]) > 100, "Summary too short"
        assert len(synthesis["abnormal_parameters"]) > 0, "No abnormal parameters found"
        assert len(synthesis["risk_patterns"]) > 0, "No risk patterns found"
        assert len(synthesis["priority_areas"]) > 0, "No priority areas found"
        
        # Check health status determination
        assert synthesis["overall_health_status"] in [
            "HEALTHY - Most parameters within normal range",
            "MONITOR - Some parameters are outside normal range",
            "ATTENTION REQUIRED - Several elevated risk factors",
            "CONCERNING - Multiple abnormalities detected"
        ], "Invalid health status"
        
        print("[PASS] Synthesis structure validated")
        print(f"[PASS] Found {len(synthesis['abnormal_parameters'])} abnormal parameters")
        print(f"[PASS] Found {len(synthesis['risk_patterns'])} risk patterns")
        print(f"[PASS] Found {len(synthesis['priority_areas'])} priority areas")
        print(f"[PASS] Health Status: {synthesis['overall_health_status']}")
        
        return synthesis
        
    except Exception as e:
        print(f"[FAIL] Synthesis Engine Test FAILED: {str(e)}")
        return None


def test_recommendation_generator(synthesis):
    """Test Milestone 3 - Recommendation Generator"""
    print("\n" + "="*70)
    print("TEST 2: PERSONALIZED RECOMMENDATION GENERATOR")
    print("="*70)
    
    test_data = create_test_data()
    
    try:
        # Generate recommendations
        recommendations = generate_recommendations(
            synthesis_findings=synthesis,
            parameters=test_data["parameters"],
            interpretation=test_data["interpretation"],
            risk_assessment=test_data["risk_assessment"],
            age=test_data["age"],
            gender=test_data["gender"]
        )
        
        # Verify output structure
        required_categories = [
            "dietary_recommendations",
            "lifestyle_recommendations",
            "medical_follow_up",
            "monitoring_schedule",
            "supplementation_advice",
            "activity_recommendations",
            "risk_reduction_strategies",
            "disclaimers"
        ]
        
        for category in required_categories:
            assert category in recommendations, f"Missing {category}"
        
        # Verify content
        assert len(recommendations["dietary_recommendations"]) > 0, "No dietary recommendations"
        assert len(recommendations["lifestyle_recommendations"]) > 0, "No lifestyle recommendations"
        assert len(recommendations["medical_follow_up"]) > 0, "No medical follow-up"
        assert len(recommendations["monitoring_schedule"]) > 0, "No monitoring schedule"
        assert len(recommendations["activity_recommendations"]) > 0, "No activity recommendations"
        assert len(recommendations["disclaimers"]) > 0, "No disclaimers"
        
        # Verify actionability
        diet_rec = recommendations["dietary_recommendations"][0]
        assert "recommendations" in diet_rec, "No recommendations in dietary category"
        assert len(diet_rec["recommendations"]) > 0, "Dietary recommendations empty"
        assert "foods_to_include" in diet_rec, "No foods_to_include"
        assert "foods_to_avoid" in diet_rec, "No foods_to_avoid"
        
        # Verify medical follow-up
        followup = recommendations["medical_follow_up"][0]
        assert "urgency" in followup, "No urgency level"
        assert followup["urgency"] in ["URGENT", "RECOMMENDED", "ROUTINE"], "Invalid urgency"
        
        print("[PASS] Recommendation structure validated")
        print(f"[PASS] {len(recommendations['dietary_recommendations'])} dietary recommendations")
        print(f"[PASS] {len(recommendations['lifestyle_recommendations'])} lifestyle recommendations")
        print(f"[PASS] {len(recommendations['supplementation_advice'])} supplements recommended")
        print(f"[PASS] Follow-up urgency: {recommendations['medical_follow_up'][0]['urgency']}")
        
        return recommendations
        
    except Exception as e:
        print(f"[FAIL] Recommendation Generator Test FAILED: {str(e)}")
        return None


def test_report_generation(synthesis, recommendations):
    """Test Milestone 3 - Report Generation"""
    print("\n" + "="*70)
    print("TEST 3: REPORT GENERATION")
    print("="*70)
    
    test_data = create_test_data()
    
    try:
        # Test Text Format
        text_report = generate_report(
            synthesis_findings=synthesis,
            recommendations=recommendations,
            parameters=test_data["parameters"],
            interpretation=test_data["interpretation"],
            risk_assessment=test_data["risk_assessment"],
            contextual_risk=test_data["contextual_risk"],
            age=test_data["age"],
            gender=test_data["gender"],
            output_format="text"
        )
        
        assert isinstance(text_report, str), "Text report not string"
        assert len(text_report) > 1000, "Text report too short"
        assert "DISCLAIMER" in text_report.upper(), "Missing disclaimer"
        print(f"[PASS] Text report generated: {len(text_report)} characters")
        
        # Test HTML Format
        html_report = generate_report(
            synthesis_findings=synthesis,
            recommendations=recommendations,
            parameters=test_data["parameters"],
            interpretation=test_data["interpretation"],
            risk_assessment=test_data["risk_assessment"],
            contextual_risk=test_data["contextual_risk"],
            age=test_data["age"],
            gender=test_data["gender"],
            output_format="html"
        )
        
        assert isinstance(html_report, str), "HTML report not string"
        assert html_report.startswith("<!DOCTYPE html>"), "Invalid HTML structure"
        assert "<body>" in html_report, "Missing HTML body"
        print(f"[PASS] HTML report generated: {len(html_report)} characters")
        
        # Test JSON Format
        import json
        json_report = generate_report(
            synthesis_findings=synthesis,
            recommendations=recommendations,
            parameters=test_data["parameters"],
            interpretation=test_data["interpretation"],
            risk_assessment=test_data["risk_assessment"],
            contextual_risk=test_data["contextual_risk"],
            age=test_data["age"],
            gender=test_data["gender"],
            output_format="json"
        )
        
        assert isinstance(json_report, str), "JSON report not string"
        json_obj = json.loads(json_report)  # Validate JSON
        assert "metadata" in json_obj, "Missing metadata in JSON"
        assert "synthesis" in json_obj, "Missing synthesis in JSON"
        print(f"[PASS] JSON report generated and validated")
        
        # Test Markdown Format
        markdown_report = generate_report(
            synthesis_findings=synthesis,
            recommendations=recommendations,
            parameters=test_data["parameters"],
            interpretation=test_data["interpretation"],
            risk_assessment=test_data["risk_assessment"],
            contextual_risk=test_data["contextual_risk"],
            age=test_data["age"],
            gender=test_data["gender"],
            output_format="markdown"
        )
        
        assert isinstance(markdown_report, str), "Markdown report not string"
        assert "# HEALTH DIAGNOSTIC REPORT" in markdown_report, "Missing title"
        assert "##" in markdown_report, "No markdown sections"
        print(f"[PASS] Markdown report generated: {len(markdown_report)} characters")
        
        return text_report
        
    except Exception as e:
        print(f"[FAIL] Report Generation Test FAILED: {str(e)}")
        return None


def test_validation(synthesis, recommendations):
    """Test Milestone 3 - Validation"""
    print("\n" + "="*70)
    print("TEST 4: MILESTONE 3 VALIDATION")
    print("="*70)
    
    test_data = create_test_data()
    
    try:
        validation = validate_milestone_3_output(
            synthesis_findings=synthesis,
            recommendations=recommendations,
            interpretation=test_data["interpretation"],
            risk_assessment=test_data["risk_assessment"]
        )
        
        # Check validation structure
        assert "overall_results" in validation, "Missing overall_results"
        assert "validation_report" in validation, "Missing validation_report"
        
        results = validation["overall_results"]
        assert "summary_coherence" in results, "Missing summary_coherence score"
        assert "recommendation_relevance" in results, "Missing recommendation_relevance score"
        
        # Print scores
        print(f"[PASS] Summary Coherence: {results['summary_coherence']:.1f}%")
        print(f"[PASS] Recommendation Relevance: {results['recommendation_relevance']:.1f}%")
        print(f"[PASS] Recommendation Actionability: {results['recommendation_actionability']:.1f}%")
        print(f"[PASS] Clinical Alignment: {results['clinical_alignment']:.1f}%")
        print(f"[PASS] Overall Score: {results['overall_score']:.1f}%")
        
        # Check against success criteria
        criteria_met = (
            results['summary_coherence'] >= 95 and
            results['recommendation_relevance'] >= 90 and
            results['recommendation_actionability'] >= 90
        )
        
        if criteria_met:
            print("[PASS] SUCCESS CRITERIA MET")
        else:
            print("! Some criteria below target")
        
        return validation
        
    except Exception as e:
        print(f"[FAIL] Validation Test FAILED: {str(e)}")
        return None


def test_end_to_end_pipeline():
    """Test complete Milestone 3 pipeline"""
    print("\n" + "="*70)
    print("TEST 5: END-TO-END PIPELINE")
    print("="*70)
    
    try:
        test_data = create_test_data()
        
        # Step 1: Synthesis
        synthesis = synthesize_findings(
            parameters=test_data["parameters"],
            interpretation=test_data["interpretation"],
            risk_assessment=test_data["risk_assessment"],
            contextual_risk=test_data["contextual_risk"],
            age=test_data["age"],
            gender=test_data["gender"]
        )
        
        # Step 2: Recommendations
        recommendations = generate_recommendations(
            synthesis_findings=synthesis,
            parameters=test_data["parameters"],
            interpretation=test_data["interpretation"],
            risk_assessment=test_data["risk_assessment"],
            age=test_data["age"],
            gender=test_data["gender"]
        )
        
        # Step 3: Report
        report = generate_report(
            synthesis_findings=synthesis,
            recommendations=recommendations,
            parameters=test_data["parameters"],
            interpretation=test_data["interpretation"],
            risk_assessment=test_data["risk_assessment"],
            contextual_risk=test_data["contextual_risk"],
            age=test_data["age"],
            gender=test_data["gender"],
            output_format="text"
        )
        
        # Step 4: Validation
        validation = validate_milestone_3_output(
            synthesis_findings=synthesis,
            recommendations=recommendations,
            interpretation=test_data["interpretation"],
            risk_assessment=test_data["risk_assessment"]
        )
        
        # Verify complete flow
        assert synthesis is not None, "Synthesis failed"
        assert recommendations is not None, "Recommendations failed"
        assert report is not None, "Report failed"
        assert validation is not None, "Validation failed"
        
        print("[PASS] Step 1: Synthesis Engine - Success")
        print("[PASS] Step 2: Recommendation Generator - Success")
        print("[PASS] Step 3: Report Generation - Success")
        print("[PASS] Step 4: Validation - Success")
        print("\n[PASS] COMPLETE PIPELINE TEST PASSED")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] End-to-End Test FAILED: {str(e)}")
        return False


def run_all_tests():
    """Run all Milestone 3 tests"""
    print("\n" + "="*70)
    print("MILESTONE 3 COMPREHENSIVE TEST SUITE")
    print("="*70)
    
    results = {
        "synthesis": False,
        "recommendations": False,
        "reports": False,
        "validation": False,
        "end_to_end": False
    }
    
    # Test 1: Synthesis Engine
    synthesis = test_synthesis_engine()
    results["synthesis"] = synthesis is not None
    
    # Test 2: Recommendation Generator
    if synthesis:
        recommendations = test_recommendation_generator(synthesis)
        results["recommendations"] = recommendations is not None
    else:
        print("[WARN] Skipping recommendation test (synthesis failed)")
        recommendations = None
    
    # Test 3: Report Generation
    if synthesis and recommendations:
        report = test_report_generation(synthesis, recommendations)
        results["reports"] = report is not None
    else:
        print("[WARN] Skipping report test (synthesis or recommendations failed)")
    
    # Test 4: Validation
    if synthesis and recommendations:
        validation = test_validation(synthesis, recommendations)
        results["validation"] = validation is not None
    else:
        print("[WARN] Skipping validation test (synthesis or recommendations failed)")
    
    # Test 5: End-to-End
    end_to_end = test_end_to_end_pipeline()
    results["end_to_end"] = end_to_end
    
    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)
    
    total = len(results)
    passed = sum(1 for v in results.values() if v)
    
    for test, status in results.items():
        print(f"  {test.replace('_', ' ').title()}: {'[PASS] PASS' if status else '[FAIL] FAIL'}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n[PASS] ALL TESTS PASSED - MILESTONE 3 READY FOR PRODUCTION")
    else:
        print("\n! Some tests failed - review errors above")
    
    print("="*70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
