"""
Reset Encrypted Storage
This script will clear your encrypted API key storage, allowing you to create a new master password.
"""

import os
from pathlib import Path

def reset_encrypted_storage():
    """Reset the encrypted storage to start fresh"""
    
    # Find the storage directory
    storage_dir = Path.home() / ".grading_agent"
    
    print("🔐 Encrypted Storage Reset Tool")
    print("=" * 40)
    
    if storage_dir.exists():
        print(f"Found encrypted storage at: {storage_dir}")
        
        # List files that will be removed
        files_to_remove = list(storage_dir.glob("*"))
        if files_to_remove:
            print("\nFiles that will be removed:")
            for file in files_to_remove:
                print(f"  - {file.name}")
            
            response = input("\nAre you sure you want to reset encrypted storage? (y/N): ")
            if response.lower() in ['y', 'yes']:
                try:
                    # Remove all files
                    for file in files_to_remove:
                        file.unlink()
                    
                    # Remove directory
                    storage_dir.rmdir()
                    
                    print("✅ Encrypted storage reset successfully!")
                    print("   You can now create a new master password when you save an API key.")
                    
                except Exception as e:
                    print(f"❌ Error resetting storage: {e}")
            else:
                print("Reset cancelled.")
        else:
            print("Storage directory is empty.")
            storage_dir.rmdir()
            print("✅ Empty storage directory removed.")
    else:
        print("📝 No encrypted storage found.")
        print("   When you save an API key, you'll be prompted to create a master password.")

if __name__ == "__main__":
    reset_encrypted_storage()
    input("\nPress Enter to exit...")
