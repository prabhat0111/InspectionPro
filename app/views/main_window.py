import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
import threading
import logging
import sv_ttk  # For modern theme
from typing import Optional, Dict

class ReportGeneratorUI:
    def __init__(self, root, report_engine):
        """Initialize the report generator UI"""
        self.root = root
        self.engine = report_engine
        self.logger = logging.getLogger(__name__)

        
        self.input_entry = None
        self.photos_entry = None
        self.output_entry = None
        self.preview_text = None
        self.generate_btn = None
        self.progress = None
        self.status_var = None

        
        self.progress_value = tk.IntVar(value=0)

    
        self.state = {
            'input_file': None,
            'photos_dir': None,
            'output_dir': None,
            'processing': False,
            'theme': 'light'  
        }

        
        self.setup_ui()

        
        self.configure_tags()
        self.setup_bindings()

    def setup_ui(self):
        self.root.title("Inspection Pro - Report Generator")
        self.root.geometry("1100x800")
        self.root.minsize(900, 650)
        sv_ttk.set_theme(self.state['theme'])

        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        self.setup_header()
        self.setup_settings_panel()
        self.setup_preview_area()
        self.setup_action_buttons()
        self.setup_status_bar()
        self.setup_menu()
        self.initialize_preview()

    def setup_header(self):
        header_frame = ttk.Frame(self.main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        self.logo_label = ttk.Label(header_frame, text="📝 Inspection Pro", font=('Segoe UI', 18, 'bold'))
        self.logo_label.pack(side=tk.LEFT)

        self.theme_btn = ttk.Button(header_frame, text="☀️" if self.state['theme'] == 'light' else "🌙", command=self.toggle_theme, width=3)
        self.theme_btn.pack(side=tk.RIGHT, padx=5)

    def setup_settings_panel(self):
        settings_frame = ttk.LabelFrame(self.main_frame, text="Report Settings", padding=(20, 15))
        settings_frame.pack(fill=tk.X, pady=(0, 20))

        self.input_entry = self.setup_file_input(settings_frame, "Claim Data File:", "Select Excel/CSV file", self.browse_input_file, row=0)
        self.photos_entry = self.setup_file_input(settings_frame, "Photos Directory:", "Optional - select folder with photos", self.browse_photos_dir, row=1)
        self.output_entry = self.setup_file_input(settings_frame, "Output Directory:", "Select save location", self.browse_output_dir, row=2)

    def setup_file_input(self, parent, label_text, placeholder, command, row):
        frame = ttk.Frame(parent)
        frame.grid(row=row, column=0, sticky='ew', pady=8)

        ttk.Label(frame, text=label_text, width=15, anchor='e').pack(side=tk.LEFT, padx=(0, 10))

        entry = ttk.Entry(frame)
        entry.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.setup_placeholder(entry, placeholder)

        browse_btn = ttk.Button(frame, text="Browse", command=command, width=10)
        browse_btn.pack(side=tk.LEFT)

        return entry

    def setup_preview_area(self):
        preview_frame = ttk.LabelFrame(self.main_frame, text="Preview", padding=(15, 10))
        preview_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(preview_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.preview_text = tk.Text(preview_frame, wrap=tk.WORD, height=15, font=('Consolas', 10),
                                    yscrollcommand=scrollbar.set, padx=10, pady=10)
        self.preview_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.preview_text.yview)

    def setup_action_buttons(self):
        button_frame = ttk.Frame(self.main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))

        self.progress = ttk.Progressbar(button_frame, orient=tk.HORIZONTAL, mode='determinate', variable=self.progress_value)
        self.progress.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 15))

        self.generate_btn = ttk.Button(button_frame, text="Generate Reports", command=self.start_report_generation,
                                       style='Accent.TButton', state=tk.DISABLED)
        self.generate_btn.pack(side=tk.RIGHT)

    def setup_status_bar(self):
        self.status_var = tk.StringVar()
        self.status_var.set("Ready")

        status_bar = ttk.Frame(self.main_frame, height=25)
        status_bar.pack(fill=tk.X, pady=(10, 0))

        ttk.Label(status_bar, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W, padding=(10, 0)).pack(fill=tk.X)

    def setup_menu(self):
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    def initialize_preview(self):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(tk.END, "Select input files to see preview here...")
        self.preview_text.config(state=tk.DISABLED)

    def configure_tags(self):
        self.preview_text.tag_config('bold', font=('Segoe UI', 9, 'bold'))
        self.preview_text.tag_config('success', foreground='#2e7d32')
        self.preview_text.tag_config('error', foreground='#c62828')
        self.preview_text.tag_config('warning', foreground='#f9a825')
        self.preview_text.tag_config('highlight', background='#e3f2fd')

    def setup_bindings(self):
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.bind('<Return>', lambda e: self.start_report_generation())

    def setup_placeholder(self, entry, placeholder):
        entry.insert(0, placeholder)
        entry.config(foreground='gray')

        def clear_placeholder(e):
            if entry.get() == placeholder:
                entry.delete(0, tk.END)
                entry.config(foreground='black')

        def restore_placeholder(e):
            if not entry.get():
                entry.insert(0, placeholder)
                entry.config(foreground='gray')

        entry.bind("<FocusIn>", clear_placeholder)
        entry.bind("<FocusOut>", restore_placeholder)

    def toggle_theme(self):
        self.state['theme'] = 'dark' if self.state['theme'] == 'light' else 'light'
        sv_ttk.set_theme(self.state['theme'])
        self.theme_btn.config(text="☀️" if self.state['theme'] == 'light' else "🌙")

    def browse_input_file(self):
        file_path = filedialog.askopenfilename(title="Select Claim Data File",
                                               filetypes=[("Excel Files", "*.xlsx *.xls"),
                                                          ("CSV Files", "*.csv"),
                                                          ("All Files", "*.*")])
        if file_path:
            self.state['input_file'] = file_path
            self.update_entry(self.input_entry, file_path)
            self.update_preview()

    def browse_photos_dir(self):
        dir_path = filedialog.askdirectory(title="Select Photos Directory")
        if dir_path:
            self.state['photos_dir'] = dir_path
            self.update_entry(self.photos_entry, dir_path)
            self.update_preview()

    def browse_output_dir(self):
        dir_path = filedialog.askdirectory(title="Select Output Directory")
        if dir_path:
            self.state['output_dir'] = dir_path
            self.update_entry(self.output_entry, dir_path)
            self.update_preview()

    def update_entry(self, entry, value):
        entry.delete(0, tk.END)
        entry.insert(0, value)
        entry.config(foreground='black')

    def update_preview(self):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.delete(1.0, tk.END)

        if self.state['input_file']:
            self.preview_text.insert(tk.END, "📄 Input File:\n", 'bold')
            self.preview_text.insert(tk.END, f"   {Path(self.state['input_file']).name}\n\n")

        if self.state['photos_dir']:
            self.preview_text.insert(tk.END, "📸 Photos Directory:\n", 'bold')
            self.preview_text.insert(tk.END, f"   {Path(self.state['photos_dir']).name}\n\n")
        else:
            self.preview_text.insert(tk.END, "⚠️ No photos directory selected\n\n", 'warning')

        if self.state['output_dir']:
            self.preview_text.insert(tk.END, "📁 Output Directory:\n", 'bold')
            self.preview_text.insert(tk.END, f"   {Path(self.state['output_dir']).name}\n\n")

        self.update_generate_button()
        self.preview_text.config(state=tk.DISABLED)

    def update_generate_button(self):
        if not hasattr(self, 'generate_btn') or self.generate_btn is None:
            return

        if all([self.state['input_file'], self.state['output_dir']]):
            self.generate_btn.config(state=tk.NORMAL)
            self.status_var.set("Ready to generate reports")
        else:
            self.generate_btn.config(state=tk.DISABLED)
            missing = []
            if not self.state['input_file']:
                missing.append("input file")
            if not self.state['output_dir']:
                missing.append("output directory")
            self.status_var.set(f"Please select {', '.join(missing)}")

    def start_report_generation(self):
        if self.state['processing']:
            return

        if not messagebox.askyesno("Confirm Generation", "Generate inspection reports with current settings?"):
            return

        self.state['processing'] = True
        self.generate_btn.config(state=tk.DISABLED)
        self.progress_value.set(0)
        self.status_var.set("Generating reports...")
        self.logger.info("Starting report generation")

        thread = threading.Thread(target=self.generate_reports, daemon=True)
        thread.start()

    def generate_reports(self):
        try:
            reports = self.engine.process_claims(self.state['input_file'], self.state['output_dir'], self.state['photos_dir'])
            self.progress_value.set(100)
            self.show_success_message(len(reports))
            self.logger.info(f"Successfully generated {len(reports)} reports")
        except Exception as e:
            self.show_error_message(str(e))
            self.logger.error(f"Report generation failed: {str(e)}")
        finally:
            self.state['processing'] = False
            if hasattr(self, 'generate_btn') and self.generate_btn:
                self.generate_btn.config(state=tk.NORMAL)

    def show_success_message(self, count):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.insert(tk.END, f"\n✅ Successfully generated {count} reports!\n", 'success')
        self.preview_text.see(tk.END)
        self.preview_text.config(state=tk.DISABLED)

        self.status_var.set(f"Generated {count} reports successfully")
        messagebox.showinfo("Success", f"Generated {count} reports successfully!")

    def show_error_message(self, error):
        self.preview_text.config(state=tk.NORMAL)
        self.preview_text.insert(tk.END, f"\n❌ Error: {error}\n", 'error')
        self.preview_text.see(tk.END)
        self.preview_text.config(state=tk.DISABLED)

        self.status_var.set("Error generating reports")
        messagebox.showerror("Error", f"Report generation failed:\n{error}")

    def show_about(self):
        about_text = (
            "Inspection Pro - Report Generator\n"
            "Version 1.0\n\n"
            "A tool for generating first inspection reports\n"
            "from claim data and photos."
        )
        messagebox.showinfo("About", about_text)

    def on_close(self):
        if self.state['processing']:
            if not messagebox.askokcancel("Reports Generating", "Reports are still being generated. Close anyway?"):
                return
        self.root.destroy()
