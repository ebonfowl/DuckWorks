"""
Canvas Integration Example

This example demonstrates how to use the Canvas LMS integration
to automatically grade an assignment and upload results.

Before running:
1. Set up your Canvas API token in canvas_config.json
2. Have a rubric file ready (sample_rubric.json)
3. Know your course ID and assignment ID

Author: Grading Agent
Date: January 2025
"""

from canvas_integration import CanvasAPI, CanvasGradingIntegration, setup_canvas_integration
from grading_agent import GradingAgent


def demo_canvas_integration():
    """Demonstrate complete Canvas integration workflow"""
    
    print("Canvas LMS Integration Demo")
    print("=" * 50)
    
    # Step 1: Setup Canvas connection
    print("\n1. Setting up Canvas connection...")
    try:
        canvas_api, config_file = setup_canvas_integration()
        print(f"✓ Canvas API configured using {config_file}")
    except Exception as e:
        print(f"✗ Failed to setup Canvas: {e}")
        return
    
    # Step 2: Test connection and show courses
    print("\n2. Testing connection and loading courses...")
    try:
        courses = canvas_api.get_courses()
        print(f"✓ Successfully connected! Found {len(courses)} courses:")
        
        for i, course in enumerate(courses[:10]):  # Show first 10 courses
            name = course.get('name', 'Unnamed Course')
            course_id = course['id']
            print(f"   {i+1}. {name} (ID: {course_id})")
        
        if len(courses) > 10:
            print(f"   ... and {len(courses)-10} more courses")
            
    except Exception as e:
        print(f"✗ Failed to load courses: {e}")
        return
    
    # Step 3: Interactive course and assignment selection
    print("\n3. Select course and assignment...")
    
    try:
        # Get course selection
        while True:
            try:
                course_choice = input(f"\nEnter course number (1-{min(len(courses), 10)}): ")
                course_index = int(course_choice) - 1
                if 0 <= course_index < min(len(courses), 10):
                    selected_course = courses[course_index]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        course_id = selected_course['id']
        course_name = selected_course['name']
        print(f"Selected course: {course_name}")
        
        # Load assignments for selected course
        print(f"Loading assignments for {course_name}...")
        assignments = canvas_api.get_assignments(course_id)
        
        print(f"Found {len(assignments)} assignments:")
        for i, assignment in enumerate(assignments[:10]):  # Show first 10
            name = assignment.get('name', 'Unnamed Assignment')
            assignment_id = assignment['id']
            due_date = assignment.get('due_at', 'No due date')
            print(f"   {i+1}. {name} (ID: {assignment_id}) - Due: {due_date}")
        
        if len(assignments) > 10:
            print(f"   ... and {len(assignments)-10} more assignments")
        
        # Get assignment selection
        while True:
            try:
                assignment_choice = input(f"\nEnter assignment number (1-{min(len(assignments), 10)}): ")
                assignment_index = int(assignment_choice) - 1
                if 0 <= assignment_index < min(len(assignments), 10):
                    selected_assignment = assignments[assignment_index]
                    break
                else:
                    print("Invalid choice. Please try again.")
            except ValueError:
                print("Please enter a valid number.")
        
        assignment_id = selected_assignment['id']
        assignment_name = selected_assignment['name']
        print(f"Selected assignment: {assignment_name}")
        
    except Exception as e:
        print(f"✗ Error during selection: {e}")
        return
    
    # Step 4: Check for submissions
    print(f"\n4. Checking submissions for '{assignment_name}'...")
    try:
        submissions = canvas_api.get_assignment_submissions(course_id, assignment_id)
        submitted_count = len([s for s in submissions if s.get('submitted_at')])
        
        print(f"Found {len(submissions)} total submissions")
        print(f"Found {submitted_count} actual submissions")
        
        if submitted_count == 0:
            print("⚠️  No submissions to grade. Exiting demo.")
            return
            
    except Exception as e:
        print(f"✗ Error checking submissions: {e}")
        return
    
    # Step 5: Confirm grading parameters
    print("\n5. Grading configuration...")
    rubric_path = input("Enter rubric file path (or press Enter for sample_rubric.json): ").strip()
    if not rubric_path:
        rubric_path = "sample_rubric.json"
    
    upload_grades = input("Upload grades to Canvas? (y/n, default=n): ").strip().lower()
    upload_grades = upload_grades == 'y'
    
    print(f"Rubric file: {rubric_path}")
    print(f"Upload grades: {upload_grades}")
    
    # Step 6: Run the grading process
    print(f"\n6. Starting grading process...")
    print("This may take several minutes depending on the number of submissions...")
    
    try:
        # Initialize grading system
        grading_agent = GradingAgent()
        integration = CanvasGradingIntegration(canvas_api, grading_agent)
        
        # Run the complete grading workflow
        results = integration.grade_canvas_assignment(
            course_id=course_id,
            assignment_id=assignment_id,
            rubric_path=rubric_path,
            upload_grades=upload_grades
        )
        
        # Display results
        print("\n" + "=" * 50)
        print("GRADING RESULTS")
        print("=" * 50)
        
        if results['success']:
            stats = results['stats']
            print(f"✓ Grading completed successfully!")
            print(f"Total submissions found: {stats['total']}")
            print(f"Successfully graded: {stats['graded']}")
            print(f"Uploaded to Canvas: {stats['uploaded']}")
            
            if 'results_file' in results:
                print(f"Results exported to: {results['results_file']}")
            
            # Show individual results
            if 'grading_results' in results and results['grading_results']:
                print(f"\nIndividual Results:")
                for user_id, result in results['grading_results'].items():
                    score = result['total_score']
                    max_score = result['max_score']
                    percentage = (score / max_score * 100) if max_score > 0 else 0
                    print(f"  User {user_id}: {score:.1f}/{max_score} ({percentage:.1f}%)")
            
        else:
            print(f"✗ Grading failed: {results['message']}")
        
    except Exception as e:
        print(f"✗ Error during grading: {e}")
        return
    
    print(f"\n7. Demo completed!")
    print(f"Next steps:")
    print(f"- Review the exported results file")
    if upload_grades:
        print(f"- Check Canvas gradebook to verify uploaded grades")
    print(f"- Use the GUI for easier future grading: start_canvas_gui.bat")


def demo_manual_workflow():
    """Demonstrate manual step-by-step Canvas workflow"""
    
    print("\nManual Canvas Workflow Demo")
    print("=" * 40)
    
    # This shows how to use the Canvas API directly
    print("This example shows how to use Canvas API components manually...")
    
    # Setup
    canvas_api, _ = setup_canvas_integration()
    
    # Example: Get specific course assignments
    course_id = input("Enter your course ID: ")
    if course_id.isdigit():
        course_id = int(course_id)
        
        try:
            assignments = canvas_api.get_assignments(course_id)
            print(f"Found {len(assignments)} assignments:")
            
            for assignment in assignments:
                print(f"- {assignment['name']} (ID: {assignment['id']})")
                
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    print("Canvas Integration Examples")
    print("1. Full automated demo")
    print("2. Manual workflow demo")
    
    choice = input("Choose demo (1 or 2): ").strip()
    
    if choice == "1":
        demo_canvas_integration()
    elif choice == "2":
        demo_manual_workflow()
    else:
        print("Invalid choice. Running full demo...")
        demo_canvas_integration()
