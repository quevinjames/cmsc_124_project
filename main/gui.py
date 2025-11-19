import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, importlib.util

# Import the parser
try:
    from parser import parse_lolcode
except ImportError:
    parse_lolcode = None
    print("Warning: parser.py not found or parse_lolcode missing.")

LEXER_MODULE_NAME = "Lexer"

def import_lexer_module():
    path = os.path.join(os.getcwd(), f"{LEXER_MODULE_NAME}.py")
    if not os.path.exists(path):
        return None
    try:
        spec = importlib.util.spec_from_file_location(LEXER_MODULE_NAME, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        return mod
    except Exception as e:
        print("Error importing lexer.py:", e)
        return None

LEXER_MOD = import_lexer_module()

class LOLGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LOLCODE Interpreter")
        self.geometry("1200x750")
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

        # ---------- LEFT COLUMN: Source Code ----------
        tk.Label(left, text="Source Code", font=("Segoe UI", 11, "bold"),
                 bg="#E9EEF2", fg="#1A3340").pack(anchor="w", pady=(0, 3))
        upload_btn = ttk.Button(left, text="Upload File", command=self.open_file)
        upload_btn.pack(anchor="w", pady=(0, 5))

        self.source_text = tk.Text(left, height=25, wrap=tk.NONE, font=("Consolas", 11),
                                   bg="white", fg="black", relief=tk.SOLID, bd=1)
        yscroll = ttk.Scrollbar(left, orient="vertical", command=self.source_text.yview)
        self.source_text.configure(yscrollcommand=yscroll.set)
        self.source_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)

        # ---------- MIDDLE COLUMN: Lexemes (Now a Table) ----------
        tk.Label(middle, text="Lexemes", font=("Segoe UI", 11, "bold"),
                 bg="#E9EEF2", fg="#1A3340").pack(anchor="w", pady=(0, 3))

        # Changed from Listbox to Treeview
        self.lexeme_table = ttk.Treeview(middle, columns=("Classification", "Lexeme"), show="headings", height=25)
        self.lexeme_table.heading("Classification", text="Classification")
        self.lexeme_table.heading("Lexeme", text="Lexeme")
        
        self.lexeme_table.column("Classification", width=150)
        self.lexeme_table.column("Lexeme", width=150)

        lex_scroll = ttk.Scrollbar(middle, orient="vertical", command=self.lexeme_table.yview)
        self.lexeme_table.configure(yscrollcommand=lex_scroll.set)
        
        self.lexeme_table.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lex_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # ---------- RIGHT COLUMN: Symbol Table ----------
        tk.Label(right, text="Symbol Table", font=("Segoe UI", 11, "bold"),
                 bg="#E9EEF2", fg="#1A3340").pack(anchor="w", pady=(0, 3))

        self.symbol_table = ttk.Treeview(right, columns=("Identifier", "Value"), show="headings", height=25)
        self.symbol_table.heading("Identifier", text="Identifier")
        self.symbol_table.heading("Value", text="Value")
        self.symbol_table.column("Identifier", width=160)
        self.symbol_table.column("Value", width=120)
        self.symbol_table.pack(fill=tk.BOTH, expand=True)

        # ---------- BUTTONS ----------
        btn_frame = tk.Frame(self, bg="#E9EEF2")
        btn_frame.pack(fill=tk.X, pady=(5, 5))
        analyze_btn = ttk.Button(btn_frame, text="Analyze", command=self.run_lexer)
        clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_all)
        analyze_btn.pack(side=tk.LEFT, padx=10, pady=5)
        clear_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # ---------- CONSOLE ----------
        tk.Label(self, text="Terminal / Console Output", font=("Segoe UI", 11, "bold"),
                 bg="#E9EEF2", fg="#1A3340").pack(anchor="w", padx=10)
        self.console = tk.Text(self, height=10, font=("Consolas", 11),
                               bg="#2B2B2B", fg="#00FF00", relief=tk.SOLID, bd=1)
        self.console.pack(fill=tk.BOTH, padx=10, pady=(0, 10), expand=True)

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

    def run_lexer(self):
        if not LEXER_MOD:
            messagebox.showerror("Error", "lexer.py not found.")
            return
        if not parse_lolcode:
            messagebox.showerror("Error", "parser.py not found or failed to import.")
            return

        code = self.source_text.get("1.0", tk.END)
        lexer_class = getattr(LEXER_MOD, "Lexer", None)
        
        if not lexer_class:
            messagebox.showerror("Error", "Lexer not found in lexer.py")
            return

        try:
            # 1. Tokenization
            lexer = lexer_class()
            tokens = lexer.tokenize(code)
            simplified = [(desc, token) for (desc, token, _, _) in tokens]

            # Update Lexemes Table
            for i in self.lexeme_table.get_children():
                self.lexeme_table.delete(i)
                
            for desc, token in simplified:
                self.lexeme_table.insert("", tk.END, values=(desc, token))

            # 2. Parsing
            success, parser_obj, symbol_table_data = parse_lolcode(tokens)

            # Update Symbol Table 
            for i in self.symbol_table.get_children():
                self.symbol_table.delete(i)
            
            if symbol_table_data:
                for identifier, data in symbol_table_data.items():
                    var_value = str(data[0])
                    self.symbol_table.insert("", tk.END, values=(identifier, var_value))

            # Update Terminal Output
            self.console.delete("1.0", tk.END)
            
            self.console.insert(tk.END, "--- LEXICAL ANALYSIS ---\n")
            for desc, token in simplified:
                self.console.insert(tk.END, f"{desc} {token}\n")
            
            self.console.insert(tk.END, "\n--- PARSER OUTPUT ---\n")
            if success:
                self.console.insert(tk.END, "Parsing Successful!\n")
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
        for i in self.lexeme_table.get_children():
            self.lexeme_table.delete(i)
        for i in self.symbol_table.get_children():
            self.symbol_table.delete(i)
        self.console.delete("1.0", tk.END)

def start_gui():
    app = LOLGui()
    app.mainloop()

if __name__ == "__main__":
    start_gui()