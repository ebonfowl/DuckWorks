"""
DuckGrade - Modern Local File Grading Interface (PyQt6)
Part of the DuckWorks Educational Automation Suite

A modern, professional interface for local file grading with PyQt6.
Features drag-and-drop, tabbed interface, and smooth animations.

Author: DuckWorks Development Team
Version: 2.0.0 (PyQt6 Edition)
"""

import sys
import os
from pathlib import Path
from typing import List, Optional
import threading
import json

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *

from duckworks_pyqt import (
    DuckWorksMainWindow, DuckWorksCard, DuckWorksButton, 
    DuckWorksProgressBar, DuckWorksIcon, DuckWorksStyle
)
from grading_agent import GradingAgent
from secure_key_manager import APIKeyManager
from openai_model_manager import OpenAIModelManager

class FileDropWidget(QLabel):
    """Drag and drop area for files"""
    
    files_dropped = pyqtSignal(list)
    
    def __init__(self, text="Drag files here", parent=None):
        super().__init__(parent)
        self.setAcceptDrops(True)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(text)
        self.setMinimumHeight(120)
        self.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {DuckWorksStyle.COLORS['primary']};
                border-radius: 8px;
                background-color: {DuckWorksStyle.COLORS['surface']};
                color: {DuckWorksStyle.COLORS['text_secondary']};
                font-size: 11pt;
                padding: 20px;
            }}
            QLabel:hover {{
                background-color: {DuckWorksStyle.COLORS['primary']};
                color: white;
            }}
        """)
    
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
            self.setStyleSheet(f"""
                QLabel {{
                    border: 2px solid {DuckWorksStyle.COLORS['primary']};
                    border-radius: 8px;
                    background-color: {DuckWorksStyle.COLORS['primary']};
                    color: white;
                    font-size: 11pt;
                    padding: 20px;
                }}
            """)
    
    def dragLeaveEvent(self, event):
        self.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed {DuckWorksStyle.COLORS['primary']};
                border-radius: 8px;
                background-color: {DuckWorksStyle.COLORS['surface']};
                color: {DuckWorksStyle.COLORS['text_secondary']};
                font-size: 11pt;
                padding: 20px;
            }}
        """)
    
    def dropEvent(self, event):
        files = []
        for url in event.mimeData().urls():
            if url.isLocalFile():
                files.append(url.toLocalFile())
        
        if files:
            self.files_dropped.emit(files)
        
        self.dragLeaveEvent(event)

class PasswordDialog(QDialog):
    """Modern password dialog for secure key management"""
    
    def __init__(self, action="unlock", parent=None):
        super().__init__(parent)
        self.action = action
        self.password = None
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("🔐 Master Password")
        self.setModal(True)
        self.setFixedSize(450, 300)
        self.setWindowIcon(DuckWorksIcon.get_duck_icon())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("🔐 Secure Key Management")
        header.setProperty("class", "title")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Description
        if self.action == "create":
            desc_text = ("Create a master password to encrypt your API keys.\n"
                        "This password will be required to access your saved credentials.")
        else:
            desc_text = ("Enter your master password to unlock encrypted configuration.\n"
                        "Your API keys are stored securely and encrypted locally.")
        
        description = QLabel(desc_text)
        description.setWordWrap(True)
        description.setAlignment(Qt.AlignmentFlag.AlignCenter)
        description.setStyleSheet(f"color: {DuckWorksStyle.COLORS['text_secondary']};")
        layout.addWidget(description)
        
        # Password input
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter master password...")
        self.password_input.returnPressed.connect(self.accept)
        layout.addWidget(self.password_input)
        
        # Show/hide password toggle
        show_password = QCheckBox("Show password")
        show_password.toggled.connect(self.toggle_password_visibility)
        layout.addWidget(show_password)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = DuckWorksButton("Cancel", "secondary")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        ok_btn = DuckWorksButton("Unlock" if self.action == "unlock" else "Create", "primary")
        ok_btn.clicked.connect(self.accept)
        button_layout.addWidget(ok_btn)
        
        layout.addLayout(button_layout)
        
        # Focus on password input
        self.password_input.setFocus()
    
    def toggle_password_visibility(self, show):
        if show:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Normal)
        else:
            self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
    
    def accept(self):
        self.password = self.password_input.text()
        if self.password:
            super().accept()
        else:
            QMessageBox.warning(self, "Warning", "Please enter a password.")

class GradingWorker(QObject):
    """Worker thread for grading operations"""
    
    progress_updated = pyqtSignal(int, str)
    log_message = pyqtSignal(str)
    grading_finished = pyqtSignal(bool, str)
    
    def __init__(self, agent, rubric_path, papers_folder, output_format, instructor_config_path):
        super().__init__()
        self.agent = agent
        self.rubric_path = rubric_path
        self.papers_folder = papers_folder
        self.output_format = output_format
        self.instructor_config_path = instructor_config_path
    
    @pyqtSlot()
    def run_grading(self):
        """Run the grading process"""
        try:
            self.log_message.emit("🚀 Starting grading process...")
            self.progress_updated.emit(10, "Initializing...")
            
            # Load instructor config
            instructor_config = {}
            if os.path.exists(self.instructor_config_path):
                with open(self.instructor_config_path, 'r') as f:
                    instructor_config = json.load(f)
                self.log_message.emit("✅ Loaded instructor configuration")
            
            self.progress_updated.emit(25, "Processing papers...")
            
            # Run grading
            output_file = self.agent.grade_papers(
                rubric_file=self.rubric_path,
                papers_folder=self.papers_folder,
                output_format=self.output_format,
                instructor_config=instructor_config
            )
            
            self.progress_updated.emit(100, "Grading complete!")
            self.log_message.emit(f"✅ Grading completed! Output saved to: {output_file}")
            self.grading_finished.emit(True, output_file)
            
        except Exception as e:
            self.log_message.emit(f"❌ Grading failed: {str(e)}")
            self.grading_finished.emit(False, str(e))

class DuckGradeLocalGUI(DuckWorksMainWindow):
    """Modern PyQt6 interface for DuckGrade local file grading"""
    
    def __init__(self):
        super().__init__("DuckGrade")
        self.init_managers()
        self.init_variables()
        self.setup_ui()
        self.load_existing_config()
    
    def init_managers(self):
        """Initialize managers"""
        self.key_manager = APIKeyManager()
        self.model_manager = None
        self.agent = None
        self.grading_worker = None
        self.grading_thread = None
    
    def init_variables(self):
        """Initialize variables"""
        self.rubric_path = ""
        self.papers_folder = ""
        self.output_format = "xlsx"
        self.instructor_config_path = "config/grading_instructor_config.json"
        self.available_models = []
        self.selected_model = "gpt-4o-mini"
    
    def setup_ui(self):
        """Setup the modern UI"""
        # Main layout
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header
        self.create_header(main_layout)
        
        # Tab widget for different sections
        self.tab_widget = QTabWidget()
        main_layout.addWidget(self.tab_widget)
        
        # Setup tabs
        self.setup_config_tab()
        self.setup_grading_tab()
        self.setup_log_tab()
    
    def create_header(self, layout):
        """Create header section"""
        header_card = DuckWorksCard()
        header_layout = QHBoxLayout()
        
        # Duck icon and title
        icon_label = QLabel()
        duck_pixmap = DuckWorksIcon.get_duck_icon().pixmap(48, 48)
        icon_label.setPixmap(duck_pixmap)
        header_layout.addWidget(icon_label)
        
        title_layout = QVBoxLayout()
        title = QLabel("DuckGrade - Local File Grading")
        title.setProperty("class", "title")
        title_layout.addWidget(title)
        
        subtitle = QLabel("AI-powered assignment grading for local files | DuckWorks Educational Suite")
        subtitle.setProperty("class", "muted")
        title_layout.addWidget(subtitle)
        
        header_layout.addLayout(title_layout)
        header_layout.addStretch()
        
        # Quick status
        self.status_label = QLabel("Ready to grade assignments")
        self.status_label.setStyleSheet(f"color: {DuckWorksStyle.COLORS['success']};")
        header_layout.addWidget(self.status_label)
        
        header_card.add_layout(header_layout)
        layout.addWidget(header_card)
    
    def setup_config_tab(self):
        """Setup configuration tab"""
        config_widget = QWidget()
        layout = QVBoxLayout(config_widget)
        layout.setSpacing(16)
        
        # API Configuration card
        api_card = DuckWorksCard("🔑 API Configuration")
        
        # API Key section
        api_layout = QGridLayout()
        
        api_layout.addWidget(QLabel("OpenAI API Key:"), 0, 0)
        self.api_key_input = QLineEdit()
        self.api_key_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.api_key_input.setPlaceholderText("Enter your OpenAI API key...")
        api_layout.addWidget(self.api_key_input, 0, 1)
        
        # API key buttons
        key_buttons = QHBoxLayout()
        save_key_btn = DuckWorksButton("Save Key", "primary", "check")
        save_key_btn.clicked.connect(self.save_api_key)
        key_buttons.addWidget(save_key_btn)
        
        load_key_btn = DuckWorksButton("Load Saved", "secondary")
        load_key_btn.clicked.connect(self.load_api_key)
        key_buttons.addWidget(load_key_btn)
        
        clear_key_btn = DuckWorksButton("Clear", "secondary")
        clear_key_btn.clicked.connect(self.clear_api_key)
        key_buttons.addWidget(clear_key_btn)
        
        api_layout.addLayout(key_buttons, 1, 1)
        
        # Model selection
        api_layout.addWidget(QLabel("AI Model:"), 2, 0)
        self.model_combo = QComboBox()
        self.model_combo.currentTextChanged.connect(self.on_model_changed)
        api_layout.addWidget(self.model_combo, 2, 1)
        
        refresh_models_btn = DuckWorksButton("Refresh Models", "secondary")
        refresh_models_btn.clicked.connect(self.refresh_models)
        api_layout.addWidget(refresh_models_btn, 3, 1)
        
        api_card.add_layout(api_layout)
        layout.addWidget(api_card)
        
        # File Configuration card
        file_card = DuckWorksCard("📁 File Configuration")
        file_layout = QGridLayout()
        
        # Rubric file
        file_layout.addWidget(QLabel("Rubric File:"), 0, 0)
        self.rubric_input = QLineEdit()
        self.rubric_input.setPlaceholderText("Select rubric file...")
        file_layout.addWidget(self.rubric_input, 0, 1)
        
        rubric_btn = DuckWorksButton("Browse", "secondary", "file")
        rubric_btn.clicked.connect(self.select_rubric_file)
        file_layout.addWidget(rubric_btn, 0, 2)
        
        # Papers folder
        file_layout.addWidget(QLabel("Papers Folder:"), 1, 0)
        self.papers_input = QLineEdit()
        self.papers_input.setPlaceholderText("Select folder containing student papers...")
        file_layout.addWidget(self.papers_input, 1, 1)
        
        papers_btn = DuckWorksButton("Browse", "secondary", "folder")
        papers_btn.clicked.connect(self.select_papers_folder)
        file_layout.addWidget(papers_btn, 1, 2)
        
        # Output format
        file_layout.addWidget(QLabel("Output Format:"), 2, 0)
        self.format_combo = QComboBox()
        self.format_combo.addItems(["xlsx", "csv", "json"])
        self.format_combo.setCurrentText("xlsx")
        self.format_combo.currentTextChanged.connect(self.on_format_changed)
        file_layout.addWidget(self.format_combo, 2, 1)
        
        file_card.add_layout(file_layout)
        layout.addWidget(file_card)
        
        layout.addStretch()
        self.tab_widget.addTab(config_widget, "⚙️ Configuration")
    
    def setup_grading_tab(self):
        """Setup grading tab"""
        grading_widget = QWidget()
        layout = QVBoxLayout(grading_widget)
        layout.setSpacing(16)
        
        # Quick Setup card
        setup_card = DuckWorksCard("🚀 Quick Setup")
        
        # Drag and drop areas
        drop_layout = QHBoxLayout()
        
        rubric_drop = FileDropWidget("🧾 Drop Rubric File Here\n(.txt, .docx, .pdf)")
        rubric_drop.files_dropped.connect(self.on_rubric_dropped)
        drop_layout.addWidget(rubric_drop)
        
        papers_drop = FileDropWidget("📁 Drop Papers Folder Here\nOr individual paper files")
        papers_drop.files_dropped.connect(self.on_papers_dropped)
        drop_layout.addWidget(papers_drop)
        
        setup_card.add_layout(drop_layout)
        layout.addWidget(setup_card)
        
        # Grading Control card
        control_card = DuckWorksCard("🎯 Grading Control")
        
        # Start grading button
        self.start_btn = DuckWorksButton("🚀 Start Grading", "primary", "play")
        self.start_btn.clicked.connect(self.start_grading)
        self.start_btn.setMinimumHeight(48)
        control_card.add_widget(self.start_btn)
        
        # Progress section
        self.progress_bar = DuckWorksProgressBar()
        self.progress_bar.setVisible(False)
        control_card.add_widget(self.progress_bar)
        
        layout.addWidget(control_card)
        
        # Results card
        self.results_card = DuckWorksCard("📊 Results")
        self.results_card.setVisible(False)
        
        self.results_label = QLabel()
        self.results_card.add_widget(self.results_label)
        
        self.open_results_btn = DuckWorksButton("Open Results", "primary", "file")
        self.open_results_btn.clicked.connect(self.open_results)
        self.results_card.add_widget(self.open_results_btn)
        
        layout.addWidget(self.results_card)
        
        layout.addStretch()
        self.tab_widget.addTab(grading_widget, "🎯 Grade Papers")
    
    def setup_log_tab(self):
        """Setup log tab"""
        log_widget = QWidget()
        layout = QVBoxLayout(log_widget)
        
        # Log card
        log_card = DuckWorksCard("📝 Activity Log")
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setFont(QFont("Consolas", 9))
        self.log_text.setMaximumHeight(400)
        log_card.add_widget(self.log_text)
        
        # Clear log button
        clear_btn = DuckWorksButton("Clear Log", "secondary")
        clear_btn.clicked.connect(self.clear_log)
        log_card.add_widget(clear_btn)
        
        layout.addWidget(log_card)
        layout.addStretch()
        self.tab_widget.addTab(log_widget, "📝 Log")
    
    def password_callback(self, action="unlock"):
        """Password callback for secure key management"""
        dialog = PasswordDialog(action, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            return dialog.password
        return None
    
    def save_api_key(self):
        """Save API key securely"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            self.show_duck_message("Error", "Please enter an API key.", "error")
            return
        
        try:
            if self.key_manager.save_openai_key(api_key, password_callback=self.password_callback):
                self.log_message("✅ API key saved securely")
                self.refresh_models()
                self.status_label.setText("API key configured")
                self.status_label.setStyleSheet(f"color: {DuckWorksStyle.COLORS['success']};")
            else:
                self.show_duck_message("Error", "Failed to save API key.", "error")
        except Exception as e:
            self.show_duck_message("Error", f"Error saving API key: {e}", "error")
    
    def load_api_key(self):
        """Load saved API key"""
        try:
            api_key = self.key_manager.get_openai_key(password_callback=self.password_callback)
            if api_key:
                self.api_key_input.setText(api_key)
                self.log_message("✅ Loaded saved API key")
                self.refresh_models()
            else:
                self.show_duck_message("Info", "No saved API key found.", "information")
        except Exception as e:
            self.show_duck_message("Error", f"Error loading API key: {e}", "error")
    
    def clear_api_key(self):
        """Clear API key"""
        try:
            self.api_key_input.clear()
            self.key_manager.clear_openai_key()
            self.model_manager = None
            self.available_models = []
            self.model_combo.clear()
            self.log_message("🗑️ API key cleared")
            self.status_label.setText("API key required")
            self.status_label.setStyleSheet(f"color: {DuckWorksStyle.COLORS['warning']};")
        except Exception as e:
            self.show_duck_message("Error", f"Error clearing API key: {e}", "error")
    
    def refresh_models(self):
        """Refresh available models"""
        api_key = self.api_key_input.text().strip()
        if not api_key:
            return
        
        try:
            self.model_manager = OpenAIModelManager(api_key)
            models = self.model_manager.get_available_models()
            
            self.model_combo.clear()
            for model in models:
                self.model_combo.addItem(model['display_text'], model['name'])
            
            # Set default model
            for i in range(self.model_combo.count()):
                if self.model_combo.itemData(i) == self.selected_model:
                    self.model_combo.setCurrentIndex(i)
                    break
            
            self.log_message(f"📊 Loaded {len(models)} available models")
        except Exception as e:
            self.log_message(f"❌ Failed to refresh models: {e}")
    
    def on_model_changed(self, text):
        """Handle model selection change"""
        current_data = self.model_combo.currentData()
        if current_data:
            self.selected_model = current_data
            self.log_message(f"🎛️ Selected model: {text}")
    
    def on_format_changed(self, format_name):
        """Handle format change"""
        self.output_format = format_name
        self.log_message(f"📄 Output format: {format_name}")
    
    def select_rubric_file(self):
        """Select rubric file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Rubric File",
            "",
            "All Supported (*.txt *.docx *.pdf);;Text Files (*.txt);;Word Documents (*.docx);;PDF Files (*.pdf)"
        )
        if file_path:
            self.rubric_path = file_path
            self.rubric_input.setText(file_path)
            self.log_message(f"📋 Selected rubric: {Path(file_path).name}")
    
    def select_papers_folder(self):
        """Select papers folder"""
        folder_path = QFileDialog.getExistingDirectory(self, "Select Papers Folder")
        if folder_path:
            self.papers_folder = folder_path
            self.papers_input.setText(folder_path)
            self.log_message(f"📁 Selected papers folder: {Path(folder_path).name}")
    
    def on_rubric_dropped(self, files):
        """Handle rubric file drop"""
        if files:
            self.rubric_path = files[0]
            self.rubric_input.setText(files[0])
            self.log_message(f"📋 Dropped rubric: {Path(files[0]).name}")
    
    def on_papers_dropped(self, files):
        """Handle papers drop"""
        if files:
            # If single folder, use it as papers folder
            if len(files) == 1 and os.path.isdir(files[0]):
                self.papers_folder = files[0]
                self.papers_input.setText(files[0])
                self.log_message(f"📁 Dropped papers folder: {Path(files[0]).name}")
            else:
                # Multiple files - create a temporary folder concept
                parent_dir = str(Path(files[0]).parent)
                self.papers_folder = parent_dir
                self.papers_input.setText(f"{parent_dir} ({len(files)} files)")
                self.log_message(f"📁 Dropped {len(files)} paper files")
    
    def start_grading(self):
        """Start the grading process"""
        # Validate inputs
        if not self.rubric_path or not os.path.exists(self.rubric_path):
            self.show_duck_message("Error", "Please select a valid rubric file.", "error")
            return
        
        if not self.papers_folder or not os.path.exists(self.papers_folder):
            self.show_duck_message("Error", "Please select a valid papers folder.", "error")
            return
        
        api_key = self.api_key_input.text().strip()
        if not api_key:
            self.show_duck_message("Error", "Please enter your OpenAI API key.", "error")
            return
        
        # Initialize agent
        try:
            self.agent = GradingAgent(api_key, model=self.selected_model)
        except Exception as e:
            self.show_duck_message("Error", f"Failed to initialize grading agent: {e}", "error")
            return
        
        # Setup UI for grading
        self.start_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        self.results_card.setVisible(False)
        
        # Start worker thread
        self.grading_worker = GradingWorker(
            self.agent, self.rubric_path, self.papers_folder, 
            self.output_format, self.instructor_config_path
        )
        
        self.grading_thread = QThread()
        self.grading_worker.moveToThread(self.grading_thread)
        
        # Connect signals
        self.grading_worker.progress_updated.connect(self.update_progress)
        self.grading_worker.log_message.connect(self.log_message)
        self.grading_worker.grading_finished.connect(self.grading_finished)
        self.grading_thread.started.connect(self.grading_worker.run_grading)
        
        # Start thread
        self.grading_thread.start()
    
    def update_progress(self, value, status):
        """Update progress bar"""
        self.progress_bar.animate_to_value(value)
        self.progress_bar.set_status_text(status)
    
    def grading_finished(self, success, result):
        """Handle grading completion"""
        self.grading_thread.quit()
        self.grading_thread.wait()
        
        self.start_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        if success:
            self.results_label.setText(f"✅ Grading completed successfully!\n\nResults saved to:\n{result}")
            self.results_card.setVisible(True)
            self.output_file = result
            self.status_label.setText("Grading completed")
            self.status_label.setStyleSheet(f"color: {DuckWorksStyle.COLORS['success']};")
        else:
            self.show_duck_message("Grading Failed", f"An error occurred during grading:\n\n{result}", "error")
            self.status_label.setText("Grading failed")
            self.status_label.setStyleSheet(f"color: {DuckWorksStyle.COLORS['error']};")
    
    def open_results(self):
        """Open results file"""
        if hasattr(self, 'output_file') and os.path.exists(self.output_file):
            os.startfile(self.output_file)
    
    def log_message(self, message):
        """Add message to log"""
        timestamp = QDateTime.currentDateTime().toString("hh:mm:ss")
        formatted_message = f"[{timestamp}] {message}"
        self.log_text.append(formatted_message)
        
        # Also update status bar
        self.status_bar.showMessage(message, 3000)
    
    def clear_log(self):
        """Clear the log"""
        self.log_text.clear()
        self.log_message("📝 Log cleared")
    
    def load_existing_config(self):
        """Load existing configuration"""
        try:
            # Try to load saved API key
            api_key = self.key_manager.get_openai_key(password_callback=self.password_callback)
            if api_key:
                self.api_key_input.setText(api_key)
                self.refresh_models()
                self.log_message("✅ Loaded existing configuration")
        except:
            self.log_message("ℹ️ No existing configuration found")

def main():
    """Main function"""
    app = QApplication(sys.argv)
    app.setApplicationName("DuckGrade")
    app.setApplicationVersion("2.0.0")
    app.setOrganizationName("DuckWorks")
    
    # Set application icon
    app.setWindowIcon(DuckWorksIcon.get_duck_icon())
    
    # Create and show main window
    window = DuckGradeLocalGUI()
    window.show()
    
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
