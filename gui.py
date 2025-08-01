"""
DuckGrade - Local File Grading Interface
Part of the DuckWorks Educational Automation Suite

Provides an easy-to-use interface for loading rubrics, papers, and running the grading system
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext, simpledialog
import os
from pathlib import Path
import threading
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


class GradingAgentGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("DuckGrade - Local File Grading | DuckWorks Educational Suite")
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
        self.agent = None
        self.api_key = tk.StringVar()
        self.selected_model = tk.StringVar(value="gpt-4o-mini")
        self.rubric_path = tk.StringVar()
        self.papers_folder = tk.StringVar()
        self.output_format = tk.StringVar(value="xlsx")
        self.instructor_config_path = tk.StringVar(value="grading_instructor_config.json")
        
        # Available models (will be populated dynamically)
        self.available_models = []
        
        self.setup_ui()
        self.load_saved_credentials()
    
    def password_callback(self, action):
        """Password callback for secure key manager"""
        dialog = PasswordDialog(self.root, action)
        self.root.wait_window(dialog.dialog)
        return dialog.result
        
    def setup_ui(self):
        """Setup the user interface"""
        # Create notebook for tabs
        self.notebook = ttk.Notebook(self.root)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Setup Tab
        self.setup_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.setup_tab, text="Setup")
        
        # Results Tab  
        self.results_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.results_tab, text="Results")
        
        self.setup_setup_tab()
        self.setup_results_tab()
        
    def setup_setup_tab(self):
        """Setup the main configuration tab"""
        
        # OpenAI API Configuration
        api_frame = ttk.LabelFrame(self.setup_tab, text="OpenAI API Configuration", padding=10)
        api_frame.pack(fill=tk.X, padx=10, pady=5)
        
        # API Key section
        api_key_frame = ttk.Frame(api_frame)
        api_key_frame.pack(fill=tk.X, pady=2)
        
        ttk.Label(api_key_frame, text="API Key:").pack(side=tk.LEFT, padx=(0, 5))
        self.api_key_entry = ttk.Entry(api_key_frame, textvariable=self.api_key, show="*", width=50)
        self.api_key_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        ttk.Button(api_key_frame, text="Save Key", command=self.save_api_key).pack(side=tk.LEFT, padx=2)
        ttk.Button(api_key_frame, text="Load Key", command=self.load_api_key).pack(side=tk.LEFT, padx=2)
        ttk.Button(api_key_frame, text="Clear", command=self.clear_api_key).pack(side=tk.LEFT, padx=2)
        
        # Model selection section
        model_frame = ttk.Frame(api_frame)
        model_frame.pack(fill=tk.X, pady=(10, 2))
        
        ttk.Label(model_frame, text="Model:").pack(side=tk.LEFT, padx=(0, 5))
        self.model_combobox = ttk.Combobox(model_frame, textvariable=self.selected_model, 
                                          state="readonly", width=50)
        self.model_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))
        
        self.refresh_models_btn = ttk.Button(model_frame, text="Refresh Models", 
                                           command=self.refresh_models)
        self.refresh_models_btn.pack(side=tk.LEFT, padx=2)
        
        # Model info label
        self.model_info_label = ttk.Label(api_frame, text="Select a model to see pricing information", 
                                         font=("Arial", 8), foreground="gray")
        self.model_info_label.pack(fill=tk.X, pady=(0, 2))
        
        # Pricing update info
        self.pricing_info_label = ttk.Label(api_frame, text="", 
                                           font=("Arial", 7), foreground="blue")
        self.pricing_info_label.pack(fill=tk.X, pady=(0, 5))
        
        # Bind model selection event
        self.model_combobox.bind('<<ComboboxSelected>>', self.on_model_selected)
        
        # Rubric Configuration
        rubric_frame = ttk.LabelFrame(self.setup_tab, text="Rubric Configuration", padding=10)
        rubric_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(rubric_frame, text="Rubric File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(rubric_frame, textvariable=self.rubric_path, width=50, state="readonly").grid(
            row=0, column=1, sticky=tk.EW, pady=2, padx=(10, 5))
        ttk.Button(rubric_frame, text="Browse", command=self.browse_rubric).grid(
            row=0, column=2, pady=2)
        
        rubric_frame.columnconfigure(1, weight=1)
        
        # Papers section
        papers_frame = ttk.LabelFrame(self.setup_tab, text="Student Papers", padding=10)
        papers_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(papers_frame, text="Papers Folder:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(papers_frame, textvariable=self.papers_folder, width=50, state="readonly").grid(
            row=0, column=1, sticky=tk.EW, pady=2, padx=(10, 5))
        ttk.Button(papers_frame, text="Browse", command=self.browse_papers_folder).grid(
            row=0, column=2, pady=2)
        
        papers_frame.columnconfigure(1, weight=1)
        
        # Instructor Configuration
        instructor_frame = ttk.LabelFrame(self.setup_tab, text="Instructor Configuration (Optional)", padding=10)
        instructor_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(instructor_frame, text="Config File:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(instructor_frame, textvariable=self.instructor_config_path, width=50, state="readonly").grid(
            row=0, column=1, sticky=tk.EW, pady=2, padx=(10, 5))
        ttk.Button(instructor_frame, text="Browse", command=self.browse_instructor_config).grid(
            row=0, column=2, pady=2)
        ttk.Button(instructor_frame, text="Clear", command=self.clear_instructor_config).grid(
            row=0, column=3, pady=2, padx=(5, 0))
        
        instructor_frame.columnconfigure(1, weight=1)
        
        # Output Configuration
        output_frame = ttk.LabelFrame(self.setup_tab, text="Output Configuration", padding=10)
        output_frame.pack(fill=tk.X, padx=10, pady=5)
        
        ttk.Label(output_frame, text="Output Format:").pack(side=tk.LEFT)
        ttk.Radiobutton(output_frame, text="Excel (.xlsx)", variable=self.output_format, 
                       value="xlsx").pack(side=tk.LEFT, padx=10)
        ttk.Radiobutton(output_frame, text="CSV (.csv)", variable=self.output_format, 
                       value="csv").pack(side=tk.LEFT, padx=10)
        
        # Action Buttons
        button_frame = ttk.Frame(self.setup_tab)
        button_frame.pack(fill=tk.X, padx=10, pady=20)
        
        ttk.Button(button_frame, text="Initialize Agent", command=self.initialize_agent).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Grade All Papers", command=self.grade_papers).pack(
            side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Export Results", command=self.export_results).pack(
            side=tk.LEFT, padx=5)
        
        # Progress bar
        self.progress = ttk.Progressbar(self.setup_tab, mode='indeterminate')
        self.progress.pack(fill=tk.X, padx=10, pady=5)
        
    def setup_results_tab(self):
        """Setup the results display tab"""
        # Results display
        self.results_text = scrolledtext.ScrolledText(self.results_tab, wrap=tk.WORD, height=20)
        self.results_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Clear results button
        clear_button = ttk.Button(self.results_tab, text="Clear Results", 
                                 command=lambda: self.results_text.delete(1.0, tk.END))
        clear_button.pack(pady=5)
    
    def load_saved_credentials(self):
        """Load saved API credentials if available"""
        try:
            # Check if encrypted config exists without trying to decrypt
            if self.key_manager.key_manager.has_config():
                # We have encrypted data but need password to access it
                # Don't automatically prompt - let user click "Load Key" when ready
                self.log_message("🔐 Encrypted API key found - click 'Load Key' to access")
            else:
                self.log_message("📝 No saved OpenAI API key found")
                
        except Exception as e:
            self.log_message(f"❌ Error checking saved credentials: {e}")
    
    def save_api_key(self):
        """Save API key securely"""
        api_key = self.api_key.get().strip()
        if not api_key:
            messagebox.showerror("Error", "Please enter an API key")
            return
        
        try:
            if self.key_manager.save_openai_key(api_key, password_callback=self.password_callback):
                self.log_message("✅ API key saved securely")
                # Initialize model manager with new key
                self.refresh_models()
            else:
                messagebox.showerror("Error", "Failed to save API key")
        except Exception as e:
            messagebox.showerror("Error", f"Error saving API key: {e}")
    
    def load_api_key(self):
        """Load saved API key"""
        try:
            api_key = self.key_manager.get_openai_key(password_callback=self.password_callback)
            if api_key:
                self.api_key.set(api_key)
                self.log_message("✅ Loaded saved API key")
                self.refresh_models()
            else:
                messagebox.showinfo("Info", "No saved API key found")
        except Exception as e:
            messagebox.showerror("Error", f"Error loading API key: {e}")
    
    def clear_api_key(self):
        """Clear API key from both display and storage"""
        try:
            self.api_key.set("")
            self.key_manager.clear_openai_key()
            self.model_manager = None
            self.available_models = []
            self.model_combobox['values'] = []
            self.model_info_label.config(text="API key cleared - enter new key to load models")
            self.log_message("✅ API key cleared")
        except Exception as e:
            messagebox.showerror("Error", f"Error clearing API key: {e}")
    
    def refresh_models(self):
        """Refresh available OpenAI models"""
        api_key = self.api_key.get().strip()
        if not api_key:
            self.log_message("❌ Please enter an OpenAI API key first")
            return
        
        def fetch_models():
            try:
                self.log_message("🔄 Fetching available OpenAI models and current pricing...")
                self.refresh_models_btn.config(state="disabled", text="Loading...")
                
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
                self.selected_model.set(models[default_idx]['id'])
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
        finally:
            self.refresh_models_btn.config(state="normal", text="Refresh Models")
    
    def handle_model_fetch_error(self, error_msg):
        """Handle error when fetching models"""
        self.log_message(f"❌ Error fetching models: {error_msg}")
        self.model_info_label.config(text="Error loading models - check API key and connection")
        self.refresh_models_btn.config(state="normal", text="Refresh Models")
    
    def on_model_selected(self, event=None):
        """Handle model selection"""
        try:
            selection_idx = self.model_combobox.current()
            if selection_idx >= 0 and self.available_models:
                selected_model = self.available_models[selection_idx]
                self.selected_model.set(selected_model['id'])
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
    
    def browse_rubric(self):
        """Browse for rubric file"""
        filename = filedialog.askopenfilename(
            title="Select Rubric File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.rubric_path.set(filename)
    
    def browse_instructor_config(self):
        """Browse for instructor configuration file"""
        filename = filedialog.askopenfilename(
            title="Select Instructor Configuration File",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.instructor_config_path.set(filename)
    
    def clear_instructor_config(self):
        """Clear instructor configuration (make it optional)"""
        self.instructor_config_path.set("")
        messagebox.showinfo("Info", "Instructor configuration cleared. Default grading style will be used.")
    
    def browse_papers_folder(self):
        """Browse for papers folder"""
        folder = filedialog.askdirectory(title="Select Folder Containing Student Papers")
        if folder:
            self.papers_folder.set(folder)
    
    def initialize_agent(self):
        """Initialize the grading agent"""
        try:
            if not self.api_key.get():
                messagebox.showerror("Error", "Please enter your OpenAI API key")
                return
            
            if not self.rubric_path.get():
                messagebox.showerror("Error", "Please select a rubric file")
                return
            
            if not self.papers_folder.get():
                messagebox.showerror("Error", "Please select a papers folder")
                return
            
            # Initialize agent with selected model
            selected_model = self.selected_model.get() or "gpt-4o-mini"
            self.agent = GradingAgent(self.api_key.get(), model=selected_model)
            
            # Load instructor configuration if provided
            instructor_config_path = self.instructor_config_path.get().strip()
            if instructor_config_path and os.path.exists(instructor_config_path):
                self.agent.load_instructor_config(instructor_config_path)
                self.log_message(f"✅ Loaded instructor configuration: {instructor_config_path}")
            else:
                self.log_message("📝 Using default grading configuration")
            
            # Load rubric and papers
            self.agent.load_rubric(self.rubric_path.get())
            self.agent.load_student_papers(self.papers_folder.get())
            
            self.log_message(f"✅ Agent initialized successfully with model: {selected_model}")
            self.log_message(f"📊 Loaded {len(self.agent.students_data)} student papers")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to initialize agent: {str(e)}")
            self.log_message(f"❌ Initialization error: {str(e)}")
    
    def grade_papers(self):
        """Grade all papers in a separate thread"""
        if not self.agent:
            messagebox.showerror("Error", "Please initialize the agent first")
            return
        
        def grade_worker():
            try:
                self.progress.start()
                self.log_message("🔄 Starting grading process...")
                
                results = self.agent.grade_all_papers()
                
                self.progress.stop()
                self.log_message(f"✅ Grading completed! Processed {len(results)} papers")
                
                # Generate summary
                summary = self.agent.generate_summary_report()
                self.log_message(f"📊 Average score: {summary.get('average_score', 0):.2f}%")
                
            except Exception as e:
                self.progress.stop()
                self.root.after(0, lambda: messagebox.showerror("Error", f"Grading failed: {str(e)}"))
                self.log_message(f"❌ Grading error: {str(e)}")
        
        threading.Thread(target=grade_worker, daemon=True).start()
    
    def export_results(self):
        """Export grading results"""
        if not self.agent or not self.agent.graded_results:
            messagebox.showerror("Error", "No grading results to export. Please grade papers first.")
            return
        
        try:
            output_format = self.output_format.get()
            filename = self.agent.export_results(output_format)
            
            self.log_message(f"✅ Results exported to: {filename}")
            messagebox.showinfo("Success", f"Results exported to:\n{filename}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Export failed: {str(e)}")
            self.log_message(f"❌ Export error: {str(e)}")
    
    def log_message(self, message):
        """Log a message to the results tab"""
        self.results_text.insert(tk.END, f"{message}\n")
        self.results_text.see(tk.END)
        self.root.update_idletasks()


def main():
    """Main function to run the GUI"""
    root = tk.Tk()
    app = GradingAgentGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
