import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys

# =================================================================
# IMPORTS & BACKEND LOADING
# =================================================================
try:
    from lexer import Lexer
    from parser import parse_lolcode
    from semantic import analyze_lolcode
    from execute import execute_lolcode
except ImportError:
    pass 

# --- CLASS TO REDIRECT PRINT() TO GUI CONSOLE ---
class IORedirector(object):
    """Redirects print() statements to the GUI console."""
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert('end', string)
        self.text_space.see('end') 
    
    def flush(self):
        pass

class LOLGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LOLCODE INTERPRETER")
        self.geometry("1350x850") # Wide enough for 3 columns
        
        # --- MODERN COLOR PALETTE ---
        self.colors = {
            "bg_main":     "#f0f2f5",    # Light Grey (App Background)
            "bg_header":   "#1e2b37",    # Dark Blue-Grey (Header)  #2c3e50
            "accent":      "#3498db",    # Bright Blue (Primary Actions)
            "accent_hov":  "#2980b9",    # Darker Blue (Hover)
            "success":     "#27ae60",    # Green (Execute)
            "success_hov": "#219150",    # Darker Green
            "danger":      "#e74c3c",    # Red (Clear/Error)
            "text_dark":   "#2c3e50",    # Dark Text
            "terminal_bg": "#1e1e1e",    # Dark Terminal Background
            "terminal_fg": "#00ff00",    # Terminal Text (Matrix Green)
            "panel_bg":    "#ffffff",    # Panels Background
        }
        
        self.configure(bg=self.colors["bg_main"])
        self.current_file = None
        
        self.setup_styles()
        self.create_widgets()

    def setup_styles(self):
        style = ttk.Style()
        # 'clam' is essential for changing background colors on buttons/progress bars
        style.theme_use('clam') 

        # -- General --
        style.configure("TFrame", background=self.colors["bg_main"])
        style.configure("Card.TFrame", background="white", relief="solid", borderwidth=1)
        
        # -- Buttons --
        style.configure("Primary.TButton", background=self.colors["accent"], foreground="white", borderwidth=0, font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Primary.TButton", background=[('active', self.colors["accent_hov"])])

        style.configure("Success.TButton", background=self.colors["success"], foreground="white", borderwidth=0, font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Success.TButton", background=[('active', self.colors["success_hov"])])

        style.configure("Danger.TButton", background=self.colors["danger"], foreground="white", borderwidth=0, font=("Segoe UI", 10, "bold"), padding=6)
        style.map("Danger.TButton", background=[('active', "#c0392b")])

        # -- Treeview (Tables) --
        # We set rowheight and colors to look like a modern data grid
        style.configure("Treeview", 
                        background="white",
                        foreground=self.colors["text_dark"],
                        rowheight=25,
                        fieldbackground="white",
                        font=("Segoe UI", 10))
        
        style.configure("Treeview.Heading", 
                        background="#dfe6e9", 
                        foreground=self.colors["text_dark"], 
                        font=("Segoe UI", 10, "bold"))
        
        style.map("Treeview", background=[('selected', self.colors["accent"])])

        # -- Labels --
        style.configure("Section.TLabel", font=("Segoe UI", 11, "bold"), background=self.colors["bg_main"], foreground="#555")

    def create_widgets(self):
        # ================== HEADER ==================
        header_frame = tk.Frame(self, bg=self.colors["bg_header"], height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False) 
        
        tk.Label(header_frame, text="LOLCODE INTERPRETER", font=("Segoe UI", 18, "bold"), 
                 bg=self.colors["bg_header"], fg="white").place(relx=0.5, rely=0.5, anchor=tk.CENTER)

        # ================== TOOLBAR ==================
        toolbar = tk.Frame(self, bg="white", height=50, bd=1, relief="solid")
        toolbar.pack(fill=tk.X, side=tk.TOP)
        toolbar.pack_propagate(False)

        ttk.Button(toolbar, text="Upload File", style="Primary.TButton", command=self.open_file).pack(side=tk.LEFT, padx=(20, 10), pady=8)
        ttk.Button(toolbar, text="Analyze", style="Success.TButton", command=self.run_execution).pack(side=tk.LEFT, padx=10, pady=8)
        ttk.Button(toolbar, text="Clear All", style="Danger.TButton", command=self.clear_all).pack(side=tk.RIGHT, padx=20, pady=8)

        # ================== MAIN CONTENT PANE ==================
        # Split into Left (Code), Middle (Lexemes), Right (Tables)
        main_pane = tk.PanedWindow(self, orient=tk.HORIZONTAL, bg=self.colors["bg_main"], sashwidth=4, sashrelief="flat")
        main_pane.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ----------------- LEFT PANEL: Source Code -----------------
        left_frame = tk.Frame(main_pane, bg=self.colors["bg_main"])
        main_pane.add(left_frame, minsize=350, stretch="always")

        ttk.Label(left_frame, text="Source Code", style="Section.TLabel").pack(anchor="w", pady=(0, 5))
        
        editor_container = tk.Frame(left_frame, bd=1, relief="solid", bg="#bdc3c7")
        editor_container.pack(fill=tk.BOTH, expand=True)

        self.line_numbers = tk.Text(editor_container, width=4, padx=5, takefocus=0, border=0,
                                    background="#ecf0f1", foreground="#7f8c8d", state="disabled", font=("Consolas", 11))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.source_text = tk.Text(editor_container, wrap=tk.NONE, font=("Consolas", 11),
                                   bg="white", fg="#2c3e50", bd=0, undo=True)
        self.source_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.yscroll = ttk.Scrollbar(editor_container, orient="vertical", command=self.sync_scroll)
        self.yscroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.source_text.config(yscrollcommand=self.on_text_scroll)
        self.source_text.bind("<KeyRelease>", self.update_line_numbers)
        self.update_line_numbers()

        # ----------------- MIDDLE PANEL: Lexemes -----------------
        mid_frame = tk.Frame(main_pane, bg=self.colors["bg_main"])
        main_pane.add(mid_frame, minsize=250)

        ttk.Label(mid_frame, text="Lexemes", style="Section.TLabel").pack(anchor="w", pady=(0, 5))

        lex_container = tk.Frame(mid_frame, bd=1, relief="solid", bg="#bdc3c7")
        lex_container.pack(fill=tk.BOTH, expand=True)

        self.lexeme_table = ttk.Treeview(lex_container, columns=("Classification", "Lexeme"), show="headings")
        self.lexeme_table.heading("Classification", text="Classification")
        self.lexeme_table.heading("Lexeme", text="Lexeme")
        self.lexeme_table.column("Classification", width=120)
        self.lexeme_table.column("Lexeme", width=120)
        
        lex_scroll = ttk.Scrollbar(lex_container, orient="vertical", command=self.lexeme_table.yview)
        self.lexeme_table.configure(yscrollcommand=lex_scroll.set)
        
        self.lexeme_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lex_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # ----------------- RIGHT PANEL: Tables (Stacked) -----------------
        right_frame = tk.Frame(main_pane, bg=self.colors["bg_main"])
        main_pane.add(right_frame, minsize=350)

        # We use a vertical PanedWindow inside the right column to stack the tables
        right_pane = tk.PanedWindow(right_frame, orient=tk.VERTICAL, bg=self.colors["bg_main"], sashwidth=4)
        right_pane.pack(fill=tk.BOTH, expand=True)

        # 1. Symbol Table (Top)
        sym_frame = tk.Frame(right_pane, bg=self.colors["bg_main"])
        right_pane.add(sym_frame, stretch="always")
        
        ttk.Label(sym_frame, text="Variable Symbol Table", style="Section.TLabel").pack(anchor="w", pady=(0, 5))
        
        # NOTE: 3 Columns: Variable, Value, Type
        self.symbol_table = ttk.Treeview(sym_frame, columns=("Identifier", "Value", "Type"), show="headings")
        self.symbol_table.heading("Identifier", text="Variable")
        self.symbol_table.heading("Value", text="Value")
        self.symbol_table.heading("Type", text="Type")
        self.symbol_table.column("Identifier", width=100)
        self.symbol_table.column("Value", width=100)
        self.symbol_table.column("Type", width=80)
        self.symbol_table.pack(fill=tk.BOTH, expand=True)

        # 2. Function Table (Bottom)
        func_frame = tk.Frame(right_pane, bg=self.colors["bg_main"])
        right_pane.add(func_frame, stretch="always")

        ttk.Label(func_frame, text="Function Table", style="Section.TLabel").pack(anchor="w", pady=(10, 5))

        self.function_table = ttk.Treeview(func_frame, columns=("Function", "Params"), show="headings")
        self.function_table.heading("Function", text="Function Name")
        self.function_table.heading("Params", text="Parameters")
        self.function_table.pack(fill=tk.BOTH, expand=True)

        # ================== CONSOLE (Bottom) ==================
        console_frame = tk.Frame(self, bg=self.colors["bg_main"], height=150)
        console_frame.pack(fill=tk.X, side=tk.BOTTOM, padx=10, pady=(0, 10))
        
        ttk.Label(console_frame, text="Terminal Output", style="Section.TLabel").pack(anchor="w", pady=(5, 2))
        
        self.console = tk.Text(console_frame, height=8, font=("Consolas", 10),
                               bg=self.colors["terminal_bg"], 
                               fg=self.colors["terminal_fg"], 
                               insertbackground="white", relief="flat", padx=10, pady=10)
        self.console.pack(fill=tk.BOTH, expand=True)

    # ---------- Scrolling Logic ----------
    def sync_scroll(self, *args):
        self.source_text.yview(*args)
        self.line_numbers.yview(*args)

    def on_text_scroll(self, *args):
        self.yscroll.set(*args)
        self.line_numbers.yview_moveto(args[0])

    def update_line_numbers(self, event=None):
        line_count = int(self.source_text.index('end-1c').split('.')[0])
        lines = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", lines)
        self.line_numbers.config(state="disabled")
        self.line_numbers.yview_moveto(self.source_text.yview()[0])

    # ---------- File Operations ----------
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("LOLCODE files", "*.lol"), ("All Files", "*.*")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        self.source_text.delete("1.0", tk.END)
        self.source_text.insert("1.0", code)
        self.current_file = path
        self.console.insert(tk.END, f"[System] Opened: {os.path.basename(path)}\n")
        self.update_line_numbers()

    # ---------- Main Logic (Robust) ----------
    def run_execution(self):
        # 1. Imports Check
        try:
            from lexer import Lexer
            from parser import parse_lolcode
            from semantic import analyze_lolcode
            from execute import execute_lolcode
        except ImportError:
            messagebox.showerror("Error", "Required modules (lexer, parser, semantic, execute) not found.")
            return

        code = self.source_text.get("1.0", tk.END)
        self.console.delete("1.0", tk.END)
        
        # 2. Tokenization
        try:
            lexer = Lexer()
            tokens = lexer.tokenize(code)
            
            # Clear and Populate Lexeme Table
            self.lexeme_table.delete(*self.lexeme_table.get_children())
            for desc, token, _, _ in tokens:
                self.lexeme_table.insert("", tk.END, values=(desc, token))

        except Exception as e:
            messagebox.showerror("Lexer Error", str(e))
            return

        # 3. Parsing
        try:
            # Safely handle 3 or 4 return values from parser
            parse_result = parse_lolcode(tokens)
            
            if len(parse_result) == 4:
                success, parser_obj, symbol_table, function_dict = parse_result
            else:
                success, parser_obj, symbol_table = parse_result
                function_dict = {}

            # Populate Initial UI State
            self.update_tables(symbol_table, function_dict)
            
            if not success:
                self.console.insert(tk.END, "[!] Parsing Failed. Errors:\n")
                if hasattr(parser_obj, 'errors'):
                    for err in parser_obj.errors:
                        self.console.insert(tk.END, f"{err}\n")
                return

        except Exception as e:
            self.console.insert(tk.END, f"[!] Parser Error: {e}\n")
            return

        # 4. Semantic Analysis & Execution
        # Redirect stdout to GUI console for the duration of execution
        old_stdout = sys.stdout 
        sys.stdout = IORedirector(self.console)

        try:
            print("\n--- SEMANTIC ANALYSIS ---")
            sem_success, sem_errors = analyze_lolcode(tokens, symbol_table, function_dict)
            
            if sem_success:
                print("\n--- EXECUTION OUTPUT ---")
                
                # Run Execution
                result = execute_lolcode(tokens, symbol_table, function_dict)
                
                # Check execution result format (Tuple vs False)
                if isinstance(result, tuple) and len(result) == 2:
                    final_vars, final_funcs = result
                    self.update_tables(final_vars, final_funcs)
                    print("\n[Execution Complete]")
                elif isinstance(result, tuple) and result[0] is False:
                     # result[1] are errors
                     print("\n[Execution Halted due to Errors]")
                else:
                    print("\n[Execution Finished]")
            
            else:
                print("\n[Semantic Analysis Failed]")
                for err in sem_errors:
                    print(f"Error: {err}")

        except Exception as e:
            print(f"\n[CRITICAL RUNTIME ERROR]: {e}")
            import traceback
            traceback.print_exc()
        finally:
            # Restore standard output
            sys.stdout = old_stdout
            self.console.insert(tk.END, "\n[Process Terminated]\n")

    def update_tables(self, var_data, func_data):
        """
        Populate the modern Treeview tables.
        This uses the robust logic you asked to keep.
        """
        # Clear tables
        self.symbol_table.delete(*self.symbol_table.get_children())
        self.function_table.delete(*self.function_table.get_children())

        # --- Variables ---
        if var_data:
            for var_name, data in var_data.items():
                val = "NOOB"
                var_type = "Untyped"

                # Robustly handle different tuple structures from Parser/Executor
                if isinstance(data, (tuple, list)):
                    # Check for size 4 tuple: (Value, ParserType, Line, ExecType)
                    if len(data) >= 4:
                        val = data[0]
                        # Prefer ExecType (idx 3), fallback to ParserType (idx 1)
                        var_type = data[3] if data[3] is not None else (data[1] if data[1] else "Untyped")
                    # Check for size 2 tuple: (Value, Type)
                    elif len(data) == 2:
                        val = data[0]
                        var_type = data[1]
                    # Check for size 1 tuple: (Value,)
                    elif len(data) == 1:
                        val = data[0]
                else:
                    # Just the value
                    val = data

                self.symbol_table.insert("", tk.END, values=(var_name, val, var_type))

        # --- Functions ---
        if func_data:
            for func_name, params in func_data.items():
                param_str = ""
                if isinstance(params, list):
                    # Convert list of params to readable string: "x (NUMBR), y (YARN)"
                    p_list = []
                    for p in params:
                        if isinstance(p, (tuple, list)) and len(p) >= 1:
                            p_name = p[0]
                            p_type = p[1] if len(p) > 1 else "NOOB"
                            p_list.append(f"{p_name} ({p_type})")
                    param_str = ", ".join(p_list)
                
                self.function_table.insert("", tk.END, values=(func_name, param_str))

    def clear_all(self):
        self.source_text.delete("1.0", tk.END)
        self.update_line_numbers()
        self.lexeme_table.delete(*self.lexeme_table.get_children())
        self.symbol_table.delete(*self.symbol_table.get_children())
        self.function_table.delete(*self.function_table.get_children())
        self.console.delete("1.0", tk.END)
        self.console.insert(tk.END, "> Workspace cleared.\n")

def start_gui():
    app = LOLGui()
    app.mainloop()

if __name__ == "__main__":
    start_gui()