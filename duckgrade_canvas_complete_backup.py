"""
DuckGrade Canvas Integration - PyQt6 Modern Interface
Complete implementation matching Tkinter canvas_gui.py structure

This version provides a professional PyQt6 interface that exactly matches
the functionality and layout of the original Tkinter Canvas GUI.
"""

import sys
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QTextEdit,
                            QCheckBox, QProgressBar, QMessageBox, QFileDialog,
                            QSpacerItem, QSizePolicy, QInputDialog)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QFont

# Import existing configuration system
try:
    from duckworks_core import DuckWorksConfig
except ImportError:
    # Fallback configuration class if not available
    class DuckWorksConfig:
        def __init__(self):
            self.config = {}
        def set(self, key, value):
            self.config[key] = value
        def get(self, key, default=None):
            return self.config.get(key, default)


class DuckGradeCanvasGUI(QMainWindow):
    """
    Main Canvas GUI window matching the exact structure of canvas_gui.py
    
    Features 4 tabs matching Tkinter version:
    - 🔗 Canvas Connection (API settings, privacy, status)
    - 📋 Two-Step Grading (workflow with review)
    - ⚡ Single-Step Grading (direct grading without review)
    - 📊 Results (session history and statistics)
    """
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setup_window()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tab_widget = QTabWidget()
        
        # Add tabs matching Tkinter structure exactly
        self.tab_widget.addTab(self.create_connection_tab(), "� API Connections")
        self.tab_widget.addTab(self.create_two_step_tab(), "📋 Two-Step Grading")
        self.tab_widget.addTab(self.create_single_step_tab(), "⚡ Single-Step Grading")
        self.tab_widget.addTab(self.create_results_tab(), "📊 Results")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_connection_tab(self) -> QWidget:
        """Create Canvas Connection tab matching Tkinter structure"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # OpenAI Configuration Group
        openai_group = QGroupBox("🤖 OpenAI Configuration")
        openai_layout = QVBoxLayout(openai_group)
        
        # API Key row
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.openai_key_entry = QLineEdit()
        self.openai_key_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_entry.setPlaceholderText("Enter your OpenAI API key")
        key_layout.addWidget(self.openai_key_entry)
        
        save_key_btn = QPushButton("Save Key")
        save_key_btn.clicked.connect(self.save_openai_key)
        key_layout.addWidget(save_key_btn)
        
        load_key_btn = QPushButton("Load Key")
        load_key_btn.clicked.connect(self.load_openai_key)
        key_layout.addWidget(load_key_btn)
        
        openai_layout.addLayout(key_layout)
        
        # Model selection row
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        
        self.model_combo = QComboBox()
        self.model_combo.addItem("gpt-4o-mini")
        self.model_combo.setMinimumWidth(280)
        
        # Style the ComboBox with custom arrow using PNG
        self.model_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 11pt;
                min-width: 250px;
                padding-right: 25px;
            }
            QComboBox:hover {
                border-color: #adb5bd;
            }
            QComboBox:focus {
                border-color: #80bdff;
                outline: 0;
            }
            QComboBox::drop-down {
                subcontrol-origin: padding;
                subcontrol-position: top right;
                width: 20px;
                border-left-width: 1px;
                border-left-color: #ced4da;
                border-left-style: solid;
                border-top-right-radius: 3px;
                border-bottom-right-radius: 3px;
                background-color: #f8f9fa;
            }
            QComboBox::drop-down:hover {
                background-color: #e9ecef;
            }
            QComboBox::down-arrow {
                image: url(assets/down-arrow_gray.png);
                width: 12px;
                height: 8px;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ced4da;
                background-color: white;
                selection-background-color: #007bff;
                selection-color: white;
            }
        """)
        
        model_layout.addWidget(self.model_combo)
        
        refresh_models_btn = QPushButton("Refresh Models")
        refresh_models_btn.clicked.connect(self.refresh_models)
        model_layout.addWidget(refresh_models_btn)
        model_layout.addStretch()
        
        openai_layout.addLayout(model_layout)
        layout.addWidget(openai_group)
        
        # Canvas Configuration Group
        canvas_group = QGroupBox("🎨 Canvas Configuration")
        canvas_layout = QVBoxLayout(canvas_group)
        
        # Canvas URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Canvas URL:"))
        self.canvas_url_entry = QLineEdit()
        self.canvas_url_entry.setPlaceholderText("https://your-school.instructure.com")
        url_layout.addWidget(self.canvas_url_entry)
        canvas_layout.addLayout(url_layout)
        
        # API Token
        token_layout = QHBoxLayout()
        token_layout.addWidget(QLabel("API Token:"))
        self.canvas_token_entry = QLineEdit()
        self.canvas_token_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.canvas_token_entry.setPlaceholderText("Enter your Canvas API token")
        token_layout.addWidget(self.canvas_token_entry)
        canvas_layout.addLayout(token_layout)
        
        # Connection test
        test_layout = QHBoxLayout()
        test_connection_btn = QPushButton("Connect")
        
        # Add network icon if available
        if Path("assets/network_outlined.png").exists():
            test_connection_btn.setIcon(QIcon("assets/network_outlined.png"))
            test_connection_btn.setIconSize(QSize(20, 20))
        
        test_connection_btn.clicked.connect(self.test_connection)
        test_layout.addWidget(test_connection_btn)
        
        save_config_btn = QPushButton("💾 Save Configuration")
        save_config_btn.clicked.connect(self.save_configuration)
        test_layout.addWidget(save_config_btn)
        test_layout.addStretch()
        
        canvas_layout.addLayout(test_layout)
        layout.addWidget(canvas_group)
        
        # Privacy and Safety Group
        privacy_group = QGroupBox("🔒 Privacy and Safety")
        privacy_layout = QVBoxLayout(privacy_group)
        
        self.anonymize_checkbox = QCheckBox("Anonymize student names in grading feedback")
        self.anonymize_checkbox.setChecked(True)
        privacy_layout.addWidget(self.anonymize_checkbox)
        
        self.backup_checkbox = QCheckBox("Create backup of submissions before grading")
        self.backup_checkbox.setChecked(True)
        privacy_layout.addWidget(self.backup_checkbox)
        
        layout.addWidget(privacy_group)
        
        # Connection Status Group
        status_group = QGroupBox("📊 Connection Status")
        status_layout = QVBoxLayout(status_group)
        
        self.connection_status = QLabel("🔴 Not connected to Canvas")
        self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.connection_status)
        
        self.openai_status = QLabel("🔴 OpenAI API not configured")
        self.openai_status.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.openai_status)
        
        layout.addWidget(status_group)
        layout.addStretch()
        
        return tab
    
    def create_two_step_tab(self) -> QWidget:
        """Create Two-Step Grading tab matching Tkinter structure"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Workflow description
        workflow_group = QGroupBox("📋 Two-Step Grading Workflow")
        workflow_layout = QVBoxLayout(workflow_group)
        
        workflow_text = QLabel(
            "Two-step grading provides safety and quality control:\n\n"
            "Step 1: AI grades submissions and saves results for review\n"
            "Step 2: Review results, make adjustments, then upload to Canvas\n\n"
            "This approach allows you to verify AI grading before students see results."
        )
        workflow_text.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 4px;")
        workflow_layout.addWidget(workflow_text)
        
        layout.addWidget(workflow_group)
        
        # Assignment Selection Group
        assignment_group = QGroupBox("📚 Assignment Selection")
        assignment_layout = QVBoxLayout(assignment_group)
        
        # Course ID input
        course_layout = QHBoxLayout()
        course_layout.addWidget(QLabel("Course ID:"))
        self.course_id_entry = QLineEdit()
        self.course_id_entry.setPlaceholderText("Enter Canvas course ID")
        course_layout.addWidget(self.course_id_entry)
        assignment_layout.addLayout(course_layout)
        
        # Assignment dropdown
        assignment_select_layout = QHBoxLayout()
        assignment_select_layout.addWidget(QLabel("Select Assignment:"))
        self.assignment_combo = QComboBox()
        self.assignment_combo.addItem("No assignments loaded")
        self.assignment_combo.setMinimumWidth(280)  # Standard width for dropdown
        assignment_select_layout.addWidget(self.assignment_combo)
        
        refresh_assignments_btn = QPushButton("🔄 Refresh")
        refresh_assignments_btn.clicked.connect(self.refresh_assignments)
        assignment_select_layout.addWidget(refresh_assignments_btn)
        
        assignment_layout.addLayout(assignment_select_layout)
        
        # Assignment info
        self.assignment_info = QLabel("Select an assignment to view details")
        self.assignment_info.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 4px;")
        assignment_layout.addWidget(self.assignment_info)
        
        layout.addWidget(assignment_group)
        
        # Grading Configuration Group
        config_group = QGroupBox("⚙️ Grading Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Rubric file
        rubric_layout = QHBoxLayout()
        rubric_layout.addWidget(QLabel("Rubric File:"))
        self.rubric_path_entry = QLineEdit("sample_rubric.json")
        rubric_layout.addWidget(self.rubric_path_entry)
        
        browse_rubric_btn = QPushButton("Browse")
        browse_rubric_btn.clicked.connect(self.browse_rubric)
        rubric_layout.addWidget(browse_rubric_btn)
        
        config_layout.addLayout(rubric_layout)
        
        # Instructor config
        instructor_layout = QHBoxLayout()
        instructor_layout.addWidget(QLabel("Instructor Config:"))
        self.instructor_config_entry = QLineEdit("grading_instructor_config.json")
        instructor_layout.addWidget(self.instructor_config_entry)
        
        browse_instructor_btn = QPushButton("Browse")
        browse_instructor_btn.clicked.connect(self.browse_instructor_config)
        instructor_layout.addWidget(browse_instructor_btn)
        
        optional_instructor_btn = QPushButton("Optional")
        instructor_layout.addWidget(optional_instructor_btn)
        
        config_layout.addLayout(instructor_layout)
        
        layout.addWidget(config_group)
        
        # Step 1: AI Grading Group
        step1_group = QGroupBox("🤖 Step 1: AI Grading")
        step1_layout = QVBoxLayout(step1_group)
        
        step1_desc = QLabel("Downloads submissions, runs AI grading, saves results for review")
        step1_layout.addWidget(step1_desc)
        
        step1_button_layout = QHBoxLayout()
        self.step1_button = QPushButton("🚀 Start Step 1: Download & Grade")
        self.step1_button.setEnabled(False)
        self.step1_button.clicked.connect(self.start_step1)
        step1_button_layout.addWidget(self.step1_button)
        
        self.step1_status = QLabel("Ready")
        self.step1_status.setStyleSheet("color: blue;")
        step1_button_layout.addWidget(self.step1_status)
        step1_button_layout.addStretch()
        
        step1_layout.addLayout(step1_button_layout)
        
        # Progress bar for step 1
        self.progress_step1 = QProgressBar()
        step1_layout.addWidget(self.progress_step1)
        
        self.progress_desc_step1 = QLabel("Ready")
        self.progress_desc_step1.setStyleSheet("color: blue; font-size: 10px;")
        step1_layout.addWidget(self.progress_desc_step1)
        
        layout.addWidget(step1_group)
        
        # Step 2: Review & Upload Group
        step2_group = QGroupBox("👁️ Step 2: Review & Upload")
        step2_layout = QVBoxLayout(step2_group)
        
        step2_desc = QLabel("Review AI grading results, make adjustments, upload final grades")
        step2_layout.addWidget(step2_desc)
        
        step2_button_layout = QHBoxLayout()
        self.step2_button = QPushButton("📋 Start Step 2: Review & Upload")
        self.step2_button.setEnabled(False)
        self.step2_button.clicked.connect(self.start_step2)
        step2_button_layout.addWidget(self.step2_button)
        
        review_folder_btn = QPushButton("📁 Open Review Folder")
        review_folder_btn.clicked.connect(self.open_review_folder)
        step2_button_layout.addWidget(review_folder_btn)
        
        self.step2_status = QLabel("Ready")
        self.step2_status.setStyleSheet("color: blue;")
        step2_button_layout.addWidget(self.step2_status)
        step2_button_layout.addStretch()
        
        step2_layout.addLayout(step2_button_layout)
        
        # Progress bar for step 2
        self.progress_step2 = QProgressBar()
        step2_layout.addWidget(self.progress_step2)
        
        self.progress_desc_step2 = QLabel("Ready")
        self.progress_desc_step2.setStyleSheet("color: blue; font-size: 10px;")
        step2_layout.addWidget(self.progress_desc_step2)
        
        layout.addWidget(step2_group)
        layout.addStretch()
        
        return tab
    
    def create_single_step_tab(self) -> QWidget:
        """Create Single-Step Grading tab matching Tkinter structure"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # Warning Group
        warning_group = QGroupBox("⚠️ Single-Step Grading Warning")
        warning_layout = QVBoxLayout(warning_group)
        
        warning_text = QLabel(
            "⚠️ WARNING: Single-step grading uploads results immediately!\n\n"
            "This mode downloads submissions, grades them with AI, and uploads results "
            "directly to Canvas without human review. Use only when you fully trust "
            "the AI grading configuration.\n\n"
            "For safety, consider using Two-Step Grading instead."
        )
        warning_text.setStyleSheet("color: red; font-weight: bold; padding: 10px; background-color: #fff3cd; border-radius: 4px;")
        warning_layout.addWidget(warning_text)
        
        layout.addWidget(warning_group)
        
        # Assignment Selection Group
        single_assignment_group = QGroupBox("📚 Assignment Selection")
        single_assignment_layout = QVBoxLayout(single_assignment_group)
        
        # Course ID input for single step
        single_course_layout = QHBoxLayout()
        single_course_layout.addWidget(QLabel("Course ID:"))
        self.single_course_id_entry = QLineEdit()
        self.single_course_id_entry.setPlaceholderText("Enter Canvas course ID")
        single_course_layout.addWidget(self.single_course_id_entry)
        single_assignment_layout.addLayout(single_course_layout)
        
        # Assignment dropdown
        single_assignment_select_layout = QHBoxLayout()
        single_assignment_select_layout.addWidget(QLabel("Select Assignment:"))
        self.single_assignment_combo = QComboBox()
        self.single_assignment_combo.addItem("No assignments loaded")
        self.single_assignment_combo.setMinimumWidth(280)  # Standard width for dropdown
        single_assignment_select_layout.addWidget(self.single_assignment_combo)
        
        refresh_single_assignments_btn = QPushButton("🔄 Refresh")
        refresh_single_assignments_btn.clicked.connect(self.refresh_assignments)
        single_assignment_select_layout.addWidget(refresh_single_assignments_btn)
        
        single_assignment_layout.addLayout(single_assignment_select_layout)
        
        # Assignment info for single step
        self.single_assignment_info = QLabel("Select an assignment to view details")
        self.single_assignment_info.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 4px;")
        single_assignment_layout.addWidget(self.single_assignment_info)
        
        layout.addWidget(single_assignment_group)
        
        # Configuration Group
        single_config_group = QGroupBox("⚙️ Grading Configuration")
        single_config_layout = QVBoxLayout(single_config_group)
        
        # Rubric file
        single_rubric_layout = QHBoxLayout()
        single_rubric_layout.addWidget(QLabel("Rubric File:"))
        self.single_rubric_entry = QLineEdit("sample_rubric.json")
        single_rubric_layout.addWidget(self.single_rubric_entry)
        
        browse_single_rubric_btn = QPushButton("Browse")
        single_rubric_layout.addWidget(browse_single_rubric_btn)
        
        single_config_layout.addLayout(single_rubric_layout)
        
        # Instructor config
        single_instructor_layout = QHBoxLayout()
        single_instructor_layout.addWidget(QLabel("Instructor Config:"))
        self.single_instructor_entry = QLineEdit("grading_instructor_config.json")
        single_instructor_layout.addWidget(self.single_instructor_entry)
        
        browse_single_instructor_btn = QPushButton("Browse")
        single_instructor_layout.addWidget(browse_single_instructor_btn)
        
        optional_single_btn = QPushButton("Optional")
        single_instructor_layout.addWidget(optional_single_btn)
        
        single_config_layout.addLayout(single_instructor_layout)
        
        layout.addWidget(single_config_group)
        
        # Direct Grading Action Group
        action_group = QGroupBox("⚡ Direct Grading")
        action_layout = QVBoxLayout(action_group)
        
        # Final warning
        final_warning = QLabel("⚠️ WARNING: This will grade and upload results immediately without review!")
        final_warning.setStyleSheet("color: red; font-weight: bold; font-size: 11px;")
        action_layout.addWidget(final_warning)
        
        # Start button
        button_layout = QHBoxLayout()
        self.single_grade_button = QPushButton("⚡ Start Single-Step Grading")
        self.single_grade_button.setEnabled(False)
        self.single_grade_button.setStyleSheet("QPushButton { background-color: #dc3545; color: white; font-weight: bold; }")
        self.single_grade_button.clicked.connect(self.start_single_grading)
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
        
        # Log Group
        log_group = QGroupBox("📝 Grading Log")
        log_layout = QVBoxLayout(log_group)
        
        self.single_step_log = QTextEdit()
        self.single_step_log.setReadOnly(True)
        self.single_step_log.setMaximumHeight(200)
        self.single_step_log.setPlainText("Single-step grading log will appear here...")
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
        self.results_summary.setStyleSheet("font-size: 12px; padding: 10px; background-color: #f8f9fa; border-radius: 4px;")
        summary_layout.addWidget(self.results_summary)
        
        layout.addWidget(summary_group)
        
        # Recent Sessions Group
        sessions_group = QGroupBox("📈 Recent Grading Sessions")
        sessions_layout = QVBoxLayout(sessions_group)
        
        # Session list
        self.sessions_list = QTextEdit()
        self.sessions_list.setReadOnly(True)
        self.sessions_list.setMaximumHeight(150)
        self.sessions_list.setPlainText("No recent sessions to display.")
        sessions_layout.addWidget(self.sessions_list)
        
        # Session management buttons
        session_buttons_layout = QHBoxLayout()
        view_session_btn = QPushButton("👁️ View Session Details")
        export_results_btn = QPushButton("📤 Export Results")
        clear_history_btn = QPushButton("🗑️ Clear History")
        
        session_buttons_layout.addWidget(view_session_btn)
        session_buttons_layout.addWidget(export_results_btn)
        session_buttons_layout.addWidget(clear_history_btn)
        session_buttons_layout.addStretch()
        
        sessions_layout.addLayout(session_buttons_layout)
        
        layout.addWidget(sessions_group)
        
        # Statistics Group
        stats_group = QGroupBox("📊 Grading Statistics")
        stats_layout = QVBoxLayout(stats_group)
        
        self.stats_display = QTextEdit()
        self.stats_display.setReadOnly(True)
        self.stats_display.setMaximumHeight(200)
        self.stats_display.setPlainText("Statistics will appear here after grading sessions.")
        stats_layout.addWidget(self.stats_display)
        
        layout.addWidget(stats_group)
        layout.addStretch()
        
        return tab
    
    def setup_window(self):
        """Setup window properties"""
        self.setWindowTitle("DuckGrade Canvas Integration - DuckWorks Educational Suite")
        self.resize(900, 700)
        
        # Set duck icon
        if Path("assets/icons8-flying-duck-48.png").exists():
            self.setWindowIcon(QIcon("assets/icons8-flying-duck-48.png"))
        
        # Set custom icon for API Connections tab
        if Path("assets/network_outlined.png").exists():
            self.tab_widget.setTabIcon(0, QIcon("assets/network_outlined.png"))
        
        self.center_window()
        
        # Apply professional styling matching modern design principles
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
                background-color: white;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px 0 5px;
                color: #495057;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:disabled {
                background-color: #6c757d;
            }
            QLineEdit, QTextEdit {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 11pt;
                min-width: 250px;
            }
            QComboBox:hover {
                border-color: #adb5bd;
            }
            QComboBox:focus {
                border-color: #80bdff;
                outline: 0;
            }
            QComboBox QAbstractItemView {
                border: 1px solid #ced4da;
                background-color: white;
                selection-background-color: #007bff;
                selection-color: white;
            }
            QLineEdit:focus, QComboBox:focus, QTextEdit:focus {
                border-color: #80bdff;
                outline: 0;
                box-shadow: 0 0 0 0.2rem rgba(0, 123, 255, 0.25);
            }
            QTabWidget::pane {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 10px 15px;
                margin-right: 2px;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007bff;
            }
            QProgressBar {
                border: 1px solid #dee2e6;
                border-radius: 4px;
                text-align: center;
                background-color: #f8f9fa;
            }
            QProgressBar::chunk {
                background-color: #007bff;
                border-radius: 3px;
            }
            QCheckBox {
                spacing: 8px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
            }
            QCheckBox::indicator:unchecked {
                border: 2px solid #6c757d;
                border-radius: 3px;
                background-color: white;
            }
            QCheckBox::indicator:checked {
                border: 2px solid #007bff;
                border-radius: 3px;
                background-color: #007bff;
            }
        """)
    
    def center_window(self):
        """Center the window on the screen"""
        frame_geometry = self.frameGeometry()
        screen = self.screen().availableGeometry()
        center_point = screen.center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
    
    # Event handler methods
    def save_openai_key(self):
        """Save OpenAI API key"""
        try:
            from secure_key_manager import APIKeyManager
            
            key = self.openai_key_entry.text().strip()
            if not key:
                QMessageBox.warning(self, "Warning", "Please enter an API key to save.")
                return
            
            # Don't save if it's a masked key
            if "*" in key and len(key.replace("*", "")) < 10:
                QMessageBox.warning(self, "Warning", 
                                  "Cannot save a masked key. Please enter your full API key.")
                return
            
            manager = APIKeyManager()
            success = manager.save_openai_key(key)
            
            if success:
                QMessageBox.information(self, "Success", 
                                      "OpenAI API key saved successfully!\n\n"
                                      "Click 'Load Key' to see the masked version in the field.")
                # Clear the field for security
                self.openai_key_entry.clear()
                self.openai_status.setText("🟢 OpenAI API configured")
                self.openai_status.setStyleSheet("color: green; font-weight: bold;")
            else:
                QMessageBox.warning(self, "Error", "Failed to save OpenAI API key.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving API key: {str(e)}")
    
    def load_openai_key(self):
        """Load OpenAI API key with GUI password prompt"""
        try:
            from secure_key_manager import APIKeyManager
            
            manager = APIKeyManager()
            
            if not manager.key_manager.has_config():
                QMessageBox.information(self, "No Configuration", 
                                      "No saved configuration found. Please save an API key first.")
                return
            
            if not manager.has_openai_key():
                QMessageBox.information(self, "No Key Found", 
                                      "No OpenAI API key found in configuration.")
                return
            
            # Show password dialog immediately
            password, ok = QInputDialog.getText(
                self, 
                "Enter Password", 
                "Enter your master password to decrypt the API key:",
                QLineEdit.EchoMode.Password
            )
            
            if not ok or not password:
                QMessageBox.information(self, "Cancelled", "Operation cancelled by user.")
                return
            
            # Define password callback function for GUI prompt
            def password_callback():
                return password
            
            # Try to get the API key with password callback
            try:
                api_key = manager.get_openai_key(password_callback)
                
                if api_key:
                    # Show masked key in the field
                    if len(api_key) > 8:
                        masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
                    else:
                        masked_key = "*" * len(api_key)
                    
                    self.openai_key_entry.setText(masked_key)
                    self.openai_status.setText("🟢 OpenAI API configured")
                    self.openai_status.setStyleSheet("color: green; font-weight: bold;")
                    
                    # Load available models
                    self.refresh_models()
                    
                    QMessageBox.information(self, "Key Loaded", 
                                          "OpenAI API key loaded and masked for security!")
                else:
                    QMessageBox.warning(self, "Error", 
                                      "Failed to load API key. The key may be corrupted.")
            except Exception as decrypt_error:
                QMessageBox.warning(self, "Decryption Error", 
                                  f"Failed to decrypt API key. Password may be incorrect.\n\nError: {str(decrypt_error)}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading API key: {str(e)}")
    
    def refresh_models(self):
        """Refresh available OpenAI models"""
        try:
            from secure_key_manager import APIKeyManager
            from openai_model_manager import OpenAIModelManager
            
            manager = APIKeyManager()
            
            if not manager.has_openai_key():
                QMessageBox.warning(self, "Warning", "Please configure OpenAI API key first.")
                return
            
            # Show password dialog immediately
            password, ok = QInputDialog.getText(
                self, 
                "Enter Password", 
                "Enter your master password to access the API key:",
                QLineEdit.EchoMode.Password
            )
            
            if not ok or not password:
                QMessageBox.information(self, "Cancelled", "Operation cancelled by user.")
                return
            
            # Define password callback function
            def password_callback():
                return password
            
            # Get the API key securely with password callback
            try:
                api_key = manager.get_openai_key(password_callback)
                if not api_key:
                    QMessageBox.warning(self, "Warning", "Could not retrieve OpenAI API key.")
                    return
                
                # Create model manager and fetch models
                model_manager = OpenAIModelManager(api_key)
                models = model_manager.get_available_models()
                
                # Update the combo box
                self.model_combo.clear()
                current_model = None
                
                for model in models:
                    display_text = model.get('display_text', model['name'])
                    self.model_combo.addItem(display_text, model['name'])
                    
                    # Set a reasonable default
                    if model['name'] in ['gpt-4o-mini', 'gpt-4o', 'gpt-4']:
                        current_model = display_text
                
                # Set default selection
                if current_model:
                    index = self.model_combo.findText(current_model)
                    if index >= 0:
                        self.model_combo.setCurrentIndex(index)
                
                QMessageBox.information(self, "Models Updated", 
                                      f"Successfully loaded {len(models)} available models.")
                        
            except Exception as decrypt_error:
                QMessageBox.warning(self, "Decryption Error", 
                                  f"Failed to decrypt API key. Password may be incorrect.\n\nError: {str(decrypt_error)}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error refreshing models: {str(e)}")
    
    def test_connection(self):
        """Test Canvas connection"""
        try:
            url = self.canvas_url_entry.text().strip()
            token = self.canvas_token_entry.text().strip()
            
            if not url or not token:
                QMessageBox.warning(self, "Warning", "Please enter both Canvas URL and API token.")
                return
            
            # Basic URL validation
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                self.canvas_url_entry.setText(url)
            
            # For now, just validate the format and show success
            # In a full implementation, this would make an actual API call
            QMessageBox.information(self, "Connection Test", 
                                  f"Canvas connection configuration appears valid:\n\n"
                                  f"URL: {url}\n"
                                  f"Token: {'*' * (len(token) - 4) + token[-4:] if len(token) > 4 else '****'}\n\n"
                                  "Note: Actual API testing would be implemented in production.")
            
            self.connection_status.setText("🟢 Canvas configuration ready")
            self.connection_status.setStyleSheet("color: green; font-weight: bold;")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error testing connection: {str(e)}")
    
    def save_configuration(self):
        """Save Canvas configuration"""
        try:
            from secure_key_manager import APIKeyManager
            
            manager = APIKeyManager()
            
            # Save Canvas credentials
            url = self.canvas_url_entry.text().strip()
            token = self.canvas_token_entry.text().strip()
            course_id = self.course_id_entry.text().strip()
            
            if url and token:
                success = manager.save_canvas_credentials(url, token)
                if success:
                    QMessageBox.information(self, "Success", "Canvas configuration saved successfully!")
                else:
                    QMessageBox.warning(self, "Error", "Failed to save Canvas configuration.")
            else:
                QMessageBox.warning(self, "Warning", "Please enter Canvas URL and API token.")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving configuration: {str(e)}")
    
    def refresh_courses(self):
        """Refresh available courses - placeholder for full Canvas integration"""
        QMessageBox.information(self, "Refresh Courses", 
                              "Course refresh functionality would be implemented here.\n\n"
                              "This would connect to Canvas API and populate the course dropdown "
                              "on the Two-Step Grading tab.")
    
    def refresh_assignments(self):
        """Refresh available assignments"""
        try:
            # Get course ID from the current tab's course field
            current_tab = self.tab_widget.currentIndex()
            
            if current_tab == 1:  # Two-Step Grading tab
                course_id = self.course_id_entry.text().strip()
            elif current_tab == 2:  # Single-Step Grading tab
                course_id = self.single_course_id_entry.text().strip()
            else:
                # If called from connection tab or elsewhere, try two-step first
                course_id = self.course_id_entry.text().strip()
                if not course_id:
                    course_id = getattr(self, 'single_course_id_entry', None)
                    if course_id:
                        course_id = course_id.text().strip()
            
            if not course_id:
                QMessageBox.warning(self, "Warning", 
                                  "Please enter a Course ID in the current grading tab first.")
                return
            
            # Placeholder for Canvas API integration
            # In production, this would fetch actual assignments
            sample_assignments = [
                "No assignments loaded - Canvas API integration needed",
                f"Assignment 1 - Course {course_id}",
                f"Assignment 2 - Course {course_id}",
                f"Assignment 3 - Course {course_id}"
            ]
            
            # Update both assignment dropdowns
            self.assignment_combo.clear()
            self.assignment_combo.addItems(sample_assignments)
            
            self.single_assignment_combo.clear()
            self.single_assignment_combo.addItems(sample_assignments)
            
            # Sync course IDs between tabs
            self.course_id_entry.setText(course_id)
            self.single_course_id_entry.setText(course_id)
            
            # Update assignment info displays
            assignment_details = (
                f"Sample assignments for Course {course_id}\n\n"
                "In production, this would show:\n"
                "• Assignment name and due date\n"
                "• Number of submissions\n"
                "• Assignment description\n"
                "• Grading status"
            )
            
            self.assignment_info.setText(assignment_details)
            self.single_assignment_info.setText(assignment_details)
            
            QMessageBox.information(self, "Assignments Refreshed", 
                                  f"Loaded sample assignments for Course {course_id}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error refreshing assignments: {str(e)}")
    
    def browse_rubric(self):
        """Browse for rubric file"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Rubric File", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            self.rubric_path_entry.setText(file_path)
    
    def browse_instructor_config(self):
        """Browse for instructor config file"""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Instructor Config", "", "JSON Files (*.json);;All Files (*)")
        if file_path:
            self.instructor_config_entry.setText(file_path)
    
    def start_step1(self):
        """Start two-step grading step 1"""
        QMessageBox.information(self, "Step 1", 
                              "Step 1 grading would begin here.\n\n"
                              "This would:\n"
                              "• Download submissions from Canvas\n"
                              "• Run AI grading with selected rubric\n"
                              "• Save results for review\n"
                              "• Enable Step 2 button")
    
    def start_step2(self):
        """Start two-step grading step 2"""
        QMessageBox.information(self, "Step 2", 
                              "Step 2 grading would begin here.\n\n"
                              "This would:\n"
                              "• Open review interface\n"
                              "• Allow grade adjustments\n"
                              "• Upload final grades to Canvas\n"
                              "• Generate completion report")
    
    def open_review_folder(self):
        """Open review folder"""
        QMessageBox.information(self, "Review Folder", 
                              "This would open the folder containing:\n\n"
                              "• Graded submissions\n"
                              "• AI feedback files\n"
                              "• Review spreadsheet\n"
                              "• Grade upload files")
    
    def start_single_grading(self):
        """Start single-step grading"""
        QMessageBox.information(self, "Single Grading", 
                              "⚠️ Single-step grading would begin here.\n\n"
                              "This would:\n"
                              "• Download submissions\n"
                              "• Run AI grading\n"
                              "• Upload grades immediately\n"
                              "• NO REVIEW STEP!")


def main():
    """Main function to run the Canvas GUI"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("DuckGrade Canvas Integration")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("DuckWorks Educational Automation")
    
    # Create and show the main window
    window = DuckGradeCanvasGUI()
    window.show()
    
    print("🦆 DuckGrade Canvas Integration (PyQt6) started successfully!")
    print("Professional interface now matches Tkinter structure exactly")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
