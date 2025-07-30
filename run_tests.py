"""
Test runner script for easy test execution.

This script provides a simple interface to run different types of tests
with common configurations and reporting options.
"""

import sys
import subprocess
import argparse
from pathlib import Path


def run_command(cmd):
    """Run a command and return success status."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        
        if result.stderr and result.returncode != 0:
            print(f"[X] Error: {result.stderr}")
            return False
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"[X] Failed to run command: {e}")
        return False


def build_pytest_command(args):
    """Build pytest command based on arguments."""
    cmd = ["uv", "run", "pytest"]
    
    # Add test type specific paths
    if args.type == "unit":
        cmd.extend(["tests/test_core.py", "tests/test_bot.py", "tests/test_utils.py", "tests/test_services.py"])
    elif args.type == "integration":
        cmd.append("tests/test_integration.py")
    elif args.type == "core":
        cmd.append("tests/test_core.py")
    elif args.type == "bot":
        cmd.append("tests/test_bot.py")
    elif args.type == "utils":
        cmd.append("tests/test_utils.py")
    elif args.type == "services":
        cmd.append("tests/test_services.py")
    else:
        cmd.append("tests/")
    
    # Add verbosity
    if args.verbose:
        cmd.append("-v")
    elif args.fast:
        cmd.append("-q")
    
    # Add coverage
    if args.coverage:
        cmd.extend(["--cov=.", "--cov-report=html", "--cov-report=term"])
    
    return " ".join(cmd)


def main():
    """Main test runner function."""
    parser = argparse.ArgumentParser(description="Telegram Bot Template Test Runner")
    parser.add_argument(
        "--type", 
        choices=["all", "unit", "integration", "core", "bot", "utils", "services", "setup"],
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Run tests with verbose output"
    )
    parser.add_argument(
        "--coverage",
        action="store_true",
        help="Run tests with coverage reporting"
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Run tests with minimal output for quick feedback"
    )
    
    args = parser.parse_args()
    
    print("[ROCKET] Telegram Bot Template - Test Runner")
    print("=" * 50)
    print(f"Running: {args.type} tests")
    
    if args.type == "setup":
        print("[SEARCH] Setup Tests")
        print("=" * 50)
        success = run_command("uv run python tests/test_setup.py")
        if not success:
            return 1
    elif args.type == "all":
        print("[GEAR] All Tests")
        print("=" * 50)
        
        # Run setup verification first
        print("1. Setup verification...")
        if not run_command("uv run python tests/test_setup.py"):
            success = False
            print("\n[X] Setup verification failed. Please fix setup issues before running tests.")
            return 1
        
        print("\n2. Running pytest...")
        cmd = build_pytest_command(args)
        if not run_command(cmd):
            success = False
            return 1
    else:
        cmd = build_pytest_command(args)
        success = run_command(cmd)
        if not success:
            return 1
    
    print("\n[PARTY] All tests completed successfully!")
    
    if args.coverage:
        print("\n[CHART] Coverage report generated in htmlcov/index.html")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())