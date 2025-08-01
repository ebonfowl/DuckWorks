"""
DuckGrade - Canvas LMS Integration
Part of the DuckWorks Educational Automation Suite

Canvas LMS GUI with Privacy Protection and Two-Step Workflow

This GUI provides:
1. Student name anonymization for ChatGPT processing
2. Two-step workflow: Grade → Review → Upload
3. Manual review and editing capability
4. Organized file management by assignment
5. Original single-step option still available

Author: DuckWorks Development Team
Date: January 2025
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import threading
import json
import os
import subprocess
import platform
from datetime import datetime
from typing import Dict, List, Optional

from canvas_integration import CanvasAPI, TwoStepCanvasGrading, setup_canvas_integration
from grading_agent import GradingAgent
from secure_key_manager import APIKeyManager
from openai_model_manager import OpenAIModelManager
from duckworks_framework import DuckWorksInfo, DuckWorksGUI, print_duckworks_header


class PasswordDialog:
    """Custom password dialog for secure key management"""
    
    def __init__(self, parent, action="unlock"):
        self.result = None
        self.action = action
        
        # Create dialog window
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Master Password")
        self.dialog.geometry("450x320")
        self.dialog.resizable(False, False)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() // 2) - (450 // 2)
        y = (self.dialog.winfo_screenheight() // 2) - (320 // 2)
        self.dialog.geometry(f"450x320+{x}+{y}")
        
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the password dialog UI"""
        main_frame = ttk.Frame(self.dialog, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Icon and title
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        ttk.Label(title_frame, text="🔐", font=("Arial", 24)).pack(side=tk.LEFT)
        ttk.Label(title_frame, text="Secure Key Management", font=("Arial", 14, "bold")).pack(side=tk.LEFT, padx=(10, 0))
        
        # Description
        if self.action == "create":
            desc_text = "Create a master password to encrypt your API keys.\nThis password will be required to access your saved keys."
            ttk.Label(main_frame, text=desc_text, justify=tk.LEFT).pack(fill=tk.X, pady=(0, 15))
            
            # Password entry
            ttk.Label(main_frame, text="New Master Password:").pack(anchor=tk.W)
            self.password_var = tk.StringVar()
            self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", font=("Arial", 10))
            self.password_entry.pack(fill=tk.X, pady=(5, 10))
            
            # Confirm password
            ttk.Label(main_frame, text="Confirm Password:").pack(anchor=tk.W)
            self.confirm_var = tk.StringVar()
            self.confirm_entry = ttk.Entry(main_frame, textvariable=self.confirm_var, show="*", font=("Arial", 10))
            self.confirm_entry.pack(fill=tk.X, pady=(5, 15))
            
            # Requirements
            req_text = "• Password must be at least 8 characters long\n• Use a strong, memorable password"
            ttk.Label(main_frame, text=req_text, font=("Arial", 8), foreground="gray").pack(fill=tk.X, pady=(0, 15))
            
        else:
            desc_text = "Enter your master password to access encrypted API keys."
            ttk.Label(main_frame, text=desc_text).pack(fill=tk.X, pady=(0, 15))
            
            # Password entry
            ttk.Label(main_frame, text="Master Password:").pack(anchor=tk.W)
            self.password_var = tk.StringVar()
            self.password_entry = ttk.Entry(main_frame, textvariable=self.password_var, show="*", font=("Arial", 10))
            self.password_entry.pack(fill=tk.X, pady=(5, 20))
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="OK", command=self.ok).pack(side=tk.RIGHT)
        
        # Focus and key bindings
        self.password_entry.focus()
        self.dialog.bind('<Return>', lambda e: self.ok())
        self.dialog.bind('<Escape>', lambda e: self.cancel())
        
    def ok(self):
        """Handle OK button"""
        password = self.password_var.get()
        
        if self.action == "create":
            confirm = self.confirm_var.get()
            
            if len(password) < 8:
                messagebox.showerror("Error", "Password must be at least 8 characters long", parent=self.dialog)
                return
                
            if password != confirm:
                messagebox.showerror("Error", "Passwords do not match", parent=self.dialog)
                return
        
        if not password:
            messagebox.showerror("Error", "Please enter a password", parent=self.dialog)
            return
            
        self.result = password
        self.dialog.destroy()
        
    def cancel(self):
        """Handle Cancel button"""
        self.result = None
        self.dialog.destroy()


class CanvasGUI:
    """DuckGrade Canvas Integration - Part of the DuckWorks Educational Suite"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DuckGrade - Canvas Integration | DuckWorks Educational Suite")
        self.root.geometry("900x700")
        
        # Apply DuckWorks theme
        DuckWorksGUI.apply_duckworks_theme(self.root)
        
        # Set duck icon
        try:
            duck_icon = tk.PhotoImage(file="assets/icons8-flying-duck-48.png")
            self.root.iconphoto(False, duck_icon)
        except Exception as e:
            print(f"Could not load duck icon: {e}")
            # Falls back to default icon if file not found
        
        # Initialize managers
        self.key_manager = APIKeyManager()
        self.model_manager = None
        
        # Initialize variables
        self.canvas_api = None
        self.grading_agent = None
        self.two_step_grading = None
        self.current_courses = []
        self.current_assignments = []
        self.current_step1_results = None
        
        # Initialize GUI variables
        self.rubric_source_var = None
        self.instructor_config_var = None
        self.openai_key_var = None
        self.selected_model_var = None
        
        # Available models (will be populated dynamically)
        self.available_models = []
        
        self.setup_gui()
        self.load_existing_config()
    
    def password_callback(self, action):
        """Password callback for secure key manager"""
        dialog = PasswordDialog(self.root, action)
        self.root.wait_window(dialog.dialog)
        return dialog.result
    
    def setup_gui(self):
        """Setup the GUI layout"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Setup tabs
        self.setup_connection_tab()
        self.setup_two_step_tab()
        self.setup_single_step_tab()
        self.setup_results_tab()
    
    def setup_connection_tab(self):
        """Setup Canvas connection configuration tab"""
        self.connection_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.connection_frame, text="🔗 Canvas Connection")
        
        # Connection settings
        settings_frame = ttk.LabelFrame(self.connection_frame, text="Canvas Settings", padding=10)
        settings_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Canvas URL
        ttk.Label(settings_frame, text="Canvas URL:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.canvas_url_var = tk.StringVar()
        self.canvas_url_entry = ttk.Entry(settings_frame, textvariable=self.canvas_url_var, width=60)
        self.canvas_url_entry.grid(row=0, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        # API Token
        ttk.Label(settings_frame, text="Canvas API Token:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.api_token_var = tk.StringVar()
        self.api_token_entry = ttk.Entry(settings_frame, textvariable=self.api_token_var, 
                                       width=60, show="*")
        self.api_token_entry.grid(row=1, column=1, columnspan=2, sticky=tk.EW, pady=2)
        
        # OpenAI API Key
        ttk.Label(settings_frame, text="OpenAI API Key:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.openai_key_var = tk.StringVar()
        self.openai_key_entry = ttk.Entry(settings_frame, textvariable=self.openai_key_var, 
                                        width=45, show="*")
        self.openai_key_entry.grid(row=2, column=1, sticky=tk.EW, pady=2)
        
        # OpenAI key management buttons
        key_buttons_frame = ttk.Frame(settings_frame)
        key_buttons_frame.grid(row=2, column=2, sticky=tk.W, padx=(5, 0))
        ttk.Button(key_buttons_frame, text="Save", command=self.save_openai_key).pack(side=tk.LEFT, padx=2)
        ttk.Button(key_buttons_frame, text="Load", command=self.load_openai_key).pack(side=tk.LEFT, padx=2)
        
        # Model selection
        ttk.Label(settings_frame, text="OpenAI Model:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.selected_model_var = tk.StringVar(value="gpt-4o-mini")
        self.model_combobox = ttk.Combobox(settings_frame, textvariable=self.selected_model_var, 
                                          state="readonly", width=45)
        self.model_combobox.grid(row=3, column=1, sticky=tk.EW, pady=2)
        
        # Model refresh button
        ttk.Button(settings_frame, text="Refresh", command=self.refresh_models).grid(row=3, column=2, sticky=tk.W, padx=(5, 0))
        
        # Model info label
        self.model_info_label = ttk.Label(settings_frame, text="Select a model to see pricing information", 
                                         font=("Arial", 8), foreground="gray")
        self.model_info_label.grid(row=4, column=0, columnspan=3, sticky=tk.W, pady=(0, 2))
        
        # Pricing update info
        self.pricing_info_label = ttk.Label(settings_frame, text="", 
                                           font=("Arial", 7), foreground="blue")
        self.pricing_info_label.grid(row=5, column=0, columnspan=3, sticky=tk.W, pady=(0, 5))
        
        # Bind model selection event
        self.model_combobox.bind('<<ComboboxSelected>>', self.on_model_selected)
        
        # Buttons
        button_frame = ttk.Frame(settings_frame)
        button_frame.grid(row=6, column=0, columnspan=3, pady=10)
        
        ttk.Button(button_frame, text="Connect", 
                  command=self.test_connection).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Save Configuration", 
                  command=self.save_configuration).pack(side=tk.LEFT, padx=5)
        
        # Configure grid weights
        settings_frame.columnconfigure(1, weight=1)
        
        # Privacy notice
        privacy_frame = ttk.LabelFrame(self.connection_frame, text="🔒 Privacy Protection", padding=10)
        privacy_frame.pack(fill=tk.X, padx=10, pady=5)
        
        privacy_text = """✓ Student names are automatically anonymized before sending to ChatGPT
✓ Only anonymized content (Student_001, Student_002, etc.) is processed by AI
✓ Real names are stored securely and restored for final grade upload
✓ Your Canvas API token is stored locally and encrypted"""
        
        privacy_label = tk.Label(privacy_frame, text=privacy_text, justify=tk.LEFT, 
                               fg="darkgreen", font=("Arial", 9))
        privacy_label.pack(anchor=tk.W)
        
        # Connection status
        self.status_frame = ttk.LabelFrame(self.connection_frame, text="Connection Status", padding=10)
        self.status_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.status_text = scrolledtext.ScrolledText(self.status_frame, height=12, state=tk.DISABLED)
        self.status_text.pack(fill=tk.BOTH, expand=True)
        
        # Instructions
        instructions = """
🚀 Canvas API Setup Instructions:

1. Log into your Canvas LMS account
2. Go to Account Settings (click your profile picture → Settings)
3. Scroll down to "Approved Integrations" section
4. Click "+ New Access Token"
5. Enter a purpose (e.g., "Grading Agent")
6. Click "Generate Token"
7. Copy the generated token and paste it above
8. Enter your Canvas URL (e.g., https://yourschool.instructure.com)
9. Click "Test Connection"

⚠️  Keep your API token secure and don't share it!

🔒 Privacy Note: Student names will be anonymized before sending to ChatGPT
"""
        self.log_message(instructions)
    
    def setup_two_step_tab(self):
        """Setup two-step grading workflow tab"""
        self.two_step_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.two_step_frame, text="📋 Two-Step Grading")
        
        # Header with explanation
        header_frame = ttk.LabelFrame(self.two_step_frame, text="🔒 Two-Step Workflow with Privacy Protection", padding=10)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        explanation = """Step 1: Download → Grade → Create Review Folder (with anonymized processing)
Step 2: Manual Review → Edit Grades → Upload to Canvas

This workflow allows you to review and modify AI grades before uploading to Canvas."""
        
        tk.Label(header_frame, text=explanation, justify=tk.LEFT, font=("Arial", 9)).pack(anchor=tk.W)
        
        # Course and Assignment Selection
        selection_frame = ttk.LabelFrame(self.two_step_frame, text="Assignment Selection", padding=10)
        selection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Course selection
        course_row = ttk.Frame(selection_frame)
        course_row.pack(fill=tk.X, pady=2)
        ttk.Label(course_row, text="Course:").pack(side=tk.LEFT, padx=5)
        ttk.Button(course_row, text="Refresh Courses", 
                  command=self.load_courses).pack(side=tk.LEFT, padx=5)
        
        self.course_var = tk.StringVar()
        self.course_combo = ttk.Combobox(course_row, textvariable=self.course_var, 
                                       width=70, state="readonly")
        self.course_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        self.course_combo.bind('<<ComboboxSelected>>', self.on_course_selected)
        
        # Assignment selection
        assignment_row = ttk.Frame(selection_frame)
        assignment_row.pack(fill=tk.X, pady=2)
        ttk.Label(assignment_row, text="Assignment:").pack(side=tk.LEFT, padx=5)
        
        self.assignment_var = tk.StringVar()
        self.assignment_combo = ttk.Combobox(assignment_row, textvariable=self.assignment_var,
                                           width=70, state="readonly")
        self.assignment_combo.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        
        # Rubric selection
        rubric_frame = ttk.LabelFrame(self.two_step_frame, text="Grading Configuration", padding=10)
        rubric_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Rubric source selection
        rubric_source_row = ttk.Frame(rubric_frame)
        rubric_source_row.pack(fill=tk.X, pady=2)
        
        ttk.Label(rubric_source_row, text="Rubric Source:").pack(side=tk.LEFT, padx=5)
        self.rubric_source_var = tk.StringVar(value="local")
        self.local_rubric_radio = ttk.Radiobutton(rubric_source_row, text="Local File", 
                                                variable=self.rubric_source_var, value="local",
                                                command=self.on_rubric_source_changed)
        self.local_rubric_radio.pack(side=tk.LEFT, padx=5)
        
        self.canvas_rubric_radio = ttk.Radiobutton(rubric_source_row, text="Canvas Rubric", 
                                                 variable=self.rubric_source_var, value="canvas",
                                                 command=self.on_rubric_source_changed)
        self.canvas_rubric_radio.pack(side=tk.LEFT, padx=5)
        
        # Local rubric file selection
        self.local_rubric_row = ttk.Frame(rubric_frame)
        ttk.Label(self.local_rubric_row, text="Rubric File:").pack(side=tk.LEFT, padx=5)
        self.rubric_path_var = tk.StringVar(value="sample_rubric.json")
        self.rubric_entry = ttk.Entry(self.local_rubric_row, textvariable=self.rubric_path_var, width=50)
        self.rubric_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(self.local_rubric_row, text="Browse", 
                  command=self.browse_rubric).pack(side=tk.LEFT, padx=5)
        
        # Canvas rubric info (initially hidden)
        self.canvas_rubric_row = ttk.Frame(rubric_frame)
        canvas_rubric_label = ttk.Label(self.canvas_rubric_row, 
                                      text="✓ Canvas rubric will be downloaded automatically from the selected assignment")
        canvas_rubric_label.pack(side=tk.LEFT, padx=5)
        
        # Initially show local rubric row (default selection)
        self.local_rubric_row.pack(fill=tk.X, pady=2)
        
        # Instructor configuration
        instructor_row = ttk.Frame(rubric_frame)
        instructor_row.pack(fill=tk.X, pady=2)
        ttk.Label(instructor_row, text="Instructor Config:").pack(side=tk.LEFT, padx=5)
        self.instructor_config_var = tk.StringVar(value="grading_instructor_config.json")
        self.instructor_entry = ttk.Entry(instructor_row, textvariable=self.instructor_config_var, width=50)
        self.instructor_entry.pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
        ttk.Button(instructor_row, text="Browse", 
                  command=self.browse_instructor_config).pack(side=tk.LEFT, padx=5)
        ttk.Button(instructor_row, text="Optional", 
                  command=self.clear_instructor_config).pack(side=tk.LEFT, padx=2)
        
        # Step buttons
        steps_frame = ttk.LabelFrame(self.two_step_frame, text="Grading Steps", padding=10)
        steps_frame.pack(fill=tk.X, padx=10, pady=5)
        
        step1_row = ttk.Frame(steps_frame)
        step1_row.pack(fill=tk.X, pady=5)
        
        self.step1_button = ttk.Button(step1_row, text="📥 Step 1: Download & Grade", 
                                     command=self.start_step1, state=tk.DISABLED)
        self.step1_button.pack(side=tk.LEFT, padx=5)
        
        self.step1_status = tk.Label(step1_row, text="Ready", fg="blue")
        self.step1_status.pack(side=tk.LEFT, padx=10)
        
        step2_row = ttk.Frame(steps_frame)
        step2_row.pack(fill=tk.X, pady=5)
        
        self.step2_button = ttk.Button(step2_row, text="📤 Step 2: Review & Upload", 
                                     command=self.start_step2, state=tk.DISABLED)
        self.step2_button.pack(side=tk.LEFT, padx=5)
        
        self.open_folder_button = ttk.Button(step2_row, text="📁 Open Review Folder", 
                                           command=self.open_review_folder, state=tk.DISABLED)
        self.open_folder_button.pack(side=tk.LEFT, padx=5)
        
        self.step2_status = tk.Label(step2_row, text="Waiting for Step 1", fg="gray")
        self.step2_status.pack(side=tk.LEFT, padx=10)
        
        # Progress bar
        self.progress_two_step = ttk.Progressbar(steps_frame, mode='determinate')
        self.progress_two_step.pack(fill=tk.X, pady=5)
        
        # Progress description label
        self.progress_desc_two_step = tk.Label(steps_frame, text="Ready", fg="blue", font=("Arial", 9))
        self.progress_desc_two_step.pack(fill=tk.X, pady=(0, 5))
        
        # Log area
        log_frame = ttk.LabelFrame(self.two_step_frame, text="Process Log", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.two_step_log = scrolledtext.ScrolledText(log_frame, height=12, state=tk.DISABLED)
        self.two_step_log.pack(fill=tk.BOTH, expand=True)
    
    def setup_single_step_tab(self):
        """Setup single-step grading (original workflow) tab"""
        self.single_step_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.single_step_frame, text="⚡ Single-Step Grading")
        
        # Header
        header_frame = ttk.LabelFrame(self.single_step_frame, text="⚡ Single-Step Workflow (Original)", padding=10)
        header_frame.pack(fill=tk.X, padx=10, pady=5)
        
        explanation = """Original workflow: Download → Grade → Upload (all automatic)
Still includes privacy protection with student name anonymization."""
        
        tk.Label(header_frame, text=explanation, justify=tk.LEFT, font=("Arial", 9)).pack(anchor=tk.W)
        
        # Course and Assignment Selection (reuse from two-step)
        selection_frame = ttk.LabelFrame(self.single_step_frame, text="Assignment Selection", padding=10)
        selection_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # Note: These will reference the same variables as two-step tab
        course_row = ttk.Frame(selection_frame)
        course_row.pack(fill=tk.X, pady=2)
        ttk.Label(course_row, text="Course:").pack(side=tk.LEFT, padx=5)
        course_info_label = tk.Label(course_row, text="(Use course selection from Two-Step tab)", fg="gray")
        course_info_label.pack(side=tk.LEFT, padx=10)
        
        assignment_row = ttk.Frame(selection_frame)
        assignment_row.pack(fill=tk.X, pady=2)
        ttk.Label(assignment_row, text="Assignment:").pack(side=tk.LEFT, padx=5)
        assignment_info_label = tk.Label(assignment_row, text="(Use assignment selection from Two-Step tab)", fg="gray")
        assignment_info_label.pack(side=tk.LEFT, padx=10)
        
        # Options
        options_frame = ttk.LabelFrame(self.single_step_frame, text="Options", padding=10)
        options_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.upload_grades_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Upload grades to Canvas automatically", 
                       variable=self.upload_grades_var).pack(anchor=tk.W, pady=2)
        
        self.save_backup_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(options_frame, text="Save local backup of results", 
                       variable=self.save_backup_var).pack(anchor=tk.W, pady=2)
        
        # Start button
        grading_control_frame = ttk.Frame(self.single_step_frame)
        grading_control_frame.pack(fill=tk.X, padx=10, pady=10)
        
        self.single_step_button = ttk.Button(grading_control_frame, text="🚀 Start Single-Step Grading", 
                                           command=self.start_single_step, state=tk.DISABLED)
        self.single_step_button.pack(side=tk.LEFT, padx=5)
        
        # Progress bar
        progress_frame = ttk.Frame(grading_control_frame)
        progress_frame.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        
        self.progress_single = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress_single.pack(fill=tk.X)
        
        # Progress description label
        self.progress_desc_single = tk.Label(progress_frame, text="Ready", fg="blue", font=("Arial", 9))
        self.progress_desc_single.pack(fill=tk.X)
        
        # Log area
        log_frame = ttk.LabelFrame(self.single_step_frame, text="Grading Progress", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        self.single_step_log = scrolledtext.ScrolledText(log_frame, height=12, state=tk.DISABLED)
        self.single_step_log.pack(fill=tk.BOTH, expand=True)
    
    def setup_results_tab(self):
        """Setup results viewing tab"""
        self.results_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.results_frame, text="📊 Results")
        
        # Results summary
        summary_frame = ttk.LabelFrame(self.results_frame, text="Grading Summary", padding=10)
        summary_frame.pack(fill=tk.X, padx=10, pady=5)
        
        self.summary_text = tk.Text(summary_frame, height=6, state=tk.DISABLED)
        self.summary_text.pack(fill=tk.X)
        
        # Recent assignment folders
        folders_frame = ttk.LabelFrame(self.results_frame, text="Recent Assignment Folders", padding=10)
        folders_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Folder list
        folder_list_frame = ttk.Frame(folders_frame)
        folder_list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.folder_listbox = tk.Listbox(folder_list_frame)
        folder_scrollbar = ttk.Scrollbar(folder_list_frame, orient=tk.VERTICAL, 
                                       command=self.folder_listbox.yview)
        self.folder_listbox.configure(yscrollcommand=folder_scrollbar.set)
        
        self.folder_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        folder_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # Folder buttons
        folder_buttons = ttk.Frame(folders_frame)
        folder_buttons.pack(fill=tk.X, pady=5)
        
        ttk.Button(folder_buttons, text="📁 Open Selected Folder", 
                  command=self.open_selected_folder).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_buttons, text="🔄 Refresh List", 
                  command=self.refresh_folder_list).pack(side=tk.LEFT, padx=5)
        ttk.Button(folder_buttons, text="📄 Export Summary", 
                  command=self.export_summary).pack(side=tk.LEFT, padx=5)
        
        # Load initial folder list
        self.refresh_folder_list()
    
    def load_existing_config(self):
        """Load existing Canvas and OpenAI configuration if available"""
        # Load Canvas config from JSON file (legacy)
        config_file = "canvas_config.json"
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                self.canvas_url_var.set(config.get('canvas_url', ''))
                self.api_token_var.set(config.get('api_token', ''))
                
                self.log_message("Loaded existing Canvas configuration")
                
            except Exception as e:
                self.log_message(f"Error loading Canvas configuration: {e}")
        
        # Load encrypted credentials
        try:
            # Check if encrypted config exists without trying to decrypt
            if self.key_manager.key_manager.has_config():
                # We have encrypted data but need password to access it
                # Don't automatically prompt - let user click "Load" when ready
                self.log_message("🔐 Encrypted credentials found - click 'Load' buttons to access")
            else:
                self.log_message("📝 No saved credentials found")
                
        except Exception as e:
            self.log_message(f"❌ Error loading saved credentials: {e}")
    
    def test_connection(self):
        """Test Canvas API connection"""
        canvas_url = self.canvas_url_var.get().strip()
        api_token = self.api_token_var.get().strip()
        
        if not canvas_url or not api_token:
            messagebox.showerror("Error", "Please enter both Canvas URL and API token")
            return
        
        try:
            self.log_message("Testing Canvas connection...")
            self.canvas_api = CanvasAPI(canvas_url, api_token)
            
            # Test with a simple API call
            courses = self.canvas_api.get_courses()
            
            self.log_message(f"✓ Successfully connected to Canvas!")
            self.log_message(f"Found {len(courses)} courses in your account")
            self.log_message(f"Privacy protection: Student names will be anonymized for AI processing")
            
            # Initialize grading systems with OpenAI API key and selected model
            openai_key = self.openai_key_var.get().strip()
            if not openai_key:
                raise ValueError("OpenAI API key is required for grading functionality")
            
            selected_model = self.selected_model_var.get() or "gpt-4o-mini"
            self.grading_agent = GradingAgent(openai_key, model=selected_model)
            self.two_step_grading = TwoStepCanvasGrading(self.canvas_api, self.grading_agent)
            
            # Enable grading tabs
            self.step1_button.config(state=tk.NORMAL)
            self.single_step_button.config(state=tk.NORMAL)
            
            # Auto-load courses after successful connection
            self.log_message("📚 Auto-loading courses...")
            self.load_courses_from_api(courses)
            
            messagebox.showinfo("Success", f"Connected successfully! Found {len(courses)} courses.\n\nPrivacy protection enabled: Student names will be anonymized.")
            
        except Exception as e:
            self.log_message(f"✗ Connection failed: {e}")
            messagebox.showerror("Connection Error", f"Failed to connect to Canvas:\n{e}")
    
    def save_openai_key(self):
        """Save OpenAI API key securely"""
        api_key = self.openai_key_var.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key")
            return
        
        try:
            if self.key_manager.save_openai_key(api_key, password_callback=self.password_callback):
                self.log_message("✅ OpenAI API key saved securely")
                # Initialize model manager with new key
                self.refresh_models()
            else:
                messagebox.showerror("Error", "Failed to save API key")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving API key: {e}")
    
    def load_openai_key(self):
        """Load saved OpenAI API key"""
        try:
            api_key = self.key_manager.get_openai_key(password_callback=self.password_callback)
            if api_key:
                self.openai_key_var.set(api_key)
                self.log_message("✅ Loaded saved OpenAI API key")
                self.refresh_models()
            else:
                messagebox.showinfo("Info", "No saved API key found")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading API key: {e}")
    
    def refresh_models(self):
        """Refresh available OpenAI models"""
        api_key = self.openai_key_var.get().strip()
        if not api_key:
            self.log_message("❌ Please enter an OpenAI API key first")
            return
        
        def fetch_models():
            try:
                self.log_message("🔄 Fetching available OpenAI models and current pricing...")
                
                self.model_manager = OpenAIModelManager(api_key)
                models = self.model_manager.get_available_models()
                
                # Update UI in main thread
                self.root.after(0, lambda: self.update_models_ui(models))
                
            except Exception as e:
                self.root.after(0, lambda: self.handle_model_fetch_error(str(e)))
        
        # Run in background thread
        threading.Thread(target=fetch_models, daemon=True).start()
    
    def update_models_ui(self, models):
        """Update the models UI with fetched models"""
        try:
            self.available_models = models
            model_values = [model['display_text'] for model in models]
            self.model_combobox['values'] = model_values
            
            # Set default selection
            if models:
                # Try to find GPT-4o Mini as default
                default_idx = 0
                for i, model in enumerate(models):
                    if 'gpt-4o-mini' in model['id']:
                        default_idx = i
                        break
                
                self.model_combobox.current(default_idx)
                self.selected_model_var.set(models[default_idx]['id'])
                self.update_model_info(models[default_idx])
            
            self.log_message(f"✅ Loaded {len(models)} available models")
            
            # Update pricing info
            if self.model_manager:
                pricing_updated = self.model_manager.get_pricing_last_updated()
                if pricing_updated:
                    self.pricing_info_label.config(
                        text=f"💰 Pricing updated: {pricing_updated.strftime('%Y-%m-%d %H:%M')} (dynamic from OpenAI API)"
                    )
                else:
                    self.pricing_info_label.config(text="💰 Using fallback pricing data")
            
        except Exception as e:
            self.log_message(f"❌ Error updating models UI: {e}")
    
    def handle_model_fetch_error(self, error_msg):
        """Handle error when fetching models"""
        self.log_message(f"❌ Error fetching models: {error_msg}")
        self.model_info_label.config(text="Error loading models - check API key and connection")
    
    def on_model_selected(self, event=None):
        """Handle model selection"""
        try:
            selection_idx = self.model_combobox.current()
            if selection_idx >= 0 and self.available_models:
                selected_model = self.available_models[selection_idx]
                self.selected_model_var.set(selected_model['id'])
                self.update_model_info(selected_model)
        except Exception as e:
            self.log_message(f"❌ Error selecting model: {e}")
    
    def update_model_info(self, model_info):
        """Update model information display"""
        try:
            info_text = (f"{model_info['description']} • "
                        f"Input: ${model_info['input_price']:.4f}/1K • "
                        f"Output: ${model_info['output_price']:.4f}/1K tokens")
            self.model_info_label.config(text=info_text)
        except Exception as e:
            self.model_info_label.config(text="Model information unavailable")
    
    def save_configuration(self):
        """Save Canvas configuration to both legacy file and secure storage"""
        canvas_url = self.canvas_url_var.get().strip()
        api_token = self.api_token_var.get().strip()
        openai_key = self.openai_key_var.get().strip()
        
        # Save to legacy file for backward compatibility
        config = {
            'canvas_url': canvas_url,
            'api_token': api_token,
            'created_at': datetime.now().isoformat()
        }
        
        try:
            with open("canvas_config.json", 'w') as f:
                json.dump(config, f, indent=2)
            
            # Save to secure storage
            if canvas_url and api_token:
                self.key_manager.save_canvas_credentials(canvas_url, api_token, password_callback=self.password_callback)
                self.log_message("✅ Canvas credentials saved securely")
            
            if openai_key:
                self.key_manager.save_openai_key(openai_key, password_callback=self.password_callback)
                self.log_message("✅ OpenAI API key saved securely")
            
            self.log_message("Configuration saved successfully")
            messagebox.showinfo("Success", "Configuration saved with secure encryption")
            
        except Exception as e:
            self.log_message(f"Error saving configuration: {e}")
            messagebox.showerror("Error", f"Failed to save configuration:\n{e}")
    
    def load_courses(self):
        """Load courses from Canvas"""
        if not self.canvas_api:
            messagebox.showerror("Error", "Please connect to Canvas first")
            return
        
        try:
            self.log_two_step("Loading courses from Canvas...")
            courses = self.canvas_api.get_courses()
            self.load_courses_from_api(courses)
            
        except Exception as e:
            self.log_two_step(f"Error loading courses: {e}")
            messagebox.showerror("Error", f"Failed to load courses:\n{e}")
    
    def load_courses_from_api(self, courses):
        """Helper method to load courses from API response"""
        self.current_courses = courses
        course_options = []
        
        for course in courses:
            name = course.get('name', 'Unnamed Course')
            course_id = course['id']
            course_options.append(f"{name} (ID: {course_id})")
        
        self.course_combo['values'] = course_options
        self.log_two_step(f"Loaded {len(courses)} courses")
    
    def on_course_selected(self, event):
        """Handle course selection"""
        selected = self.course_combo.current()
        if selected >= 0:
            course = self.current_courses[selected]
            course_id = course['id']
            
            try:
                self.log_two_step(f"Loading assignments for course: {course['name']}")
                assignments = self.canvas_api.get_assignments(course_id)
                
                self.current_assignments = assignments
                assignment_options = []
                
                for assignment in assignments:
                    name = assignment.get('name', 'Unnamed Assignment')
                    assignment_id = assignment['id']
                    due_date = assignment.get('due_at', 'No due date')
                    assignment_options.append(f"{name} (ID: {assignment_id}) - Due: {due_date}")
                
                self.assignment_combo['values'] = assignment_options
                self.log_two_step(f"Loaded {len(assignments)} assignments")
                
            except Exception as e:
                self.log_two_step(f"Error loading assignments: {e}")
                messagebox.showerror("Error", f"Failed to load assignments:\n{e}")
    
    def browse_rubric(self):
        """Browse for rubric file"""
        filename = filedialog.askopenfilename(
            title="Select Rubric File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.rubric_path_var.set(filename)
    
    def browse_instructor_config(self):
        """Browse for instructor configuration file"""
        filename = filedialog.askopenfilename(
            title="Select Instructor Configuration File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.instructor_config_var.set(filename)
    
    def clear_instructor_config(self):
        """Clear instructor configuration (make it optional)"""
        self.instructor_config_var.set("")
        messagebox.showinfo("Info", "Instructor configuration cleared. Default grading style will be used.")
    
    def on_rubric_source_changed(self):
        """Handle rubric source selection change"""
        try:
            source = self.rubric_source_var.get()
            
            if source == "local":
                # Show local rubric row, hide canvas rubric row
                self.canvas_rubric_row.pack_forget()
                self.local_rubric_row.pack(fill=tk.X, pady=2)
            else:  # canvas
                # Hide local rubric row, show canvas rubric row
                self.local_rubric_row.pack_forget()
                self.canvas_rubric_row.pack(fill=tk.X, pady=2)
        except Exception as e:
            # If there's an issue with packing, just ignore it during initialization
            print(f"Note: Rubric source change handled during initialization: {e}")
    
    def validate_grading_inputs(self):
        """Validate inputs before starting grading"""
        if not self.canvas_api:
            messagebox.showerror("Error", "Please connect to Canvas first")
            return False
        
        if self.course_combo.current() < 0:
            messagebox.showerror("Error", "Please select a course")
            return False
        
        if self.assignment_combo.current() < 0:
            messagebox.showerror("Error", "Please select an assignment")
            return False
        
        # Validate rubric based on source
        if self.rubric_source_var.get() == "local":
            rubric_path = self.rubric_path_var.get().strip()
            if not rubric_path or not os.path.exists(rubric_path):
                messagebox.showerror("Error", "Please select a valid rubric file")
                return False
        # For Canvas rubric, validation will happen during download
        
        return True
    
    def start_step1(self):
        """Start Step 1 of two-step process"""
        if not self.validate_grading_inputs():
            return
        
        # Run in separate thread
        thread = threading.Thread(target=self.run_step1, daemon=True)
        thread.start()
    
    def run_step1(self):
        """Run Step 1 in background thread"""
        try:
            # Get selected data
            course = self.current_courses[self.course_combo.current()]
            assignment = self.current_assignments[self.assignment_combo.current()]
            
            # Determine rubric settings
            use_canvas_rubric = (self.rubric_source_var.get() == "canvas")
            rubric_path = None if use_canvas_rubric else self.rubric_path_var.get().strip()
            
            # Get instructor configuration (optional)
            instructor_config_path = self.instructor_config_var.get().strip()
            if not instructor_config_path or not os.path.exists(instructor_config_path):
                instructor_config_path = None
            
            # Update UI
            self.root.after(0, lambda: self.update_progress_two_step(10, "Initializing..."))
            self.root.after(0, lambda: self.step1_button.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.step1_status.config(text="Running...", fg="orange"))
            
            self.log_two_step("Starting Step 1: Download and Grade with Privacy Protection")
            self.log_two_step(f"Course: {course['name']}")
            self.log_two_step(f"Assignment: {assignment['name']}")
            if use_canvas_rubric:
                self.log_two_step("Will download Canvas rubric automatically")
            else:
                self.log_two_step(f"Using local rubric: {os.path.basename(rubric_path)}")
            
            if instructor_config_path:
                self.log_two_step(f"Using instructor config: {os.path.basename(instructor_config_path)}")
            else:
                self.log_two_step("Using default grading style")
            
            self.log_two_step(f"Student names will be anonymized for ChatGPT processing")
            
            # Update progress
            self.root.after(0, lambda: self.update_progress_two_step(30, "Downloading submissions..."))
            
            # Create progress callback that updates the GUI
            def progress_update(percent, description):
                self.root.after(0, lambda: self.update_progress_two_step(percent, description))
            
            # Run Step 1 with new parameters
            results = self.two_step_grading.step1_download_and_grade(
                course_id=course['id'],
                assignment_id=assignment['id'],
                assignment_name=assignment['name'],
                rubric_path=rubric_path,
                instructor_config_path=instructor_config_path,
                use_canvas_rubric=use_canvas_rubric,
                progress_callback=progress_update
            )
            
            # Store results for Step 2
            self.current_step1_results = results
            
            # Update metadata file with Canvas IDs
            if results['success']:
                metadata_file = os.path.join(results['folder_path'], "assignment_metadata.json")
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                metadata['course_id'] = course['id']
                metadata['assignment_id'] = assignment['id']
                with open(metadata_file, 'w') as f:
                    json.dump(metadata, f, indent=2)
            
            # Update UI based on results
            self.root.after(0, lambda: self.handle_step1_completion(results))
            
        except Exception as e:
            self.log_two_step(f"ERROR in Step 1: {e}")
            self.root.after(0, lambda: messagebox.showerror("Step 1 Error", f"Step 1 failed:\n{e}"))
            self.root.after(0, lambda: self.step1_status.config(text="Failed", fg="red"))
        
        finally:
            # Re-enable UI
            self.root.after(0, lambda: self.reset_progress_two_step())
            self.root.after(0, lambda: self.step1_button.config(state=tk.NORMAL))
    
    def handle_step1_completion(self, results):
        """Handle Step 1 completion"""
        if results['success']:
            self.update_progress_two_step(100, "Step 1 complete!")
            self.step1_status.config(text="✓ Complete", fg="green")
            self.step2_button.config(state=tk.NORMAL)
            self.open_folder_button.config(state=tk.NORMAL)
            self.step2_status.config(text="Ready for review", fg="blue")
            
            self.log_two_step("✓ Step 1 completed successfully!")
            self.log_two_step(f"Graded {len(results.get('grading_results', {}))} submissions")
            self.log_two_step(f"Review folder: {results['folder_path']}")
            self.log_two_step("Next: Review the spreadsheet and run Step 2")
            
            # Ask if user wants to open the folder
            graded_count = len(results.get('grading_results', {}))
            response = messagebox.askyesno(
                "Step 1 Complete", 
                f"Step 1 completed successfully!\n\n"
                f"Created folder: {results['assignment_folder']}\n"
                f"Graded: {graded_count} submissions\n\n"
                f"Would you like to open the review folder now?"
            )
            
            if response:
                self.open_review_folder()
        else:
            self.step1_status.config(text="Failed", fg="red")
            self.log_two_step(f"Step 1 failed: {results['message']}")
    
    def open_review_folder(self):
        """Open the review folder in file explorer"""
        if not self.current_step1_results or not self.current_step1_results['success']:
            messagebox.showwarning("Warning", "No completed Step 1 results available")
            return
        
        folder_path = self.current_step1_results['folder_path']
        
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")
    
    def start_step2(self):
        """Start Step 2 of two-step process"""
        if not self.current_step1_results or not self.current_step1_results['success']:
            messagebox.showerror("Error", "Please complete Step 1 first")
            return
        
        # Confirm the user has reviewed the spreadsheet
        response = messagebox.askyesno(
            "Confirm Step 2",
            "Have you reviewed and edited the grade spreadsheet as needed?\n\n"
            "Step 2 will upload the grades from the spreadsheet to Canvas."
        )
        
        if not response:
            return
        
        # Run in separate thread
        thread = threading.Thread(target=self.run_step2, daemon=True)
        thread.start()
    
    def run_step2(self):
        """Run Step 2 in background thread"""
        try:
            # Update UI
            self.root.after(0, lambda: self.update_progress_two_step(10, "Reading spreadsheet..."))
            self.root.after(0, lambda: self.step2_button.config(state=tk.DISABLED))
            self.root.after(0, lambda: self.step2_status.config(text="Uploading...", fg="orange"))
            
            self.log_two_step("Starting Step 2: Review and Upload")
            self.log_two_step("Reading edited spreadsheet and uploading to Canvas...")
            
            # Update progress
            self.root.after(0, lambda: self.update_progress_two_step(40, "Uploading grades to Canvas..."))
            
            # Run Step 2
            folder_path = self.current_step1_results['folder_path']
            results = self.two_step_grading.step2_review_and_upload(folder_path)
            
            # Update progress
            self.root.after(0, lambda: self.update_progress_two_step(90, "Finalizing upload..."))
            
            # Update UI based on results
            self.root.after(0, lambda: self.handle_step2_completion(results))
            
        except Exception as e:
            self.log_two_step(f"ERROR in Step 2: {e}")
            self.root.after(0, lambda: messagebox.showerror("Step 2 Error", f"Step 2 failed:\n{e}"))
            self.root.after(0, lambda: self.step2_status.config(text="Failed", fg="red"))
        
        finally:
            # Re-enable UI
            self.root.after(0, lambda: self.reset_progress_two_step())
            self.root.after(0, lambda: self.step2_button.config(state=tk.NORMAL))
    
    def handle_step2_completion(self, results):
        """Handle Step 2 completion"""
        if results['success']:
            self.update_progress_two_step(100, "Upload complete!")
            self.step2_status.config(text="✓ Complete", fg="green")
            
            self.log_two_step("✓ Step 2 completed successfully!")
            self.log_two_step(f"Uploaded {results['uploaded_count']} grades to Canvas")
            
            messagebox.showinfo(
                "Step 2 Complete",
                f"Grades uploaded successfully!\n\n"
                f"Uploaded: {results['uploaded_count']} grades\n"
                f"Total: {results['total_grades']} submissions\n\n"
                f"Check your Canvas gradebook to verify the uploads."
            )
            
            # Refresh folder list
            self.refresh_folder_list()
        else:
            self.step2_status.config(text="Failed", fg="red")
            self.log_two_step(f"Step 2 failed: {results['message']}")
    
    def start_single_step(self):
        """Start single-step grading process"""
        if not self.validate_grading_inputs():
            return
        
        # Run in separate thread
        thread = threading.Thread(target=self.run_single_step, daemon=True)
        thread.start()
    
    def run_single_step(self):
        """Run single-step grading in background thread"""
        try:
            # Get selected data
            course = self.current_courses[self.course_combo.current()]
            assignment = self.current_assignments[self.assignment_combo.current()]
            rubric_path = self.rubric_path_var.get().strip()
            upload_grades = self.upload_grades_var.get()
            
            # Update UI
            self.root.after(0, lambda: self.update_progress_single(10, "Initializing grading..."))
            self.root.after(0, lambda: self.single_step_button.config(state=tk.DISABLED))
            
            self.log_single_step("Starting single-step grading with privacy protection")
            self.log_single_step(f"Course: {course['name']}")
            self.log_single_step(f"Assignment: {assignment['name']}")
            self.log_single_step(f"Upload grades: {upload_grades}")
            self.log_single_step(f"Student names will be anonymized for ChatGPT processing")
            
            # Update progress
            self.root.after(0, lambda: self.update_progress_single(30, "Processing submissions..."))
            
            # Use the original integration for single-step
            from canvas_integration import CanvasGradingIntegration
            original_integration = CanvasGradingIntegration(self.canvas_api, self.grading_agent)
            
            # Update progress
            self.root.after(0, lambda: self.update_progress_single(70, "Grading with AI..."))
            
            # Run grading
            results = original_integration.grade_canvas_assignment(
                course_id=course['id'],
                assignment_id=assignment['id'],
                rubric_path=rubric_path,
                upload_grades=upload_grades
            )
            
            # Update progress
            self.root.after(0, lambda: self.update_progress_single(90, "Finalizing results..."))
            
            # Update UI with results
            self.root.after(0, lambda: self.display_single_step_results(results))
            
        except Exception as e:
            self.log_single_step(f"ERROR: {e}")
            self.root.after(0, lambda: messagebox.showerror("Grading Error", f"An error occurred:\n{e}"))
        
        finally:
            # Re-enable UI
            self.root.after(0, lambda: self.reset_progress_single())
            self.root.after(0, lambda: self.single_step_button.config(state=tk.NORMAL))
    
    def display_single_step_results(self, results):
        """Display single-step grading results"""
        # Update progress to complete
        self.update_progress_single(100, "Grading complete!")
        
        # Switch to results tab
        self.notebook.select(3)
        
        # Update summary
        self.summary_text.config(state=tk.NORMAL)
        self.summary_text.delete(1.0, tk.END)
        
        if results['success']:
            stats = results['stats']
            summary = f"""Single-Step Grading Completed!

Total Submissions: {stats['total']}
Successfully Graded: {stats['graded']}
Uploaded to Canvas: {stats['uploaded']}

Results exported to: {results.get('results_file', 'N/A')}

Privacy Protection: Student names were anonymized for AI processing
"""
        else:
            summary = f"Grading Failed: {results['message']}"
        
        self.summary_text.insert(tk.END, summary)
        self.summary_text.config(state=tk.DISABLED)
        
        # Log completion
        self.log_single_step("Single-step grading completed!")
        self.log_single_step(f"Results: {results['message']}")
        
        # Refresh folder list
        self.refresh_folder_list()
    
    def refresh_folder_list(self):
        """Refresh the list of assignment folders"""
        self.folder_listbox.delete(0, tk.END)
        
        # Find assignment folders in current directory
        try:
            for item in os.listdir(os.getcwd()):
                if os.path.isdir(item) and '_20' in item:  # Look for date pattern
                    # Check if it's an assignment folder
                    if os.path.exists(os.path.join(item, "INSTRUCTIONS.txt")):
                        self.folder_listbox.insert(tk.END, item)
        except Exception as e:
            self.log_message(f"Error refreshing folder list: {e}")
    
    def open_selected_folder(self):
        """Open selected assignment folder"""
        selection = self.folder_listbox.curselection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a folder first")
            return
        
        folder_name = self.folder_listbox.get(selection[0])
        folder_path = os.path.join(os.getcwd(), folder_name)
        
        try:
            if platform.system() == "Windows":
                os.startfile(folder_path)
            elif platform.system() == "Darwin":  # macOS
                subprocess.run(["open", folder_path])
            else:  # Linux
                subprocess.run(["xdg-open", folder_path])
        except Exception as e:
            messagebox.showerror("Error", f"Could not open folder:\n{e}")
    
    def export_summary(self):
        """Export summary of all grading activities"""
        try:
            filename = filedialog.asksaveasfilename(
                title="Export Summary",
                defaultextension=".txt",
                filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
            )
            if filename:
                with open(filename, 'w') as f:
                    f.write("Canvas Grading Summary\n")
                    f.write("=" * 30 + "\n")
                    f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                    
                    f.write("Assignment Folders:\n")
                    for i in range(self.folder_listbox.size()):
                        folder_name = self.folder_listbox.get(i)
                        f.write(f"- {folder_name}\n")
                
                messagebox.showinfo("Success", f"Summary exported to:\n{filename}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to export summary:\n{e}")
    
    def log_message(self, message):
        """Add message to status log"""
        self.status_text.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.status_text.insert(tk.END, f"[{timestamp}] {message}\n")
        self.status_text.see(tk.END)
        self.status_text.config(state=tk.DISABLED)
    
    def log_two_step(self, message):
        """Add message to two-step log"""
        self.two_step_log.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.two_step_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.two_step_log.see(tk.END)
        self.two_step_log.config(state=tk.DISABLED)
    
    def log_single_step(self, message):
        """Add message to single-step log"""
        self.single_step_log.config(state=tk.NORMAL)
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.single_step_log.insert(tk.END, f"[{timestamp}] {message}\n")
        self.single_step_log.see(tk.END)
        self.single_step_log.config(state=tk.DISABLED)
    
    def update_progress_two_step(self, value, description):
        """Update two-step progress bar and description"""
        self.progress_two_step.config(value=value)
        self.progress_desc_two_step.config(text=description)
        self.root.update_idletasks()
    
    def update_progress_single(self, value, description):
        """Update single-step progress bar and description"""
        self.progress_single.config(value=value)
        self.progress_desc_single.config(text=description)
        self.root.update_idletasks()
    
    def reset_progress_two_step(self):
        """Reset two-step progress bar"""
        self.progress_two_step.config(value=0)
        self.progress_desc_two_step.config(text="Ready")
    
    def reset_progress_single(self):
        """Reset single-step progress bar"""
        self.progress_single.config(value=0)
        self.progress_desc_single.config(text="Ready")
    
    def run(self):
        """Start the GUI application"""
        self.root.mainloop()


if __name__ == "__main__":
    app = CanvasGUI()
    app.run()
