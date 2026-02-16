#!/usr/bin/env python3
"""
Test script to check agent orchestrator functionality.
"""

import sys
import os
import asyncio
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.agent.agent_orchestrator import MultiAgentOrchestrator

async def test_agent():
    """Test the multi-agent orchestrator."""
    print("Testing Multi-Agent Orchestrator...")
    print("=" * 50)

    # Sample medical parameters
    sample_params = {
        "hemoglobin": 12.5,
        "glucose": 95,
        "cholesterol": 220,
        "triglycerides": 150,
        "hdl": 45,
        "ldl": 140,
        "creatinine": 0.9,
        "urea": 35,
        "bilirubin": 0.8,
        "sgot": 25,
        "sgpt": 30,
        "alkaline_phosphatase": 80
    }

    # Initialize orchestrator
    orchestrator = MultiAgentOrchestrator()

    try:
        # Run analysis
        print("Running multi-agent analysis...")
        report = await orchestrator.execute(sample_params)

        print(f"Status: {report.status}")
        print(f"Parameters processed: {len(report.extracted_parameters)}")
        print(f"Interpretations: {len(report.interpretations)}")
        print(f"Risks identified: {len(report.risks)}")
        print(f"Recommendations: {len(report.recommendations)}")
        print(f"Prescriptions: {len(report.prescriptions)}")

        # Show agent results
        print("\nAgent Results:")
        for result in report.agent_results:
            status = "✓" if result.success else "✗"
            print(f"{status} {result.agent_name}: {result.execution_time:.2f}s")
            if result.error:
                print(f"  Error: {result.error}")

        # Show sample recommendations
        if report.recommendations:
            print("\nSample Recommendations:")
            for i, rec in enumerate(report.recommendations[:3]):
                print(f"{i+1}. {rec}")

    except Exception as e:
        print(f"Test failed: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\nTest completed.")

if __name__ == "__main__":
    asyncio.run(test_agent())
