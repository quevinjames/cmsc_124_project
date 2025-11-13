import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os, importlib.util, re

LEXER_MODULE_NAME = "lexer"

# --- Import lexer.py ---
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

# --- GUI Class ---
class LOLGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("LOLCODE Interpreter")
        self.geometry("1200x750")
        self.configure(bg="#E9EEF2")  # light gray-blue background
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

        # ---------- MIDDLE COLUMN: Lexemes ----------
        tk.Label(middle, text="Symbol Table", font=("Segoe UI", 11, "bold"),
                 bg="#E9EEF2", fg="#1A3340").pack(anchor="w", pady=(0, 3))

        self.lexeme_list = tk.Listbox(middle, font=("Consolas", 11), height=25,
                                      bg="white", fg="black", selectbackground="#BFD7ED")
        lex_scroll = ttk.Scrollbar(middle, orient="vertical", command=self.lexeme_list.yview)
        self.lexeme_list.configure(yscrollcommand=lex_scroll.set)
        self.lexeme_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        lex_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        # ---------- RIGHT COLUMN: Classification / Symbol Table ----------
        tk.Label(right, text="Lexemmes", font=("Segoe UI", 11, "bold"),
                 bg="#E9EEF2", fg="#1A3340").pack(anchor="w", pady=(0, 3))

        self.symbol_table = ttk.Treeview(right, columns=("Lexeme", "Type"), show="headings", height=25)
        self.symbol_table.heading("Lexeme", text="Lexeme")
        self.symbol_table.heading("Type", text="Type")
        self.symbol_table.column("Lexeme", width=160)
        self.symbol_table.column("Type", width=120)
        self.symbol_table.pack(fill=tk.BOTH, expand=True)

        # ---------- BUTTONS ----------
        btn_frame = tk.Frame(self, bg="#E9EEF2")
        btn_frame.pack(fill=tk.X, pady=(5, 5))
        analyze_btn = ttk.Button(btn_frame, text="Analyze", command=self.run_lexer)
        clear_btn = ttk.Button(btn_frame, text="Clear", command=self.clear_all)
        analyze_btn.pack(side=tk.LEFT, padx=10, pady=5)
        clear_btn.pack(side=tk.LEFT, padx=5, pady=5)

        # ---------- CONSOLE ----------
        tk.Label(self, text="Console Output", font=("Segoe UI", 11, "bold"),
                 bg="#E9EEF2", fg="#1A3340").pack(anchor="w", padx=10)
        self.console = tk.Text(self, height=10, font=("Consolas", 11),
                               bg="white", fg="black", relief=tk.SOLID, bd=1)
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

        code = self.source_text.get("1.0", tk.END)
        lexer_class = getattr(LEXER_MOD, "LOLCODELexer", None)
        if not lexer_class:
            messagebox.showerror("Error", "LOLCODELexer not found in lexer.py")
            return

        try:
            lexer = lexer_class()
            tokens = lexer.tokenize(code)
            simplified = [(desc, token) for (desc, token, _, _) in tokens]

            # update lexeme list
            self.lexeme_list.delete(0, tk.END)
            for desc, token in simplified:
                self.lexeme_list.insert(tk.END, f"{token}")

            # update symbol table
            for i in self.symbol_table.get_children():
                self.symbol_table.delete(i)
            for desc, token in simplified:
                self.symbol_table.insert("", tk.END, values=(token, desc))

            # show in console
            self.console.delete("1.0", tk.END)
            for desc, token in simplified:
                self.console.insert(tk.END, f"{desc} {token}\n")
            self.console.insert(tk.END, "\n[Analysis Complete]\n")
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def clear_all(self):
        self.source_text.delete("1.0", tk.END)
        self.lexeme_list.delete(0, tk.END)
        for i in self.symbol_table.get_children():
            self.symbol_table.delete(i)
        self.console.delete("1.0", tk.END)

if __name__ == "__main__":
    app = LOLGui()
    app.mainloop()
