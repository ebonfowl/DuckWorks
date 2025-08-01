"""
Secure Key Manager
Handles encrypted storage and retrieval of API keys
"""

import os
import json
import base64
import hashlib
from typing import Optional, Dict, Any
from pathlib import Path
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import getpass
import logging

class SecureKeyManager:
    """Manages encrypted storage of API keys and sensitive configuration"""
    
    def __init__(self, config_dir: str = None):
        """
        Initialize the secure key manager
        
        Args:
            config_dir: Directory to store encrypted config files
        """
        if config_dir is None:
            config_dir = os.path.join(os.path.expanduser("~"), ".grading_agent")
        
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(exist_ok=True)
        
        self.config_file = self.config_dir / "secure_config.enc"
        self.salt_file = self.config_dir / "config.salt"
        
        # In-memory storage for current session
        self._decrypted_config = {}
        self._current_key = None
        
    def _generate_key(self, password: str, salt: bytes) -> bytes:
        """Generate encryption key from password and salt"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def _get_or_create_salt(self) -> bytes:
        """Get existing salt or create new one"""
        if self.salt_file.exists():
            with open(self.salt_file, 'rb') as f:
                return f.read()
        else:
            salt = os.urandom(16)
            with open(self.salt_file, 'wb') as f:
                f.write(salt)
            return salt
    
    def _get_master_password(self, action: str = "unlock", password_callback=None) -> str:
        """Get master password from user"""
        if password_callback:
            try:
                # Use GUI callback for password input
                password = password_callback(action)
                if password:  # Ensure we got a valid password
                    return password
                else:
                    # If callback returns None/empty, user cancelled - don't fall back to console
                    raise ValueError("Password input cancelled by user")
            except Exception as callback_error:
                print(f"   ⚠️ Error with password callback: {callback_error}")
                # If callback was provided but failed, don't fall back to console
                # This prevents GUI apps from unexpectedly prompting in console
                raise callback_error
        
        # If no password callback is provided and we're not in console mode,
        # raise an exception to avoid blocking
        try:
            # Check if we're in a GUI environment by testing for stdin
            import sys
            if not sys.stdin.isatty():
                raise ValueError("Password input required but no GUI callback provided")
        except:
            pass
        
        # Fallback to console input only if explicitly in console mode
        print(f"\n🔐 Secure Key Management")
        print(f"   Action: {action} encrypted configuration")
        print(f"   Config location: {self.config_file}")
        
        if action == "create":
            print("   Creating new master password for encrypting API keys...")
            password = getpass.getpass("   Enter new master password: ")
            confirm = getpass.getpass("   Confirm master password: ")
            
            if password != confirm:
                raise ValueError("Passwords do not match")
            
            if len(password) < 8:
                raise ValueError("Password must be at least 8 characters long")
                
            return password
        else:
            return getpass.getpass(f"   Enter master password to {action}: ")
    
    def save_config(self, config_data: Dict[str, Any], password: str = None, password_callback=None) -> bool:
        """
        Save configuration data with encryption
        
        Args:
            config_data: Dictionary of configuration to encrypt
            password: Master password (will prompt if not provided)
            password_callback: Function to get password from GUI (optional)
            
        Returns:
            True if successful
        """
        try:
            if password is None:
                if self.config_file.exists():
                    password = self._get_master_password("update", password_callback)
                else:
                    password = self._get_master_password("create", password_callback)
            
            # Get or create salt
            salt = self._get_or_create_salt()
            
            # Generate encryption key
            key = self._generate_key(password, salt)
            fernet = Fernet(key)
            
            # Encrypt the configuration
            config_json = json.dumps(config_data, indent=2)
            encrypted_data = fernet.encrypt(config_json.encode())
            
            # Save encrypted config
            with open(self.config_file, 'wb') as f:
                f.write(encrypted_data)
            
            # Store in memory for current session
            self._decrypted_config = config_data.copy()
            self._current_key = key
            
            print(f"   ✅ Configuration saved and encrypted successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ Error saving encrypted configuration: {e}")
            logging.error(f"Error saving secure config: {e}")
            return False
    
    def load_config(self, password: str = None, password_callback=None) -> Dict[str, Any]:
        """
        Load and decrypt configuration data
        
        Args:
            password: Master password (will prompt if not provided)
            password_callback: Function to get password from GUI (optional)
            
        Returns:
            Decrypted configuration dictionary
        """
        # Return cached config if available
        if self._decrypted_config and self._current_key:
            return self._decrypted_config.copy()
        
        if not self.config_file.exists():
            print(f"   📝 No encrypted configuration found")
            return {}
        
        try:
            if password is None:
                password = self._get_master_password("unlock", password_callback)
            
            # Load salt
            if not self.salt_file.exists():
                raise ValueError("Salt file not found - configuration may be corrupted")
            
            salt = self._get_or_create_salt()
            
            # Generate decryption key
            key = self._generate_key(password, salt)
            fernet = Fernet(key)
            
            # Read and decrypt configuration
            with open(self.config_file, 'rb') as f:
                encrypted_data = f.read()
            
            decrypted_data = fernet.decrypt(encrypted_data)
            config_data = json.loads(decrypted_data.decode())
            
            # Cache for current session
            self._decrypted_config = config_data.copy()
            self._current_key = key
            
            print(f"   ✅ Configuration decrypted successfully")
            return config_data
            
        except Exception as e:
            print(f"   ❌ Error loading encrypted configuration: {e}")
            logging.error(f"Error loading secure config: {e}")
            return {}
    
    def update_config(self, key: str, value: Any) -> bool:
        """
        Update a single configuration value
        
        Args:
            key: Configuration key to update
            value: New value
            
        Returns:
            True if successful
        """
        try:
            # Load current config
            current_config = self.load_config()
            
            # Update the value
            current_config[key] = value
            
            # Save updated config (will use cached password)
            return self.save_config(current_config, password="cached")
            
        except Exception as e:
            print(f"   ❌ Error updating configuration: {e}")
            logging.error(f"Error updating secure config: {e}")
            return False
    
    def get_config_value(self, key: str, default: Any = None, password_callback=None) -> Any:
        """
        Get a specific configuration value
        
        Args:
            key: Configuration key
            default: Default value if key not found
            password_callback: Function to get password from GUI (optional)
            
        Returns:
            Configuration value or default
        """
        try:
            config = self.load_config(password_callback=password_callback)
            return config.get(key, default)
        except Exception:
            return default
    
    def has_config(self) -> bool:
        """Check if encrypted configuration exists"""
        return self.config_file.exists() and self.salt_file.exists()
    
    def delete_config(self) -> bool:
        """
        Delete encrypted configuration (after confirmation)
        
        Returns:
            True if deleted successfully
        """
        if not self.has_config():
            print("   📝 No encrypted configuration to delete")
            return True
        
        print(f"\n⚠️  Warning: This will permanently delete your encrypted configuration")
        print(f"   Config file: {self.config_file}")
        print(f"   This includes all stored API keys and settings")
        
        confirm = input("   Type 'DELETE' to confirm: ")
        if confirm != "DELETE":
            print("   ❌ Deletion cancelled")
            return False
        
        try:
            if self.config_file.exists():
                self.config_file.unlink()
            if self.salt_file.exists():
                self.salt_file.unlink()
            
            # Clear memory cache
            self._decrypted_config = {}
            self._current_key = None
            
            print("   ✅ Encrypted configuration deleted successfully")
            return True
            
        except Exception as e:
            print(f"   ❌ Error deleting configuration: {e}")
            logging.error(f"Error deleting secure config: {e}")
            return False
    
    def change_password(self) -> bool:
        """
        Change the master password
        
        Returns:
            True if successful
        """
        if not self.has_config():
            print("   📝 No existing configuration to change password for")
            return False
        
        try:
            # Load current config with old password
            print("   Step 1: Verify current password")
            current_config = self.load_config()
            
            if not current_config:
                print("   ❌ Could not decrypt current configuration")
                return False
            
            # Get new password
            print("   Step 2: Set new password")
            new_password = self._get_master_password("create")
            
            # Remove old salt and regenerate
            if self.salt_file.exists():
                self.salt_file.unlink()
            
            # Save with new password
            success = self.save_config(current_config, new_password)
            
            if success:
                print("   ✅ Master password changed successfully")
            
            return success
            
        except Exception as e:
            print(f"   ❌ Error changing password: {e}")
            logging.error(f"Error changing password: {e}")
            return False
    
    def export_config(self, export_path: str, include_sensitive: bool = False) -> bool:
        """
        Export configuration to a file (optionally excluding sensitive data)
        
        Args:
            export_path: Path to export file
            include_sensitive: Whether to include API keys and tokens
            
        Returns:
            True if successful
        """
        try:
            config = self.load_config()
            
            if not include_sensitive:
                # Remove sensitive keys
                sensitive_keys = ['openai_api_key', 'canvas_api_token', 'api_key', 'token']
                export_config = {}
                
                for key, value in config.items():
                    if not any(sensitive in key.lower() for sensitive in sensitive_keys):
                        export_config[key] = value
                    else:
                        export_config[key] = "[REDACTED]"
            else:
                export_config = config.copy()
            
            with open(export_path, 'w') as f:
                json.dump(export_config, f, indent=2)
            
            print(f"   ✅ Configuration exported to: {export_path}")
            if not include_sensitive:
                print(f"   📝 Sensitive data was excluded from export")
            
            return True
            
        except Exception as e:
            print(f"   ❌ Error exporting configuration: {e}")
            logging.error(f"Error exporting config: {e}")
            return False


class APIKeyManager:
    """Simplified interface for managing API keys specifically"""
    
    def __init__(self):
        self.key_manager = SecureKeyManager()
    
    def save_openai_key(self, api_key: str, password_callback=None) -> bool:
        """Save OpenAI API key"""
        config = self.key_manager.load_config(password_callback=password_callback)
        config['openai_api_key'] = api_key
        config['openai_key_saved_at'] = str(Path().cwd())  # Remember where key was saved
        return self.key_manager.save_config(config, password_callback=password_callback)
    
    def get_openai_key(self, password_callback=None) -> Optional[str]:
        """Get saved OpenAI API key"""
        return self.key_manager.get_config_value('openai_api_key', password_callback=password_callback)
    
    def save_canvas_credentials(self, canvas_url: str, api_token: str, password_callback=None) -> bool:
        """Save Canvas LMS credentials"""
        config = self.key_manager.load_config(password_callback=password_callback)
        config['canvas_url'] = canvas_url
        config['canvas_api_token'] = api_token
        config['canvas_credentials_saved_at'] = str(Path().cwd())
        return self.key_manager.save_config(config, password_callback=password_callback)
    
    def get_canvas_credentials(self, password_callback=None) -> Dict[str, Optional[str]]:
        """Get saved Canvas credentials"""
        config = self.key_manager.load_config(password_callback=password_callback)
        return {
            'canvas_url': config.get('canvas_url'),
            'canvas_api_token': config.get('canvas_api_token')
        }
    
    def has_openai_key(self) -> bool:
        """Check if OpenAI API key is stored"""
        try:
            # If we have cached config, check that first
            if self.key_manager._decrypted_config:
                return 'openai_api_key' in self.key_manager._decrypted_config
            
            # Otherwise, just check if config file exists
            # We can't check the content without the password
            return self.key_manager.has_config()
        except:
            return False
    
    def has_canvas_credentials(self) -> bool:
        """Check if Canvas credentials are stored"""
        creds = self.get_canvas_credentials()
        return bool(creds['canvas_url'] and creds['canvas_api_token'])
    
    def clear_openai_key(self, password_callback=None) -> bool:
        """Clear stored OpenAI API key"""
        config = self.key_manager.load_config(password_callback=password_callback)
        if 'openai_api_key' in config:
            del config['openai_api_key']
        return self.key_manager.save_config(config, password_callback=password_callback)
    
    def clear_canvas_credentials(self, password_callback=None) -> bool:
        """Clear stored Canvas credentials"""
        config = self.key_manager.load_config(password_callback=password_callback)
        for key in ['canvas_url', 'canvas_api_token']:
            if key in config:
                del config[key]
        return self.key_manager.save_config(config, password_callback=password_callback)


def test_key_manager():
    """Test function for the key manager"""
    print("Testing Secure Key Manager...")
    
    manager = APIKeyManager()
    
    # Test if config exists
    if manager.key_manager.has_config():
        print("✅ Found existing encrypted configuration")
        
        # Try to load
        key = manager.get_openai_key()
        if key:
            print(f"✅ OpenAI API key found (length: {len(key)})")
        else:
            print("📝 No OpenAI API key stored")
    else:
        print("📝 No encrypted configuration found")
    
    print("Test completed")


if __name__ == "__main__":
    test_key_manager()
