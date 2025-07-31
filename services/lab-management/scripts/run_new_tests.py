#!/usr/bin/env python3
"""
Test runner for new features and enhancements.
Runs all tests for newly implemented features.
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
        if result.stdout:
            print("STDOUT:", result.stdout[-500:])  # Last 500 chars
        return True
    except subprocess.CalledProcessError as e:
        print("❌ FAILED")
        print("STDERR:", e.stderr)
        if e.stdout:
            print("STDOUT:", e.stdout)
        return False

def main():
    """Run all new feature tests."""
    
    # Change to the project directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    print("🚀 Running tests for new features and enhancements")
    print(f"Working directory: {os.getcwd()}")
    
    # Test categories to run
    test_categories = [
        {
            "name": "File Management Integration Tests",
            "command": "python -m pytest tests/api/v1/test_files_integration.py -v",
            "description": "Testing file upload/download functionality"
        },
        {
            "name": "Analytics Integration Tests", 
            "command": "python -m pytest tests/api/v1/test_analytics_integration.py -v",
            "description": "Testing analytics and reporting endpoints"
        },
        {
            "name": "Search Integration Tests",
            "command": "python -m pytest tests/api/v1/test_search_integration.py -v", 
            "description": "Testing advanced search functionality"
        },
        {
            "name": "Health Check Integration Tests",
            "command": "python -m pytest tests/api/v1/test_health_integration.py -v",
            "description": "Testing health check and monitoring endpoints"
        },
        {
            "name": "Cache Service Unit Tests",
            "command": "python -m pytest tests/unit/test_cache_service.py -v",
            "description": "Testing caching functionality"
        },
        {
            "name": "Rate Limiter Unit Tests", 
            "command": "python -m pytest tests/unit/test_rate_limiter.py -v",
            "description": "Testing rate limiting functionality"
        },
        {
            "name": "Audit Service Unit Tests",
            "command": "python -m pytest tests/unit/test_audit_service.py -v",
            "description": "Testing audit logging functionality"
        },
        {
            "name": "Celery Tasks Unit Tests",
            "command": "python -m pytest tests/unit/test_celery_tasks.py -v",
            "description": "Testing background task functionality"
        },
        {
            "name": "Exception Handling Unit Tests",
            "command": "python -m pytest tests/unit/test_exceptions.py -v", 
            "description": "Testing exception handling system"
        }
    ]
    
    # Run all test categories
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
        print("🎉 All new feature tests passed!")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the output above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())