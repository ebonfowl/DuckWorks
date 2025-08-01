#!/usr/bin/env python3
"""
Test script for Review Tab functionality
"""

import sys
import os
from pathlib import Path

# Test imports
try:
    from PyQt6.QtWidgets import QApplication
    print("✓ PyQt6 available")
except ImportError as e:
    print(f"✗ PyQt6 not available: {e}")
    sys.exit(1)

try:
    import pandas as pd
    print("✓ pandas available")
except ImportError as e:
    print(f"✗ pandas not available: {e}")
    sys.exit(1)

try:
    import openpyxl
    print("✓ openpyxl available")
except ImportError as e:
    print(f"✗ openpyxl not available: {e}")
    sys.exit(1)

# Test basic Review Tab creation
def test_review_tab_creation():
    """Test if Review Tab can be created without errors"""
    app = QApplication(sys.argv)
    
    try:
        # Import the main class
        from duckgrade_canvas_complete import DuckGradeCanvasGUI
        
        # Create main window
        window = DuckGradeCanvasGUI()
        
        # Test that Review Tab attributes exist
        assert hasattr(window, 'review_tab_visible'), "Missing review_tab_visible attribute"
        assert hasattr(window, 'create_review_tab'), "Missing create_review_tab method"
        assert hasattr(window, 'show_review_tab'), "Missing show_review_tab method"
        assert hasattr(window, 'hide_review_tab'), "Missing hide_review_tab method"
        
        print("✓ Review Tab methods and attributes present")
        
        # Test that review tab is initially not visible
        assert window.review_tab_visible == False, "Review tab should not be visible initially"
        print("✓ Review Tab initial state correct")
        
        return True
        
    except Exception as e:
        print(f"✗ Review Tab creation test failed: {e}")
        return False
    finally:
        app.quit()

if __name__ == "__main__":
    print("Testing Review Tab implementation...")
    
    if test_review_tab_creation():
        print("\n🎉 All Review Tab tests passed!")
    else:
        print("\n❌ Review Tab tests failed!")
        sys.exit(1)
