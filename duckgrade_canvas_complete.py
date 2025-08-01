"""
DuckGrade Canvas Integration - PyQt6 Modern Interface
Complete implementation matching Tkinter canvas_gui.py structure

This version provides a professional PyQt6 interface that exactly matches
the functionality and layout of the original Tkinter Canvas GUI.
"""

import sys
from pathlib import Path
import threading
import json
import os
from PyQt6.QtWidgets import (QApplication, QMainWindow, QTabWidget, QWidget, 
                            QVBoxLayout, QHBoxLayout, QGroupBox, QLabel, 
                            QLineEdit, QPushButton, QComboBox, QTextEdit,
                            QCheckBox, QProgressBar, QMessageBox, QFileDialog,
                            QSpacerItem, QSizePolicy, QInputDialog, QScrollArea,
                            QRadioButton, QButtonGroup)
from PyQt6.QtCore import Qt, QSize, QEvent, QTimer, QObject, pyqtSignal
from PyQt6.QtGui import QIcon, QFont

# Import Canvas integration components
try:
    from canvas_integration import CanvasAPI, TwoStepCanvasGrading
except ImportError:
    print("Warning: Canvas integration module not found. Some functionality may be limited.")
    CanvasAPI = None
    TwoStepCanvasGrading = None

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


class Step1Worker(QObject):
    """Worker class for running Step 1 in background thread with proper signals"""
    progress_updated = pyqtSignal(int, str)  # percent, description
    log_message = pyqtSignal(str)  # message
    completed = pyqtSignal(dict)  # results
    error_occurred = pyqtSignal(str)  # error message
    
    def __init__(self, canvas_api, course_id, course_name, assignment_id, assignment_name, 
                 use_canvas_rubric, rubric_path, instructor_config_path, openai_key, selected_model):
        super().__init__()
        self.canvas_api = canvas_api
        self.course_id = course_id
        self.course_name = course_name
        self.assignment_id = assignment_id
        self.assignment_name = assignment_name
        self.use_canvas_rubric = use_canvas_rubric
        self.rubric_path = rubric_path
        self.instructor_config_path = instructor_config_path
        self.openai_key = openai_key
        self.selected_model = selected_model
    
    def run(self):
        """Run Step 1 process"""
        try:
            # Log start of Step 1
            self.progress_updated.emit(10, "Initializing...")
            self.log_message.emit("Starting Step 1: Download and Grade with Privacy Protection")
            self.log_message.emit(f"Course: {self.course_name}")
            self.log_message.emit(f"Assignment: {self.assignment_name}")
            
            if self.use_canvas_rubric:
                self.log_message.emit("Will download Canvas rubric automatically")
            else:
                self.log_message.emit(f"Using local rubric: {Path(self.rubric_path).name}")
            
            if self.instructor_config_path:
                self.log_message.emit(f"Using instructor config: {Path(self.instructor_config_path).name}")
            else:
                self.log_message.emit("Using default grading style")
            
            self.log_message.emit("Student names will be anonymized for AI processing")
            
            # Check if we have the TwoStepCanvasGrading class
            if TwoStepCanvasGrading is None:
                raise Exception("Canvas integration module not available. Please ensure canvas_integration.py is present.")
            
            # Initialize grading agent
            try:
                from grading_agent import GradingAgent
                grading_agent = GradingAgent(self.openai_key, model=self.selected_model)
                two_step_grading = TwoStepCanvasGrading(self.canvas_api, grading_agent)
            except ImportError:
                raise Exception("Grading agent module not found. Please ensure grading_agent.py is available.")
            
            # Update progress
            self.progress_updated.emit(30, "Downloading submissions...")
            
            # Create progress callback that emits signals
            def progress_callback(percent, description):
                self.progress_updated.emit(percent, description)
                
            # Create log callback that emits signals
            def log_callback(message):
                self.log_message.emit(message)
            
            # Run Step 1
            results = two_step_grading.step1_download_and_grade(
                course_id=self.course_id,
                assignment_id=self.assignment_id,
                assignment_name=self.assignment_name,
                rubric_path=self.rubric_path,
                instructor_config_path=self.instructor_config_path,
                use_canvas_rubric=self.use_canvas_rubric,
                progress_callback=progress_callback,
                log_callback=log_callback
            )
            
            # Log results for debugging
            self.log_message.emit(f"Step 1 results: success={results.get('success', False)}")
            if 'review_file' in results:
                self.log_message.emit(f"Review file reported: {results['review_file']}")
                if os.path.exists(results['review_file']):
                    self.log_message.emit("✓ Review file exists on disk")
                else:
                    self.log_message.emit("❌ Review file not found on disk")
            else:
                self.log_message.emit("❌ No review_file in results")
            
            # Update metadata file with Canvas IDs
            if results['success']:
                metadata_file = os.path.join(results['folder_path'], "assignment_metadata.json")
                if os.path.exists(metadata_file):
                    with open(metadata_file, 'r') as f:
                        metadata = json.load(f)
                    metadata['course_id'] = self.course_id
                    metadata['assignment_id'] = self.assignment_id
                    with open(metadata_file, 'w') as f:
                        json.dump(metadata, f, indent=2)
            
            # Emit completion signal
            self.completed.emit(results)
            
        except Exception as e:
            self.error_occurred.emit(str(e))


class ScrollFriendlyComboBox(QComboBox):
    """
    Custom ComboBox that doesn't capture wheel events when not focused.
    This allows users to scroll the parent widget without interruption.
    """
    def __init__(self, parent=None):
        super().__init__(parent)
        self._wheel_enabled = False
    
    def wheelEvent(self, event):
        # Only process wheel events if explicitly enabled (after clicking)
        if self._wheel_enabled and self.hasFocus():
            super().wheelEvent(event)
        else:
            # Ignore the wheel event and let it propagate to parent
            event.ignore()
    
    def mousePressEvent(self, event):
        # Enable wheel events when combo box is clicked
        self._wheel_enabled = True
        super().mousePressEvent(event)
    
    def focusOutEvent(self, event):
        # Disable wheel events when focus is lost
        self._wheel_enabled = False
        super().focusOutEvent(event)


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
        # Cache for decrypted credentials to avoid repeated password prompts
        self._cached_openai_key = None
        self._cached_canvas_url = None
        self._cached_canvas_token = None
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
        self.tab_widget.addTab(self.create_connection_tab(), "API Connections")
        self.tab_widget.addTab(self.create_two_step_tab(), "📋 Two-Step Grading")
        self.tab_widget.addTab(self.create_single_step_tab(), "⚡ Single-Step Grading")
        self.tab_widget.addTab(self.create_results_tab(), "📊 Results")
        
        main_layout.addWidget(self.tab_widget)
    
    def create_connection_tab(self) -> QWidget:
        """Create Canvas Connection tab matching Tkinter structure"""
        # Create main tab widget
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget that will go inside scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
        # OpenAI Configuration Group
        openai_group = QGroupBox("🤖 OpenAI Configuration")
        openai_layout = QVBoxLayout(openai_group)
        
        # API Key row
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.openai_key_entry = QLineEdit()
        self.openai_key_entry.setEchoMode(QLineEdit.EchoMode.Password)
        self.openai_key_entry.setPlaceholderText("Enter your OpenAI API key")
        self.openai_key_entry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        key_layout.addWidget(self.openai_key_entry)
        
        openai_layout.addLayout(key_layout)
        
        # Model selection row
        model_layout = QHBoxLayout()
        model_layout.addWidget(QLabel("Model:"))
        
        self.model_combo = ScrollFriendlyComboBox()
        self.model_combo.addItem("gpt-4o-mini")
        self.model_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Style the ComboBox with custom arrow using PNG
        self.model_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 10pt;
                min-width: 350px;
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
        
        # Connection test and configuration buttons
        test_layout = QHBoxLayout()
        test_connection_btn = QPushButton("Connect")
        
        # Add network icon if available
        if Path("assets/network_outlined.png").exists():
            test_connection_btn.setIcon(QIcon("assets/network_outlined.png"))
            test_connection_btn.setIconSize(QSize(16, 16))
        
        test_connection_btn.clicked.connect(self.test_connection)
        test_layout.addWidget(test_connection_btn)
        
        load_config_btn = QPushButton("📂 Load Configuration")
        load_config_btn.clicked.connect(self.load_configuration)
        test_layout.addWidget(load_config_btn)
        
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
        
        self.openai_status = QLabel("🔴 OpenAI API not configured")
        self.openai_status.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.openai_status)
        
        self.connection_status = QLabel("🔴 Not connected to Canvas")
        self.connection_status.setStyleSheet("color: red; font-weight: bold;")
        status_layout.addWidget(self.connection_status)
        
        # Test mode button for development/testing
        test_mode_layout = QHBoxLayout()
        test_mode_btn = QPushButton("🧪 Enable Test Mode")
        test_mode_btn.setToolTip("Enable grading buttons for testing without Canvas connection")
        test_mode_btn.clicked.connect(self.enable_test_mode)
        test_mode_btn.setFixedHeight(21)
        test_mode_layout.addWidget(test_mode_btn)
        test_mode_layout.addStretch()
        status_layout.addLayout(test_mode_layout)
        
        layout.addWidget(status_group)
        layout.addStretch()
        
        # Set the content widget in the scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to the main tab layout
        tab_layout.addWidget(scroll_area)
        
        return tab
    
    def create_two_step_tab(self) -> QWidget:
        """Create Two-Step Grading tab matching Tkinter structure"""
        # Create main tab widget
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget that will go inside scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
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
        
        # Course selection input
        course_layout = QHBoxLayout()
        course_layout.addWidget(QLabel("Course:"))
        
        self.course_id_combo = ScrollFriendlyComboBox()
        self.course_id_combo.addItem("No courses loaded")
        self.course_id_combo.setEditable(True)  # Allow manual entry
        self.course_id_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Style the ComboBox with custom arrow using PNG (same as Model dropdown)
        self.course_id_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 10pt;
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
        
        course_layout.addWidget(self.course_id_combo)
        
        # Connect course selection to assignment refresh
        self.course_id_combo.currentIndexChanged.connect(self.on_course_selected)
        
        assignment_layout.addLayout(course_layout)
        
        # Assignment dropdown
        assignment_select_layout = QHBoxLayout()
        assignment_select_layout.addWidget(QLabel("Select Assignment:"))
        self.assignment_combo = ScrollFriendlyComboBox()
        self.assignment_combo.addItem("No assignments loaded")
        self.assignment_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        # Style the assignment ComboBox with custom arrow (same as Model and Course dropdowns)
        self.assignment_combo.setStyleSheet("""
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 10pt;
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
        
        assignment_select_layout.addWidget(self.assignment_combo)
        
        refresh_assignments_btn = QPushButton("↻ Refresh")
        refresh_assignments_btn.clicked.connect(self.refresh_assignments)
        assignment_select_layout.addWidget(refresh_assignments_btn)
        
        assignment_layout.addLayout(assignment_select_layout)
        
        # Assignment info (removed - no details functionality implemented)
        # self.assignment_info = QLabel("Select an assignment to view details")
        # self.assignment_info.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 4px;")
        # assignment_layout.addWidget(self.assignment_info)
        
        layout.addWidget(assignment_group)
        
        # Grading Configuration Group
        config_group = QGroupBox("⚙️ Grading Configuration")
        config_layout = QVBoxLayout(config_group)
        
        # Rubric source selection
        rubric_source_layout = QHBoxLayout()
        rubric_source_layout.addWidget(QLabel("Rubric Source:"))
        
        # Create button group for radio buttons (ensures mutual exclusivity)
        self.rubric_source_group = QButtonGroup(self)
        
        self.local_rubric_radio = QRadioButton("Local File")
        self.local_rubric_radio.setChecked(True)  # Default to local file
        self.local_rubric_radio.toggled.connect(self.on_rubric_source_changed)
        self.rubric_source_group.addButton(self.local_rubric_radio, 0)
        rubric_source_layout.addWidget(self.local_rubric_radio)
        
        self.canvas_rubric_radio = QRadioButton("Canvas Rubric")
        self.canvas_rubric_radio.toggled.connect(self.on_rubric_source_changed)
        self.rubric_source_group.addButton(self.canvas_rubric_radio, 1)
        rubric_source_layout.addWidget(self.canvas_rubric_radio)
        
        rubric_source_layout.addStretch()
        config_layout.addLayout(rubric_source_layout)
        
        # Local rubric file selection (initially visible)
        self.local_rubric_widget = QWidget()
        local_rubric_layout = QHBoxLayout(self.local_rubric_widget)
        local_rubric_layout.setContentsMargins(0, 0, 0, 0)
        local_rubric_layout.addWidget(QLabel("Rubric File:"))
        self.rubric_path_entry = QLineEdit("rubrics/sample_rubric.json")
        self.rubric_path_entry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        local_rubric_layout.addWidget(self.rubric_path_entry)
        
        browse_rubric_btn = QPushButton("Browse")
        browse_rubric_btn.setFixedHeight(21)
        browse_rubric_btn.clicked.connect(self.browse_rubric)
        local_rubric_layout.addWidget(browse_rubric_btn)
        
        config_layout.addWidget(self.local_rubric_widget)
        
        # Canvas rubric info (initially hidden)
        self.canvas_rubric_widget = QWidget()
        canvas_rubric_layout = QHBoxLayout(self.canvas_rubric_widget)
        canvas_rubric_layout.setContentsMargins(0, 0, 0, 0)
        canvas_rubric_info = QLabel("✓ Canvas rubric will be downloaded automatically from the selected assignment")
        canvas_rubric_info.setStyleSheet("color: #28a745; font-weight: bold; padding: 5px;")
        canvas_rubric_layout.addWidget(canvas_rubric_info)
        canvas_rubric_layout.addStretch()
        
        config_layout.addWidget(self.canvas_rubric_widget)
        self.canvas_rubric_widget.hide()  # Initially hidden
        
        # Instructor config
        instructor_layout = QHBoxLayout()
        instructor_layout.addWidget(QLabel("Instructor Config (Optional):"))
        self.instructor_config_entry = QLineEdit("config/grading_instructor_config.json")
        instructor_layout.addWidget(self.instructor_config_entry)
        
        browse_instructor_btn = QPushButton("Browse")
        browse_instructor_btn.clicked.connect(self.browse_instructor_config)
        instructor_layout.addWidget(browse_instructor_btn)
        
        config_layout.addLayout(instructor_layout)
        
        layout.addWidget(config_group)
        
        # Step 1: AI Grading Group
        step1_group = QGroupBox("🤖 Step 1: AI Grading")
        step1_layout = QVBoxLayout(step1_group)
        
        step1_desc = QLabel("Downloads submissions, runs AI grading, saves results for review")
        step1_layout.addWidget(step1_desc)
        
        step1_button_layout = QHBoxLayout()
        self.step1_button = QPushButton("🚀 Start Step 1: Download and Grade")
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
        
        # Step 2: Review and Upload Group
        step2_group = QGroupBox("👁️ Step 2: Review and Upload")
        step2_layout = QVBoxLayout(step2_group)
        
        step2_desc = QLabel("Review AI grading results, make adjustments, upload final grades")
        step2_layout.addWidget(step2_desc)
        
        step2_button_layout = QHBoxLayout()
        self.step2_button = QPushButton("📋 Start Step 2: Upload")
        self.step2_button.setEnabled(False)
        self.step2_button.clicked.connect(self.start_step2)
        step2_button_layout.addWidget(self.step2_button)
        
        review_folder_btn = QPushButton("📁 Open Review Folder")
        review_folder_btn.clicked.connect(self.open_review_folder)
        step2_button_layout.addWidget(review_folder_btn)
        
        # Store as instance variable for enabling/disabling
        self.review_folder_btn = review_folder_btn
        
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
        
        # Log Group
        log_group = QGroupBox("📋 Grading Log")
        log_layout = QVBoxLayout(log_group)
        
        self.two_step_log = QTextEdit()
        self.two_step_log.setReadOnly(True)
        self.two_step_log.setMaximumHeight(500)  # Increased from 200 to 500 (2.5x)
        self.two_step_log.setPlainText("Two-step grading log will appear here...")
        log_layout.addWidget(self.two_step_log)
        
        layout.addWidget(log_group)
        layout.addStretch()
        
        # Set the content widget in the scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to the main tab layout
        tab_layout.addWidget(scroll_area)
        
        return tab
    
    def create_single_step_tab(self) -> QWidget:
        """Create Single-Step Grading tab matching Tkinter structure"""
        # Create main tab widget
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget that will go inside scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
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
        self.single_assignment_combo = ScrollFriendlyComboBox()
        self.single_assignment_combo.addItem("No assignments loaded")
        self.single_assignment_combo.setMinimumWidth(280)  # Standard width for dropdown
        single_assignment_select_layout.addWidget(self.single_assignment_combo)
        
        refresh_single_assignments_btn = QPushButton("↻ Refresh")
        refresh_single_assignments_btn.clicked.connect(self.refresh_assignments)
        single_assignment_select_layout.addWidget(refresh_single_assignments_btn)
        
        single_assignment_layout.addLayout(single_assignment_select_layout)
        
        # Assignment info for single step (removed - no details functionality implemented)
        # self.single_assignment_info = QLabel("Select an assignment to view details")
        # self.single_assignment_info.setStyleSheet("padding: 10px; background-color: #f8f9fa; border-radius: 4px;")
        # single_assignment_layout.addWidget(self.single_assignment_info)
        
        layout.addWidget(single_assignment_group)
        
        # Configuration Group
        single_config_group = QGroupBox("⚙️ Grading Configuration")
        single_config_layout = QVBoxLayout(single_config_group)
        
        # Rubric source selection for single step
        single_rubric_source_layout = QHBoxLayout()
        single_rubric_source_layout.addWidget(QLabel("Rubric Source:"))
        
        # Create button group for radio buttons (ensures mutual exclusivity)
        self.single_rubric_source_group = QButtonGroup(self)
        
        self.single_local_rubric_radio = QRadioButton("Local File")
        self.single_local_rubric_radio.setChecked(True)  # Default to local file
        self.single_local_rubric_radio.toggled.connect(self.on_single_rubric_source_changed)
        self.single_rubric_source_group.addButton(self.single_local_rubric_radio, 0)
        single_rubric_source_layout.addWidget(self.single_local_rubric_radio)
        
        self.single_canvas_rubric_radio = QRadioButton("Canvas Rubric")
        self.single_canvas_rubric_radio.toggled.connect(self.on_single_rubric_source_changed)
        self.single_rubric_source_group.addButton(self.single_canvas_rubric_radio, 1)
        single_rubric_source_layout.addWidget(self.single_canvas_rubric_radio)
        
        single_rubric_source_layout.addStretch()
        single_config_layout.addLayout(single_rubric_source_layout)
        
        # Local rubric file selection (initially visible)
        self.single_local_rubric_widget = QWidget()
        single_local_rubric_layout = QHBoxLayout(self.single_local_rubric_widget)
        single_local_rubric_layout.setContentsMargins(0, 0, 0, 0)
        single_local_rubric_layout.addWidget(QLabel("Rubric File:"))
        self.single_rubric_entry = QLineEdit("rubrics/sample_rubric.json")
        self.single_rubric_entry.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        single_local_rubric_layout.addWidget(self.single_rubric_entry)
        
        browse_single_rubric_btn = QPushButton("Browse")
        browse_single_rubric_btn.setFixedHeight(21)
        browse_single_rubric_btn.clicked.connect(self.browse_single_rubric)
        single_local_rubric_layout.addWidget(browse_single_rubric_btn)
        
        single_config_layout.addWidget(self.single_local_rubric_widget)
        
        # Canvas rubric info for single step (initially hidden)
        self.single_canvas_rubric_widget = QWidget()
        single_canvas_rubric_layout = QHBoxLayout(self.single_canvas_rubric_widget)
        single_canvas_rubric_layout.setContentsMargins(0, 0, 0, 0)
        single_canvas_rubric_info = QLabel("✓ Canvas rubric will be downloaded automatically from the selected assignment")
        single_canvas_rubric_info.setStyleSheet("color: #28a745; font-weight: bold; padding: 5px;")
        single_canvas_rubric_layout.addWidget(single_canvas_rubric_info)
        single_canvas_rubric_layout.addStretch()
        
        single_config_layout.addWidget(self.single_canvas_rubric_widget)
        self.single_canvas_rubric_widget.hide()  # Initially hidden
        
        # Instructor config
        single_instructor_layout = QHBoxLayout()
        single_instructor_layout.addWidget(QLabel("Instructor Config (Optional):"))
        self.single_instructor_entry = QLineEdit("config/grading_instructor_config.json")
        single_instructor_layout.addWidget(self.single_instructor_entry)
        
        browse_single_instructor_btn = QPushButton("Browse")
        single_instructor_layout.addWidget(browse_single_instructor_btn)
        
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
        self.single_step_log.setMaximumHeight(500)  # Increased from 200 to 500 (2.5x)
        self.single_step_log.setPlainText("Single-step grading log will appear here...")
        log_layout.addWidget(self.single_step_log)
        
        layout.addWidget(log_group)
        layout.addStretch()
        
        # Set the content widget in the scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to the main tab layout
        tab_layout.addWidget(scroll_area)
        
        return tab
    
    def create_results_tab(self) -> QWidget:
        """Create Results tab matching Tkinter structure"""
        # Create main tab widget
        tab = QWidget()
        tab_layout = QVBoxLayout(tab)
        
        # Create scroll area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Create content widget that will go inside scroll area
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        
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
        
        # Set the content widget in the scroll area
        scroll_area.setWidget(content_widget)
        
        # Add scroll area to the main tab layout
        tab_layout.addWidget(scroll_area)
        
        return tab
    
    def setup_window(self):
        """Setup window properties"""
        self.setWindowTitle("DuckGrade Canvas Integration - DuckWorks Educational Suite")
        
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
                height: 21px;
                min-height: 21px;
                max-height: 21px;
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
                font-size: 10pt;
            }
            QComboBox {
                border: 1px solid #ced4da;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
                font-size: 10pt;
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
            QScrollArea {
                border: none;
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #f8f9fa;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #6c757d;
                border-radius: 6px;
                min-height: 20px;
            }
            QScrollBar::handle:vertical:hover {
                background-color: #495057;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
        """)
    
    def center_window(self):
        """Center the window on the screen"""
        frame_geometry = self.frameGeometry()
        screen = self.screen().availableGeometry()
        center_point = screen.center()
        frame_geometry.moveCenter(center_point)
        self.move(frame_geometry.topLeft())
    
    def save_configuration(self):
        """Save unified configuration (OpenAI API key + Canvas credentials)"""
        try:
            from secure_key_manager import APIKeyManager
            
            # Get all configuration values
            openai_key = self.openai_key_entry.text().strip()
            canvas_url = self.canvas_url_entry.text().strip()
            canvas_token = self.canvas_token_entry.text().strip()
            
            # Validate inputs
            if not openai_key and not (canvas_url and canvas_token):
                QMessageBox.warning(self, "Warning", 
                                  "Please enter at least an OpenAI API key or Canvas credentials to save.")
                return
            
            # Don't save if OpenAI key is masked
            if openai_key and "*" in openai_key and len(openai_key.replace("*", "")) < 10:
                QMessageBox.warning(self, "Warning", 
                                  "Cannot save a masked OpenAI key. Please enter your full API key or leave it blank.")
                return
            
            # Don't save if Canvas token is masked
            if canvas_token and "*" in canvas_token and len(canvas_token.replace("*", "")) < 10:
                QMessageBox.warning(self, "Warning", 
                                  "Cannot save a masked Canvas token. Please enter your full API token or leave it blank.")
                return
            
            # Show password dialog for encryption
            password, ok = QInputDialog.getText(
                self, 
                "Set Master Password", 
                "Enter a master password to encrypt your configuration:\n\n"
                "This password will be required to load your saved settings.\n"
                "Please remember this password - it cannot be recovered!",
                QLineEdit.EchoMode.Password
            )
            
            if not ok or not password:
                QMessageBox.information(self, "Cancelled", "Configuration save cancelled by user.")
                return
            
            if len(password) < 4:
                QMessageBox.warning(self, "Password Too Short", 
                                  "Please enter a password with at least 4 characters for security.")
                return
            
            # Confirm password
            confirm_password, ok = QInputDialog.getText(
                self, 
                "Confirm Password", 
                "Please confirm your master password:",
                QLineEdit.EchoMode.Password
            )
            
            if not ok or confirm_password != password:
                QMessageBox.warning(self, "Password Mismatch", 
                                  "Passwords do not match. Please try again.")
                return
            
            # Create manager and define password callback
            def password_callback(action="unlock"):
                return password
            
            manager = APIKeyManager()
            success_messages = []
            
            # Save OpenAI API key if provided
            if openai_key:
                success = manager.save_openai_key(openai_key, password_callback)
                if success:
                    success_messages.append("✅ OpenAI API key saved")
                    self.openai_status.setText("🟢 OpenAI API configured")
                    self.openai_status.setStyleSheet("color: green; font-weight: bold;")
                    # Cache the newly saved key for this session
                    self._cached_openai_key = openai_key
                    # Don't clear the field - keep the manually entered key visible
                    # Only clear if it was already masked
                    # self.openai_key_entry.clear()
                else:
                    QMessageBox.warning(self, "Error", "Failed to save OpenAI API key.")
                    return
            
            # Save Canvas credentials if provided
            if canvas_url and canvas_token:
                success = manager.save_canvas_credentials(canvas_url, canvas_token, password_callback)
                if success:
                    success_messages.append("✅ Canvas credentials saved")
                    # Cache the newly saved credentials for this session
                    self._cached_canvas_url = canvas_url
                    self._cached_canvas_token = canvas_token
                else:
                    QMessageBox.warning(self, "Error", "Failed to save Canvas credentials.")
                    return
            
            # Show success message
            if success_messages:
                QMessageBox.information(self, "Configuration Saved", 
                                      "Configuration saved successfully!\n\n" + 
                                      "\n".join(success_messages) + 
                                      "\n\nYour settings are encrypted with your master password.\n" +
                                      "Click 'Load Configuration' to restore these settings later.")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving configuration: {str(e)}")
    
    def load_configuration(self):
        """Load unified configuration (OpenAI API key + Canvas credentials)"""
        try:
            from secure_key_manager import APIKeyManager
            
            # Create manager first to check if config exists
            temp_manager = APIKeyManager()
            
            if not temp_manager.key_manager.has_config():
                QMessageBox.information(self, "No Configuration", 
                                      "No saved configuration found. Please save configuration first.")
                return
            
            # Show password dialog immediately
            password, ok = QInputDialog.getText(
                self, 
                "Enter Master Password", 
                "Enter your master password to decrypt the saved configuration:",
                QLineEdit.EchoMode.Password
            )
            
            if not ok or not password:
                QMessageBox.information(self, "Cancelled", "Operation cancelled by user.")
                return
            
            # Define password callback function for GUI prompt
            def password_callback(action="unlock"):
                return password
            
            # Create manager
            manager = APIKeyManager()
            
            try:
                loaded_items = []
                
                # Try to load OpenAI API key
                if manager.has_openai_key():
                    try:
                        api_key = manager.get_openai_key(password_callback)
                        if api_key:
                            # Cache the real API key for later use
                            self._cached_openai_key = api_key
                            
                            # Show masked key in the field
                            if len(api_key) > 8:
                                masked_key = api_key[:4] + "*" * (len(api_key) - 8) + api_key[-4:]
                            else:
                                masked_key = "*" * len(api_key)
                            
                            self.openai_key_entry.setText(masked_key)
                            self.openai_status.setText("🟢 OpenAI API configured")
                            self.openai_status.setStyleSheet("color: green; font-weight: bold;")
                            loaded_items.append("✅ OpenAI API key loaded")
                            
                            # Load available models with the same password
                            self.refresh_models(password)
                    except Exception:
                        loaded_items.append("⚠️ OpenAI API key could not be loaded")
                
                # Try to load Canvas credentials
                try:
                    canvas_creds = manager.get_canvas_credentials(password_callback)
                    if canvas_creds.get('canvas_url') and canvas_creds.get('canvas_api_token'):
                        # Cache the real credentials for later use
                        self._cached_canvas_url = canvas_creds['canvas_url']
                        self._cached_canvas_token = canvas_creds['canvas_api_token']
                        
                        self.canvas_url_entry.setText(canvas_creds['canvas_url'])
                        # Show masked token
                        token = canvas_creds['canvas_api_token']
                        if len(token) > 8:
                            masked_token = token[:4] + "*" * (len(token) - 8) + token[-4:]
                        else:
                            masked_token = "*" * len(token)
                        self.canvas_token_entry.setText(masked_token)
                        loaded_items.append("✅ Canvas credentials loaded")
                except Exception:
                    loaded_items.append("⚠️ Canvas credentials could not be loaded")
                
                # Show results
                if loaded_items:
                    QMessageBox.information(self, "Configuration Loaded", 
                                          "Configuration loaded successfully!\n\n" + 
                                          "\n".join(loaded_items) + 
                                          "\n\nCredentials are masked for security.")
                else:
                    QMessageBox.warning(self, "No Data", 
                                      "No configuration data could be loaded.")
                    
            except Exception as decrypt_error:
                QMessageBox.warning(self, "Decryption Error", 
                                  f"Failed to decrypt configuration. Password may be incorrect.\n\nError: {str(decrypt_error)}")
                
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error loading configuration: {str(e)}")
    
    def refresh_models(self, existing_password=None):
        """Refresh available OpenAI models"""
        try:
            from secure_key_manager import APIKeyManager
            from openai_model_manager import OpenAIModelManager
            
            temp_manager = APIKeyManager()
            
            if not temp_manager.has_openai_key():
                QMessageBox.warning(self, "Warning", "Please configure OpenAI API key first.")
                return
            
            # Use existing password if provided, otherwise try cached key, then show password dialog
            api_key = None
            if existing_password:
                password = existing_password
            elif self._cached_openai_key:
                # Use cached API key directly
                api_key = self._cached_openai_key
            else:
                # Show password dialog immediately
                password, ok = QInputDialog.getText(
                    self, 
                    "Enter Master Password", 
                    "Enter your master password to access the API key:",
                    QLineEdit.EchoMode.Password
                )
                
                if not ok or not password:
                    QMessageBox.information(self, "Cancelled", "Operation cancelled by user.")
                    return
            
            # Get the API key securely with password callback or from cache
            try:
                if not api_key:
                    # Define password callback function
                    def password_callback(action="unlock"):
                        return password
                    
                    # Create manager
                    manager = APIKeyManager()
                    
                    api_key = manager.get_openai_key(password_callback)
                    if api_key:
                        # Cache the key for future use
                        self._cached_openai_key = api_key
                
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
                    model_id = model.get('base_model', model['name'])  # Use base_model for API calls
                    self.model_combo.addItem(display_text, model_id)
                    
                    # Set a reasonable default
                    if model_id in ['gpt-4o-mini', 'gpt-4o', 'gpt-4']:
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
        """Test Canvas connection with real API call"""
        try:
            url = self.canvas_url_entry.text().strip()
            token = self.canvas_token_entry.text().strip()
            
            if not url or not token:
                QMessageBox.warning(self, "Warning", "Please enter both Canvas URL and API token.")
                return
            
            # Check if token is masked - if so, get the real token from cache or secure storage
            if "*" in token and len(token.replace("*", "")) < 10:
                # Token appears to be masked, try to use cached credentials first
                if self._cached_canvas_url and self._cached_canvas_token:
                    # Use cached credentials - no password prompt needed
                    url = self._cached_canvas_url
                    token = self._cached_canvas_token
                else:
                    # No cached credentials, get from secure storage
                    try:
                        from secure_key_manager import APIKeyManager
                        
                        manager = APIKeyManager()
                        if not manager.key_manager.has_config():
                            QMessageBox.warning(self, "Warning", 
                                              "No saved configuration found. Please enter your full Canvas API token.")
                            return
                        
                        # Show password dialog to get real credentials
                        password, ok = QInputDialog.getText(
                            self, 
                            "Enter Master Password", 
                            "Enter your master password to access saved Canvas credentials:",
                            QLineEdit.EchoMode.Password
                        )
                        
                        if not ok or not password:
                            QMessageBox.information(self, "Cancelled", "Operation cancelled by user.")
                            return
                        
                        # Define password callback function
                        def password_callback(action="unlock"):
                            return password
                        
                        # Get real credentials
                        canvas_creds = manager.get_canvas_credentials(password_callback)
                        if canvas_creds.get('canvas_url') and canvas_creds.get('canvas_api_token'):
                            url = canvas_creds['canvas_url']
                            token = canvas_creds['canvas_api_token']
                            # Cache for future use
                            self._cached_canvas_url = url
                            self._cached_canvas_token = token
                        else:
                            QMessageBox.warning(self, "Warning", 
                                              "Could not retrieve Canvas credentials. Please enter them manually.")
                            return
                            
                    except Exception as cred_error:
                        QMessageBox.warning(self, "Error", 
                                          f"Failed to retrieve saved credentials: {str(cred_error)}\n\n"
                                          f"Please enter your full Canvas API token manually.")
                        return
            
            # Basic URL validation
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url
                self.canvas_url_entry.setText(url)
            
            # Import Canvas API class
            try:
                from canvas_integration import CanvasAPI
            except ImportError:
                QMessageBox.critical(self, "Error", "Canvas integration module not found. Please ensure canvas_integration.py is available.")
                return
            
            # Create Canvas API instance and test connection
            try:
                canvas_api = CanvasAPI(url, token)
                
                # Test connection with actual API call
                courses = canvas_api.get_courses()
                
                # Success! Show connection details
                QMessageBox.information(self, "Connection Successful", 
                                      f"✅ Successfully connected to Canvas!\n\n"
                                      f"URL: {url}\n"
                                      f"Token: {'*' * (len(token) - 4) + token[-4:] if len(token) > 4 else '****'}\n"
                                      f"Courses found: {len(courses)}\n\n"
                                      f"Privacy protection: Student names will be anonymized for AI processing.")
                
                self.connection_status.setText("🟢 Connected to Canvas")
                self.connection_status.setStyleSheet("color: green; font-weight: bold;")
                
                # Store the Canvas API instance for later use
                self.canvas_api = canvas_api
                
                # Populate course dropdowns with the retrieved courses
                self.populate_course_dropdowns(courses)
                
                # Enable buttons that require Canvas connection
                self.step1_button.setEnabled(True)
                self.single_grade_button.setEnabled(True)
                
            except Exception as api_error:
                # Connection failed - show specific error
                error_msg = str(api_error)
                
                if "401" in error_msg or "unauthorized" in error_msg.lower():
                    QMessageBox.critical(self, "Connection Failed", 
                                       f"❌ Authentication failed.\n\n"
                                       f"Please check your API token:\n"
                                       f"• Token may be invalid or expired\n"
                                       f"• Token may not have required permissions\n\n"
                                       f"Error: {error_msg}")
                elif "404" in error_msg or "not found" in error_msg.lower():
                    QMessageBox.critical(self, "Connection Failed", 
                                       f"❌ Canvas URL not found.\n\n"
                                       f"Please check your Canvas URL:\n"
                                       f"• Ensure the URL is correct\n"
                                       f"• Include the full domain (e.g., yourschool.instructure.com)\n\n"
                                       f"Error: {error_msg}")
                elif "timeout" in error_msg.lower() or "connection" in error_msg.lower():
                    QMessageBox.critical(self, "Connection Failed", 
                                       f"❌ Network connection failed.\n\n"
                                       f"Please check:\n"
                                       f"• Your internet connection\n"
                                       f"• Canvas server availability\n"
                                       f"• Firewall settings\n\n"
                                       f"Error: {error_msg}")
                else:
                    QMessageBox.critical(self, "Connection Failed", 
                                       f"❌ Canvas connection failed.\n\n"
                                       f"Error: {error_msg}")
                
                self.connection_status.setText("� Canvas connection failed")
                self.connection_status.setStyleSheet("color: red; font-weight: bold;")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error during connection test: {str(e)}")
            self.connection_status.setText("🔴 Connection test error")
            self.connection_status.setStyleSheet("color: red; font-weight: bold;")
    
    def populate_course_dropdowns(self, courses):
        """Populate course dropdowns with retrieved courses from Canvas"""
        try:
            # Clear existing items from course dropdowns
            self.course_id_combo.clear()
            
            # Check if we have courses
            if not courses:
                self.course_id_combo.addItem("No courses found")
                return
            
            # Add placeholder for course selection
            self.course_id_combo.addItem("Please select a course", None)
            
            # Sort courses by name for easier selection
            sorted_courses = sorted(courses, key=lambda c: c.get('name', ''))
            
            # Add courses to dropdown
            for course in sorted_courses:
                course_id = course.get('id')
                course_name = course.get('name', 'Unnamed Course')
                
                # Create display text: "Course Name (ID: 12345)"
                display_text = f"{course_name} (ID: {course_id})"
                
                # Add item with display text, store course_id as data
                self.course_id_combo.addItem(display_text, course_id)
            
            # Set current index to the placeholder
            self.course_id_combo.setCurrentIndex(0)
            
            print(f"🦆 Populated course dropdown with {len(sorted_courses)} courses")
            
        except Exception as e:
            print(f"Error populating course dropdowns: {str(e)}")
            self.course_id_combo.clear()
            self.course_id_combo.addItem("Error loading courses")
    
    def on_course_selected(self):
        """Handle course selection and auto-populate assignments"""
        try:
            # Check if Canvas is connected
            if not hasattr(self, 'canvas_api') or not self.canvas_api:
                return
            
            # Get the selected course ID
            current_index = self.course_id_combo.currentIndex()
            course_id = self.course_id_combo.itemData(current_index)
            
            # Skip if no valid course selected (placeholder or None)
            if course_id is None or current_index == 0:
                self.assignment_combo.clear()
                self.assignment_combo.addItem("Select a course first")
                return
            
            # Populate assignments for the selected course
            self.populate_assignments_for_course(course_id)
            
        except Exception as e:
            print(f"Error in course selection: {str(e)}")
    
    def populate_assignments_for_course(self, course_id):
        """Populate assignments dropdown for a specific course"""
        try:
            # Clear assignments dropdown
            self.assignment_combo.clear()
            self.assignment_combo.addItem("Loading assignments...")
            
            # Get assignments from Canvas API
            assignments = self.canvas_api.get_assignments(course_id)
            
            # Clear and populate
            self.assignment_combo.clear()
            
            if not assignments:
                self.assignment_combo.addItem("No assignments found")
                return
            
            # Add placeholder
            self.assignment_combo.addItem("Please select an assignment", None)
            
            # Sort assignments by name
            sorted_assignments = sorted(assignments, key=lambda a: a.get('name', ''))
            
            # Add assignments to dropdown
            for assignment in sorted_assignments:
                assignment_id = assignment.get('id')
                assignment_name = assignment.get('name', 'Unnamed Assignment')
                
                # Create display text
                display_text = f"{assignment_name}"
                
                # Add item with display text, store assignment_id as data
                self.assignment_combo.addItem(display_text, assignment_id)
            
            # Set to placeholder
            self.assignment_combo.setCurrentIndex(0)
            
            print(f"🦆 Populated assignments dropdown with {len(sorted_assignments)} assignments")
            
        except Exception as e:
            print(f"Error populating assignments: {str(e)}")
            self.assignment_combo.clear()
            self.assignment_combo.addItem("Error loading assignments")
    
    def refresh_courses(self):
        """Refresh available courses - placeholder for full Canvas integration"""
        QMessageBox.information(self, "Refresh Courses", 
                              "Course refresh functionality would be implemented here.\n\n"
                              "This would connect to Canvas API and populate the course dropdown "
                              "on the Two-Step Grading tab.")
    
    def enable_test_mode(self):
        """Enable test mode for grading buttons without Canvas connection"""
        reply = QMessageBox.question(self, "Enable Test Mode", 
                                   "Enable test mode to allow grading functionality without Canvas connection?\n\n"
                                   "⚠️ This is for testing purposes only. Actual grading will not work without "
                                   "proper Canvas connection.\n\n"
                                   "Enable test mode?", 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            # Enable grading buttons
            self.step1_button.setEnabled(True)
            self.single_grade_button.setEnabled(True)
            
            # Update connection status
            self.connection_status.setText("🧪 Test mode enabled")
            self.connection_status.setStyleSheet("color: orange; font-weight: bold;")
            
            QMessageBox.information(self, "Test Mode Enabled", 
                                  "🧪 Test mode enabled!\n\n"
                                  "Grading buttons are now active for testing the interface.\n"
                                  "Remember: Actual Canvas functionality requires proper connection.")
    
    def refresh_assignments(self):
        """Refresh available assignments from Canvas"""
        try:
            # Check if Canvas is connected
            if not hasattr(self, 'canvas_api') or not self.canvas_api:
                QMessageBox.warning(self, "Warning", 
                                  "Please connect to Canvas first using the 'Connect' button.")
                return
            
            # Get course ID from the current tab's course field
            current_tab = self.tab_widget.currentIndex()
            
            if current_tab == 1:  # Two-Step Grading tab
                # Try to get course ID from current data (if dropdown selection)
                current_index = self.course_id_combo.currentIndex()
                if current_index >= 0 and self.course_id_combo.itemData(current_index):
                    course_id = str(self.course_id_combo.itemData(current_index))
                else:
                    # Fall back to manual entry text
                    course_id = self.course_id_combo.currentText().strip()
                    # Extract course ID from display text format "Course Name (ID: 12345)"
                    if "(ID: " in course_id and ")" in course_id:
                        try:
                            course_id = course_id.split("(ID: ")[1].split(")")[0]
                        except:
                            pass  # Keep original text if parsing fails
            elif current_tab == 2:  # Single-Step Grading tab
                course_id = self.single_course_id_entry.text().strip()
            else:
                # If called from connection tab or elsewhere, try two-step first
                current_index = self.course_id_combo.currentIndex()
                if current_index >= 0 and self.course_id_combo.itemData(current_index):
                    course_id = str(self.course_id_combo.itemData(current_index))
                else:
                    course_id = self.course_id_combo.currentText().strip()
                    # Extract course ID from display text format "Course Name (ID: 12345)"
                    if "(ID: " in course_id and ")" in course_id:
                        try:
                            course_id = course_id.split("(ID: ")[1].split(")")[0]
                        except:
                            pass  # Keep original text if parsing fails
                if not course_id:
                    course_id = getattr(self, 'single_course_id_entry', None)
                    if course_id:
                        course_id = course_id.text().strip()
            
            if not course_id or course_id in ["No courses loaded", "No courses found", "Error loading courses", "Please select a course", "Select a course first"]:
                QMessageBox.warning(self, "Warning", 
                                  "Please select a Course from the dropdown or enter a Course ID first.")
                return
            
            # Validate course ID is numeric
            if not course_id.isdigit():
                QMessageBox.warning(self, "Warning", 
                                  "Course ID must be a number. You can find this in your Canvas course URL.")
                return
            
            course_id = int(course_id)
            
            try:
                # Fetch real assignments from Canvas
                assignments = self.canvas_api.get_assignments(course_id)
                
                if not assignments:
                    QMessageBox.information(self, "No Assignments", 
                                          f"No assignments found for Course {course_id}.")
                    return
                
                # Clear and populate assignment dropdowns
                self.assignment_combo.clear()
                if hasattr(self, 'single_assignment_combo'):
                    self.single_assignment_combo.clear()
                
                # Add placeholder
                self.assignment_combo.addItem("Please select an assignment", None)
                if hasattr(self, 'single_assignment_combo'):
                    self.single_assignment_combo.addItem("Please select an assignment", None)
                
                assignment_details_list = []
                
                # Sort assignments by name
                sorted_assignments = sorted(assignments, key=lambda a: a.get('name', ''))
                
                for assignment in sorted_assignments:
                    assignment_name = assignment.get('name', 'Unnamed Assignment')
                    assignment_id = assignment.get('id', '')
                    due_at = assignment.get('due_at', 'No due date')
                    points_possible = assignment.get('points_possible', 'No points set')
                    
                    # Add to dropdowns with assignment_id as data
                    self.assignment_combo.addItem(assignment_name, assignment_id)
                    if hasattr(self, 'single_assignment_combo'):
                        self.single_assignment_combo.addItem(assignment_name, assignment_id)
                    
                    # Collect assignment details
                    assignment_details_list.append({
                        'name': assignment_name,
                        'id': assignment_id,
                        'due_at': due_at,
                        'points': points_possible,
                        'description': assignment.get('description', 'No description available')[:200] + '...' if assignment.get('description') else 'No description available'
                    })
                
                # Set to placeholder
                self.assignment_combo.setCurrentIndex(0)
                if hasattr(self, 'single_assignment_combo'):
                    self.single_assignment_combo.setCurrentIndex(0)
                
                # Update assignment info displays with the first assignment
                if assignment_details_list:
                    first_assignment = assignment_details_list[0]
                    assignment_details = (
                        f"Found {len(assignments)} assignments for Course {course_id}\n\n"
                        f"First assignment details:\n"
                        f"• Name: {first_assignment['name']}\n"
                        f"• ID: {first_assignment['id']}\n"
                        f"• Due: {first_assignment['due_at']}\n"
                        f"• Points: {first_assignment['points']}\n"
                        f"• Description: {first_assignment['description']}"
                    )
                else:
                    assignment_details = f"No assignment details available for Course {course_id}"
                
                # Assignment details functionality removed since it's not implemented
                # self.assignment_info.setText(assignment_details)
                # if hasattr(self, 'single_assignment_info'):
                #     self.single_assignment_info.setText(assignment_details)
                
                QMessageBox.information(self, "Assignments Loaded", 
                                      f"✅ Successfully loaded {len(assignments)} assignments for Course {course_id}!")
                
            except Exception as api_error:
                error_msg = str(api_error)
                
                if "404" in error_msg:
                    QMessageBox.critical(self, "Course Not Found", 
                                       f"❌ Course {course_id} not found.\n\n"
                                       f"Please check:\n"
                                       f"• Course ID is correct\n"
                                       f"• You have access to this course\n"
                                       f"• Course is published and active")
                elif "403" in error_msg or "unauthorized" in error_msg.lower():
                    QMessageBox.critical(self, "Access Denied", 
                                       f"❌ Access denied to Course {course_id}.\n\n"
                                       f"Please check:\n"
                                       f"• You are enrolled in this course\n"
                                       f"• Your API token has sufficient permissions")
                else:
                    QMessageBox.critical(self, "Error Loading Assignments", 
                                       f"❌ Failed to load assignments for Course {course_id}.\n\n"
                                       f"Error: {error_msg}")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Unexpected error refreshing assignments: {str(e)}")
    
    def browse_rubric(self):
        """Browse for rubric file"""
        import os
        default_dir = "rubrics" if os.path.exists("rubrics") else ""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Rubric File", default_dir, "JSON Files (*.json);;All Files (*)")
        if file_path:
            self.rubric_path_entry.setText(file_path)
    
    def browse_instructor_config(self):
        """Browse for instructor config file"""
        import os
        default_dir = "config" if os.path.exists("config") else ""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Instructor Config", default_dir, "JSON Files (*.json);;All Files (*)")
        if file_path:
            self.instructor_config_entry.setText(file_path)
    
    def on_rubric_source_changed(self):
        """Handle rubric source selection change for two-step grading"""
        if self.local_rubric_radio.isChecked():
            # Show local rubric widget, hide canvas rubric widget
            self.canvas_rubric_widget.hide()
            self.local_rubric_widget.show()
        else:
            # Hide local rubric widget, show canvas rubric widget
            self.local_rubric_widget.hide()
            self.canvas_rubric_widget.show()
    
    def on_single_rubric_source_changed(self):
        """Handle rubric source selection change for single-step grading"""
        if self.single_local_rubric_radio.isChecked():
            # Show local rubric widget, hide canvas rubric widget
            self.single_canvas_rubric_widget.hide()
            self.single_local_rubric_widget.show()
        else:
            # Hide local rubric widget, show canvas rubric widget
            self.single_local_rubric_widget.hide()
            self.single_canvas_rubric_widget.show()
    
    def browse_single_rubric(self):
        """Browse for rubric file in single-step grading"""
        import os
        default_dir = "rubrics" if os.path.exists("rubrics") else ""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Select Rubric File", default_dir, "JSON Files (*.json);;All Files (*)")
        if file_path:
            self.single_rubric_entry.setText(file_path)
    
    def start_step1(self):
        """Start two-step grading step 1"""
        if not self.validate_step1_inputs():
            return
        
        # Disable button during processing
        self.step1_button.setEnabled(False)
        self.step1_button.setText("🔄 Running Step 1...")
        
        # Get all the parameters needed for the worker
        course_index = self.course_id_combo.currentIndex()
        course_id = self.course_id_combo.itemData(course_index)
        course_name = self.course_id_combo.currentText()
        
        assignment_index = self.assignment_combo.currentIndex()
        assignment_id = self.assignment_combo.itemData(assignment_index)
        assignment_name = self.assignment_combo.currentText()
        
        # Determine rubric settings
        use_canvas_rubric = self.canvas_rubric_radio.isChecked()
        rubric_path = None if use_canvas_rubric else self.rubric_path_entry.text().strip()
        
        # Get instructor configuration (optional)
        instructor_config_path = self.instructor_config_entry.text().strip()
        if not instructor_config_path or not Path(instructor_config_path).exists():
            instructor_config_path = None
        
        # Get API key and model
        # Use cached key if available (real key), otherwise fall back to text field
        if hasattr(self, '_cached_openai_key') and self._cached_openai_key:
            openai_key = self._cached_openai_key
            self.log_two_step("🔑 Using cached OpenAI API key")
        else:
            openai_key = self.openai_key_entry.text().strip()
            self.log_two_step("🔑 Using API key from text field")
            
        # Get the actual model ID (not display text) from combo box data
        current_index = self.model_combo.currentIndex()
        if current_index >= 0:
            selected_model = self.model_combo.itemData(current_index) or "gpt-4o-mini"
        else:
            selected_model = "gpt-4o-mini"
        
        # Debug: Check API key format (don't log the actual key)
        if openai_key and len(openai_key) > 20:
            self.log_two_step(f"🔍 API key format: {openai_key[:10]}...{openai_key[-10:]}")
        else:
            self.log_two_step(f"🔍 API key length: {len(openai_key) if openai_key else 0}")
        
        if not openai_key:
            QMessageBox.warning(self, "Missing API Key", "Please enter your OpenAI API key.")
            self.reset_step1_ui()
            return
        
        # Create worker and thread
        self.step1_worker = Step1Worker(
            self.canvas_api, course_id, course_name, assignment_id, assignment_name,
            use_canvas_rubric, rubric_path, instructor_config_path, openai_key, selected_model
        )
        
        self.step1_thread = threading.Thread(target=self.step1_worker.run, daemon=True)
        
        # Connect worker signals to GUI update methods
        self.step1_worker.progress_updated.connect(self.update_step1_progress)
        self.step1_worker.log_message.connect(self.log_two_step)
        self.step1_worker.completed.connect(self.handle_step1_completion)
        self.step1_worker.error_occurred.connect(self.handle_step1_error)
        
        # Start the thread
        self.step1_thread.start()
    
    def handle_step1_error(self, error_msg):
        """Handle Step 1 error"""
        self.log_two_step(f"ERROR in Step 1: {error_msg}")
        QMessageBox.critical(self, "Step 1 Error", f"Step 1 failed:\n{error_msg}")
        self.reset_step1_ui()
    
    def validate_step1_inputs(self):
        """Validate inputs before starting Step 1"""
        # Check Canvas connection
        if not hasattr(self, 'canvas_api') or not self.canvas_api:
            QMessageBox.warning(self, "Validation Error", "Please connect to Canvas first.")
            return False
        
        # Check course selection
        current_index = self.course_id_combo.currentIndex()
        if current_index <= 0 or not self.course_id_combo.itemData(current_index):
            QMessageBox.warning(self, "Validation Error", "Please select a course.")
            return False
        
        # Check assignment selection
        assignment_index = self.assignment_combo.currentIndex()
        if assignment_index <= 0 or not self.assignment_combo.itemData(assignment_index):
            QMessageBox.warning(self, "Validation Error", "Please select an assignment.")
            return False
        
        # Validate rubric source selection
        if self.local_rubric_radio.isChecked():
            rubric_path = self.rubric_path_entry.text().strip()
            if not rubric_path:
                QMessageBox.warning(self, "Validation Error", "Please specify a rubric file path.")
                return False
            if not Path(rubric_path).exists():
                QMessageBox.warning(self, "Validation Error", f"Rubric file not found: {rubric_path}")
                return False
        
        return True
    
    def update_step1_progress(self, percent, description):
        """Update Step 1 progress bar and description"""
        self.progress_step1.setValue(percent)
        self.progress_desc_step1.setText(description)
    
    def handle_step1_completion(self, results):
        """Handle Step 1 completion"""
        if results['success']:
            self.update_step1_progress(100, "Step 1 complete!")
            self.step2_button.setEnabled(True)
            self.review_folder_btn.setEnabled(True)
            
            self.log_two_step("✓ Step 1 completed successfully!")
            self.log_two_step(f"Graded {len(results.get('grading_results', {}))} submissions")
            self.log_two_step(f"Review folder: {results['folder_path']}")
            
            # Check if review spreadsheet was created
            review_file = results.get('review_file', '')
            if review_file and os.path.exists(review_file):
                self.log_two_step(f"✓ Review spreadsheet created: {os.path.basename(review_file)}")
                spreadsheet_status = "✅ Review spreadsheet is ready"
            else:
                self.log_two_step("⚠️ Review spreadsheet was not created or not found")
                spreadsheet_status = "⚠️ Review spreadsheet missing - check logs"
            
            self.log_two_step("Next: Review the spreadsheet and run Step 2")
            
            # Store results for Step 2
            self.current_step1_results = results
            
            # Show completion notification with "Open Review Folder" option
            self.show_completion_dialog(results)
        else:
            error_msg = results.get('error', 'Unknown error')
            self.log_two_step(f"Step 1 completed with errors: {error_msg}")
            QMessageBox.warning(self, "Step 1 Warning", 
                              f"Step 1 completed but encountered issues:\n{error_msg}")
        
        self.reset_step1_ui()
    
    def show_completion_dialog(self, results):
        """Show completion dialog with option to open review folder"""
        from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton
        import os
        import subprocess
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Step 1 Complete")
        dialog.setModal(True)
        dialog.resize(400, 200)
        
        layout = QVBoxLayout()
        
        # Success message
        message = QLabel(f"✅ Step 1 completed successfully!\n\n"
                        f"• Graded {len(results.get('grading_results', {}))} submissions\n"
                        f"• Results saved to: {results['folder_path']}\n"
                        f"• Review spreadsheet created: {results.get('review_file', 'N/A')}\n\n"
                        f"Next: Review the results and run Step 2 to upload grades.")
        message.setWordWrap(True)
        layout.addWidget(message)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        open_folder_btn = QPushButton("Open Review Folder Now")
        open_folder_btn.clicked.connect(lambda: self.open_review_folder(results['folder_path']))
        button_layout.addWidget(open_folder_btn)
        
        ok_btn = QPushButton("OK")
        ok_btn.clicked.connect(dialog.accept)
        ok_btn.setDefault(True)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        dialog.setLayout(layout)
        dialog.exec()
    
    def open_review_folder(self, folder_path, checked=False):
        """Open the review folder in Windows Explorer"""
        import os
        import subprocess
        
        try:
            if os.path.exists(folder_path):
                # Use Windows Explorer to open the folder
                subprocess.run(['explorer', folder_path])
                self.log_two_step(f"📁 Opened review folder: {folder_path}")
            else:
                QMessageBox.warning(self, "Folder Not Found", f"Could not find folder: {folder_path}")
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Failed to open folder: {str(e)}")
    
    def reset_step1_ui(self):
        """Reset Step 1 UI elements"""
        self.step1_button.setEnabled(True)
        self.step1_button.setText("🚀 Start Step 1: Download and Grade")
        self.progress_step1.setValue(0)
        self.progress_desc_step1.setText("Ready to start...")
    
    def log_two_step(self, message):
        """Add message to two-step grading log"""
        current_text = self.two_step_log.toPlainText()
        if current_text:
            new_text = current_text + "\n" + message
        else:
            new_text = message
        self.two_step_log.setPlainText(new_text)
        # Scroll to bottom
        scrollbar = self.two_step_log.verticalScrollBar()
        scrollbar.setValue(scrollbar.maximum())
    
    def start_step2(self):
        """Start two-step grading step 2"""
        QMessageBox.information(self, "Step 2", 
                              "Step 2 grading would begin here.\n\n"
                              "This would:\n"
                              "• Open review interface\n"
                              "• Allow grade adjustments\n"
                              "• Upload final grades to Canvas\n"
                              "• Generate completion report")
    
    def start_single_grading(self):
        """Start single-step grading"""
        # Validate rubric source selection
        if self.single_local_rubric_radio.isChecked():
            rubric_path = self.single_rubric_entry.text().strip()
            if not rubric_path:
                QMessageBox.warning(self, "Validation Error", "Please specify a rubric file path.")
                return
            if not Path(rubric_path).exists():
                QMessageBox.warning(self, "Validation Error", f"Rubric file not found: {rubric_path}")
                return
            rubric_info = f"Using local rubric: {rubric_path}"
        else:
            rubric_info = "Using Canvas rubric (will be downloaded automatically)"
        
        QMessageBox.information(self, "Single Grading", 
                              f"⚠️ Single-step grading would begin here.\n\n"
                              f"Configuration:\n"
                              f"• {rubric_info}\n"
                              f"• Download submissions\n"
                              f"• Run AI grading\n"
                              f"• Upload grades immediately\n"
                              f"• NO REVIEW STEP!")
    
    # Placeholder methods for button click handlers
    def browse_rubric(self):
        """Browse for rubric file"""
        import os
        default_dir = "rubrics" if os.path.exists("rubrics") else ""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, 
            "Select Rubric File", 
            default_dir, 
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.rubric_path_entry.setText(file_path)
    
    def browse_instructor_config(self):
        """Browse for instructor config file"""
        import os
        default_dir = "config" if os.path.exists("config") else ""
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self, 
            "Select Instructor Config File", 
            default_dir, 
            "JSON Files (*.json);;All Files (*)"
        )
        if file_path:
            self.instructor_config_entry.setText(file_path)


def main():
    """Main function to run the Canvas GUI"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("DuckGrade Canvas Integration")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("DuckWorks Educational Automation")
    
    # Create and show the main window
    window = DuckGradeCanvasGUI()
    window.showMaximized()  # Start in fullscreen/maximized mode
    
    print("🦆 DuckGrade Canvas Integration (PyQt6) started successfully!")
    print("Professional interface now matches Tkinter structure exactly")
    
    return app.exec()


if __name__ == "__main__":
    sys.exit(main())
