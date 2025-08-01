@echo off
title DuckGrade - Canvas Integration (Direct)
echo 🦆 Starting DuckGrade Canvas Integration (PyQt6)
echo ===============================================
echo.
echo Using local Python environment directly...
echo.

REM Check if local Python exists
if not exist ".conda\python.exe" (
    echo ❌ Local Python environment not found at .conda\python.exe
    echo Please ensure the local conda environment is set up properly.
    pause
    exit /b 1
)

echo ✅ Local Python found
echo Starting Canvas Integration...
echo.

".conda\python.exe" duckgrade_canvas_complete.py

if %errorlevel% neq 0 (
    echo.
    echo ❌ Error starting DuckGrade Canvas GUI
    echo Check the error messages above for details.
    echo.
    pause
) else (
    echo.
    echo ✅ DuckGrade Canvas GUI closed successfully
    REM Exit immediately when GUI closes successfully
    exit /b 0
)
