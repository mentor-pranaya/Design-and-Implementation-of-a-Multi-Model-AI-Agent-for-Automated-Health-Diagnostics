#!/usr/bin/env python3
"""
Simple setup and launch script for INBLOODO AGENT
Handles venv setup, dependency installation, and server startup
"""
import subprocess
import sys
import os
from pathlib import Path

def run_command(cmd, description=""):
    """Run a shell command and handle output"""
    if description:
        print(f"\n{'='*60}")
        print(f"  {description}")
        print(f"{'='*60}")
    
    try:
        result = subprocess.run(cmd, shell=True, capture_output=False, text=True, cwd=os.getcwd())
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    print("\n" + "="*60)
    print("         INBLOODO AGENT - Setup & Launch Server")
    print("="*60 + "\n")
    
    # Step 1: Verify Python
    print("[OK] Verifying Python installation...")
    result = subprocess.run([sys.executable, "--version"], capture_output=True, text=True)
    print(f"  {result.stdout.strip()}")
    
    # Step 2: Create/verify venv
    venv_path = Path("venv")
    if not venv_path.exists():
        print("\n[OK] Creating virtual environment...")
        if not run_command(f'"{sys.executable}" -m venv venv'):
            print("❌ Failed to create venv")
            return False
    else:
        print("\n[OK] Virtual environment exists")
    
    # Step 3: Get pip path
    if sys.platform == "win32":
        pip_exe = venv_path / "Scripts" / "pip.exe"
        python_exe = venv_path / "Scripts" / "python.exe"
    else:
        pip_exe = venv_path / "bin" / "pip"
        python_exe = venv_path / "bin" / "python"
    
    # Step 4: Upgrade pip
    print("\n[OK] Upgrading pip...")
    run_command(f'"{python_exe}" -m pip install --upgrade pip --quiet')
    
    # Step 5: Install requirements
    print("\n[OK] Installing dependencies...")
    req_file = "requirements.txt"
    if Path(req_file).exists():
        if not run_command(f'"{python_exe}" -m pip install -r {req_file} --quiet'):
            print("⚠ Warning: Some dependencies failed to install")
    else:
        print("  Installing minimal requirements (requirements.txt not found)...")
        run_command(f'"{python_exe}" -m pip install fastapi uvicorn sqlalchemy pydantic --quiet')
    
    # Step 6: Start server
    print("\n" + "="*60)
    print("  Starting FastAPI Server...")
    print("="*60)
    print("\n[OK] Server starting on http://0.0.0.0:10000")
    print("[OK] Access at: http://localhost:10000")
    print("\n[DOCS] API Documentation: http://localhost:10000/docs")
    print("[HEALTH] Health Check: http://localhost:10000/health")
    print("\n[STOP] Press Ctrl+C to stop the server\n")
    
    # Run server
    server_cmd = f'"{python_exe}" -m uvicorn src.api:app --host 0.0.0.0 --port 10000 --reload'
    subprocess.run(server_cmd, shell=True)

if __name__ == "__main__":
    main()
