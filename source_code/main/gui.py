import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, importlib.util
import sys

# =================================================================
# IMPORTS
# =================================================================
try:
    from lexer import Lexer
    from parser import parse_lolcode
    from semantic import analyze_lolcode
    from execute import execute_lolcode
except ImportError:
    # Fallback or manual handling if needed, but for now we print error
    print("Error: Ensure lexer.py, parser.py, semantic.py, and execute.py are in the same folder.")

# --- CLASS TO REDIRECT PRINT() TO GUI ---
class IORedirector(object):
    """A helper class to redirect stdout (print) to the Tkinter Text widget"""
    def __init__(self, text_widget):
        self.text_space = text_widget

    def write(self, string):
        self.text_space.insert('end', string)
        self.text_space.see('end') 
    
    def flush(self):
        pass

LEXER_MODULE_NAME = "Lexer"
LEXER_MOD = None

# Attempt to load lexer module dynamically if needed, 
# though direct import above is preferred.
try:
    path = os.path.join(os.getcwd(), f"{LEXER_MODULE_NAME}.py")
    if os.path.exists(path):
        spec = importlib.util.spec_from_file_location(LEXER_MODULE_NAME, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        LEXER_MOD = mod
except Exception:
    pass

class LOLGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LOLCODE Interpreter")
        self.geometry("1300x750") # Slightly wider to accommodate tables
        self.configure(bg="#E9EEF2")
        self.current_file = None
        self.create_widgets()

    def create_widgets(self):
        # ---------- HEADER ----------
        header = tk.Frame(self, bg="#D0E0EB", height=60)
        header.pack(fill=tk.X, pady=(10, 5))
        tk.Label(header, text="LOLCODE INTERPRETER", font=("Segoe UI", 20, "bold"),
                 bg="#D0E0EB", fg="#2A4D69").pack(pady=10)

        # ---------- MAIN BODY ----------
        body = tk.Frame(self, bg="#E9EEF2")
        body.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        # Three main columns
        left = tk.Frame(body, bg="#E9EEF2")
        middle = tk.Frame(body, bg="#E9EEF2")
        right = tk.Frame(body, bg="#E9EEF2")
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        middle.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
        right.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)

        # ---------- LEFT COLUMN: Source Code with Line Numbers ----------
        tk.Label(left, text="Source Code", font=("Segoe UI", 11, "bold"),
                 bg="#E9EEF2", fg="#1A3340").pack(anchor="w", pady=(0, 3))
        
        upload_btn = ttk.Button(left, text="Upload File", command=self.open_file)
        upload_btn.pack(anchor="w", pady=(0, 5))

        # Container for Text + LineNumbers + Scrollbar
        editor_frame = tk.Frame(left)
        editor_frame.pack(fill=tk.BOTH, expand=True)

        self.yscroll = ttk.Scrollbar(editor_frame, orient="vertical", command=self.sync_scroll)
        self.yscroll.pack(side=tk.RIGHT, fill=tk.Y)

        self.line_numbers = tk.Text(editor_frame, width=4, padx=5, takefocus=0, border=0,
                                    background="#D0E0EB", state="disabled", font=("Consolas", 11))
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)

        self.source_text = tk.Text(editor_frame, height=25, wrap=tk.NONE, font=("Consolas", 11),
                                   bg="white", fg="black", relief=tk.SOLID, bd=1)
        self.source_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.source_text.bind('<KeyRelease>', self.update_line_numbers)
        self.source_text.bind('<MouseWheel>', self.sync_scroll_wheel)
        self.source_text.config(yscrollcommand=self.on_text_scroll)

        # ---------- MIDDLE COLUMN: Lexemes ----------
        tk.Label(middle, text="Lexemes", font=("Segoe UI", 11, "bold"),
                 bg="#E9EEF2", fg="#1A3340").pack(anchor="w", pady=(0, 3))

        self.lexeme_table = ttk.Treeview(middle, columns=("Classification", "Lexeme"), show="headings", height=25)
        self.lexeme_table.heading("Classification", text="Classification")
        self.lexeme_table.heading("Lexeme", text="Lexeme")
        
        self.lexeme_table.column("Classification", width=140)
        self.lexeme_table.column("Lexeme", width=140)

        lex_scroll = ttk.Scrollbar(middle, orient="vertical", command=self.lexeme_table.yview)
        self.lexeme_table.configure(yscrollcommand=lex_scroll.set)
        
        self.lexeme_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lex_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # ---------- RIGHT COLUMN: Symbol Tables ----------
        # SPLIT INTO TWO SECTIONS: Variables (Top) and Functions (Bottom)
        
        # 1. Symbol Table (Top)
        right_top = tk.Frame(right, bg="#E9EEF2")
        right_top.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=(0, 5))

        tk.Label(right_top, text="Symbol Table", font=("Segoe UI", 11, "bold"),
                 bg="#E9EEF2", fg="#1A3340").pack(anchor="w", pady=(0, 3))

        self.symbol_table = ttk.Treeview(right_top, columns=("Identifier", "Value"), show="headings", height=10)
        self.symbol_table.heading("Identifier", text="Identifier")
        self.symbol_table.heading("Value", text="Value")
        self.symbol_table.column("Identifier", width=120)
        self.symbol_table.column("Value", width=120)
        
        st_scroll = ttk.Scrollbar(right_top, orient="vertical", command=self.symbol_table.yview)
        self.symbol_table.configure(yscrollcommand=st_scroll.set)
        self.symbol_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        st_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # 2. Function Symbol Table (Bottom)
        right_bottom = tk.Frame(right, bg="#E9EEF2")
        right_bottom.pack(side=tk.BOTTOM, fill=tk.BOTH, expand=True, pady=(5, 0))

        tk.Label(right_bottom, text="Function Symbol Table", font=("Segoe UI", 11, "bold"),
                 bg="#E9EEF2", fg="#1A3340").pack(anchor="w", pady=(0, 3))

        # 3 Columns: Function, Variable, Value (Data Type initially)
        self.function_table = ttk.Treeview(right_bottom, columns=("Function", "Variable", "Value"), show="headings", height=10)
        self.function_table.heading("Function", text="Function")
        self.function_table.heading("Variable", text="Variable")
        self.function_table.heading("Value", text="Value/Type")
        
        self.function_table.column("Function", width=80)
        self.function_table.column("Variable", width=80)
        self.function_table.column("Value", width=80)

        ft_scroll = ttk.Scrollbar(right_bottom, orient="vertical", command=self.function_table.yview)
        self.function_table.configure(yscrollcommand=ft_scroll.set)
        self.function_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ft_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # ---------- BUTTONS ----------
        btn_frame = tk.Frame(self, bg="#E9EEF2")
        btn_frame.pack(fill=tk.X, pady=(5, 5))
        analyze_btn = ttk.Button(btn_frame, text="Analyze", command=self.run_lexer)
        clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_all)
        analyze_btn.pack(side=tk.LEFT, padx=10, pady=5)
        clear_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # ---------- CONSOLE (EDITABLE) ----------
        tk.Label(self, text="Terminal / Console Output", font=("Segoe UI", 11, "bold"),
                 bg="#E9EEF2", fg="#1A3340").pack(anchor="w", padx=10)
        
        self.console = tk.Text(self, height=10, font=("Consolas", 11),
                               bg="#2B2B2B", fg="#00F7FF", relief=tk.SOLID, bd=1)
        self.console.pack(fill=tk.BOTH, padx=10, pady=(0, 10), expand=True)

        self.update_line_numbers()

    # ---------- Scrolling Logic ----------
    def sync_scroll(self, *args):
        self.source_text.yview(*args)
        self.line_numbers.yview(*args)

    def on_text_scroll(self, *args):
        self.yscroll.set(*args)
        self.line_numbers.yview_moveto(args[0])

    def sync_scroll_wheel(self, event):
        self.after(10, lambda: self.line_numbers.yview_moveto(self.source_text.yview()[0]))

    def update_line_numbers(self, event=None):
        lines = self.source_text.get('1.0', 'end-1c').count('\n') + 1
        line_content = "\n".join(str(i) for i in range(1, lines + 1))
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', tk.END)
        self.line_numbers.insert('1.0', line_content)
        self.line_numbers.config(state='disabled')
        self.line_numbers.yview_moveto(self.source_text.yview()[0])

    # ---------- Functionality ----------
    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("LOLCODE files", "*.lol"), ("All Files", "*.*")])
        if not path:
            return
        with open(path, "r", encoding="utf-8") as f:
            code = f.read()
        self.source_text.delete("1.0", tk.END)
        self.source_text.insert("1.0", code)
        self.current_file = path
        self.console.insert(tk.END, f"[Opened] {path}\n")
        self.update_line_numbers()

    def update_function_table_ui(self, function_dictionary):
        """Helper to populate the Function Symbol Table"""
        self.function_table.delete(*self.function_table.get_children())
        if function_dictionary:
            # Expected format: {'add_nums': [('a', 'NUMBR'), ('b', 'NUMBR')]}
            for func_name, params in function_dictionary.items():
                if isinstance(params, list):
                    for param in params:
                        # param is typically tuple (variable_name, data_type/value)
                        if isinstance(param, tuple) or isinstance(param, list):
                            var_name = param[0]
                            val_type = param[1] if len(param) > 1 else ""
                            self.function_table.insert("", tk.END, values=(func_name, var_name, val_type))

    def update_symbol_table_ui(self, symbol_table):
        """Helper to populate the Global Symbol Table"""
        self.symbol_table.delete(*self.symbol_table.get_children())
        if symbol_table:
            for identifier, data in symbol_table.items():
                # data is often (value, type, line, ...) or just value
                if isinstance(data, tuple) or isinstance(data, list):
                    var_value = str(data[0])
                else:
                    var_value = str(data)
                self.symbol_table.insert("", tk.END, values=(identifier, var_value))

    def run_lexer(self):
        # 1. Imports check
        if not LEXER_MOD or not parse_lolcode:
            messagebox.showerror("Error", "Modules missing.")
            return

        code = self.source_text.get("1.0", tk.END)
        lexer_class = getattr(LEXER_MOD, "Lexer", None)
        if not lexer_class:
            messagebox.showerror("Error", "Lexer class not found.")
            return

        try:
            # 2. Tokenization
            lexer = lexer_class()
            tokens = lexer.tokenize(code)
            simplified = [(desc, token) for (desc, token, _, _) in tokens]

            self.lexeme_table.delete(*self.lexeme_table.get_children())
            for desc, token in simplified:
                self.lexeme_table.insert("", tk.END, values=(desc, token))

            # 3. Parsing
            # Updated to expect 4 return values: success, parser, symbol_table, function_dictionary
            parse_result = parse_lolcode(tokens)
            
            # Unpack safely (handle potential 3-value return if parser.py isn't updated yet)
            if len(parse_result) == 4:
                success, parser_obj, symbol_table_data, function_data = parse_result
            else:
                success, parser_obj, symbol_table_data = parse_result
                function_data = {} # Default empty if parser doesn't return it

            # Populate tables with initial state
            self.update_symbol_table_ui(symbol_table_data)
            self.update_function_table_ui(function_data)

            # 4. Console Output
            self.console.delete("1.0", tk.END)
            self.console.insert(tk.END, "--- PARSER OUTPUT ---\n")
            
            if success:
                self.console.insert(tk.END, "Parsing Successful!\n")
                
                # 5. Semantic & Execution
                if analyze_lolcode and execute_lolcode:
                    self.console.insert(tk.END, "--- EXECUTION OUTPUT ---\n")
                    
                    # Redirect print() output to GUI
                    old_stdout = sys.stdout 
                    sys.stdout = IORedirector(self.console) 
                    
                    try:
                        # Semantic Analysis
                        sem_success, sem_errors = analyze_lolcode(tokens, symbol_table_data, function_data)
                        
                        if sem_success:
                            print("\n[Executing...]")
                            # Execute Code
                            # returns final_symbol_table, final_function_table
                            result = execute_lolcode(tokens, symbol_table_data, function_data)
                            
                            # Update UI with FINAL state after execution
                            if isinstance(result, tuple) and len(result) == 2:
                                final_sym, final_func = result
                                self.update_symbol_table_ui(final_sym)
                                self.update_function_table_ui(final_func)
                            
                        else:
                            print("\n[Semantic Errors Prevented Execution]")

                    except Exception as sem_err:
                        print(f"\nRuntime Error: {sem_err}")
                        import traceback
                        traceback.print_exc()
                    finally:
                        sys.stdout = old_stdout
                        
                self.console.insert(tk.END, "\n[Analysis Complete]\n")
            else:
                self.console.insert(tk.END, "Parsing Failed. Found errors:\n\n")
                if hasattr(parser_obj, 'errors') and parser_obj.errors:
                    for error in parser_obj.errors:
                        self.console.insert(tk.END, f"{error}\n")
                else:
                    self.console.insert(tk.END, "Unknown error occurred.\n")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            import traceback
            traceback.print_exc()

    def clear_all(self):
        self.source_text.delete("1.0", tk.END)
        self.update_line_numbers()
        self.lexeme_table.delete(*self.lexeme_table.get_children())
        self.symbol_table.delete(*self.symbol_table.get_children())
        self.function_table.delete(*self.function_table.get_children())
        self.console.delete("1.0", tk.END)

def start_gui():
    app = LOLGui()
    app.mainloop()

if __name__ == "__main__":
    start_gui()