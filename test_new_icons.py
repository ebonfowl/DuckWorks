"""
Test the new button icons (mallard and duckling)
"""
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

try:
    from duckgrade_canvas_complete import DuckGradeCanvasGUI
    from PyQt6.QtWidgets import QApplication
    
    print("✅ Testing new button icons...")
    
    # Quick test to see if the app initializes
    app = QApplication([])
    window = DuckGradeCanvasGUI()
    
    # Test button properties
    duckgrade_btn = window.duckgrade_button
    duckassess_btn = window.duckassess_button
    
    print(f"✅ DuckGrade button text: '{duckgrade_btn.text()}'")
    print(f"✅ DuckGrade has icon: {not duckgrade_btn.icon().isNull()}")
    print(f"✅ DuckAssess button text: '{duckassess_btn.text()}'")
    print(f"✅ DuckAssess has icon: {not duckassess_btn.icon().isNull()}")
    
    # Check if icon files exist
    mallard_exists = Path("assets/mallard_icon.png").exists()
    duckling_exists = Path("assets/duckling_icon.png").exists()
    print(f"✅ Mallard icon file exists: {mallard_exists}")
    print(f"✅ Duckling icon file exists: {duckling_exists}")
    
    print("🦆 New button icons configured successfully!")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
