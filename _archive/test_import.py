#!/usr/bin/env python
"""Quick test to verify API imports"""
import sys
print("Testing imports...")
try:
    from src.api import app
    print("API imports successfully")
    print(f"App title: {app.title}")
    print("Project is ready to run!")
    sys.exit(0)
except Exception as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
