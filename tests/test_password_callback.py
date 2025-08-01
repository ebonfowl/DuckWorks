"""
Test the password callback functionality directly
"""

import sys
from PyQt6.QtWidgets import QApplication, QInputDialog, QLineEdit, QMessageBox
from secure_key_manager import APIKeyManager

def test_password_callback():
    """Test password callback functionality"""
    print("Testing password callback...")
    
    # Create a simple GUI application
    app = QApplication(sys.argv)
    
    def password_callback(action="unlock"):
        print(f"Password callback called with action: {action}")
        password, ok = QInputDialog.getText(
            None, 
            "Test Password Callback", 
            f"Enter password for action '{action}':",
            QLineEdit.EchoMode.Password
        )
        
        if ok and password:
            print(f"Password collected via GUI: {'*' * len(password)}")
            return password
        else:
            print("Password dialog cancelled")
            return None
    
    try:
        # Test the APIKeyManager with our callback
        manager = APIKeyManager()
        
        print("Testing has_openai_key...")
        has_key = manager.has_openai_key()
        print(f"Has OpenAI key: {has_key}")
        
        if has_key:
            print("Testing get_openai_key with password callback...")
            api_key = manager.get_openai_key(password_callback)
            
            if api_key:
                print(f"Successfully retrieved API key: {api_key[:10]}...")
                QMessageBox.information(None, "Success", "Password callback worked! API key retrieved successfully.")
            else:
                print("Failed to retrieve API key")
                QMessageBox.warning(None, "Failed", "Failed to retrieve API key")
        else:
            print("No API key stored - cannot test retrieval")
            QMessageBox.information(None, "No Key", "No API key stored to test with")
            
    except Exception as e:
        print(f"Error during test: {e}")
        QMessageBox.critical(None, "Error", f"Error during test: {str(e)}")
    
    print("Test completed")

if __name__ == "__main__":
    test_password_callback()
