#!/usr/bin/env python
"""
Test runner script with common test execution patterns
Run: python run_tests.py [options]
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors"""
    print(f"\n{'='*60}")
    print(f"📋 {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd)
    if result.returncode != 0:
        print(f"❌ {description} failed!")
        return False
    else:
        print(f"✅ {description} succeeded!")
        return True


def main():
    """Main test runner"""
    import argparse
    
    parser = argparse.ArgumentParser(description="URL Shortener Test Runner")
    parser.add_argument(
        "--mode",
        choices=["quick", "full", "coverage", "watch", "specific"],
        default="full",
        help="Test execution mode"
    )
    parser.add_argument(
        "--test",
        help="Specific test file or test to run (with --mode=specific)"
    )
    parser.add_argument(
        "--markers",
        help="Run tests with specific markers (e.g., 'auth', 'url', 'security')"
    )
    parser.add_argument(
        "--verbose",
        "-v",
        action="store_true",
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    # Base command
    cmd_base = [sys.executable, "-m", "pytest"]
    
    if args.mode == "quick":
        # Fast tests only
        cmd = cmd_base + ["tests/", "-x", "-v"]
        description = "Running quick tests"
    
    elif args.mode == "full":
        # All tests
        cmd = cmd_base + ["tests/", "-v", "--tb=short"]
        description = "Running full test suite"
    
    elif args.mode == "coverage":
        # With coverage report
        cmd = cmd_base + [
            "tests/",
            "-v",
            "--cov=app",
            "--cov-report=html",
            "--cov-report=term-missing"
        ]
        description = "Running tests with coverage report"
    
    elif args.mode == "watch":
        # Watch mode (requires pytest-watch)
        try:
            import pytest_watch
        except ImportError:
            print("❌ pytest-watch not installed. Install with: pip install pytest-watch")
            return 1
        cmd = [sys.executable, "-m", "pytest_watch", "tests/", "-v"]
        description = "Running tests in watch mode"
    
    elif args.mode == "specific":
        if not args.test:
            print("❌ --test parameter required for --mode=specific")
            return 1
        cmd = cmd_base + [args.test, "-v"]
        description = f"Running specific test: {args.test}"
    
    # Add markers if specified
    if args.markers:
        cmd.extend(["-m", args.markers])
        description += f" (markers: {args.markers})"
    
    # Add verbosity
    if args.verbose:
        cmd.append("-vv")
    
    # Run tests
    success = run_command(cmd, description)
    
    # Print summary
    print(f"\n{'='*60}")
    if success:
        print("✨ All tests passed!")
        print(f"{'='*60}\n")
        return 0
    else:
        print("⚠️ Some tests failed. Check output above.")
        print(f"{'='*60}\n")
        return 1


if __name__ == "__main__":
    sys.exit(main())
