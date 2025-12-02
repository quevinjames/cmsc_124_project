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
        self.title("CAUSE GROUP CMSC 124")
        self.geometry("1350x850") 
        
        # --- MODERN COLOR PALETTE ---
        self.colors = {
            "bg_main":     "#f0f2f5",    # Light Grey (App Background)
            "bg_header":   "#1e2b37",    # Dark Blue-Grey (Header)
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

        # ================== MAIN SPLIT (Vertical PanedWindow) ==================
        # This splits the window into TOP (Editors/Tables) and BOTTOM (Terminal)
        # Allows dragging up/down to resize terminal
        self.main_split = tk.PanedWindow(self, orient=tk.VERTICAL, bg=self.colors["bg_main"], sashwidth=6, sashrelief="flat")
        self.main_split.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ================== TOP SECTION (Horizontal PanedWindow) ==================
        # This splits Source Code | Lexemes | Tables
        self.editor_pane = tk.PanedWindow(self.main_split, orient=tk.HORIZONTAL, bg=self.colors["bg_main"], sashwidth=4, sashrelief="flat")
        
        # Add the editor pane to the top of main split
        self.main_split.add(self.editor_pane, height=550, stretch="always")

        # ----------------- LEFT PANEL: Source Code -----------------
        left_frame = tk.Frame(self.editor_pane, bg=self.colors["bg_main"])
        self.editor_pane.add(left_frame, minsize=350, stretch="always")

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
        mid_frame = tk.Frame(self.editor_pane, bg=self.colors["bg_main"])
        self.editor_pane.add(mid_frame, minsize=250)

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
        right_frame = tk.Frame(self.editor_pane, bg=self.colors["bg_main"])
        self.editor_pane.add(right_frame, minsize=350)

        # Vertical PanedWindow to stack Symbol Table (Top) and Function Table (Bottom)
        right_pane = tk.PanedWindow(right_frame, orient=tk.VERTICAL, bg=self.colors["bg_main"], sashwidth=4)
        right_pane.pack(fill=tk.BOTH, expand=True)

        # 1. Symbol Table (Top)
        sym_frame = tk.Frame(right_pane, bg=self.colors["bg_main"])
        right_pane.add(sym_frame, stretch="always")
        
        ttk.Label(sym_frame, text="Symbol Table", style="Section.TLabel").pack(anchor="w", pady=(0, 5))
        
        self.symbol_table = ttk.Treeview(sym_frame, columns=("Identifier", "Value"), show="headings")
        self.symbol_table.heading("Identifier", text="Identifier")
        self.symbol_table.heading("Value", text="Value")
        self.symbol_table.column("Identifier", width=150)
        self.symbol_table.column("Value", width=150)
        self.symbol_table.pack(fill=tk.BOTH, expand=True)

        # 2. Function Table (Bottom)
        func_frame = tk.Frame(right_pane, bg=self.colors["bg_main"])
        right_pane.add(func_frame, stretch="always")

        ttk.Label(func_frame, text="Function Table", style="Section.TLabel").pack(anchor="w", pady=(10, 5))

        self.function_table = ttk.Treeview(func_frame, columns=("Function", "Variable", "Value"), show="headings")
        self.function_table.heading("Function", text="Function Name")
        self.function_table.heading("Variable", text="Variable Name")
        self.function_table.heading("Value", text="Value")
        self.function_table.column("Function", width=100)
        self.function_table.column("Variable", width=100)
        self.function_table.column("Value", width=100)
        self.function_table.pack(fill=tk.BOTH, expand=True)

        # ================== CONSOLE PANE (Bottom) ==================
        console_frame = tk.Frame(self.main_split, bg=self.colors["bg_main"])
        
        # Add console frame to the bottom of main split
        self.main_split.add(console_frame, minsize=150)
        
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
        line_content = "\n".join(str(i) for i in range(1, line_count + 1))
        self.line_numbers.config(state="normal")
        self.line_numbers.delete("1.0", tk.END)
        self.line_numbers.insert("1.0", line_content)
        self.line_numbers.config(state="disabled")

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

    # ---------- Main Logic (Updated) ----------
    def run_execution(self):
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
        
        # --- 1. Tokenization ---
        try:
            lexer = Lexer()
            tokens = lexer.tokenize(code)
            
            # Show Lexer Errors first if any
            if hasattr(lexer, 'errors') and lexer.errors:
                self.console.insert(tk.END, "[!] Lexer Errors:\n")
                for err in lexer.errors:
                    self.console.insert(tk.END, f"{err}\n")
                return # Stop if lexer errors

            self.lexeme_table.delete(*self.lexeme_table.get_children())
            for desc, token, _, _ in tokens:
                self.lexeme_table.insert("", tk.END, values=(desc, token))
                
        except Exception as e:
            messagebox.showerror("Lexer Error", str(e))
            return

        # --- 2. Parsing ---
        try:
            # Parse returns: success, parser, symbol_table, function_dictionary, parse_errors
            parse_results = parse_lolcode(tokens)
            
            # Unpack assuming 5 return values (based on your main.py logic)
            if len(parse_results) == 5:
                success, parser_obj, symbol_table, function_dict, parse_errors = parse_results
            else:
                # Fallback for older parser versions
                success = parse_results[0]
                parser_obj = parse_results[1]
                symbol_table = parse_results[2]
                function_dict = parse_results[3] if len(parse_results) > 3 else {}
                parse_errors = []

            # Update UI with initial parse state
            self.update_tables(symbol_table, function_dict)
            
            if not success:
                self.console.insert(tk.END, "[!] Parsing Failed. Errors:\n")
                if parse_errors:
                    for err in parse_errors:
                        self.console.insert(tk.END, f"{err}\n")
                elif hasattr(parser_obj, 'errors'):
                    for err in parser_obj.errors:
                        self.console.insert(tk.END, f"{err}\n")
                return # Stop if parser errors

        except Exception as e:
            self.console.insert(tk.END, f"[!] Parser Crash: {e}\n")
            import traceback
            traceback.print_exc()
            return

        # --- 3. Semantic Analysis & Execution ---
        old_stdout = sys.stdout 
        sys.stdout = IORedirector(self.console)

        try:
            sem_success, sem_errors = analyze_lolcode(tokens, symbol_table, function_dict)
            
            if sem_success:
                
                # Execute logic matching main.py structure
                # Returns: final_symbol_table, final_function_table, final_errors
                exec_result = execute_lolcode(tokens, symbol_table, function_dict)
                
                # Unpack results
                if isinstance(exec_result, tuple) and len(exec_result) == 3:
                    final_vars, final_funcs, final_errors = exec_result
                    
                    if final_errors:
                        print("\n[Execution Errors Occurred]")
                        for err in final_errors:
                            print(f"{err}")
                    else:
                        # Update tables with final execution state
                        self.update_tables(final_vars, final_funcs)
                        print("\n[Execution Finished Successfully]")
                
                elif isinstance(exec_result, tuple) and len(exec_result) == 2:
                    # Fallback for 2-value return (success, errors) or (sym, func)
                    r1, r2 = exec_result
                    if isinstance(r1, dict): # (sym, func)
                        self.update_tables(r1, r2)
                        print("\n[Execution Finished]")
                    else: # (success, errors)
                        if not r1:
                            print("\n[Execution Errors]")
                            for err in r2: print(err)

            else:
                print("\n[Semantic Analysis Failed]")
                for err in sem_errors:
                    print(f"Error: {err}")

        except Exception as e:
            print(f"\n[CRITICAL RUNTIME ERROR]: {e}")
            import traceback
            traceback.print_exc()
        finally:
            sys.stdout = old_stdout
            self.console.insert(tk.END, "\n[Process Terminated]\n")

    def update_tables(self, var_data, func_data):
        """
        Populate the tables using the requested column structure.
        """
        # Clear tables
        self.symbol_table.delete(*self.symbol_table.get_children())
        self.function_table.delete(*self.function_table.get_children())

        # --- Update Symbol Table (Identifier, Value) ---
        if var_data:
            for var_name, data in var_data.items():
                val = "NOOB"
                if isinstance(data, (tuple, list)):
                    if len(data) >= 1:
                        val = data[0]
                else:
                    val = data
                self.symbol_table.insert("", tk.END, values=(var_name, val))

        # --- Update Function Table (Function Name, Variable Name, Value) ---
        if func_data:
            for func_name, params in func_data.items():
                if isinstance(params, list):
                    for param in params:
                        if isinstance(param, (tuple, list)) and len(param) >= 1:
                            p_name = param[0]
                            p_val = param[1] if len(param) > 1 else "NOOB"
                            self.function_table.insert("", tk.END, values=(func_name, p_name, p_val))

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