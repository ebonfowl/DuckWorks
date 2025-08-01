"""
Quick test script to verify the DuckWorks GUI loads correctly
"""
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from duckgrade_canvas_complete import DuckGradeCanvasGUI
    from PyQt6.QtWidgets import QApplication
    
    print("✅ All imports successful")
    print("✅ GUI classes loaded successfully")
    
    # Quick test to see if the app initializes
    app = QApplication([])
    window = DuckGradeCanvasGUI()
    print("✅ GUI window created successfully")
    print("✅ Multi-tool interface is ready!")
    print(f"✅ Current tool tabs: {window.tab_widget.count()}")
    
    # Don't show the window, just verify it loads
    print("🦆 DuckWorks Educational Suite - Ready for testing!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
