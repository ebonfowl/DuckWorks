#!/usr/bin/env python3
"""
Debug script to test grading functionality
"""

import sys
import os
from pathlib import Path
import json

def test_grading():
    print("🦆 Testing grading functionality...")
    
    # Import grading agent
    try:
        from grading_agent import GradingAgent
        print("✅ GradingAgent imported successfully")
    except Exception as e:
        print(f"❌ Failed to import GradingAgent: {e}")
        return False
    
    # Get OpenAI key
    try:
        with open('OpenAI_APIKey.txt', 'r') as f:
            api_key = f.read().strip()
        print("✅ API key loaded")
    except Exception as e:
        print(f"❌ Failed to load API key: {e}")
        return False
    
    # Initialize grading agent
    try:
        agent = GradingAgent(api_key, model='gpt-4o-mini')
        print("✅ GradingAgent initialized")
    except Exception as e:
        print(f"❌ Failed to initialize GradingAgent: {e}")
        return False
    
    # Find the latest test folder
    test_folders = [d for d in os.listdir('.') if d.startswith('Final_Project_')]
    if not test_folders:
        print("❌ No test folders found")
        return False
    
    latest_folder = sorted(test_folders)[-1]
    print(f"📁 Using test folder: {latest_folder}")
    
    # Load rubric
    rubric_path = f"{latest_folder}/canvas_rubric.json"
    try:
        agent.load_rubric(rubric_path)
        print(f"✅ Rubric loaded from {rubric_path}")
    except Exception as e:
        print(f"❌ Failed to load rubric: {e}")
        return False
    
    # Find a test file
    submissions_dir = f"{latest_folder}/submissions"
    student_dirs = [d for d in os.listdir(submissions_dir) if os.path.isdir(os.path.join(submissions_dir, d))]
    
    if not student_dirs:
        print("❌ No student directories found")
        return False
    
    test_student_dir = student_dirs[0]
    test_dir_path = os.path.join(submissions_dir, test_student_dir)
    test_files = [f for f in os.listdir(test_dir_path) if f.endswith(('.docx', '.pdf', '.txt'))]
    
    if not test_files:
        print(f"❌ No suitable test files found in {test_dir_path}")
        return False
    
    test_file_path = os.path.join(test_dir_path, test_files[0])
    print(f"📄 Testing with file: {test_file_path}")
    
    # Test grading
    try:
        student_data = {
            'name': 'Test Student',
            'content': '',  # Will be extracted by grade_paper
            'file_path': str(test_file_path)
        }
        
        print("🤖 Attempting to grade...")
        result = agent.grade_paper(student_data)
        
        if result:
            print("✅ Grading successful!")
            print(f"📊 Result keys: {list(result.keys())}")
            print(f"📊 Overall score: {result.get('overall_score', 'N/A')}")
            print(f"📊 Max score: {result.get('max_possible_score', 'N/A')}")
            return True
        else:
            print("❌ Grading returned None/empty result")
            return False
            
    except Exception as e:
        print(f"❌ Grading failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = test_grading()
    if success:
        print("\n🎉 Grading test completed successfully!")
    else:
        print("\n💥 Grading test failed!")
