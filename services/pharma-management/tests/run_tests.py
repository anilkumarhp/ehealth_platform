#!/usr/bin/env python
"""
Test runner script for pharma management service
"""

import os
import sys
import pytest

def run_tests():
    """Run tests with specified arguments."""
    args = [
        "--cov=app",
        "--cov-report=term-missing",
        "--cov-report=html:coverage_html",
        "-v"
    ]
    
    # Add any command line arguments
    if len(sys.argv) > 1:
        args.extend(sys.argv[1:])
    
    # Run pytest with arguments
    return pytest.main(args)

if __name__ == "__main__":
    # Ensure we're in the correct directory
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    
    # Run tests
    exit_code = run_tests()
    sys.exit(exit_code)