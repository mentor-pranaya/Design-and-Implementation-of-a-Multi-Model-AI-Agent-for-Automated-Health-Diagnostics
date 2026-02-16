import sys
import traceback

try:
    print("Attempting to import MultiAgentOrchestrator...")
    from src.agent.agent_orchestrator import MultiAgentOrchestrator
    print("Import successful!")
except Exception:
    with open("import_error.log", "w") as f:
        traceback.print_exc(file=f)
    print("Import failed. Traceback written to import_error.log")
