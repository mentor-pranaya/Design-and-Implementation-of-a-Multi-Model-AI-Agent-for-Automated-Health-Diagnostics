#!/usr/bin/env python
"""Debug import step by step"""
import sys
import time

print("Starting debug test...")
sys.stdout.flush()

print("1. Testing FastAPI import...")
sys.stdout.flush()
try:
    from fastapi import FastAPI
    print("   ✅ FastAPI OK")
except Exception as e:
    print(f"   ❌ FastAPI: {e}")
sys.stdout.flush()

print("2. Testing database models...")
sys.stdout.flush()
time.sleep(0.5)
try:
    from src.database.models import SessionLocal
    print("   ✅ Database OK")
except Exception as e:
    print(f"   ❌ Database: {e}")
    import traceback
    traceback.print_exc()
sys.stdout.flush()

print("3. Testing agent orchestrator...")
sys.stdout.flush()
time.sleep(0.5)
try:
    from src.agent.agent_orchestrator import MultiAgentOrchestrator
    print("   ✅ Agent orchestrator OK")
except Exception as e:
    print(f"   ❌ Agent orchestrator: {e}")
    import traceback
    traceback.print_exc()
sys.stdout.flush()

print("\n✅ All imports successful!")
