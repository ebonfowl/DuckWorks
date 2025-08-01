# DuckGrade PyQt6 Launch Instructions

## ⭐ **RECOMMENDED - Quick Start (Direct Method)**
Use the **_direct.bat** files that bypass conda activation issues:
- `start_duckgrade_direct.bat` - Main launcher menu
- `start_duckgrade_gui_direct.bat` - Local file grading
- `start_duckgrade_canvas_direct.bat` - Canvas integration

## Individual Launchers

### 🎯 **Direct Method (RECOMMENDED)**
- **Local File Grading**: `start_duckgrade_gui_direct.bat`
- **Canvas Integration**: `start_duckgrade_canvas_direct.bat`
- **Main Launcher**: `start_duckgrade_direct.bat`
- ✅ **Advantage**: Bypasses conda activation issues, works immediately

### 🔧 **Conda Method (Alternative)**
- **Local File Grading**: `start_duckgrade_gui.bat`
- **Canvas Integration**: `start_duckgrade_canvas.bat`
- **Main Launcher**: `start_duckgrade.bat`
- ⚠️ **Note**: Requires `conda init cmd.exe` to be run first

## Environment Setup
Both methods use the **local conda environment**:
- Environment path: `d:\College of Idaho\GradingAgent\.conda`
- All required packages are pre-installed
- Isolated from your base Anaconda installation

## Icon Usage
All interfaces use your professional duck icon (`assets/icons8-flying-duck-48.png`) instead of emoji characters.

## Requirements (Pre-installed in Local Environment)
- ✅ PyQt6
- ✅ openai
- ✅ python-docx
- ✅ openpyxl
- ✅ PyPDF2
- ✅ cryptography

## Troubleshooting
If conda method fails, use the **direct method** instead:
1. The direct method calls `.conda\python.exe` directly
2. No conda activation required
3. Works immediately after environment setup

## Testing
Run `tests/test_environment.py` to verify everything is working correctly.

🦆 Part of DuckWorks Educational Automation Suite - Using Local Environment
