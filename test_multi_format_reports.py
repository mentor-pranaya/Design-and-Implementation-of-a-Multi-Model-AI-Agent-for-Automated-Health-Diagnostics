#!/usr/bin/env python3
"""
Test script to generate blood report analysis for different file formats using LLM.
Tests PDF, CSV, JSON, TXT, and image formats with the multi-agent system.
"""

import sys
import os
import asyncio
import json
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agent.agent_orchestrator import MultiAgentOrchestrator
from src.input_parser.pdf_parser import extract_text_from_pdf
from src.input_parser.image_parser import extract_text_with_fallback
from src.input_parser.csv_parser import extract_data_from_csv
from src.extraction.parameter_extractor import extract_parameters_from_text
from src.extraction.csv_parameter_mapper import extract_parameters_from_csv
from src.llm.multi_llm_service import get_multi_llm_service

class MockUploadFile:
    """Mock UploadFile for testing different formats."""
    def __init__(self, file_path):
        self.filename = os.path.basename(file_path)
        with open(file_path, 'rb') as f:
            self.file = f
            self.size = os.path.getsize(file_path)

def test_file_format(file_path, format_name):
    """Test a specific file format and return analysis results."""
    print(f"\n{'='*60}")
    print(f"TESTING {format_name.upper()} FORMAT: {os.path.basename(file_path)}")
    print('='*60)

    try:
        # Create mock file object
        mock_file = MockUploadFile(file_path)
        params = {}

        # Process based on file extension
        ext = Path(file_path).suffix.lower()

        if ext == '.pdf':
            text = extract_text_from_pdf(mock_file)
            params = extract_parameters_from_text(text)
            print(f"✓ PDF text extracted: {len(text)} characters")

        elif ext in ['.png', '.jpg', '.jpeg', '.tiff', '.tif', '.bmp']:
            text = extract_text_with_fallback(mock_file)
            params = extract_parameters_from_text(text)
            print(f"✓ Image OCR completed: {len(text)} characters")

        elif ext == '.csv':
            df = extract_data_from_csv(mock_file)
            params = extract_parameters_from_csv(df.to_csv().encode('utf-8'))
            print(f"✓ CSV processed: {len(df)} rows, {len(df.columns)} columns")

        elif ext == '.json':
            with open(file_path, 'r') as f:
                data = json.load(f)
            params = {k.lower(): v for k, v in data.items() if isinstance(v, (int, float))}
            print(f"✓ JSON loaded: {len(params)} parameters")

        elif ext == '.txt':
            with open(file_path, 'r') as f:
                text = f.read()
            params = extract_parameters_from_text(text)
            print(f"✓ TXT processed: {len(text)} characters")

        if not params:
            print(f"✗ No parameters extracted from {format_name}")
            return None

        print(f"✓ Extracted {len(params)} medical parameters:")
        for k, v in list(params.items())[:5]:  # Show first 5
            print(f"  - {k}: {v}")
        if len(params) > 5:
            print(f"  ... and {len(params)-5} more")

        # Run multi-agent analysis
        print("\n🤖 Running Multi-Agent Analysis...")
        orchestrator = MultiAgentOrchestrator()
        report = asyncio.run(orchestrator.execute(params))

        # Get LLM service info
        llm_service = get_multi_llm_service()
        llm_info = llm_service.get_provider_info()

        # Generate comprehensive report
        analysis_report = {
            "file_format": format_name,
            "filename": os.path.basename(file_path),
            "extraction_success": True,
            "parameters_extracted": len(params),
            "parameters": params,
            "interpretations": report.interpretations,
            "risks": report.risks,
            "ai_prediction": report.ai_prediction,
            "recommendations": report.recommendations,
            "prescriptions": report.prescriptions,
            "synthesis": report.synthesis,
            "overall_risk": "High" if any("high" in r.lower() for r in report.risks) else "Moderate",
            "llm_provider": llm_info.get("primary", "None"),
            "agent_performance": {
                "total_agents": len(report.agent_results),
                "successful": len([r for r in report.agent_results if r.success]),
                "execution_times": {r.agent_name: r.execution_time for r in report.agent_results}
            }
        }

        return analysis_report

    except Exception as e:
        print(f"✗ Error processing {format_name}: {str(e)}")
        import traceback
        traceback.print_exc()
        return {
            "file_format": format_name,
            "filename": os.path.basename(file_path),
            "extraction_success": False,
            "error": str(e)
        }

def generate_comprehensive_report(all_results):
    """Generate a comprehensive summary report."""
    print(f"\n{'='*80}")
    print("COMPREHENSIVE MULTI-FORMAT ANALYSIS REPORT")
    print('='*80)

    successful_formats = [r for r in all_results if r.get("extraction_success", False)]
    failed_formats = [r for r in all_results if not r.get("extraction_success", False)]

    print(f"\n📊 SUMMARY:")
    print(f"Total formats tested: {len(all_results)}")
    print(f"Successful extractions: {len(successful_formats)}")
    print(f"Failed extractions: {len(failed_formats)}")

    if successful_formats:
        print(f"\n✅ SUCCESSFUL FORMATS:")
        for result in successful_formats:
            print(f"\n🗂️  {result['file_format'].upper()}: {result['filename']}")
            print(f"   Parameters: {result['parameters_extracted']}")
            print(f"   Interpretations: {len(result['interpretations'])}")
            print(f"   Risks: {len(result['risks'])}")
            print(f"   Recommendations: {len(result['recommendations'])}")
            print(f"   LLM Provider: {result['llm_provider']}")
            print(f"   Overall Risk: {result['overall_risk']}")

            # Show sample interpretations
            if result['interpretations']:
                print("   Sample Interpretations:")
                for interp in result['interpretations'][:2]:
                    print(f"     • {interp}")

            # Show sample recommendations
            if result['recommendations']:
                print("   Sample LLM Recommendations:")
                for rec in result['recommendations'][:2]:
                    print(f"     • {rec}")

    if failed_formats:
        print(f"\n❌ FAILED FORMATS:")
        for result in failed_formats:
            print(f"   {result['file_format'].upper()}: {result.get('error', 'Unknown error')}")

    # LLM Performance Analysis
    llm_providers = {}
    for result in successful_formats:
        provider = result.get('llm_provider', 'None')
        llm_providers[provider] = llm_providers.get(provider, 0) + 1

    print(f"\n🤖 LLM PROVIDER USAGE:")
    for provider, count in llm_providers.items():
        print(f"   {provider}: {count} analyses")

    # Agent Performance Summary
    if successful_formats:
        total_agents = sum(r['agent_performance']['total_agents'] for r in successful_formats)
        successful_agents = sum(r['agent_performance']['successful'] for r in successful_formats)
        success_rate = (successful_agents / total_agents * 100) if total_agents > 0 else 0

        print(f"\n⚙️  AGENT PERFORMANCE:")
        print(f"   Total agent executions: {total_agents}")
        print(f"   Successful executions: {successful_agents}")
        print(f"   Success rate: {success_rate:.1f}%")

    print(f"\n{'='*80}")
    print("REPORT GENERATION COMPLETE")
    print('='*80)

def main():
    """Main test function."""
    print("🩺 BLOOD REPORT AI - MULTI-FORMAT ANALYSIS TEST")
    print("Testing LLM-powered analysis across different file formats")

    # Define test files
    test_files = [
        ("test_samples/standard_report.pdf", "PDF Document"),
        ("test_samples/anemic_high_cholesterol.csv", "CSV Spreadsheet"),
        ("test_samples/normal.json", "JSON Data"),
        ("test_samples/diabetic.txt", "Text File"),
        ("test_samples/critical_image.png", "Medical Image"),
    ]

    all_results = []

    for file_path, format_name in test_files:
        if os.path.exists(file_path):
            result = test_file_format(file_path, format_name)
            if result:
                all_results.append(result)
        else:
            print(f"\n⚠️  File not found: {file_path}")
            all_results.append({
                "file_format": format_name,
                "filename": os.path.basename(file_path),
                "extraction_success": False,
                "error": "File not found"
            })

    # Generate comprehensive report
    generate_comprehensive_report(all_results)

    # Save detailed results to JSON
    output_file = "multi_format_analysis_results.json"
    with open(output_file, 'w') as f:
        json.dump(all_results, f, indent=2, default=str)

    print(f"\n💾 Detailed results saved to: {output_file}")

if __name__ == "__main__":
    main()
