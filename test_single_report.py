"""
Test processing a single blood report to verify the pipeline works.
"""

import sys
import os
from pathlib import Path

# Add project paths
sys.path.append('core_phase1')
sys.path.append('core_phase2') 
sys.path.append('core_phase3')

def test_single_report():
    """Test processing one blood report."""
    
    print("=" * 80)
    print("TESTING SINGLE BLOOD REPORT")
    print("=" * 80)
    
    # Find the first PDF report
    test_dir = "data/test_reports"
    pdf_files = [f for f in os.listdir(test_dir) if f.endswith('.pdf')]
    
    if not pdf_files:
        print("❌ No PDF files found in test_reports directory")
        return False
    
    # Use the first PDF report
    test_report = os.path.join(test_dir, sorted(pdf_files)[0])
    print(f"Testing with: {test_report}")
    
    try:
        # Import and initialize orchestrator
        from core_phase3.orchestrator import MultiModelOrchestrator
        
        print("✅ Successfully imported MultiModelOrchestrator")
        
        # Initialize orchestrator
        orchestrator = MultiModelOrchestrator(verbose=True)
        print("✅ Successfully initialized orchestrator")
        
        # Process the report
        print(f"\nProcessing report: {os.path.basename(test_report)}")
        result = orchestrator.process_blood_report(test_report)
        
        print("✅ Successfully processed report!")
        print(f"Result keys: {list(result.keys()) if isinstance(result, dict) else 'Not a dict'}")
        
        # Save result for inspection
        import json
        with open("test_result.json", "w") as f:
            json.dump(result, f, indent=2, default=str)
        
        print("✅ Result saved to test_result.json")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all required modules are available")
        return False
        
    except Exception as e:
        print(f"❌ Processing error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_single_report()
    
    if success:
        print("\n🎉 Single report test PASSED!")
        print("✅ Your pipeline is working correctly")
        print("✅ Ready to run full evaluation on all reports")
    else:
        print("\n❌ Single report test FAILED")
        print("❌ Need to fix issues before running full evaluation")