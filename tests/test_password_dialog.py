"""
Test the password dialog functionality
"""

import tkinter as tk
from secure_key_manager import APIKeyManager

def test_password_dialog():
    """Test the password dialog with the key manager"""
    
    # Create a test GUI window
    root = tk.Tk()
    root.withdraw()  # Hide the main window
    
    # Test the key manager with password callbacks
    print("Testing password dialog functionality...")
    
    try:
        # Initialize key manager
        key_manager = APIKeyManager()
        
        # Define a simple password callback for testing
        def password_callback(action):
            print(f"Would show password dialog for action: {action}")
            # Return a test password
            if action == "create":
                return "testpassword123"
            else:
                return "testpassword123"
        
        # Test saving a key
        print("Testing save functionality...")
        result = key_manager.save_openai_key("test-api-key-12345", password_callback=password_callback)
        print(f"Save result: {result}")
        
        # Test loading a key
        print("Testing load functionality...")
        loaded_key = key_manager.get_openai_key(password_callback=password_callback)
        print(f"Loaded key: {loaded_key[:10]}..." if loaded_key else "No key loaded")
        
        print("✅ Password callback functionality working!")
        
    except Exception as e:
        print(f"❌ Error testing password dialog: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        root.destroy()

if __name__ == "__main__":
    test_password_dialog()
