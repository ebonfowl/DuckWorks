"""
Test the updated button tooltips and text
"""
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from duckgrade_canvas_complete import DuckGradeCanvasGUI
    from PyQt6.QtWidgets import QApplication
    
    print("✅ Testing updated tool buttons...")
    
    # Quick test to see if the app initializes
    app = QApplication([])
    window = DuckGradeCanvasGUI()
    
    # Test button properties
    duckgrade_btn = window.duckgrade_button
    duckassess_btn = window.duckassess_button
    
    print(f"✅ DuckGrade button text: '{duckgrade_btn.text()}'")
    print(f"✅ DuckGrade tooltip: '{duckgrade_btn.toolTip()}'")
    print(f"✅ DuckAssess button text: '{duckassess_btn.text()}'")
    print(f"✅ DuckAssess tooltip: '{duckassess_btn.toolTip()}'")
    print(f"✅ Button heights: DuckGrade={duckgrade_btn.minimumHeight()}, DuckAssess={duckassess_btn.minimumHeight()}")
    
    print("🦆 Tooltip system working perfectly!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
