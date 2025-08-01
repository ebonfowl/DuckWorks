"""
DuckGrade Welcome Script
Launch this to see DuckWorks suite information and quick access to all tools
"""

import sys
import os
import subprocess
from duckworks_framework import DuckWorksInfo, print_duckworks_header

def main():
    print_duckworks_header("DuckGrade")
    
    print("\n🦆 Welcome to DuckGrade!")
    print("The first tool in the DuckWorks Educational Automation Suite")
    print()
    
    print("📋 What would you like to do?")
    print("1. 📁 Grade Local Files (PDF, DOCX, TXT, etc.)")
    print("2. 🌐 Grade Canvas Assignments (LMS Integration)")
    print("3. 🧪 Test DuckGrader Features")
    print("4. 📖 View Project Documentation")
    print("5. 🔧 Setup and Configuration")
    print("6. ❓ Help and Information")
    print("7. 🚪 Exit")
    
    while True:
        try:
            choice = input("\n🦆 Enter your choice (1-7): ").strip()
            
            if choice == "1":
                print("\n🚀 Launching DuckGrade Local File Interface...")
                if os.name == 'nt':  # Windows
                    subprocess.run(["start_local_gui.bat"], shell=True)
                else:  # Unix/Linux/Mac
                    subprocess.run(["python", "gui.py"])
                break
                
            elif choice == "2":
                print("\n🚀 Launching DuckGrade Canvas Integration...")
                if os.name == 'nt':  # Windows
                    subprocess.run(["start_canvas_gui.bat"], shell=True)
                else:  # Unix/Linux/Mac
                    subprocess.run(["python", "canvas_gui.py"])
                break
                
            elif choice == "3":
                print("\n🧪 Running DuckGrade Feature Tests...")
                subprocess.run([sys.executable, "test_features.py"])
                input("\nPress Enter to return to menu...")
                main()
                break
                
            elif choice == "4":
                print("\n📖 DuckGrade Documentation:")
                print("• PROJECT_SUMMARY.md - Complete project overview")
                print("• SESSION_LOG.md - Development session history")
                print("• README.md - Setup and usage instructions")
                print("• duckworks_framework.py - Framework documentation")
                
                doc_choice = input("\nOpen PROJECT_SUMMARY.md? (y/n): ").strip().lower()
                if doc_choice == 'y':
                    if os.name == 'nt':  # Windows
                        os.startfile("PROJECT_SUMMARY.md")
                    else:  # Unix/Linux/Mac
                        subprocess.run(["open", "PROJECT_SUMMARY.md"])  # Mac
                input("\nPress Enter to return to menu...")
                main()
                break
                
            elif choice == "5":
                print("\n🔧 DuckGrade Setup and Configuration:")
                print("• First time? Run option 1 or 2 to set up API keys")
                print("• Keys are encrypted and stored securely")
                print("• Configuration files in ~/.duckworks/duckgrade/")
                print("• Models and pricing update automatically")
                input("\nPress Enter to return to menu...")
                main()
                break
                
            elif choice == "6":
                print("\n❓ DuckGrade Help:")
                print()
                print("🦆 About DuckGrade:")
                print("DuckGrade is an AI-powered assignment grading tool that automates")
                print("the assessment process while maintaining educational quality.")
                print()
                print("🎯 Key Features:")
                print("• Multi-format file support (.pdf, .docx, .txt, .html, .odt, .rtf)")
                print("• Canvas LMS integration with privacy protection")
                print("• Customizable rubrics and instructor personalities")
                print("• Secure API key management")
                print("• Real-time progress tracking")
                print("• Professional duck branding 🦆")
                print()
                print("🚀 Quick Start:")
                print("1. Choose option 1 or 2 from main menu")
                print("2. Enter OpenAI API key when prompted")
                print("3. Select grading model and configure settings")
                print("4. Load rubric and student submissions")
                print("5. Let DuckGrade do the work!")
                print()
                print("💡 Tips:")
                print("• Test with a few submissions first")
                print("• Review grades before uploading to Canvas")
                print("• Use instructor config to match your grading style")
                print("• Check the log for detailed progress information")
                input("\nPress Enter to return to menu...")
                main()
                break
                
            elif choice == "7":
                print("\n🦆 Thank you for using DuckGrade!")
                print("Part of the DuckWorks Educational Automation Suite")
                print("Educational Automation That Just Works! 🎓")
                break
                
            else:
                print("❌ Invalid choice. Please enter 1-7.")
                
        except KeyboardInterrupt:
            print("\n\n🦆 Goodbye! Thanks for using DuckGrade!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            print("Please try again.")

if __name__ == "__main__":
    main()
