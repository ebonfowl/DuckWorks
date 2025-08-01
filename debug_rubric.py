#!/usr/bin/env python3
"""
Debug script to test Canvas rubric detection
This helps isolate rubric fetching issues without running the full grading process
"""

import os
import json
from canvas_integration import CanvasAPI

def debug_rubric_detection():
    """Debug Canvas rubric detection for a specific assignment"""
    
    print("🔍 Canvas Rubric Detection Debug Tool")
    print("=" * 50)
    
    # Get Canvas connection details
    canvas_url = input("Enter Canvas URL (e.g., https://canvas.collegeidaho.edu): ").strip()
    api_token = input("Enter Canvas API Token: ").strip()
    
    if not canvas_url or not api_token:
        print("❌ Canvas URL and API token are required")
        return
    
    # Initialize Canvas API
    try:
        canvas = CanvasAPI(canvas_url, api_token)
        print("✅ Canvas API connection initialized")
    except Exception as e:
        print(f"❌ Failed to initialize Canvas API: {e}")
        return
    
    # Get course list
    print("\n📚 Fetching available courses...")
    try:
        courses = canvas.get_courses()
        if not courses:
            print("❌ No courses found")
            return
        
        print(f"Found {len(courses)} courses:")
        for i, course in enumerate(courses, 1):
            print(f"  {i}. {course['name']} (ID: {course['id']})")
        
    except Exception as e:
        print(f"❌ Error fetching courses: {e}")
        return
    
    # Select course
    try:
        course_choice = int(input(f"\nSelect course (1-{len(courses)}): ")) - 1
        selected_course = courses[course_choice]
        course_id = selected_course['id']
        print(f"Selected: {selected_course['name']}")
    except (ValueError, IndexError):
        print("❌ Invalid course selection")
        return
    
    # Get assignments for the course
    print(f"\n📋 Fetching assignments for course {course_id}...")
    try:
        assignments = canvas.get_assignments(course_id)
        if not assignments:
            print("❌ No assignments found")
            return
        
        print(f"Found {len(assignments)} assignments:")
        for i, assignment in enumerate(assignments, 1):
            print(f"  {i}. {assignment['name']} (ID: {assignment['id']})")
        
    except Exception as e:
        print(f"❌ Error fetching assignments: {e}")
        return
    
    # Select assignment
    try:
        assignment_choice = int(input(f"\nSelect assignment (1-{len(assignments)}): ")) - 1
        selected_assignment = assignments[assignment_choice]
        assignment_id = selected_assignment['id']
        print(f"Selected: {selected_assignment['name']}")
    except (ValueError, IndexError):
        print("❌ Invalid assignment selection")
        return
    
    # Test rubric detection
    print(f"\n🔍 Testing rubric detection for assignment {assignment_id}...")
    print("=" * 50)
    
    try:
        rubric_data = canvas.get_assignment_rubric(course_id, assignment_id)
        
        if rubric_data:
            print("✅ SUCCESS: Rubric found!")
            print(f"📋 Rubric Title: {rubric_data.get('canvas_rubric_title', 'No title')}")
            print(f"📊 Number of criteria: {len(rubric_data.get('criteria', []))}")
            
            # Save the rubric for inspection
            output_file = f"debug_rubric_{assignment_id}.json"
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(rubric_data, f, indent=2)
            print(f"💾 Saved rubric to: {output_file}")
            
            # Show criteria summary
            criteria = rubric_data.get('criteria', {})
            if criteria:
                print(f"\n📋 Rubric Criteria:")
                for i, (criterion_name, criterion_data) in enumerate(criteria.items(), 1):
                    print(f"  {i}. {criterion_name}")
                    ratings = criterion_data.get('ratings', [])
                    print(f"     Ratings: {len(ratings)} levels")
                    if ratings:
                        for rating in ratings:
                            print(f"       - {rating.get('description', 'No description')} ({rating.get('points', 0)} pts)")
            
        else:
            print("❌ FAILED: No rubric found")
            print("\nThis could mean:")
            print("  1. The assignment doesn't have a rubric attached")
            print("  2. The rubric exists but isn't properly linked")
            print("  3. There's a permission issue with the API token")
            print("  4. The rubric is in a format we don't recognize")
            
            print(f"\n💡 Try checking the assignment in Canvas:")
            print(f"   {canvas_url}/courses/{course_id}/assignments/{assignment_id}")
            
    except Exception as e:
        print(f"❌ ERROR during rubric detection: {e}")
        import traceback
        print(f"🔍 Full traceback:")
        print(traceback.format_exc())
    
    print("\n" + "=" * 50)
    print("🔍 Debug session complete")

if __name__ == "__main__":
    debug_rubric_detection()
