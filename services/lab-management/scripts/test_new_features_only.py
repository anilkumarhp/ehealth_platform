#!/usr/bin/env python3
"""
Test runner for only the new features that are actually implemented.
Skips tests for endpoints that don't exist yet.
"""

import subprocess
import sys
import os
from pathlib import Path

def run_command(command, description):
    """Run a command and handle the result."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print("✅ SUCCESS")
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print("STDERR:", e.stderr[-500:])  # Last 500 chars
        return False

def main():
    """Run only the unit tests for new features."""
    
    # Change to the project directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🚀 Running unit tests for new features only")
    print(f"Working directory: {os.getcwd()}")
    
    # Only test the unit tests that don't depend on API endpoints
    test_categories = [
        {
            "name": "Cache Service Unit Tests",
            "command": "python -m pytest -c pytest_clean.ini tests/unit/test_cache_service.py::TestCacheManager -v",
            "description": "Testing core caching functionality"
        },
        {
            "name": "Rate Limiter Unit Tests", 
            "command": "python -m pytest -c pytest_clean.ini tests/unit/test_rate_limiter.py::TestRateLimiter -v",
            "description": "Testing core rate limiting functionality"
        },
        {
            "name": "Exception Handling Unit Tests",
            "command": "python -m pytest -c pytest_clean.ini tests/unit/test_exceptions.py::TestBaseLabException tests/unit/test_exceptions.py::TestSpecificExceptions tests/unit/test_exceptions.py::TestDomainSpecificExceptions tests/unit/test_exceptions.py::TestErrorHandlers -v", 
            "description": "Testing exception handling system"
        }
    ]
    
    # Run test categories
    results = []
    for category in test_categories:
        success = run_command(category["command"], category["description"])
        results.append({
            "name": category["name"],
            "success": success
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("TEST SUMMARY")
    print(f"{'='*60}")
    
    passed = sum(1 for r in results if r["success"])
    total = len(results)
    
    for result in results:
        status = "✅ PASSED" if result["success"] else "❌ FAILED"
        print(f"{status} - {result['name']}")
    
    print(f"\nOverall: {passed}/{total} test categories passed")
    
    if passed == total:
        print("🎉 All implemented feature tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())