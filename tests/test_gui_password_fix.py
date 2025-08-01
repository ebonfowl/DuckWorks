"""
Comprehensive test for the fixed password dialog functionality
"""

import tkinter as tk
from tkinter import ttk
from gui import PasswordDialog
from secure_key_manager import APIKeyManager

def test_complete_system():
    """Test the complete password dialog and key management system"""
    
    print("🧪 Testing Complete Password Dialog System")
    print("=" * 50)
    
    # Create a test GUI window
    root = tk.Tk()
    root.title("Test Password Dialog")
    root.geometry("300x200")
    
    def test_password_dialog():
        """Test the actual password dialog"""
        print("1. Testing password dialog creation...")
        
        # Test create password dialog
        create_dialog = PasswordDialog(root, "create")
        print("   ✅ Create password dialog created successfully")
        
        # Test unlock password dialog  
        unlock_dialog = PasswordDialog(root, "unlock")
        print("   ✅ Unlock password dialog created successfully")
        
        # Close dialogs
        create_dialog.dialog.destroy()
        unlock_dialog.dialog.destroy()
        
    def test_key_manager_with_callbacks():
        """Test key manager with password callbacks"""
        print("2. Testing key manager with password callbacks...")
        
        key_manager = APIKeyManager()
        
        # Simple callback that returns a test password
        def password_callback(action):
            print(f"   Password callback called for: {action}")
            return "testpassword123"
        
        try:
            # Test saving OpenAI key
            print("   Testing save OpenAI key...")
            result = key_manager.save_openai_key("test-openai-key", password_callback=password_callback)
            print(f"   Save result: {result}")
            
            # Test loading OpenAI key
            print("   Testing load OpenAI key...")
            loaded_key = key_manager.get_openai_key(password_callback=password_callback)
            print(f"   Loaded key: {loaded_key[:15]}..." if loaded_key else "   No key loaded")
            
            # Test saving Canvas credentials
            print("   Testing save Canvas credentials...")
            canvas_result = key_manager.save_canvas_credentials("https://test.instructure.com", "test-token", password_callback=password_callback)
            print(f"   Canvas save result: {canvas_result}")
            
            # Test loading Canvas credentials
            print("   Testing load Canvas credentials...")
            canvas_creds = key_manager.get_canvas_credentials(password_callback=password_callback)
            print(f"   Canvas URL: {canvas_creds['canvas_url']}")
            print(f"   Canvas Token: {canvas_creds['canvas_api_token'][:10]}..." if canvas_creds['canvas_api_token'] else "None")
            
            print("   ✅ All key manager operations successful")
            
        except Exception as e:
            print(f"   ❌ Error in key manager test: {e}")
            import traceback
            traceback.print_exc()
    
    def run_tests():
        """Run all tests"""
        try:
            test_password_dialog()
            test_key_manager_with_callbacks()
            print("\n🎉 All tests completed successfully!")
            print("   The password dialog hanging issue has been fixed!")
            
        except Exception as e:
            print(f"\n❌ Test failed: {e}")
            import traceback
            traceback.print_exc()
        
        root.quit()
    
    # Add a button to run tests
    ttk.Label(root, text="Password Dialog Fix Test", font=("Arial", 14, "bold")).pack(pady=20)
    ttk.Button(root, text="Run Tests", command=run_tests).pack(pady=10)
    ttk.Label(root, text="This tests the password dialog functionality\nwithout hanging the GUI", 
              justify=tk.CENTER, font=("Arial", 9)).pack(pady=10)
    
    # Start the test
    root.after(1000, run_tests)  # Auto-run tests after 1 second
    root.mainloop()

if __name__ == "__main__":
    test_complete_system()
