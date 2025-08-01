"""
Test script for GradingAgent system
Run this to verify your setup is working correctly
"""

import os
import json
from pathlib import Path
from grading_agent import GradingAgent

def test_system():
    """Test the GradingAgent system with sample data"""
    print("🧪 Testing GradingAgent System")
    print("=" * 50)
    
    # Test 1: Check if required files exist
    print("\n1. Checking required files...")
    
    required_files = [
        "grading_agent.py",
        "gui.py", 
        "sample_rubric.json",
        "sample_papers/John_Smith.txt",
        "sample_papers/Sarah_Johnson.txt",
        "sample_papers/Mike_Davis.txt"
    ]
    
    missing_files = []
    for file in required_files:
        if not Path(file).exists():
            missing_files.append(file)
        else:
            print(f"   ✓ {file}")
    
    if missing_files:
        print(f"   ✗ Missing files: {missing_files}")
        return False
    
    # Test 2: Validate rubric JSON
    print("\n2. Validating rubric format...")
    try:
        with open("sample_rubric.json", 'r') as f:
            rubric = json.load(f)
        print("   ✓ Rubric JSON is valid")
        print(f"   ✓ Assignment: {rubric['assignment_title']}")
        print(f"   ✓ Total Points: {rubric['total_points']}")
        print(f"   ✓ Criteria Count: {len(rubric['criteria'])}")
    except Exception as e:
        print(f"   ✗ Rubric validation failed: {e}")
        return False
    
    # Test 3: Test file loading (without API key)
    print("\n3. Testing file loading...")
    try:
        # Create a dummy agent (without API key for testing)
        agent = GradingAgent("dummy-key")
        
        # Test rubric loading
        agent.load_rubric("sample_rubric.json")
        print("   ✓ Rubric loaded successfully")
        
        # Test paper loading
        papers = agent.load_student_papers("sample_papers")
        print(f"   ✓ Loaded {len(papers)} student papers")
        
        for paper in papers:
            print(f"      - {paper['name']}: {len(paper['content'])} characters")
            
    except Exception as e:
        print(f"   ✗ File loading failed: {e}")
        return False
    
    # Test 4: Check package imports
    print("\n4. Checking package imports...")
    try:
        import openai
        print("   ✓ openai package available")
        
        import pandas
        print("   ✓ pandas package available")
        
        import openpyxl
        print("   ✓ openpyxl package available")
        
        from docx import Document
        print("   ✓ python-docx package available")
        
        import PyPDF2
        print("   ✓ PyPDF2 package available")
        
        import tkinter
        print("   ✓ tkinter package available")
        
    except ImportError as e:
        print(f"   ✗ Package import failed: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("🎉 All tests passed!")
    print("\nYour GradingAgent system is ready to use!")
    print("\nNext steps:")
    print("1. Get your OpenAI API key from https://platform.openai.com/")
    print("2. Run the GUI: python gui.py")
    print("3. Or run the CLI: python grading_agent.py")
    print("\nSee README.md for detailed instructions.")
    
    return True

def create_demo_config():
    """Create a demo configuration file"""
    print("\n📋 Creating demo configuration...")
    
    config_content = """
# Demo Configuration for GradingAgent
# Replace 'your-api-key-here' with your actual OpenAI API key

OPENAI_API_KEY = "your-api-key-here"
DEFAULT_RUBRIC_PATH = "./sample_rubric.json"
DEFAULT_PAPERS_FOLDER = "./sample_papers"
DEFAULT_OUTPUT_FORMAT = "xlsx"

# Note: This is a demo configuration
# Copy config_template.py for full configuration options
"""
    
    with open("demo_config.py", "w") as f:
        f.write(config_content)
    
    print("   ✓ Created demo_config.py")
    print("   📝 Edit demo_config.py to add your OpenAI API key")

if __name__ == "__main__":
    if test_system():
        create_demo_config()
    else:
        print("\n❌ System test failed. Please check the errors above.")
