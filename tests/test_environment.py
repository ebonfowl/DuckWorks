"""
Quick Environment Test for DuckGrade Local Setup
Verifies that the local conda environment is properly configured
"""

import sys
import os
from pathlib import Path

def test_environment():
    """Test the local conda environment setup"""
    print("🦆 DuckGrade Local Environment Test")
    print("=" * 40)
    
    # Check Python path
    python_path = Path(sys.executable)
    print(f"Python executable: {python_path}")
    
    # Check if we're in the local environment
    if ".conda" in str(python_path):
        print("✅ Running in local conda environment")
    else:
        print("⚠️  Not running in local conda environment")
    
    # Test required imports
    required_packages = [
        ("PyQt6.QtWidgets", "PyQt6"),
        ("openai", "OpenAI"),
        ("docx", "python-docx"),
        ("openpyxl", "openpyxl"), 
        ("PyPDF2", "PyPDF2"),
        ("cryptography", "cryptography")
    ]
    
    print("\nPackage availability:")
    all_available = True
    
    for import_name, package_name in required_packages:
        try:
            __import__(import_name)
            print(f"✅ {package_name}")
        except ImportError:
            print(f"❌ {package_name} - Missing")
            all_available = False
    
    # Check duck icon
    icon_path = Path("assets/icons8-flying-duck-48.png")
    if icon_path.exists():
        print(f"✅ Duck icon found: {icon_path}")
    else:
        print(f"❌ Duck icon missing: {icon_path}")
        all_available = False
    
    print("\n" + "=" * 40)
    if all_available:
        print("🎉 Environment is ready for DuckGrade!")
        print("\n🚀 To launch DuckGrade:")
        print("• start_duckgrade.bat - Main launcher")
        print("• start_duckgrade_gui.bat - Local file interface")
        print("• start_duckgrade_canvas.bat - Canvas integration")
    else:
        print("⚠️  Some components are missing")
        
    return all_available

if __name__ == "__main__":
    test_environment()
