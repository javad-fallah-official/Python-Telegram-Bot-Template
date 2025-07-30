#!/usr/bin/env python3
"""
Setup verification script for the Telegram Bot Template.
This script checks if the environment is properly configured.
"""

import sys
import os
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def check_environment():
    """Check if the environment is properly set up."""
    print("Checking environment setup...")
    
    # Check Python version
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"[OK] Python {python_version}")
    
    # Check required files
    required_files = [".env.example", "pyproject.toml"]
    for file in required_files:
        if Path(file).exists():
            print(f"[OK] {file} file found")
        else:
            print(f"[FAIL] {file} file missing")
            return False
    
    # Check .env file (optional but recommended)
    if Path(".env").exists():
        print("[OK] .env file found")
    else:
        print("[WARN] .env file not found (copy from .env.example)")
    
    return True


def test_imports():
    """Test that critical modules can be imported."""
    print("\nTesting imports...")
    
    modules = [
        "core.config",
        "core.logger", 
        "core.runner",
        "bot.factory",
        "main"
    ]
    
    for module in modules:
        try:
            __import__(module)
            print(f"[OK] {module}")
        except ImportError as e:
            print(f"[FAIL] {module}: {e}")
            assert False, f"Failed to import {module}: {e}"


def test_configuration():
    """Test that configuration loads correctly."""
    print("\nTesting configuration...")
    
    try:
        from core.config import Config
        print("[OK] Config loaded")
        
        # Check critical config values
        print(f"   - Bot mode: {getattr(Config, 'BOT_MODE', 'Not set')}")
        print(f"   - Debug: {getattr(Config, 'DEBUG', 'Not set')}")
        print(f"   - Database URL: {'Set' if getattr(Config, 'DATABASE_URL', None) else 'Not set'}")
        
        # Basic validation
        assert hasattr(Config, 'BOT_MODE'), "BOT_MODE not configured"
        assert hasattr(Config, 'DEBUG'), "DEBUG not configured"
        
    except Exception as e:
        print(f"[FAIL] Configuration error: {e}")
        assert False, f"Configuration failed: {e}"


def main():
    """Run all setup tests."""
    print("Telegram Bot Template - Setup Verification")
    print("=" * 50)
    
    tests = [
        ("Environment", check_environment),
        ("Imports", test_imports),
        ("Configuration", test_configuration)
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            # For functions that return None (assert-based), consider them passed
            if result is None:
                results.append(True)
            else:
                results.append(result)
        except AssertionError as e:
            print(f"[FAIL] {test_name} test failed: {e}")
            results.append(False)
        except Exception as e:
            print(f"[FAIL] {test_name} test failed: {e}")
            results.append(False)
    
    print("\n" + "=" * 50)
    if all(results):
        print("All tests passed! Your setup is ready.")
        print("\nNext steps:")
        print("1. Copy .env.example to .env and configure your BOT_TOKEN")
        print("2. Run: uv run python main.py")
        return True
    else:
        print("Some tests failed. Please fix the issues above.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)