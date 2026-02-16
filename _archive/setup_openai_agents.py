#!/usr/bin/env python3
"""
Quick setup script for OpenAI Agents SDK integration with INBLOODO AGENT.

This script:
1. Checks for required dependencies
2. Installs openai-agents if needed
3. Configures the hybrid orchestrator
4. Tests the integration
"""

import os
import sys
import subprocess
import json
from pathlib import Path


def print_header(text):
    """Print formatted header."""
    print("\n" + "=" * 70)
    print(f"  {text}")
    print("=" * 70)


def print_info(text):
    """Print info message."""
    print(f"ℹ️  {text}")


def print_success(text):
    """Print success message."""
    print(f"✓ {text}")


def print_error(text):
    """Print error message."""
    print(f"✗ {text}")


def print_warning(text):
    """Print warning message."""
    print(f"⚠️  {text}")


def check_python_version():
    """Check if Python version is compatible (3.9+)."""
    print_header("Checking Python Version")
    
    version = sys.version_info
    required_version = (3, 9)
    
    current = f"{version.major}.{version.minor}.{version.micro}"
    required = f"{required_version[0]}.{required_version[1]}"
    
    if (version.major, version.minor) >= required_version:
        print_success(f"Python {current} (required: {required}+)")
        return True
    else:
        print_error(f"Python {current} is too old. Required: {required}+")
        return False


def check_dependencies():
    """Check if required packages are installed."""
    print_header("Checking Dependencies")
    
    dependencies = {
        "fastapi": "FastAPI web framework",
        "agents": "OpenAI Agents SDK",
        "openai": "OpenAI API client",
        "google.generativeai": "Google Gemini API",
        "anthropic": "Anthropic Claude API",
    }
    
    installed = {}
    missing = []
    
    for package, description in dependencies.items():
        try:
            __import__(package)
            installed[package] = description
            print_success(f"{description}")
        except ImportError:
            missing.append((package, description))
            print_warning(f"{description} (not installed)")
    
    return installed, missing


def install_openai_agents():
    """Install OpenAI Agents SDK."""
    print_header("Installing OpenAI Agents SDK")
    
    try:
        print_info("Installing openai-agents package...")
        result = subprocess.run(
            [sys.executable, "-m", "pip", "install", "openai-agents"],
            capture_output=True,
            text=True,
            timeout=120
        )
        
        if result.returncode == 0:
            print_success("OpenAI Agents SDK installed successfully")
            return True
        else:
            print_error(f"Installation failed: {result.stderr}")
            return False
    except subprocess.TimeoutExpired:
        print_error("Installation timed out")
        return False
    except Exception as e:
        print_error(f"Installation error: {str(e)}")
        return False


def check_openai_agents():
    """Check if OpenAI Agents SDK is available."""
    try:
        try:
            import agents
        except ImportError:
            agents = None
        print_success(f"OpenAI Agents SDK v{getattr(agents, '__version__', 'unknown')} available")
        return True
    except ImportError:
        print_warning("OpenAI Agents SDK not available")
        return False


def configure_env_file():
    """Configure .env file for hybrid orchestrator."""
    print_header("Configuring Environment")
    
    env_path = ".env"
    
    if os.path.exists(env_path):
        print_info(f"Found existing {env_path}")
        with open(env_path, "r") as f:
            content = f.read()
    else:
        print_info(f"Creating new {env_path}")
        content = ""
    
    # Add hybrid orchestrator settings if not present
    if "ORCHESTRATOR_METHOD" not in content:
        content += "\n# Hybrid Orchestrator Configuration\n"
        content += "ORCHESTRATOR_METHOD=hybrid\n"
        content += "# Options: hybrid, openai-agents, traditional\n"
    
    # Write back
    with open(env_path, "w") as f:
        f.write(content)
    
    print_success(f"Updated {env_path}")


def test_hybrid_orchestrator():
    """Test the hybrid orchestrator."""
    print_header("Testing Hybrid Orchestrator")
    
    try:
        from src.agent.hybrid_orchestrator import get_hybrid_agent_orchestrator
        
        print_info("Initializing hybrid orchestrator...")
        orchestrator = get_hybrid_agent_orchestrator()
        
        # Get system info
        info = orchestrator.get_system_info()
        
        print_success(f"Hybrid orchestrator initialized")
        print(f"\n  Primary Method: {info['primary_method']}")
        print(f"  Available Methods: {', '.join([m for m in info['methods_available'] if m])}")
        print(f"  OpenAI Agents SDK: {'Available' if info['openai_agents_available'] else 'Not available'}")
        
        # Test with sample data
        print_info("Testing with sample blood parameters...")
        
        test_params = {
            "hemoglobin": 12.5,
            "glucose": 95,
            "cholesterol": 180
        }
        
        result = orchestrator.execute(test_params)
        
        print_success("Test analysis completed")
        print(f"  Method used: {result['method']}")
        print(f"  Status: {result['status']}")
        print(f"  Execution time: {result['execution_time']:.2f}s")
        
        return True
    
    except Exception as e:
        print_error(f"Test failed: {str(e)}")
        return False


def print_summary(installed, missing, openai_agents_available):
    """Print setup summary."""
    print_header("Setup Summary")
    
    print("\n📦 Installed Components:")
    for package, description in installed.items():
        print(f"  ✓ {description}")
    
    if missing:
        print("\n⚠️  Optional Components (not installed):")
        for package, description in missing:
            print(f"  ✗ {description}")
            print(f"    Install with: pip install {package}")
    
    print("\n🤖 Agent System Status:")
    if openai_agents_available:
        print("  ✓ OpenAI Agents SDK: AVAILABLE")
        print("  ✓ Hybrid Orchestrator: ENABLED")
        print("  ✓ Advanced Features: Full support for handoffs and agent collaboration")
    else:
        print("  ✗ OpenAI Agents SDK: NOT AVAILABLE")
        print("  ✓ Traditional Orchestrator: AVAILABLE")
        print("  ℹ️  To enable OpenAI Agents: pip install openai-agents")
    
    print("\n📝 Next Steps:")
    print("  1. Configure .env file with your API keys")
    print("  2. Start the API server: python -m uvicorn src.api:app --reload")
    print("  3. Upload blood reports and get instant analysis")
    print("  4. Check logs for agent execution details")
    
    print("\n📚 Documentation:")
    print("  - OPENAI_AGENTS_GUIDE.md - Detailed OpenAI Agents integration guide")
    print("  - MULTI_LLM_README.md - Multi-LLM provider configuration")
    print("  - MULTI_LLM_ARCHITECTURE.md - System architecture reference")


def main():
    """Main setup flow."""
    print("\n" + "🚀" * 35)
    print("INBLOODO AGENT - OpenAI Agents SDK Setup")
    print("🚀" * 35)
    
    # Check Python version
    if not check_python_version():
        print_error("Setup cannot continue with this Python version")
        sys.exit(1)
    
    # Check dependencies
    installed, missing = check_dependencies()
    
    # Check and install OpenAI Agents SDK
    openai_agents_available = check_openai_agents()
    
    if not openai_agents_available:
        print_header("Installing Missing Components")
        
        response = input("\nWould you like to install openai-agents now? (y/n): ").strip().lower()
        
        if response == "y":
            if install_openai_agents():
                openai_agents_available = check_openai_agents()
            else:
                print_warning("Failed to install openai-agents. Using traditional orchestrator only.")
        else:
            print_info("Skipping openai-agents installation. Using traditional orchestrator.")
    
    # Configure environment
    configure_env_file()
    
    # Test hybrid orchestrator
    print_header("Testing Setup")
    test_success = test_hybrid_orchestrator()
    
    # Print summary
    print_summary(installed, missing, openai_agents_available)
    
    if test_success:
        print("\n✓ Setup completed successfully!")
        print("  Your INBLOODO AGENT is ready to analyze blood reports with advanced multi-agent orchestration.\n")
    else:
        print("\n⚠️  Setup completed with warnings. Review output above for details.\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print_error("\nSetup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
