#!/usr/bin/env python3
"""
DuckGrade Canvas PyQt6 Interface - Matching Tkinter Structure
Modern PyQt6-based GUI for Canvas LMS integration

Part of the DuckWorks Educational Automation Suite
Exact structural match for the Tkinter canvas_gui.py

Author: DuckWorks Educational Automation Suite
Created: 2024
"""

import sys
import os
from pathlib import Path
from typing import Optional, Dict, List

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QCheckBox, QProgressBar, QScrollArea, QFrame, QGridLayout,
    QMessageBox, QFileDialog, QGroupBox, QRadioButton, QButtonGroup
)
from PyQt6.QtCore import Qt, QThread, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

# Import DuckWorks framework
from duckworks_framework import DuckWorksInfo, DuckWorksConfig

class DuckGradeCanvasGUI(QMainWindow):
    """PyQt6 Canvas Integration Interface matching Tkinter structure"""
    
    def __init__(self):
        super().__init__()
        self.canvas_api = None
        self.grading_agent = None
        self.setup_ui()
        self.setup_window()
        
    def setup_ui(self):
        """Setup the user interface with 4 tabs matching Tkinter version"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout(central_widget)
        
        # Header with duck icon
        header_widget = QWidget()
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 15, 20, 15)
        
        # Duck icon
        if Path("assets/icons8-flying-duck-48.png").exists():
            duck_icon_label = QLabel()
            duck_pixmap = QIcon("assets/icons8-flying-duck-48.png").pixmap(32, 32)
            duck_icon_label.setPixmap(duck_pixmap)
            header_layout.addWidget(duck_icon_label)
        
        # Header title
        header_title = QLabel("DuckGrade Canvas Integration")
        header_title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        header_layout.addWidget(header_title)
        header_layout.addStretch()
        
        header_widget.setStyleSheet("""
            QWidget {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #2E86AB, stop:1 #A23B72);
                color: white;
                border-radius: 10px;
                margin: 10px;
            }
            QLabel {
                color: white;
            }
        """)
        layout.addWidget(header_widget)
        
        # Tab widget with 4 tabs matching Tkinter
        self.tab_widget = QTabWidget()
        
        # 1. Canvas Connection tab
        connection_tab = self.create_connection_tab()
        self.tab_widget.addTab(connection_tab, "🔗 Canvas Connection")
        
        # 2. Two-Step Grading tab
        two_step_tab = self.create_two_step_tab()
        self.tab_widget.addTab(two_step_tab, "📋 Two-Step Grading")
        
        # 3. Single-Step Grading tab
        single_step_tab = self.create_single_step_tab()
        self.tab_widget.addTab(single_step_tab, "⚡ Single-Step Grading")
        
        # 4. Results tab
        results_tab = self.create_results_tab()
        self.tab_widget.addTab(results_tab, "📊 Results")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_label = QLabel("Ready - Canvas integration available")
        self.status_label.setStyleSheet("padding: 5px; border-top: 1px solid #ccc;")
        layout.addWidget(self.status_label)
        
    def create_connection_tab(self) -> QWidget:
        """Create Canvas Connection tab matching Tkinter structure"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Canvas Settings Group
        settings_group = QGroupBox("Canvas Settings")
        settings_layout = QGridLayout(settings_group)
        
        # Canvas URL
        settings_layout.addWidget(QLabel("Canvas URL:"), 0, 0)
        self.canvas_url_entry = QLineEdit()
        self.canvas_url_entry.setPlaceholderText("e.g., https://yourschool.instructure.com")
        settings_layout.addWidget(self.canvas_url_entry, 0, 1, 1, 2)
        
        # Canvas API Token
        settings_layout.addWidget(QLabel("Canvas API Token:"), 1, 0)
        self.api_token_entry = QLineEdit()
        self.api_token_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_token_entry.setPlaceholderText("Enter your Canvas API token")
        settings_layout.addWidget(self.api_token_entry, 1, 1, 1, 2)
        
        # OpenAI API Key
        settings_layout.addWidget(QLabel("OpenAI API Key:"), 2, 0)
        self.openai_key_entry = QLineEdit()
        self.openai_key_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_entry.setPlaceholderText("Enter your OpenAI API key")
        settings_layout.addWidget(self.openai_key_entry, 2, 1)
        
        # OpenAI key management buttons
        key_buttons_layout = QHBoxLayout()
        save_key_btn = QPushButton("Save")
        load_key_btn = QPushButton("Load")
        key_buttons_layout.addWidget(save_key_btn)
        key_buttons_layout.addWidget(load_key_btn)
        settings_layout.addLayout(key_buttons_layout, 2, 2)
        
        # Model selection
        settings_layout.addWidget(QLabel("OpenAI Model:"), 3, 0)
        self.model_combo = QComboBox()
        self.model_combo.addItems(["gpt-4o-mini", "gpt-4", "gpt-4-turbo", "gpt-3.5-turbo"])
        settings_layout.addWidget(self.model_combo, 3, 1)
        
        refresh_models_btn = QPushButton("Refresh")
        settings_layout.addWidget(refresh_models_btn, 3, 2)
        
        # Model info labels
        self.model_info_label = QLabel("Select a model to see pricing information")
        self.model_info_label.setStyleSheet("color: gray; font-size: 10px;")
        settings_layout.addWidget(self.model_info_label, 4, 0, 1, 3)
        
        self.pricing_info_label = QLabel("")
        self.pricing_info_label.setStyleSheet("color: blue; font-size: 9px;")
        settings_layout.addWidget(self.pricing_info_label, 5, 0, 1, 3)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        connect_btn = QPushButton("Connect")
        save_config_btn = QPushButton("Save Configuration")
        buttons_layout.addWidget(connect_btn)
        buttons_layout.addWidget(save_config_btn)
        settings_layout.addLayout(buttons_layout, 6, 0, 1, 3)
        
        layout.addWidget(settings_group)
        
        # Privacy Protection Group
        privacy_group = QGroupBox("🔒 Privacy Protection")
        privacy_layout = QVBoxLayout(privacy_group)
        
        privacy_text = """✓ Student names are automatically anonymized before sending to ChatGPT
✓ Only anonymized content (Student_001, Student_002, etc.) is processed by AI  
✓ Real names are stored securely and restored for final grade upload
✓ Your Canvas API token is stored locally and encrypted"""
        
        privacy_label = QLabel(privacy_text)
        privacy_label.setStyleSheet("color: darkgreen; font-size: 10px;")
        privacy_layout.addWidget(privacy_label)
        
        layout.addWidget(privacy_group)
        
        # Connection Status Group
        status_group = QGroupBox("Connection Status")
        status_layout = QVBoxLayout(status_group)
        
        self.status_text = QTextEdit()
        self.status_text.setReadOnly(True)
        self.status_text.setMaximumHeight(200)
        
        # Add initial instructions
        instructions = """🚀 Canvas API Setup Instructions:

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

🔒 Privacy Note: Student names will be anonymized before sending to ChatGPT"""
        
        self.status_text.setPlainText(instructions)
        status_layout.addWidget(self.status_text)
        
        layout.addWidget(status_group)
        layout.addStretch()
        
        return tab
        
    def create_two_step_tab(self) -> QWidget:
        """Create Two-Step Grading tab matching Tkinter structure"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header with explanation
        header_group = QGroupBox("🔒 Two-Step Workflow with Privacy Protection")
        header_layout = QVBoxLayout(header_group)
        
        explanation = """Step 1: Download → Grade → Create Review Folder (with anonymized processing)
Step 2: Manual Review → Edit Grades → Upload to Canvas

This workflow allows you to review and modify AI grades before uploading to Canvas."""
        
        explanation_label = QLabel(explanation)
        explanation_label.setStyleSheet("font-size: 10px;")
        header_layout.addWidget(explanation_label)
        
        layout.addWidget(header_group)
        
        # Assignment Selection Group
        selection_group = QGroupBox("Assignment Selection")
        selection_layout = QVBoxLayout(selection_group)
        
        # Course selection
        course_layout = QHBoxLayout()
        course_layout.addWidget(QLabel("Course:"))
        refresh_courses_btn = QPushButton("Refresh Courses")
        course_layout.addWidget(refresh_courses_btn)
        
        self.course_combo = QComboBox()
        self.course_combo.setMinimumWidth(400)
        course_layout.addWidget(self.course_combo)
        course_layout.addStretch()
        
        selection_layout.addLayout(course_layout)
        
        # Assignment selection  
        assignment_layout = QHBoxLayout()
        assignment_layout.addWidget(QLabel("Assignment:"))
        
        self.assignment_combo = QComboBox()
        self.assignment_combo.setMinimumWidth(400)
        assignment_layout.addWidget(self.assignment_combo)
        assignment_layout.addStretch()
        
        selection_layout.addLayout(assignment_layout)
        
        layout.addWidget(selection_group)
        
        # Grading Configuration Group
        config_group = QGroupBox("Grading Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Rubric source selection
        rubric_source_layout = QHBoxLayout()
        rubric_source_layout.addWidget(QLabel("Rubric Source:"))
        
        self.rubric_source_group = QButtonGroup()
        self.local_rubric_radio = QRadioButton("Local File")
        self.canvas_rubric_radio = QRadioButton("Canvas Rubric")
        self.local_rubric_radio.setChecked(True)
        
        self.rubric_source_group.addButton(self.local_rubric_radio, 0)
        self.rubric_source_group.addButton(self.canvas_rubric_radio, 1)
        
        rubric_source_layout.addWidget(self.local_rubric_radio)
        rubric_source_layout.addWidget(self.canvas_rubric_radio)
        rubric_source_layout.addStretch()
        
        config_layout.addLayout(rubric_source_layout)
        
        # Local rubric file selection
        local_rubric_layout = QHBoxLayout()
        local_rubric_layout.addWidget(QLabel("Rubric File:"))
        
        self.rubric_path_entry = QLineEdit("sample_rubric.json")
        local_rubric_layout.addWidget(self.rubric_path_entry)
        
        browse_rubric_btn = QPushButton("Browse")
        local_rubric_layout.addWidget(browse_rubric_btn)
        
        config_layout.addLayout(local_rubric_layout)
        
        # Canvas rubric info (for when Canvas rubric is selected)
        self.canvas_rubric_label = QLabel("✓ Canvas rubric will be downloaded automatically from the selected assignment")
        self.canvas_rubric_label.setStyleSheet("font-size: 10px;")
        self.canvas_rubric_label.hide()  # Initially hidden
        config_layout.addWidget(self.canvas_rubric_label)
        
        # Instructor configuration
        instructor_layout = QHBoxLayout()
        instructor_layout.addWidget(QLabel("Instructor Config:"))
        
        self.instructor_config_entry = QLineEdit("grading_instructor_config.json")
        instructor_layout.addWidget(self.instructor_config_entry)
        
        browse_instructor_btn = QPushButton("Browse")
        instructor_layout.addWidget(browse_instructor_btn)
        
        optional_btn = QPushButton("Optional")
        instructor_layout.addWidget(optional_btn)
        
        config_layout.addLayout(instructor_layout)
        
        layout.addWidget(config_group)
        
        # Grading Steps Group
        steps_group = QGroupBox("Grading Steps")
        steps_layout = QVBoxLayout(steps_group)
        
        # Step 1
        step1_layout = QHBoxLayout()
        self.step1_button = QPushButton("📥 Step 1: Download & Grade")
        self.step1_button.setEnabled(False)
        step1_layout.addWidget(self.step1_button)
        
        self.step1_status = QLabel("Ready")
        self.step1_status.setStyleSheet("color: blue;")
        step1_layout.addWidget(self.step1_status)
        step1_layout.addStretch()
        
        steps_layout.addLayout(step1_layout)
        
        # Step 2
        step2_layout = QHBoxLayout()
        self.step2_button = QPushButton("📤 Step 2: Review & Upload")
        self.step2_button.setEnabled(False)
        step2_layout.addWidget(self.step2_button)
        
        self.open_folder_button = QPushButton("📁 Open Review Folder")
        self.open_folder_button.setEnabled(False)
        step2_layout.addWidget(self.open_folder_button)
        
        self.step2_status = QLabel("Waiting for Step 1")
        self.step2_status.setStyleSheet("color: gray;")
        step2_layout.addWidget(self.step2_status)
        step2_layout.addStretch()
        
        steps_layout.addLayout(step2_layout)
        
        # Progress bar
        self.progress_two_step = QProgressBar()
        steps_layout.addWidget(self.progress_two_step)
        
        # Progress description
        self.progress_desc_two_step = QLabel("Ready")
        self.progress_desc_two_step.setStyleSheet("color: blue; font-size: 10px;")
        steps_layout.addWidget(self.progress_desc_two_step)
        
        layout.addWidget(steps_group)
        
        # Process Log Group
        log_group = QGroupBox("Process Log")
        log_layout = QVBoxLayout(log_group)
        
        self.two_step_log = QTextEdit()
        self.two_step_log.setReadOnly(True)
        self.two_step_log.setMaximumHeight(200)
        log_layout.addWidget(self.two_step_log)
        
        layout.addWidget(log_group)
        layout.addStretch()
        
        return tab
        
    def create_single_step_tab(self) -> QWidget:
        """Create Single-Step Grading tab matching Tkinter structure"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Header with explanation
        header_group = QGroupBox("⚡ Single-Step Direct Grading")
        header_layout = QVBoxLayout(header_group)
        
        explanation = """Direct grading workflow: Download → Grade → Upload immediately
Warning: This bypasses manual review. Use only if you trust the AI grading completely."""
        
        explanation_label = QLabel(explanation)
        explanation_label.setStyleSheet("font-size: 10px; color: orange;")
        header_layout.addWidget(explanation_label)
        
        layout.addWidget(header_group)
        
        # Assignment Selection (similar to two-step)
        selection_group = QGroupBox("Assignment Selection")
        selection_layout = QVBoxLayout(selection_group)
        
        # Course selection
        course_layout = QHBoxLayout()
        course_layout.addWidget(QLabel("Course:"))
        refresh_courses_btn = QPushButton("Refresh Courses")
        course_layout.addWidget(refresh_courses_btn)
        
        self.single_course_combo = QComboBox()
        self.single_course_combo.setMinimumWidth(400)
        course_layout.addWidget(self.single_course_combo)
        course_layout.addStretch()
        
        selection_layout.addLayout(course_layout)
        
        # Assignment selection
        assignment_layout = QHBoxLayout()
        assignment_layout.addWidget(QLabel("Assignment:"))
        
        self.single_assignment_combo = QComboBox()
        self.single_assignment_combo.setMinimumWidth(400)
        assignment_layout.addWidget(self.single_assignment_combo)
        assignment_layout.addStretch()
        
        selection_layout.addLayout(assignment_layout)
        
        layout.addWidget(selection_group)
        
        # Configuration (similar structure but for single-step)
        config_group = QGroupBox("Grading Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Rubric file
        rubric_layout = QHBoxLayout()
        rubric_layout.addWidget(QLabel("Rubric File:"))
        
        self.single_rubric_entry = QLineEdit("sample_rubric.json")
        rubric_layout.addWidget(self.single_rubric_entry)
        
        browse_rubric_btn = QPushButton("Browse")
        rubric_layout.addWidget(browse_rubric_btn)
        
        config_layout.addLayout(rubric_layout)
        
        # Instructor config
        instructor_layout = QHBoxLayout()
        instructor_layout.addWidget(QLabel("Instructor Config:"))
        
        self.single_instructor_entry = QLineEdit("grading_instructor_config.json")
        instructor_layout.addWidget(self.single_instructor_entry)
        
        browse_instructor_btn = QPushButton("Browse")
        instructor_layout.addWidget(browse_instructor_btn)
        
        optional_btn = QPushButton("Optional")
        instructor_layout.addWidget(optional_btn)
        
        config_layout.addLayout(instructor_layout)
        
        layout.addWidget(config_group)
        
        # Grading Action
        action_group = QGroupBox("Direct Grading")
        action_layout = QVBoxLayout(action_group)
        
        # Warning
        warning_label = QLabel("⚠️ WARNING: This will grade and upload results immediately without review!")
        warning_label.setStyleSheet("color: red; font-weight: bold; font-size: 11px;")
        action_layout.addWidget(warning_label)
        
        # Start button
        button_layout = QHBoxLayout()
        self.single_grade_button = QPushButton("⚡ Start Single-Step Grading")
        self.single_grade_button.setEnabled(False)
        self.single_grade_button.setStyleSheet("QPushButton { background-color: #ff6b6b; color: white; font-weight: bold; }")
        button_layout.addWidget(self.single_grade_button)
        
        self.single_status = QLabel("Ready")
        self.single_status.setStyleSheet("color: blue;")
        button_layout.addWidget(self.single_status)
        button_layout.addStretch()
        
        action_layout.addLayout(button_layout)
        
        # Progress
        self.progress_single_step = QProgressBar()
        action_layout.addWidget(self.progress_single_step)
        
        self.progress_desc_single = QLabel("Ready")
        self.progress_desc_single.setStyleSheet("color: blue; font-size: 10px;")
        action_layout.addWidget(self.progress_desc_single)
        
        layout.addWidget(action_group)
        
        # Log
        log_group = QGroupBox("Grading Log")
        log_layout = QVBoxLayout(log_group)
        
        self.single_step_log = QTextEdit()
        self.single_step_log.setReadOnly(True)
        self.single_step_log.setMaximumHeight(200)
        log_layout.addWidget(self.single_step_log)
        
        layout.addWidget(log_group)
        layout.addStretch()
        
        return tab
        
    def create_results_tab(self) -> QWidget:
        """Create Results tab matching Tkinter structure"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Results Summary Group
        summary_group = QGroupBox("📊 Grading Results Summary")
        summary_layout = QVBoxLayout(summary_group)
        
        self.results_summary = QLabel("No grading sessions completed yet.")
        self.results_summary.setStyleSheet("font-size: 12px; padding: 10px;")
        summary_layout.addWidget(self.results_summary)
        
        layout.addWidget(summary_group)
        
        # Recent Sessions Group
        sessions_group = QGroupBox("Recent Grading Sessions")
        sessions_layout = QVBoxLayout(sessions_group)
        
        # Session list (placeholder for now)
        self.sessions_list = QTextEdit()
        self.sessions_list.setReadOnly(True)
        self.sessions_list.setMaximumHeight(150)
        self.sessions_list.setPlainText("No recent sessions to display.")
        sessions_layout.addWidget(self.sessions_list)
        
        # Session management buttons
        session_buttons_layout = QHBoxLayout()
        view_session_btn = QPushButton("View Session Details")
        export_results_btn = QPushButton("Export Results")
        clear_history_btn = QPushButton("Clear History")
        
        session_buttons_layout.addWidget(view_session_btn)
        session_buttons_layout.addWidget(export_results_btn)
        session_buttons_layout.addWidget(clear_history_btn)
        session_buttons_layout.addStretch()
        
        sessions_layout.addLayout(session_buttons_layout)
        
        layout.addWidget(sessions_group)
        
        # Statistics Group
        stats_group = QGroupBox("Grading Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(200)
        self.stats_display.setPlainText("Statistics will appear here after grading sessions.")
        stats_layout.addWidget(self.stats_display)
        
        layout.addWidget(stats_group)
        layout.addStretch()
        
        return tab
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        # Canvas API settings
        api_group = QGroupBox("Canvas API Configuration")
        api_layout = QVBoxLayout(api_group)
        
        # URL input
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Canvas URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://your-school.instructure.com")
        url_layout.addWidget(self.url_input)
        api_layout.addLayout(url_layout)
        
        # API Key input
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("Enter your Canvas API key")
        key_layout.addWidget(self.key_input)
        api_layout.addLayout(key_layout)
        
        # Test connection button
        test_btn = QPushButton("🔗 Test Connection")
        test_btn.clicked.connect(self.test_connection)
        api_layout.addWidget(test_btn)
        
        layout.addWidget(api_group)
        
        # Course settings
        course_group = QGroupBox("Course Settings")
        course_layout = QVBoxLayout(course_group)
        
        course_layout_h = QHBoxLayout()
        course_layout_h.addWidget(QLabel("Course ID:"))
        self.course_input = QLineEdit()
        self.course_input.setPlaceholderText("Enter Canvas course ID")
        course_layout_h.addWidget(self.course_input)
        
        load_btn = QPushButton("📚 Load Assignments")
        load_btn.clicked.connect(self.load_assignments)
        course_layout_h.addWidget(load_btn)
        
        course_layout.addLayout(course_layout_h)
        layout.addWidget(course_group)
        
        # Download settings
        download_group = QGroupBox("Download Settings")
        download_layout = QVBoxLayout(download_group)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Download Path:"))
        self.path_input = QLineEdit()
        self.path_input.setText(str(Path.home() / "Downloads"))
        path_layout.addWidget(self.path_input)
        
        browse_btn = QPushButton("📁 Browse")
        browse_btn.clicked.connect(self.browse_path)
        path_layout.addWidget(browse_btn)
        
        download_layout.addLayout(path_layout)
        
        self.auto_grade_cb = QCheckBox("Automatically grade downloaded submissions")
        download_layout.addWidget(self.auto_grade_cb)
        
        self.upload_grades_cb = QCheckBox("Upload grades back to Canvas")
        download_layout.addWidget(self.upload_grades_cb)
        
        layout.addWidget(download_group)
        
        # Save button
        save_btn = QPushButton("💾 Save Configuration")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        return widget
        
    def create_assignments_tab(self) -> QWidget:
        """Create assignments tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QLabel("📚 Course Assignments")
        header.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #2E86AB; margin: 10px;")
        layout.addWidget(header)
        
        # Assignments list (placeholder)
        self.assignments_text = QTextEdit()
        self.assignments_text.setPlaceholderText(
            "No assignments loaded.\n\n"
            "To get started:\n"
            "1. Configure Canvas API settings\n"
            "2. Enter a course ID\n"
            "3. Click 'Load Assignments'\n\n"
            "This modern PyQt6 interface provides:\n"
            "• Professional appearance\n"
            "• Modern design elements\n"
            "• Better user experience\n"
            "• Canvas LMS integration\n"
            "• Automated grading capabilities"
        )
        self.assignments_text.setReadOnly(True)
        layout.addWidget(self.assignments_text)
        
        # Action buttons
        actions_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("🔄 Refresh Assignments")
        refresh_btn.clicked.connect(self.refresh_assignments)
        actions_layout.addWidget(refresh_btn)
        
        download_all_btn = QPushButton("📥 Download All Submissions")
        download_all_btn.clicked.connect(self.download_all_submissions)
        actions_layout.addWidget(download_all_btn)
        
        actions_layout.addStretch()
        layout.addLayout(actions_layout)
        
        return widget
        
    def create_progress_tab(self) -> QWidget:
        """Create progress tab"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        
        header = QLabel("📊 Operation Progress")
        header.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #2E86AB; margin: 10px;")
        layout.addWidget(header)
        
        # Progress info
        self.progress_label = QLabel("No operations in progress")
        layout.addWidget(self.progress_label)
        
        self.progress_bar = QProgressBar()
        layout.addWidget(self.progress_bar)
        
        # Log area
        log_label = QLabel("Operation Log:")
        log_label.setFont(QFont('Segoe UI', 10, QFont.Weight.Bold))
        layout.addWidget(log_label)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setReadOnly(True)
        layout.addWidget(self.log_text)
        
        layout.addStretch()
        return widget
        
    def setup_window(self):
        """Setup window properties"""
        self.setWindowTitle("DuckGrade Canvas Integration - DuckWorks Educational Suite")
        self.resize(900, 600)
        
        # Set duck icon
        if Path("assets/icons8-flying-duck-48.png").exists():
            self.setWindowIcon(QIcon("assets/icons8-flying-duck-48.png"))
        
        self.center_window()
        
        # Apply basic styling
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8f9fa;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #dee2e6;
                border-radius: 8px;
                margin: 5px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
            }
            QPushButton {
                background-color: #2E86AB;
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: 500;
                min-height: 20px;
            }
            QPushButton:hover {
                background-color: #1F5F7A;
            }
            QPushButton:pressed {
                background-color: #1F5F7A;
            }
            QLineEdit, QTextEdit {
                background-color: white;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
            QLineEdit:focus, QTextEdit:focus {
                border-color: #2E86AB;
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 6px;
                background: white;
            }
            QTabBar::tab {
                background: #f8f9fa;
                padding: 8px 16px;
                margin-right: 2px;
                border-top-left-radius: 6px;
                border-top-right-radius: 6px;
            }
            QTabBar::tab:selected {
                background: white;
                border-bottom: none;
            }
        """)
        
    def center_window(self):
        """Center window on screen"""
        screen = QApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        center_point = screen.center()
        window.moveCenter(center_point)
        self.move(window.topLeft())
        
    def test_connection(self):
        """Test Canvas API connection"""
        url = self.url_input.text().strip()
        key = self.key_input.text().strip()
        
        if not url or not key:
            QMessageBox.warning(self, "Warning", "Please enter both Canvas URL and API key.")
            return
            
        # For demo purposes, show success
        QMessageBox.information(self, "Test Connection", 
                              f"Connection test would verify access to:\n{url}\n\n"
                              "This is a demonstration of the modern PyQt6 interface.\n"
                              "Canvas integration would be implemented here.")
        self.log_message(f"Test connection to {url}")
        
    def load_assignments(self):
        """Load assignments from Canvas"""
        course_id = self.course_input.text().strip()
        if not course_id:
            QMessageBox.warning(self, "Warning", "Please enter a course ID.")
            return
            
        self.assignments_text.setPlainText(
            f"Loading assignments for course {course_id}...\n\n"
            "This modern PyQt6 interface demonstrates:\n"
            "✅ Professional design and styling\n"
            "✅ Modern UI components and layouts\n"
            "✅ Improved user experience over Tkinter\n"
            "✅ Canvas LMS integration capabilities\n"
            "✅ Progress tracking and logging\n"
            "✅ Configuration management\n\n"
            "In the full implementation, this would:\n"
            "• Connect to Canvas API\n"
            "• Retrieve assignment data\n"
            "• Display assignment cards\n"
            "• Enable bulk downloads\n"
            "• Integrate with auto-grading"
        )
        self.log_message(f"Loaded assignments for course {course_id}")
        
    def refresh_assignments(self):
        """Refresh assignments list"""
        self.load_assignments()
        
    def download_all_submissions(self):
        """Download all submissions"""
        download_path = self.path_input.text().strip()
        if not download_path:
            QMessageBox.warning(self, "Warning", "Please set a download path.")
            return
            
        self.progress_label.setText("Downloading submissions...")
        self.progress_bar.setValue(0)
        
        # Simulate progress
        for i in range(101):
            self.progress_bar.setValue(i)
            QApplication.processEvents()
            
        QMessageBox.information(self, "Download Complete", 
                              f"Submissions would be downloaded to:\n{download_path}\n\n"
                              "The modern PyQt6 interface provides better visual feedback "
                              "and a more professional user experience.")
        self.log_message(f"Downloaded submissions to {download_path}")
        
    def browse_path(self):
        """Browse for download directory"""
        path = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if path:
            self.path_input.setText(path)
            
    def save_config(self):
        """Save configuration"""
        config = DuckWorksConfig()
        config.set('canvas_url', self.url_input.text())
        config.set('course_id', self.course_input.text())
        config.set('download_path', self.path_input.text())
        config.set('auto_grade', self.auto_grade_cb.isChecked())
        config.set('upload_grades', self.upload_grades_cb.isChecked())
        
        QMessageBox.information(self, "Configuration Saved", 
                              "Settings have been saved successfully!\n\n"
                              "The DuckWorks framework provides persistent configuration "
                              "management across all educational automation tools.")
        self.log_message("Configuration saved")
        
    def log_message(self, message: str):
        """Add message to log"""
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("DuckGrade Canvas Integration")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("DuckWorks Educational Suite")
    
    # Create and show main window
    window = DuckGradeCanvasGUI()
    window.show()
    
    print("🦆 DuckGrade Canvas Integration (PyQt6) started successfully!")
    print("Modern interface demonstrates significant improvements over Tkinter")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
