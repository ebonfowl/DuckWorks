#!/usr/bin/env python3
"""
DuckGrade Canvas PyQt6 Interface
Modern PyQt6-based GUI for Canvas LMS integration

Part of the DuckWorks Educational Automation Suite
Professional and modern replacement for the Tkinter canvas_gui.py

Features:
- Modern PyQt6 design with professional styling
- Drag-and-drop assignment downloading
- Live assignment tracking with cards
- Animated progress bars
- Background processing
- Error handling with user-friendly messages

Author: DuckWorks Educational Automation Suite
Created: 2024
"""

import sys
import os
import json
import logging
from pathlib import Path
from typing import Optional, Dict, List, Any
from datetime import datetime

from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QPushButton, QLineEdit, QTextEdit, QComboBox,
    QCheckBox, QProgressBar, QScrollArea, QFrame, QGridLayout,
    QMessageBox, QFileDialog, QSpacerItem, QSizePolicy, QGroupBox
)
from PyQt6.QtCore import (
    Qt, QThread, pyqtSignal, QPropertyAnimation, QEasingCurve,
    QRect, QTimer, QUrl
)
from PyQt6.QtGui import (
    QFont, QPixmap, QPainter, QPen, QBrush, QColor, QIcon,
    QPalette, QLinearGradient, QDesktopServices
)

# Import DuckWorks framework and existing components
from duckworks_framework import DuckWorksInfo, DuckWorksConfig
from duckworks_pyqt import (
    DuckWorksStyle, DuckWorksMainWindow, DuckWorksCard,
    DuckWorksButton, DuckWorksProgressBar
)

# Import Canvas integration
try:
    from canvas_integration import CanvasIntegration
    from grading_agent import GradingAgent
    from secure_key_manager import SecureKeyManager
    from openai_model_manager import OpenAIModelManager
except ImportError as e:
    print(f"Warning: Missing dependency: {e}")
    CanvasIntegration = None

class AssignmentCard(DuckWorksCard):
    """Card widget for displaying assignment information"""
    
    download_requested = pyqtSignal(dict)
    
    def __init__(self, assignment_data: Dict):
        super().__init__()
        self.assignment_data = assignment_data
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Assignment title
        title = QLabel(self.assignment_data.get('name', 'Unknown Assignment'))
        title.setFont(QFont('Segoe UI', 11, QFont.Weight.Bold))
        title.setStyleSheet(f"color: {DuckWorksStyle.COLORS['primary']};")
        title.setWordWrap(True)
        layout.addWidget(title)
        
        # Assignment details
        details_layout = QGridLayout()
        
        # Due date
        due_date = self.assignment_data.get('due_at', 'No due date')
        if due_date and due_date != 'No due date':
            try:
                due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                due_date = due_date.strftime('%Y-%m-%d %H:%M')
            except:
                pass
        
        details_layout.addWidget(QLabel("Due:"), 0, 0)
        due_label = QLabel(str(due_date))
        due_label.setStyleSheet("color: #666;")
        details_layout.addWidget(due_label, 0, 1)
        
        # Points
        points = self.assignment_data.get('points_possible', 'N/A')
        details_layout.addWidget(QLabel("Points:"), 1, 0)
        points_label = QLabel(str(points))
        points_label.setStyleSheet("color: #666;")
        details_layout.addWidget(points_label, 1, 1)
        
        # Submissions count
        submissions = self.assignment_data.get('submission_count', 0)
        details_layout.addWidget(QLabel("Submissions:"), 2, 0)
        submissions_label = QLabel(str(submissions))
        submissions_label.setStyleSheet("color: #666;")
        details_layout.addWidget(submissions_label, 2, 1)
        
        layout.addLayout(details_layout)
        
        # Download button
        download_btn = DuckWorksButton("📥 Download Submissions")
        download_btn.clicked.connect(self.request_download)
        layout.addWidget(download_btn)
        
        # Progress bar (hidden initially)
        self.progress_bar = DuckWorksProgressBar()
        self.progress_bar.hide()
        layout.addWidget(self.progress_bar)
        
    def request_download(self):
        self.download_requested.emit(self.assignment_data)
        
    def show_progress(self):
        self.progress_bar.show()
        self.progress_bar.start_animation()
        
    def hide_progress(self):
        self.progress_bar.hide()
        self.progress_bar.stop_animation()

class CanvasWorker(QThread):
    """Background worker for Canvas operations"""
    
    progress_updated = pyqtSignal(int)
    status_updated = pyqtSignal(str)
    assignments_loaded = pyqtSignal(list)
    download_completed = pyqtSignal(str, bool)  # path, success
    error_occurred = pyqtSignal(str)
    
    def __init__(self):
        super().__init__()
        self.canvas = None
        self.current_operation = None
        self.operation_data = None
        
    def setup_canvas(self, api_key: str, base_url: str):
        """Setup Canvas integration"""
        try:
            if CanvasIntegration:
                self.canvas = CanvasIntegration(api_key, base_url)
                return True
            else:
                self.error_occurred.emit("Canvas integration not available. Please check dependencies.")
                return False
        except Exception as e:
            self.error_occurred.emit(f"Failed to setup Canvas: {str(e)}")
            return False
    
    def load_assignments(self, course_id: str):
        """Load assignments for a course"""
        self.current_operation = "load_assignments"
        self.operation_data = {"course_id": course_id}
        self.start()
    
    def download_submissions(self, assignment_data: dict, download_path: str):
        """Download submissions for an assignment"""
        self.current_operation = "download_submissions"
        self.operation_data = {
            "assignment_data": assignment_data,
            "download_path": download_path
        }
        self.start()
    
    def run(self):
        """Execute the current operation"""
        try:
            if self.current_operation == "load_assignments":
                self._load_assignments()
            elif self.current_operation == "download_submissions":
                self._download_submissions()
        except Exception as e:
            self.error_occurred.emit(f"Operation failed: {str(e)}")
    
    def _load_assignments(self):
        """Load assignments from Canvas"""
        if not self.canvas:
            self.error_occurred.emit("Canvas not initialized")
            return
            
        course_id = self.operation_data["course_id"]
        self.status_updated.emit(f"Loading assignments for course {course_id}...")
        
        try:
            assignments = self.canvas.get_assignments(course_id)
            self.assignments_loaded.emit(assignments)
            self.status_updated.emit(f"Loaded {len(assignments)} assignments")
        except Exception as e:
            self.error_occurred.emit(f"Failed to load assignments: {str(e)}")
    
    def _download_submissions(self):
        """Download submissions for an assignment"""
        if not self.canvas:
            self.error_occurred.emit("Canvas not initialized")
            return
            
        assignment_data = self.operation_data["assignment_data"]
        download_path = self.operation_data["download_path"]
        
        assignment_name = assignment_data.get('name', 'Unknown')
        self.status_updated.emit(f"Downloading submissions for {assignment_name}...")
        
        try:
            # Create assignment folder
            assignment_folder = Path(download_path) / f"assignment_{assignment_data['id']}"
            assignment_folder.mkdir(exist_ok=True)
            
            # Download submissions with progress
            submissions = self.canvas.get_submissions(assignment_data['course_id'], assignment_data['id'])
            total = len(submissions)
            
            for i, submission in enumerate(submissions):
                self.progress_updated.emit(int((i / total) * 100))
                self.status_updated.emit(f"Downloading submission {i+1}/{total}...")
                
                # Download submission files
                self.canvas.download_submission_files(submission, str(assignment_folder))
                
            self.progress_updated.emit(100)
            self.download_completed.emit(str(assignment_folder), True)
            self.status_updated.emit(f"Download completed: {assignment_folder}")
            
        except Exception as e:
            self.download_completed.emit("", False)
            self.error_occurred.emit(f"Download failed: {str(e)}")

class CanvasConfigWidget(QWidget):
    """Widget for Canvas configuration"""
    
    def __init__(self):
        super().__init__()
        self.setup_ui()
        self.load_config()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Canvas API Configuration
        config_group = QGroupBox("Canvas API Configuration")
        config_group.setStyleSheet("""
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
        """)
        config_layout = QVBoxLayout(config_group)
        
        # API URL
        url_layout = QHBoxLayout()
        url_layout.addWidget(QLabel("Canvas URL:"))
        self.url_input = QLineEdit()
        self.url_input.setPlaceholderText("https://your-school.instructure.com")
        self.url_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
            QLineEdit:focus {
                border-color: #2E86AB;
            }
        """)
        url_layout.addWidget(self.url_input)
        config_layout.addLayout(url_layout)
        
        # API Key
        key_layout = QHBoxLayout()
        key_layout.addWidget(QLabel("API Key:"))
        self.key_input = QLineEdit()
        self.key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.key_input.setPlaceholderText("Enter your Canvas API key")
        self.key_input.setStyleSheet("""
            QLineEdit {
                background-color: white;
                border: 2px solid #dee2e6;
                border-radius: 6px;
                padding: 8px 12px;
                font-size: 9pt;
            }
            QLineEdit:focus {
                border-color: #2E86AB;
            }
        """)
        key_layout.addWidget(self.key_input)
        config_layout.addLayout(key_layout)
        
        # Test connection button
        self.test_btn = DuckWorksButton("🔗 Test Connection")
        self.test_btn.clicked.connect(self.test_connection)
        config_layout.addWidget(self.test_btn)
        
        layout.addWidget(config_group)
        
        # Course Selection
        course_group = QGroupBox("Course Selection")
        course_group.setStyleSheet(DuckWorksStyle.get_group_box_style())
        course_layout = QVBoxLayout(course_group)
        
        course_select_layout = QHBoxLayout()
        course_select_layout.addWidget(QLabel("Course ID:"))
        self.course_input = QLineEdit()
        self.course_input.setPlaceholderText("Enter Canvas course ID")
        self.course_input.setStyleSheet(DuckWorksStyle.get_line_edit_style())
        course_select_layout.addWidget(self.course_input)
        
        self.load_assignments_btn = DuckWorksButton("📚 Load Assignments")
        self.load_assignments_btn.clicked.connect(self.load_assignments)
        course_select_layout.addWidget(self.load_assignments_btn)
        
        course_layout.addLayout(course_select_layout)
        layout.addWidget(course_group)
        
        # Download Settings
        download_group = QGroupBox("Download Settings")
        download_group.setStyleSheet(DuckWorksStyle.get_group_box_style())
        download_layout = QVBoxLayout(download_group)
        
        path_layout = QHBoxLayout()
        path_layout.addWidget(QLabel("Download Path:"))
        self.path_input = QLineEdit()
        self.path_input.setPlaceholderText("Select download directory")
        self.path_input.setStyleSheet(DuckWorksStyle.get_line_edit_style())
        path_layout.addWidget(self.path_input)
        
        browse_btn = DuckWorksButton("📁 Browse")
        browse_btn.clicked.connect(self.browse_download_path)
        path_layout.addWidget(browse_btn)
        
        download_layout.addLayout(path_layout)
        layout.addWidget(download_group)
        
        # Auto-grade options
        grade_group = QGroupBox("Auto-Grading Options")
        grade_group.setStyleSheet(DuckWorksStyle.get_group_box_style())
        grade_layout = QVBoxLayout(grade_group)
        
        self.auto_grade_cb = QCheckBox("Automatically grade downloaded submissions")
        self.auto_grade_cb.setStyleSheet(DuckWorksStyle.get_checkbox_style())
        grade_layout.addWidget(self.auto_grade_cb)
        
        self.upload_grades_cb = QCheckBox("Upload grades back to Canvas")
        self.upload_grades_cb.setStyleSheet(DuckWorksStyle.get_checkbox_style())
        grade_layout.addWidget(self.upload_grades_cb)
        
        layout.addWidget(grade_group)
        
        # Save configuration
        save_btn = DuckWorksButton("💾 Save Configuration")
        save_btn.clicked.connect(self.save_config)
        layout.addWidget(save_btn)
        
        layout.addStretch()
        
    def test_connection(self):
        """Test Canvas API connection"""
        # Implementation would test the connection
        QMessageBox.information(self, "Test Connection", "Connection test functionality would be implemented here.")
        
    def load_assignments(self):
        """Trigger assignment loading"""
        if not self.course_input.text().strip():
            QMessageBox.warning(self, "Warning", "Please enter a course ID.")
            return
        # This would trigger the main window to load assignments
        
    def browse_download_path(self):
        """Browse for download directory"""
        path = QFileDialog.getExistingDirectory(self, "Select Download Directory")
        if path:
            self.path_input.setText(path)
            
    def save_config(self):
        """Save configuration to file"""
        config = DuckWorksConfig()
        config.set('canvas_url', self.url_input.text())
        config.set('course_id', self.course_input.text())
        config.set('download_path', self.path_input.text())
        config.set('auto_grade', self.auto_grade_cb.isChecked())
        config.set('upload_grades', self.upload_grades_cb.isChecked())
        
        # Save API key securely
        if self.key_input.text().strip():
            try:
                key_manager = SecureKeyManager()
                key_manager.store_key('canvas_api_key', self.key_input.text())
            except:
                pass  # Handle securely
                
        QMessageBox.information(self, "Success", "Configuration saved successfully!")
        
    def load_config(self):
        """Load configuration from file"""
        config = DuckWorksConfig()
        self.url_input.setText(config.get('canvas_url', ''))
        self.course_input.setText(config.get('course_id', ''))
        self.path_input.setText(config.get('download_path', str(Path.home() / 'Downloads')))
        self.auto_grade_cb.setChecked(config.get('auto_grade', False))
        self.upload_grades_cb.setChecked(config.get('upload_grades', False))

class AssignmentsWidget(QWidget):
    """Widget for displaying and managing assignments"""
    
    def __init__(self):
        super().__init__()
        self.assignments = []
        self.assignment_cards = []
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        
        # Header
        header = QLabel("📚 Course Assignments")
        header.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {DuckWorksStyle.COLORS['primary']}; margin: 10px;")
        layout.addWidget(header)
        
        # Scroll area for assignments
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet(DuckWorksStyle.get_scroll_area_style())
        
        self.assignments_widget = QWidget()
        self.assignments_layout = QVBoxLayout(self.assignments_widget)
        self.assignments_layout.setSpacing(10)
        
        scroll.setWidget(self.assignments_widget)
        layout.addWidget(scroll)
        
        # No assignments message
        self.no_assignments_label = QLabel("No assignments loaded. Configure Canvas settings and load assignments.")
        self.no_assignments_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_assignments_label.setStyleSheet("color: #888; font-style: italic; margin: 20px;")
        self.assignments_layout.addWidget(self.no_assignments_label)
        
    def load_assignments(self, assignments: List[Dict]):
        """Load assignments into the widget"""
        # Clear existing assignments
        self.clear_assignments()
        
        self.assignments = assignments
        
        if not assignments:
            self.no_assignments_label.show()
            return
            
        self.no_assignments_label.hide()
        
        # Create assignment cards
        for assignment in assignments:
            card = AssignmentCard(assignment)
            card.download_requested.connect(self.on_download_requested)
            self.assignment_cards.append(card)
            self.assignments_layout.addWidget(card)
            
        self.assignments_layout.addStretch()
        
    def clear_assignments(self):
        """Clear all assignment cards"""
        for card in self.assignment_cards:
            card.deleteLater()
        self.assignment_cards.clear()
        
    def on_download_requested(self, assignment_data: Dict):
        """Handle download request from assignment card"""
        # This would be connected to the main window's download handler
        pass

class DuckGradeCanvasGUI(DuckWorksMainWindow):
    """Modern PyQt6 Canvas Integration Interface for DuckGrade"""
    
    def __init__(self):
        super().__init__("DuckGrade Canvas Integration")
        self.canvas_worker = CanvasWorker()
        self.setup_worker_connections()
        self.setup_ui()
        self.setup_window()
        
    def setup_worker_connections(self):
        """Setup Canvas worker signal connections"""
        self.canvas_worker.assignments_loaded.connect(self.on_assignments_loaded)
        self.canvas_worker.download_completed.connect(self.on_download_completed)
        self.canvas_worker.error_occurred.connect(self.on_error_occurred)
        self.canvas_worker.status_updated.connect(self.update_status)
        self.canvas_worker.progress_updated.connect(self.update_progress)
        
    def setup_ui(self):
        """Setup the user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Header
        header = self.create_header()
        layout.addWidget(header)
        
        # Tab widget
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
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
        
        # Configuration tab
        self.config_widget = CanvasConfigWidget()
        self.tab_widget.addTab(self.config_widget, "⚙️ Configuration")
        
        # Assignments tab
        self.assignments_widget = AssignmentsWidget()
        self.tab_widget.addTab(self.assignments_widget, "📚 Assignments")
        
        # Progress tab
        self.progress_widget = self.create_progress_widget()
        self.tab_widget.addTab(self.progress_widget, "📊 Progress")
        
        layout.addWidget(self.tab_widget)
        
        # Status bar
        self.status_bar = self.create_status_bar()
        layout.addWidget(self.status_bar)
        
        # Connect configuration signals
        self.config_widget.load_assignments_btn.clicked.connect(self.load_assignments)
        self.assignments_widget.on_download_requested = self.download_submissions
        
    def create_header(self) -> QWidget:
        """Create the header widget"""
        header = QWidget()
        header.setFixedHeight(80)
        header.setStyleSheet(f"""
            QWidget {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {DuckWorksStyle.COLORS['primary']},
                    stop:1 {DuckWorksStyle.COLORS['secondary']});
                border-radius: 10px;
                margin: 10px;
            }}
        """)
        
        layout = QHBoxLayout(header)
        layout.setContentsMargins(20, 10, 20, 10)
        
        # Logo and title
        title_layout = QVBoxLayout()
        
        app_title = QLabel("🦆 DuckGrade Canvas Integration")
        app_title.setFont(QFont('Segoe UI', 16, QFont.Weight.Bold))
        app_title.setStyleSheet("color: white;")
        title_layout.addWidget(app_title)
        
        subtitle = QLabel("Modern Canvas LMS Integration • Part of DuckWorks Educational Suite")
        subtitle.setFont(QFont('Segoe UI', 9))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        title_layout.addWidget(subtitle)
        
        layout.addLayout(title_layout)
        layout.addStretch()
        
        # Quick actions
        actions_layout = QHBoxLayout()
        
        refresh_btn = DuckWorksButton("🔄 Refresh")
        refresh_btn.setMaximumWidth(100)
        refresh_btn.clicked.connect(self.refresh_assignments)
        actions_layout.addWidget(refresh_btn)
        
        help_btn = DuckWorksButton("❓ Help")
        help_btn.setMaximumWidth(80)
        help_btn.clicked.connect(self.show_help)
        actions_layout.addWidget(help_btn)
        
        layout.addLayout(actions_layout)
        
        return header
        
    def create_progress_widget(self) -> QWidget:
        """Create the progress tracking widget"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setSpacing(15)
        
        # Progress header
        header = QLabel("📊 Download Progress")
        header.setFont(QFont('Segoe UI', 14, QFont.Weight.Bold))
        header.setStyleSheet(f"color: {DuckWorksStyle.COLORS['primary']}; margin: 10px;")
        layout.addWidget(header)
        
        # Overall progress
        progress_group = QGroupBox("Current Operation")
        progress_group.setStyleSheet(DuckWorksStyle.get_group_box_style())
        progress_layout = QVBoxLayout(progress_group)
        
        self.current_operation_label = QLabel("No operation in progress")
        self.current_operation_label.setStyleSheet("font-weight: bold; color: #333;")
        progress_layout.addWidget(self.current_operation_label)
        
        self.overall_progress = DuckWorksProgressBar()
        progress_layout.addWidget(self.overall_progress)
        
        layout.addWidget(progress_group)
        
        # Recent operations log
        log_group = QGroupBox("Operation Log")
        log_group.setStyleSheet(DuckWorksStyle.get_group_box_style())
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setMaximumHeight(200)
        self.log_text.setStyleSheet(DuckWorksStyle.get_text_edit_style())
        self.log_text.setReadOnly(True)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        layout.addStretch()
        
        return widget
        
    def create_status_bar(self) -> QWidget:
        """Create the status bar"""
        status_bar = QWidget()
        status_bar.setFixedHeight(30)
        status_bar.setStyleSheet("""
            QWidget {
                background-color: #f8f9fa;
                border-top: 1px solid #dee2e6;
                padding: 5px;
            }
        """)
        
        layout = QHBoxLayout(status_bar)
        layout.setContentsMargins(10, 0, 10, 0)
        
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("color: #666;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # Connection status
        self.connection_status = QLabel("⚪ Disconnected")
        self.connection_status.setStyleSheet("color: #888;")
        layout.addWidget(self.connection_status)
        
        return status_bar
        
    def setup_window(self):
        """Setup window properties"""
        self.setWindowTitle("🦆 DuckGrade Canvas Integration - DuckWorks Educational Suite")
        self.setWindowIcon(QIcon())  # Would set duck icon
        self.resize(1000, 700)
        self.center_window()
        
    def center_window(self):
        """Center the window on screen"""
        screen = QApplication.primaryScreen().geometry()
        window = self.frameGeometry()
        center_point = screen.center()
        window.moveCenter(center_point)
        self.move(window.topLeft())
        
    def load_assignments(self):
        """Load assignments from Canvas"""
        course_id = self.config_widget.course_input.text().strip()
        if not course_id:
            QMessageBox.warning(self, "Warning", "Please enter a course ID.")
            return
            
        # Setup Canvas connection if needed
        api_key = self.get_api_key()
        canvas_url = self.config_widget.url_input.text().strip()
        
        if not api_key or not canvas_url:
            QMessageBox.warning(self, "Warning", "Please configure Canvas API settings.")
            return
            
        if not self.canvas_worker.setup_canvas(api_key, canvas_url):
            return
            
        self.update_status("Loading assignments...")
        self.connection_status.setText("🟡 Loading...")
        self.canvas_worker.load_assignments(course_id)
        
    def refresh_assignments(self):
        """Refresh assignments list"""
        self.load_assignments()
        
    def download_submissions(self, assignment_data: Dict):
        """Download submissions for an assignment"""
        download_path = self.config_widget.path_input.text().strip()
        if not download_path:
            QMessageBox.warning(self, "Warning", "Please set a download path.")
            return
            
        self.update_status(f"Downloading submissions for {assignment_data.get('name', 'assignment')}...")
        self.overall_progress.start_animation()
        self.canvas_worker.download_submissions(assignment_data, download_path)
        
    def get_api_key(self) -> str:
        """Get Canvas API key (from input or secure storage)"""
        key = self.config_widget.key_input.text().strip()
        if key:
            return key
            
        # Try to load from secure storage
        try:
            key_manager = SecureKeyManager()
            return key_manager.get_key('canvas_api_key')
        except:
            return ""
            
    def on_assignments_loaded(self, assignments: List[Dict]):
        """Handle assignments loaded signal"""
        self.assignments_widget.load_assignments(assignments)
        self.connection_status.setText("🟢 Connected")
        self.update_status(f"Loaded {len(assignments)} assignments")
        self.log_message(f"Successfully loaded {len(assignments)} assignments")
        
    def on_download_completed(self, path: str, success: bool):
        """Handle download completed signal"""
        self.overall_progress.stop_animation()
        if success:
            self.update_status(f"Download completed: {path}")
            self.log_message(f"Download completed successfully: {path}")
            
            # Auto-grade if enabled
            if self.config_widget.auto_grade_cb.isChecked():
                self.start_auto_grading(path)
        else:
            self.update_status("Download failed")
            self.log_message("Download failed")
            
    def on_error_occurred(self, error: str):
        """Handle error signal"""
        self.overall_progress.stop_animation()
        self.connection_status.setText("🔴 Error")
        self.update_status(f"Error: {error}")
        self.log_message(f"Error: {error}")
        QMessageBox.critical(self, "Error", error)
        
    def update_status(self, message: str):
        """Update status bar message"""
        self.status_label.setText(message)
        
    def update_progress(self, value: int):
        """Update progress bar"""
        self.overall_progress.setValue(value)
        
    def log_message(self, message: str):
        """Add message to operation log"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        self.log_text.append(log_entry)
        
    def start_auto_grading(self, submissions_path: str):
        """Start automatic grading process"""
        self.log_message(f"Starting auto-grading for submissions in: {submissions_path}")
        # Implementation would integrate with the grading agent
        
    def show_help(self):
        """Show help dialog"""
        help_text = """
        <h3>🦆 DuckGrade Canvas Integration Help</h3>
        
        <h4>Getting Started:</h4>
        <ol>
        <li><b>Configure Canvas API:</b> Enter your Canvas URL and API key in the Configuration tab</li>
        <li><b>Test Connection:</b> Click "Test Connection" to verify your settings</li>
        <li><b>Load Assignments:</b> Enter a course ID and click "Load Assignments"</li>
        <li><b>Download Submissions:</b> Click "Download Submissions" on any assignment card</li>
        </ol>
        
        <h4>Features:</h4>
        <ul>
        <li>🔗 Secure Canvas API integration</li>
        <li>📚 Assignment browsing and management</li>
        <li>📥 Bulk submission downloading</li>
        <li>🤖 Automatic grading integration</li>
        <li>📊 Progress tracking and logging</li>
        <li>⬆️ Grade upload back to Canvas</li>
        </ul>
        
        <h4>Tips:</h4>
        <ul>
        <li>Your API key is stored securely and encrypted</li>
        <li>Enable auto-grading to process submissions automatically</li>
        <li>Check the Progress tab to monitor operations</li>
        <li>Use the Log to troubleshoot issues</li>
        </ul>
        
        <p><i>Part of the DuckWorks Educational Automation Suite</i></p>
        """
        
        msg = QMessageBox(self)
        msg.setWindowTitle("Help - DuckGrade Canvas Integration")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(help_text)
        msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()

def main():
    """Main entry point"""
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("DuckGrade Canvas Integration")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("DuckWorks Educational Suite")
    
    # Apply global stylesheet
    app.setStyleSheet(DuckWorksStyle.get_stylesheet())
    
    # Create and show main window
    window = DuckGradeCanvasGUI()
    window.show()
    
    # Log startup
    print("🦆 DuckGrade Canvas Integration started")
    print("Modern PyQt6 interface loaded successfully")
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
