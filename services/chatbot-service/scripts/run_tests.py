#!/usr/bin/env python3
import os
import sys
import subprocess
import argparse

def run_tests(test_type=None, coverage=False, verbose=False):
    """Run tests with pytest."""
    # Set up command
    cmd = ["pytest"]
    
    # Add test type
    if test_type == "unit":
        cmd.append("tests/unit")
    elif test_type == "integration":
        cmd.append("tests/integration")
    elif test_type == "llm":
        cmd.append("tests/llm-service")
    
    # Add coverage
    if coverage:
        cmd.extend(["--cov=app", "--cov-report=term", "--cov-report=html"])
    
    # Add verbose
    if verbose:
        cmd.append("-v")
    
    # Run tests
    result = subprocess.run(cmd)
    return result.returncode

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run tests for the chatbot service.")
    parser.add_argument(
        "--type", 
        choices=["unit", "integration", "llm", "all"], 
        default="all",
        help="Type of tests to run"
    )
    parser.add_argument(
        "--coverage", 
        action="store_true", 
        help="Generate coverage report"
    )
    parser.add_argument(
        "-v", "--verbose", 
        action="store_true", 
        help="Verbose output"
    )
    
    args = parser.parse_args()
    
    sys.exit(run_tests(args.type, args.coverage, args.verbose))