"""
Main entry point for running tests as a module
"""

import os
import sys
import pytest

if __name__ == "__main__":
    # Add parent directory to path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
    
    # Run pytest with arguments
    sys.exit(pytest.main(sys.argv[1:]))