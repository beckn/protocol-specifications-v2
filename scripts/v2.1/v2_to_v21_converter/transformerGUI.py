#!/usr/bin/env python3
"""
Beckn Protocol Version Transformer - GUI Application

A graphical user interface for transforming Beckn protocol JSON files between versions.
Provides dual-pane JSON viewing with file upload and real-time transformation.

Author: Beckn Protocol Team
Version: 1.0.0
License: MIT
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import tempfile
import os
import webbrowser
from pathlib import Path
from datetime import datetime
from becknVersionTransform import IRITransformer, strip_prefixes
from becknSemanticTransform import SemanticTransformer

class TransformerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Beckn Protocol Version Transformer")
        self.root.geometry("1400x900")
        
        # File paths storage
        self.input_json_path = None
        self.context_path = None
        self.vocab_path = None
        self.attributes_path = None
        self.structural_rules_path = None
        self.shacl_shapes_path = None
        self.expected_output_path = None
        self.output_version = "2.1"
        self.strip_prefixes_var = tk.BooleanVar(value=True)
        self.transformer_mode = tk.StringVar(value="semantic")  # "semantic" or "hybrid"
        self.last_report_path = None
        
        # Create UI
        self.create_ui()
        
    def create_ui(self):
        """Create the main UI layout"""
        # Main container with padding
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)
        
        # Top section: File uploads and controls
        self.create_control_panel(main_frame)
        
        # Bottom section: Dual-pane JSON viewer
        self.create_json_viewer(main_frame)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_control_panel(self, parent):
        """Create the control panel with file uploads and transform button"""
        control_frame = ttk.LabelFrame(parent, text="Configuration", padding="10")
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        
        row = 0
        
        # Input JSON file
        ttk.Label(control_frame, text="Input JSON:").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.input_label = ttk.Label(control_frame, text="No file selected", foreground="gray")
        self.input_label.grid(row=row, column=1, sticky=tk.W, padx=10)
        ttk.Button(control_frame, text="Browse...", command=self.select_input_json).grid(row=row, column=2, padx=5)
        row += 1
        
        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Context file
        ttk.Label(control_frame, text="Context File (.jsonld):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.context_label = ttk.Label(control_frame, text="No file selected", foreground="gray")
        self.context_label.grid(row=row, column=1, sticky=tk.W, padx=10)
        ttk.Button(control_frame, text="Browse...", command=self.select_context).grid(row=row, column=2, padx=5)
        row += 1
        
        # Vocab file
        ttk.Label(control_frame, text="Vocab File (.jsonld):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.vocab_label = ttk.Label(control_frame, text="No file selected", foreground="gray")
        self.vocab_label.grid(row=row, column=1, sticky=tk.W, padx=10)
        ttk.Button(control_frame, text="Browse...", command=self.select_vocab).grid(row=row, column=2, padx=5)
        row += 1
        
        # Attributes file
        ttk.Label(control_frame, text="Attributes File (.yaml):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.attributes_label = ttk.Label(control_frame, text="No file selected", foreground="gray")
        self.attributes_label.grid(row=row, column=1, sticky=tk.W, padx=10)
        ttk.Button(control_frame, text="Browse...", command=self.select_attributes).grid(row=row, column=2, padx=5)
        row += 1
        
        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Transformer mode selection
        ttk.Label(control_frame, text="Transformation Mode:").grid(row=row, column=0, sticky=tk.W, pady=5)
        mode_frame = ttk.Frame(control_frame)
        mode_frame.grid(row=row, column=1, columnspan=2, sticky=tk.W, padx=10)
        ttk.Radiobutton(mode_frame, text="Semantic (DCT + @container)", 
                       variable=self.transformer_mode, value="semantic").pack(side=tk.LEFT, padx=5)
        ttk.Radiobutton(mode_frame, text="Hybrid (IRI + Structural Rules)", 
                       variable=self.transformer_mode, value="hybrid").pack(side=tk.LEFT, padx=5)
        row += 1
        
        # Structural rules file (for hybrid mode)
        ttk.Label(control_frame, text="Structural Rules (hybrid):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.structural_rules_label = ttk.Label(control_frame, text="No file selected", foreground="gray")
        self.structural_rules_label.grid(row=row, column=1, sticky=tk.W, padx=10)
        ttk.Button(control_frame, text="Browse...", command=self.select_structural_rules).grid(row=row, column=2, padx=5)
        row += 1
        
        # SHACL shapes file (for semantic mode)
        ttk.Label(control_frame, text="SHACL Shapes (semantic):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.shacl_label = ttk.Label(control_frame, text="No file selected", foreground="gray")
        self.shacl_label.grid(row=row, column=1, sticky=tk.W, padx=10)
        ttk.Button(control_frame, text="Browse...", command=self.select_shacl).grid(row=row, column=2, padx=5)
        row += 1
        
        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Expected output file (optional)
        ttk.Label(control_frame, text="Expected Output (optional):").grid(row=row, column=0, sticky=tk.W, pady=5)
        self.expected_label = ttk.Label(control_frame, text="No file selected", foreground="gray")
        self.expected_label.grid(row=row, column=1, sticky=tk.W, padx=10)
        ttk.Button(control_frame, text="Browse...", command=self.select_expected).grid(row=row, column=2, padx=5)
        row += 1
        
        # Separator
        ttk.Separator(control_frame, orient='horizontal').grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=10)
        row += 1
        
        # Options frame
        options_frame = ttk.Frame(control_frame)
        options_frame.grid(row=row, column=0, columnspan=3, sticky=tk.W, pady=5)
        
        # Strip prefixes checkbox
        ttk.Checkbutton(options_frame, text="Strip beckn: and schema: prefixes", 
                       variable=self.strip_prefixes_var).pack(side=tk.LEFT, padx=10)
        
        # Output version (when not using custom files)
        ttk.Label(options_frame, text="Output Version:").pack(side=tk.LEFT, padx=(20, 5))
        self.version_entry = ttk.Entry(options_frame, width=10)
        self.version_entry.insert(0, "2.1")
        self.version_entry.pack(side=tk.LEFT)
        
        row += 1
        
        # Buttons frame
        btn_frame = ttk.Frame(control_frame)
        btn_frame.grid(row=row, column=0, columnspan=3, pady=10)
        
        # Transform button
        self.transform_btn = ttk.Button(btn_frame, text="🔄 Transform", 
                                       command=self.transform, style="Accent.TButton")
        self.transform_btn.pack(side=tk.LEFT, padx=5)
        
        # View Report button (initially hidden)
        self.view_report_btn = ttk.Button(btn_frame, text="📊 View Diff Report", 
                                         command=self.view_report)
        
        # Clear button
        ttk.Button(btn_frame, text="Clear All", command=self.clear_all).pack(side=tk.LEFT, padx=5)
        
    def create_json_viewer(self, parent):
        """Create dual-pane JSON viewer"""
        viewer_frame = ttk.Frame(parent)
        viewer_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        viewer_frame.columnconfigure(0, weight=1)
        viewer_frame.columnconfigure(1, weight=1)
        viewer_frame.rowconfigure(0, weight=1)
        
        # Input JSON pane
        input_frame = ttk.LabelFrame(viewer_frame, text="Input JSON", padding="5")
        input_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 5))
        input_frame.columnconfigure(0, weight=1)
        input_frame.rowconfigure(0, weight=1)
        
        self.input_text = scrolledtext.ScrolledText(input_frame, wrap=tk.WORD, 
                                                    font=("Courier New", 10))
        self.input_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Output JSON pane
        output_frame = ttk.LabelFrame(viewer_frame, text="Output JSON", padding="5")
        output_frame.grid(row=0, column=1, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(5, 0))
        output_frame.columnconfigure(0, weight=1)
        output_frame.rowconfigure(0, weight=1)
        
        self.output_text = scrolledtext.ScrolledText(output_frame, wrap=tk.WORD, 
                                                     font=("Courier New", 10))
        self.output_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Copy and save buttons for output
        btn_frame = ttk.Frame(output_frame)
        btn_frame.grid(row=1, column=0, sticky=tk.E, pady=(5, 0))
        ttk.Button(btn_frame, text="Copy", command=self.copy_output).pack(side=tk.LEFT, padx=2)
        ttk.Button(btn_frame, text="Save...", command=self.save_output).pack(side=tk.LEFT, padx=2)
        
    def create_status_bar(self, parent):
        """Create status bar"""
        self.status_var = tk.StringVar(value="Ready")
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(10, 0))
        
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, 
                                      relief=tk.SUNKEN, anchor=tk.W)
        self.status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Progress bar
        self.progress = ttk.Progressbar(status_frame, mode='indeterminate', length=100)
        self.progress.pack(side=tk.RIGHT, padx=5)
        
    def select_input_json(self):
        """Select input JSON file"""
        filename = filedialog.askopenfilename(
            title="Select Input JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.input_json_path = filename
            self.input_label.config(text=Path(filename).name, foreground="black")
            self.load_input_json()
            
    def select_context(self):
        """Select context.jsonld file"""
        filename = filedialog.askopenfilename(
            title="Select Context File",
            filetypes=[("JSON-LD files", "*.jsonld"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.context_path = filename
            self.context_label.config(text=Path(filename).name, foreground="black")
            
    def select_vocab(self):
        """Select vocab.jsonld file"""
        filename = filedialog.askopenfilename(
            title="Select Vocab File",
            filetypes=[("JSON-LD files", "*.jsonld"), ("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.vocab_path = filename
            self.vocab_label.config(text=Path(filename).name, foreground="black")
            
    def select_attributes(self):
        """Select attributes.yaml file"""
        filename = filedialog.askopenfilename(
            title="Select Attributes File",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
        if filename:
            self.attributes_path = filename
            self.attributes_label.config(text=Path(filename).name, foreground="black")
    
    def select_structural_rules(self):
        """Select structural rules YAML file"""
        filename = filedialog.askopenfilename(
            title="Select Structural Rules File",
            filetypes=[("YAML files", "*.yaml *.yml"), ("All files", "*.*")]
        )
        if filename:
            self.structural_rules_path = filename
            self.structural_rules_label.config(text=Path(filename).name, foreground="black")
    
    def select_shacl(self):
        """Select SHACL shapes file"""
        filename = filedialog.askopenfilename(
            title="Select SHACL Shapes File",
            filetypes=[("Turtle files", "*.ttl"), ("JSON-LD files", "*.jsonld"), ("All files", "*.*")]
        )
        if filename:
            self.shacl_shapes_path = filename
            self.shacl_label.config(text=Path(filename).name, foreground="black")
    
    def select_expected(self):
        """Select expected output JSON file"""
        filename = filedialog.askopenfilename(
            title="Select Expected Output JSON",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.expected_output_path = filename
            self.expected_label.config(text=Path(filename).name, foreground="black")
            
    def load_input_json(self):
        """Load and display input JSON"""
        if not self.input_json_path:
            return
            
        try:
            with open(self.input_json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                formatted = json.dumps(data, indent=2, ensure_ascii=False)
                self.input_text.delete('1.0', tk.END)
                self.input_text.insert('1.0', formatted)
                self.status_var.set(f"Loaded: {Path(self.input_json_path).name}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load JSON:\n{str(e)}")
            self.status_var.set("Error loading file")
            
    def transform(self):
        """Perform the transformation"""
        # Validate inputs
        if not self.input_json_path:
            messagebox.showwarning("Missing Input", "Please select an input JSON file")
            return
            
        using_custom_files = self.context_path or self.vocab_path or self.attributes_path
        
        if using_custom_files:
            if not (self.context_path and self.vocab_path and self.attributes_path):
                messagebox.showwarning("Missing Files", 
                    "When using custom files, all three must be provided:\n"
                    "- Context file\n- Vocab file\n- Attributes file")
                return
        else:
            self.output_version = self.version_entry.get()
            if not self.output_version:
                messagebox.showwarning("Missing Version", "Please specify output version")
                return
        
        # Start transformation
        self.status_var.set("Transforming...")
        self.progress.start()
        self.transform_btn.config(state='disabled')
        
        # Use after() to prevent UI freezing
        self.root.after(100, self._do_transform)
        
    def _do_transform(self):
        """Actually perform the transformation"""
        try:
            # Load input JSON
            with open(self.input_json_path, 'r', encoding='utf-8') as f:
                input_data = json.load(f)
            
            mode = self.transformer_mode.get()
            
            # Initialize transformer based on mode
            if mode == "semantic":
                # Semantic transformer
                if self.context_path and self.vocab_path and self.attributes_path:
                    transformer = SemanticTransformer(
                        output_version="custom",
                        context_file=self.context_path,
                        vocab_file=self.vocab_path,
                        attributes_file=self.attributes_path,
                        shacl_shapes_file=self.shacl_shapes_path
                    )
                else:
                    transformer = SemanticTransformer(
                        output_version=self.output_version,
                        shacl_shapes_file=self.shacl_shapes_path
                    )
                
                # Transform with semantic transformer
                transformed, warnings, stats = transformer.transform(input_data)
                
            else:  # hybrid mode
                # Hybrid transformer (IRI + structural rules)
                if self.context_path and self.vocab_path and self.attributes_path:
                    transformer = IRITransformer(
                        output_version="custom",
                        context_file=self.context_path,
                        vocab_file=self.vocab_path,
                        attributes_file=self.attributes_path,
                        structural_rules_file=self.structural_rules_path
                    )
                else:
                    transformer = IRITransformer(
                        output_version=self.output_version,
                        structural_rules_file=self.structural_rules_path
                    )
                
                # Transform with hybrid transformer
                transformed, warnings, stats, applied_rules = transformer.transform_and_validate(input_data)
                
                # Add applied rules info
                if applied_rules:
                    stats["applied_structural_rules"] = applied_rules
            
            # Remove metadata
            transformed.pop("_transformation_warnings", None)
            transformed.pop("_transformation_stats", None)
            
            # Strip prefixes if requested
            if self.strip_prefixes_var.get():
                transformed = strip_prefixes(transformed)
            
            # Display output
            formatted = json.dumps(transformed, indent=2, ensure_ascii=False)
            self.output_text.delete('1.0', tk.END)
            self.output_text.insert('1.0', formatted)
            
            # Show statistics
            status_msg = f"✓ Transformation complete"
            if warnings:
                status_msg += f" ({len(warnings)} warnings)"
            self.status_var.set(status_msg)
            
            # Compare with expected output if provided
            if self.expected_output_path:
                try:
                    with open(self.expected_output_path, 'r', encoding='utf-8') as f:
                        expected_data = json.load(f)
                    
                    # Compare
                    if self.compare_json(transformed, expected_data):
                        self.status_var.set("✓ Transformation complete - Output matches expected!")
                        self.view_report_btn.pack_forget()  # Hide report button
                    else:
                        # Generate diff report
                        report_path = self.generate_diff_report(transformed, expected_data)
                        self.last_report_path = report_path
                        self.status_var.set("⚠ Output differs from expected - View report for details")
                        self.view_report_btn.pack(side=tk.LEFT, padx=5)  # Show report button
                        messagebox.showwarning("Difference Detected", 
                            "The transformed output differs from the expected output.\n"
                            "Click 'View Diff Report' to see the differences.")
                except Exception as e:
                    messagebox.showerror("Comparison Error", f"Failed to compare with expected output:\n{str(e)}")
            else:
                # Show warnings if any
                if warnings:
                    warning_msg = "\n".join(warnings[:10])  # Show first 10
                    if len(warnings) > 10:
                        warning_msg += f"\n... and {len(warnings) - 10} more"
                    messagebox.showinfo("Transformation Warnings", warning_msg)
            
        except Exception as e:
            messagebox.showerror("Transformation Error", f"Failed to transform:\n{str(e)}")
            self.status_var.set("Transformation failed")
        finally:
            self.progress.stop()
            self.transform_btn.config(state='normal')
    
    def compare_json(self, obj1, obj2):
        """Deep comparison of two JSON objects"""
        return json.dumps(obj1, sort_keys=True) == json.dumps(obj2, sort_keys=True)
    
    def generate_diff_report(self, actual, expected):
        """Generate HTML diff report"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = Path(tempfile.gettempdir()) / f"beckn_diff_report_{timestamp}.html"
        
        # Generate differences
        diffs = self.find_differences(expected, actual, "")
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Beckn Transformation Diff Report</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background-color: #f5f5f5;
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        }}
        h1 {{
            color: #333;
            border-bottom: 3px solid #4CAF50;
            padding-bottom: 10px;
        }}
        .summary {{
            background: #e3f2fd;
            padding: 15px;
            border-radius: 5px;
            margin: 20px 0;
        }}
        .summary h2 {{
            margin-top: 0;
            color: #1976d2;
        }}
        .diff-container {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 20px;
            margin-top: 20px;
        }}
        .json-pane {{
            border: 1px solid #ddd;
            border-radius: 5px;
            overflow: hidden;
        }}
        .json-pane h3 {{
            background: #f5f5f5;
            margin: 0;
            padding: 10px;
            border-bottom: 2px solid #ddd;
        }}
        .json-pane pre {{
            margin: 0;
            padding: 15px;
            overflow-x: auto;
            background: #fafafa;
            max-height: 600px;
            overflow-y: auto;
        }}
        .differences {{
            margin-top: 30px;
        }}
        .diff-item {{
            background: #fff3cd;
            border-left: 4px solid #ffc107;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
        }}
        .diff-item .path {{
            font-weight: bold;
            color: #856404;
            font-family: monospace;
        }}
        .diff-item .values {{
            margin-top: 10px;
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 10px;
        }}
        .expected, .actual {{
            padding: 10px;
            border-radius: 4px;
            font-family: monospace;
            font-size: 0.9em;
        }}
        .expected {{
            background: #ffebee;
            border-left: 3px solid #f44336;
        }}
        .actual {{
            background: #e8f5e9;
            border-left: 3px solid #4caf50;
        }}
        .label {{
            font-weight: bold;
            margin-bottom: 5px;
        }}
        .timestamp {{
            color: #666;
            font-size: 0.9em;
            margin-top: 20px;
        }}
        .no-diff {{
            background: #d4edda;
            border-left: 4px solid #28a745;
            padding: 15px;
            margin: 10px 0;
            border-radius: 4px;
            color: #155724;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🔍 Beckn Transformation Diff Report</h1>
        
        <div class="summary">
            <h2>Summary</h2>
            <p><strong>Total Differences Found:</strong> {len(diffs)}</p>
            <p><strong>Generated:</strong> {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
        </div>
        
        <div class="diff-container">
            <div class="json-pane">
                <h3>Expected Output</h3>
                <pre>{json.dumps(expected, indent=2, ensure_ascii=False)}</pre>
            </div>
            <div class="json-pane">
                <h3>Actual Output</h3>
                <pre>{json.dumps(actual, indent=2, ensure_ascii=False)}</pre>
            </div>
        </div>
        
        <div class="differences">
            <h2>Differences</h2>
            {"".join([f'''
            <div class="diff-item">
                <div class="path">Path: {diff["path"]}</div>
                <div class="values">
                    <div class="expected">
                        <div class="label">Expected:</div>
                        <div>{json.dumps(diff["expected"], indent=2, ensure_ascii=False) if diff["expected"] != "[MISSING]" else "[MISSING]"}</div>
                    </div>
                    <div class="actual">
                        <div class="label">Actual:</div>
                        <div>{json.dumps(diff["actual"], indent=2, ensure_ascii=False) if diff["actual"] != "[MISSING]" else "[MISSING]"}</div>
                    </div>
                </div>
            </div>
            ''' for diff in diffs]) if diffs else '<div class="no-diff">✓ No differences found! Output matches expected.</div>'}
        </div>
        
        <div class="timestamp">
            Report generated on {datetime.now().strftime("%Y-%m-%d at %H:%M:%S")}
        </div>
    </div>
</body>
</html>
"""
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return str(report_path)
    
    def find_differences(self, expected, actual, path="root"):
        """Recursively find differences between two JSON objects"""
        diffs = []
        
        if type(expected) != type(actual):
            diffs.append({
                "path": path,
                "expected": expected,
                "actual": actual
            })
            return diffs
        
        if isinstance(expected, dict):
            all_keys = set(expected.keys()) | set(actual.keys())
            for key in all_keys:
                new_path = f"{path}.{key}" if path else key
                if key not in expected:
                    diffs.append({
                        "path": new_path,
                        "expected": "[MISSING]",
                        "actual": actual[key]
                    })
                elif key not in actual:
                    diffs.append({
                        "path": new_path,
                        "expected": expected[key],
                        "actual": "[MISSING]"
                    })
                else:
                    diffs.extend(self.find_differences(expected[key], actual[key], new_path))
        
        elif isinstance(expected, list):
            if len(expected) != len(actual):
                diffs.append({
                    "path": f"{path}[length]",
                    "expected": f"length={len(expected)}",
                    "actual": f"length={len(actual)}"
                })
            for i in range(min(len(expected), len(actual))):
                new_path = f"{path}[{i}]"
                diffs.extend(self.find_differences(expected[i], actual[i], new_path))
        
        else:
            if expected != actual:
                diffs.append({
                    "path": path,
                    "expected": expected,
                    "actual": actual
                })
        
        return diffs
    
    def view_report(self):
        """Open the diff report in browser"""
        if self.last_report_path and Path(self.last_report_path).exists():
            webbrowser.open('file://' + self.last_report_path)
            self.status_var.set("Opening diff report in browser...")
        else:
            messagebox.showinfo("No Report", "No diff report available")
            
    def copy_output(self):
        """Copy output to clipboard"""
        output = self.output_text.get('1.0', tk.END)
        if output.strip():
            self.root.clipboard_clear()
            self.root.clipboard_append(output)
            self.status_var.set("Output copied to clipboard")
        else:
            messagebox.showinfo("No Output", "No output to copy")
            
    def save_output(self):
        """Save output to file"""
        output = self.output_text.get('1.0', tk.END).strip()
        if not output:
            messagebox.showinfo("No Output", "No output to save")
            return
            
        filename = filedialog.asksaveasfilename(
            title="Save Output JSON",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(output)
                self.status_var.set(f"Saved: {Path(filename).name}")
                messagebox.showinfo("Success", f"Output saved to:\n{filename}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file:\n{str(e)}")
                
    def clear_all(self):
        """Clear all inputs and outputs"""
        self.input_json_path = None
        self.context_path = None
        self.vocab_path = None
        self.attributes_path = None
        self.structural_rules_path = None
        self.shacl_shapes_path = None
        self.expected_output_path = None
        self.last_report_path = None
        
        self.input_label.config(text="No file selected", foreground="gray")
        self.context_label.config(text="No file selected", foreground="gray")
        self.vocab_label.config(text="No file selected", foreground="gray")
        self.attributes_label.config(text="No file selected", foreground="gray")
        self.structural_rules_label.config(text="No file selected", foreground="gray")
        self.shacl_label.config(text="No file selected", foreground="gray")
        self.expected_label.config(text="No file selected", foreground="gray")
        
        self.input_text.delete('1.0', tk.END)
        self.output_text.delete('1.0', tk.END)
        
        self.view_report_btn.pack_forget()  # Hide report button
        
        self.status_var.set("Ready")


def main():
    """Main entry point"""
    root = tk.Tk()
    
    # Set theme
    style = ttk.Style()
    try:
        style.theme_use('clam')  # Modern look
    except:
        pass
    
    # Create and run app
    app = TransformerGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
