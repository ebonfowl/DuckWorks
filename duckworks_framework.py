"""
DuckWorks Framework - Educational Automation That Just Works!
===========================================================

This module provides shared components and branding for all DuckWorks tools.
DuckGrader is the first tool in the DuckWorks educational automation suite.

Author: DuckWorks Development Team
License: Educational Use
Version: 1.0.0
"""

import os
import sys
from datetime import datetime

class DuckWorksInfo:
    """Information and branding for the DuckWorks suite"""
    
    SUITE_NAME = "DuckWorks"
    SUITE_TAGLINE = "Educational Automation That Just Works!"
    VERSION = "1.0.0"
    
    # Current Tools
    TOOLS = {
        "DuckGrade": {
            "name": "DuckGrade", 
            "description": "AI-powered assignment grading automation",
            "version": "1.0.0",
            "icon": "🦆",
            "status": "Active"
        }
    }
    
    # Future Tools (Roadmap)
    ROADMAP = {
        "DuckScheduler": "Class scheduling automation",
        "DuckAnalyzer": "Student performance analytics", 
        "DuckContent": "Curriculum content generation",
        "DuckFeedback": "Automated feedback systems",
        "DuckAssess": "Assessment creation tools"
    }
    
    @classmethod
    def get_welcome_banner(cls, tool_name=None):
        """Get a formatted welcome banner for any DuckWorks tool"""
        banner = f"""
🦆 {cls.SUITE_NAME} - {cls.SUITE_TAGLINE}
{'=' * 60}"""
        
        if tool_name and tool_name in cls.TOOLS:
            tool_info = cls.TOOLS[tool_name]
            banner += f"""
Currently running: {tool_info['name']} v{tool_info['version']}
{tool_info['description']}
"""
        
        return banner
    
    @classmethod
    def get_suite_info(cls):
        """Get complete suite information"""
        return {
            "suite_name": cls.SUITE_NAME,
            "tagline": cls.SUITE_TAGLINE,
            "version": cls.VERSION,
            "tools": cls.TOOLS,
            "roadmap": cls.ROADMAP,
            "timestamp": datetime.now().isoformat()
        }

class DuckWorksConfig:
    """Shared configuration management for DuckWorks tools"""
    
    def __init__(self, tool_name):
        self.tool_name = tool_name
        self.config_dir = os.path.join(os.path.expanduser("~"), ".duckworks")
        self.tool_config_dir = os.path.join(self.config_dir, tool_name.lower())
        
        # Ensure config directories exist
        os.makedirs(self.tool_config_dir, exist_ok=True)
    
    def get_config_path(self, filename):
        """Get full path for a config file"""
        return os.path.join(self.tool_config_dir, filename)
    
    def get_shared_config_path(self, filename):
        """Get full path for a shared config file"""
        return os.path.join(self.config_dir, filename)

class DuckWorksGUI:
    """Shared GUI components and styling for DuckWorks tools"""
    
    # Color scheme
    COLORS = {
        "primary": "#2E86AB",      # Duck blue
        "secondary": "#A23B72",    # Duck purple
        "accent": "#F18F01",       # Duck orange
        "success": "#C73E1D",      # Duck red
        "background": "#F5F5F5",   # Light gray
        "text": "#333333"          # Dark gray
    }
    
    # Common styling
    FONTS = {
        "title": ("Arial", 14, "bold"),
        "heading": ("Arial", 12, "bold"),
        "body": ("Arial", 10),
        "small": ("Arial", 8)
    }
    
    @classmethod
    def get_icon_path(cls):
        """Get path to the standard DuckWorks icon"""
        return os.path.join("assets", "icons8-flying-duck-48.png")
    
    @classmethod
    def apply_duckworks_theme(cls, root):
        """Apply standard DuckWorks theme to a Tkinter window"""
        try:
            # Set icon if available
            icon_path = cls.get_icon_path()
            if os.path.exists(icon_path):
                root.iconbitmap(icon_path)
        except:
            pass  # Icon loading is optional
        
        # Set background color
        root.configure(bg=cls.COLORS["background"])

def print_duckworks_header(tool_name=None):
    """Print a standardized header for any DuckWorks tool"""
    print(DuckWorksInfo.get_welcome_banner(tool_name))
    
def get_duckworks_version():
    """Get the current DuckWorks framework version"""
    return DuckWorksInfo.VERSION

# Tool registration decorator
def duckworks_tool(name, description, version="1.0.0"):
    """Decorator to register a class as a DuckWorks tool"""
    def decorator(cls):
        # Add tool metadata
        cls._duckworks_name = name
        cls._duckworks_description = description
        cls._duckworks_version = version
        
        # Register in the tools registry
        DuckWorksInfo.TOOLS[name] = {
            "name": name,
            "description": description,
            "version": version,
            "icon": "🦆",
            "status": "Active"
        }
        
        return cls
    return decorator

if __name__ == "__main__":
    # Demo the framework
    print_duckworks_header("DuckGrader")
    print("\n📋 Current DuckWorks Tools:")
    for tool_name, tool_info in DuckWorksInfo.TOOLS.items():
        print(f"  {tool_info['icon']} {tool_name} - {tool_info['description']}")
    
    print("\n🗺️ Future DuckWorks Tools:")
    for tool_name, description in DuckWorksInfo.ROADMAP.items():
        print(f"  🔮 {tool_name} - {description}")
    
    print(f"\n🦆 DuckWorks Framework v{get_duckworks_version()} - Ready for educational automation!")
