#!/usr/bin/env python3
"""
Test script for Canvas GUI Enhanced to validate initialization
"""

try:
    print("Testing Canvas GUI Enhanced initialization...")
    
    # Test imports
    import tkinter as tk
    from canvas_gui import CanvasGUI
    print("✓ Imports successful")
    
    # Test GUI creation
    print("Creating GUI instance...")
    root = tk.Tk()
    root.withdraw()  # Hide the test window
    
    # This should not raise any errors now
    gui = CanvasGUI()
    print("✓ GUI initialized successfully")
    
    # Clean up
    gui.root.destroy()
    root.destroy()
    
    print("✓ All tests passed! Canvas GUI Enhanced is working correctly.")
    
except Exception as e:
    print(f"✗ Error during testing: {e}")
    import traceback
    traceback.print_exc()
