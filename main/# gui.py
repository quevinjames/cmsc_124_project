# gui.py
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import subprocess
import importlib.util
import tempfile

# ---------- Configuration ----------
LEXER_MODULE_NAME = "lexer"  # expects lexer.py in same folder
TEMP_LOL = "sample_tmp.lol"  # temporary file used when running lexer

# ---------- Helper: dynamically import lexer.py if available ----------
def import_lexer_module():
    """Try to import lexer.py as a module. Return module or None."""
    path = os.path.join(os.getcwd(), f"{LEXER_MODULE_NAME}.py")
    if not os.path.exists(path):
        return None
    try:
        spec = importlib.util.spec_from_file_location(LEXER_MODULE_NAME, path)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        print("Error importing lexer.py:", e)
        return None

LEXER_MOD = import_lexer_module()

# ---------- GUI Application ----------
class LOLGui(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CMSC124 — LOLCode IDE (GUI)")
        self.geometry("1000x700")
        self.create_widgets()

    def create_widgets(self):
        # Top toolbar with Run/Open/Save
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X)

        open_btn = ttk.Button(toolbar, text="Open", command=self.open_file)
        open_btn.pack(side=tk.LEFT, padx=4, pady=4)
        save_btn = ttk.Button(toolbar, text="Save", command=self.save_file)
        save_btn.pack(side=tk.LEFT, padx=4, pady=4)
        run_btn = ttk.Button(toolbar, text="Run (Lex)", command=self.run_lexer)
        run_btn.pack(side=tk.LEFT, padx=8, pady=4)

        # Notebook (tabs)
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True)

        # Code Editor tab
        self.editor_frame = ttk.Frame(self.nb)
        self.nb.add(self.editor_frame, text="Code Editor")
        self._make_editor(self.editor_frame)

        # Lexeme Table tab
        self.lexeme_frame = ttk.Frame(self.nb)
        self.nb.add(self.lexeme_frame, text="Lexeme Table")
        self._make_lexeme_table(self.lexeme_frame)

        # Symbol Table tab
        self.symbol_frame = ttk.Frame(self.nb)
        self.nb.add(self.symbol_frame, text="Symbol Table")
        self._make_symbol_table(self.symbol_frame)

        # Terminal / Output tab
        self.terminal_frame = ttk.Frame(self.nb)
        self.nb.add(self.terminal_frame, text="Terminal / Output")
        self._make_terminal(self.terminal_frame)

        # Put a sample or blank in the editor
        self.current_file = None
        self.load_default_sample()

    # ---------------- Editor ----------------
    def _make_editor(self, parent):
        # Text area with vertical scrollbar
        self.editor = tk.Text(parent, wrap=tk.NONE, undo=True, font=("Consolas", 12))
        vbar = ttk.Scrollbar(parent, orient=tk.VERTICAL, command=self.editor.yview)
        hbar = ttk.Scrollbar(parent, orient=tk.HORIZONTAL, command=self.editor.xview)
        self.editor.configure(yscrollcommand=vbar.set, xscrollcommand=hbar.set)
        vbar.pack(side=tk.RIGHT, fill=tk.Y)
        hbar.pack(side=tk.BOTTOM, fill=tk.X)
        self.editor.pack(fill=tk.BOTH, expand=True)

    def load_default_sample(self):
        # If sample.lol exists, load it; otherwise leave blank
        sample_path = os.path.join(os.getcwd(), "sample.lol")
        if os.path.exists(sample_path):
            with open(sample_path, "r", encoding="utf-8") as f:
                content = f.read()
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", content)
            self.current_file = sample_path

    def open_file(self):
        p = filedialog.askopenfilename(filetypes=[("LOLCODE files", "*.lol"), ("All files", "*.*")])
        if not p:
            return
        try:
            with open(p, "r", encoding="utf-8") as f:
                data = f.read()
            self.editor.delete("1.0", tk.END)
            self.editor.insert("1.0", data)
            self.current_file = p
            self.status_message(f"Opened: {p}")
        except Exception as e:
            messagebox.showerror("Open Error", str(e))

    def save_file(self):
        if self.current_file:
            path = self.current_file
        else:
            path = filedialog.asksaveasfilename(defaultextension=".lol",
                                                filetypes=[("LOLCODE files", "*.lol"), ("All files", "*.*")])
            if not path:
                return
            self.current_file = path
        try:
            text = self.editor.get("1.0", tk.END)
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            self.status_message(f"Saved: {path}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    # ---------------- Lexeme Table ----------------
    def _make_lexeme_table(self, parent):
        cols = ("Type", "Lexeme")
        self.lex_tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        self.lex_tree.heading("Type", text="Token Type")
        self.lex_tree.heading("Lexeme", text="Lexeme")
        self.lex_tree.column("Type", width=300, anchor=tk.W)
        self.lex_tree.column("Lexeme", width=500, anchor=tk.W)
        self.lex_tree.pack(fill=tk.BOTH, expand=True)
        # Add vertical scrollbar
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.lex_tree.yview)
        self.lex_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    # ---------------- Symbol Table ----------------
    def _make_symbol_table(self, parent):
        cols = ("Variable", "Type", "Value")
        self.sym_tree = ttk.Treeview(parent, columns=cols, show="headings", selectmode="browse")
        for c, w in zip(cols, (200, 150, 300)):
            self.sym_tree.heading(c, text=c)
            self.sym_tree.column(c, width=w, anchor=tk.W)
        self.sym_tree.pack(fill=tk.BOTH, expand=True)
        vsb = ttk.Scrollbar(parent, orient="vertical", command=self.sym_tree.yview)
        self.sym_tree.configure(yscrollcommand=vsb.set)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

    # ---------------- Terminal ----------------
    def _make_terminal(self, parent):
        # Text area (read-only)
        self.terminal = tk.Text(parent, wrap=tk.WORD, state=tk.NORMAL, font=("Consolas", 11))
        self.terminal.pack(fill=tk.BOTH, expand=True)
        # Buttons for clear/save
        bottom = ttk.Frame(parent)
        bottom.pack(fill=tk.X)
        clear_btn = ttk.Button(bottom, text="Clear", command=lambda: (self.terminal.delete("1.0", tk.END)))
        clear_btn.pack(side=tk.LEFT, padx=4, pady=4)
        save_btn = ttk.Button(bottom, text="Save Output...", command=self.save_output)
        save_btn.pack(side=tk.LEFT, padx=4, pady=4)

    def save_output(self):
        p = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text", "*.txt"), ("All", "*.*")])
        if not p:
            return
        content = self.terminal.get("1.0", tk.END)
        try:
            with open(p, "w", encoding="utf-8") as f:
                f.write(content)
            self.status_message(f"Saved output to {p}")
        except Exception as e:
            messagebox.showerror("Save Error", str(e))

    # ---------------- Run / Tokenize ----------------
    def run_lexer(self):
        """Save editor content to temp file, run lexer, populate lexeme and symbol tables and terminal."""
        source = self.editor.get("1.0", tk.END)
        # write to a temp lol file
        with open(TEMP_LOL, "w", encoding="utf-8") as f:
            f.write(source)

        tokens = []
        formatted_lines = []

        # Try to call lex_file from lexer module if available
        if LEXER_MOD and hasattr(LEXER_MOD, "lex_file"):
            try:
                # lex_file should return list of (type, lexeme)
                tokens = LEXER_MOD.lex_file(TEMP_LOL)
                # If module offers format_output, use it for nicer terminal display
                if hasattr(LEXER_MOD, "format_output"):
                    # Some implementations require strings; format_output may expect tokens or call lex_file itself.
                    try:
                        formatted_lines = LEXER_MOD.format_output(tokens)
                    except Exception:
                        # try calling format_output without args (it may read its own sample.lol)
                        try:
                            formatted_lines = LEXER_MOD.format_output()
                        except Exception:
                            formatted_lines = []
                else:
                    # create simple formatted lines from tokens
                    formatted_lines = [f"{t} {l}" if t not in ('NUMBR Literal','NUMBAR Literal','YARN Literal','Boolean Value') else f"{'Integer Literal' if t=='NUMBR Literal' else 'Float Literal' if t=='NUMBAR Literal' else 'String Literal' if t=='YARN Literal' else 'Boolean Value'} {l} {l}" for t,l in tokens]
            except Exception as e:
                # fallback to subprocess if something fails
                print("Error calling lex_file:", e)
                tokens, formatted_lines = self._run_lexer_subprocess(TEMP_LOL)
        else:
            # No module; call lexer.py as subprocess
            tokens, formatted_lines = self._run_lexer_subprocess(TEMP_LOL)

        # Populate lexeme table
        self.populate_lexeme_table(tokens)

        # Build a simple symbol table from tokens
        sym_list = self.build_symbol_table(tokens)
        self.populate_symbol_table(sym_list)

        # Populate terminal
        self.terminal.delete("1.0", tk.END)
        for line in formatted_lines:
            self.terminal.insert(tk.END, line + "\n")

        # Also write tokens_output.txt for consistency with submission
        try:
            with open("tokens_output.txt", "w", encoding="utf-8") as out:
                for line in formatted_lines:
                    out.write(line + "\n")
        except Exception as e:
            print("Error writing tokens_output.txt:", e)

        self.status_message("Lexing complete.")

    def _run_lexer_subprocess(self, lol_path):
        """
        Run `python lexer.py sample_tmp.lol` as a subprocess if importing failed or lex_file is not available.
        Parses tokens_output.txt (if produced) to reconstruct tokens/formatted lines.
        """
        formatted_lines = []
        tokens = []
        try:
            # Run lexer.py (some versions ignore args and read sample.lol; pass temp as cwd fallback)
            # Many implementations simply read sample.lol. Some accept filename arg.
            proc = subprocess.run([sys.executable, f"{LEXER_MODULE_NAME}.py", lol_path],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, cwd=os.getcwd(), timeout=8)
            stdout = proc.stdout
            stderr = proc.stderr
            # If stdout contains useful token info, use it
            if stdout and stdout.strip():
                # split lines and use as formatted lines
                formatted_lines = [ln.rstrip() for ln in stdout.splitlines() if ln.strip()]
            # If tokens_output.txt exists (lexer might have written it), read it
            outpath = os.path.join(os.getcwd(), "tokens_output.txt")
            if os.path.exists(outpath):
                with open(outpath, "r", encoding="utf-8") as f:
                    formatted_lines = [ln.rstrip("\n") for ln in f.readlines() if ln.strip()]
            # Try to reconstruct tokens from formatted_lines by splitting first word/group
            for ln in formatted_lines:
                # naive parse: split into type and lexeme(s)
                parts = ln.split()
                if not parts:
                    continue
                # Type is everything up to the first lexeme token that looks like an actual lexeme or quoted string
                # We'll attempt to find last token that matches an identifier/literal pattern
                # Simple heuristic: last token is lexeme (or last two tokens for literal repeated)
                lexeme = parts[-1]
                # type_text is remainder
                type_text = " ".join(parts[:-1])
                tokens.append((type_text, lexeme))
        except Exception as e:
            formatted_lines = [f"Error running lexer subprocess: {e}"]
            tokens = []
        return tokens, formatted_lines

    def populate_lexeme_table(self, tokens):
        # Clear existing
        for i in self.lex_tree.get_children():
            self.lex_tree.delete(i)
        # tokens is list of tuples (type, lexeme) or formatted lines if fallback
        for item in tokens:
            if isinstance(item, tuple) and len(item) >= 2:
                ttype, lexeme = item[0], item[1]
            else:
                # fallback: parse line
                parts = str(item).split()
                if len(parts) >= 2:
                    ttype = " ".join(parts[:-1])
                    lexeme = parts[-1]
                else:
                    ttype = str(item)
                    lexeme = ""
            self.lex_tree.insert("", tk.END, values=(ttype, lexeme))

    def build_symbol_table(self, tokens):
        """
        Very small symbol table extractor:
        - Look for pattern: ("Variable Declaration", var_name) optionally followed later by ("Variable Assignment", ITZ) and a literal
        - We'll scan tokens sequentially and update symbols dict.
        """
        symbols = {}  # name -> (type, value)
        awaiting_decl = None  # store var name after I HAS A

        # tokens might be tuples like ("Variable Declaration","I HAS A") or ("Variable Identifier","num")
        # normalize tokens: if token tuple matches known types from our lexer, use them; otherwise attempt to infer
        for item in tokens:
            if not isinstance(item, (list, tuple)) or len(item) < 2:
                continue
            ttype, lex = item[0], item[1]

            # If we see "Variable Declaration" token lexeme may be "I HAS A" (multiword); next identifier is var name
            if ttype.lower().startswith("variable declaration") or lex == "I HAS A":
                # next token should be identifier; mark awaiting
                awaiting_decl = True
                continue

            # If awaiting decl and got an identifier
            if awaiting_decl and re.fullmatch(r"^[A-Za-z][A-Za-z0-9_]*$", lex):
                varname = lex
                symbols[varname] = ("NOOB", "NOOB")  # default uninitialized
                # set context to watch for ITZ for initialization
                awaiting_decl = ("declared", varname)
                continue

            # If we see Variable Assignment token or literal indicating assignment following I HAS A
            if ttype.lower().startswith("variable assignment") and awaiting_decl and isinstance(awaiting_decl, tuple):
                # next token likely literal or identifier storing value; handled next iteration
                awaiting_decl = ("assign_wait", awaiting_decl[1])
                continue

            # If we are waiting for assignment and current is literal or identifier
            if isinstance(awaiting_decl, tuple) and awaiting_decl[0] == "assign_wait":
                varname = awaiting_decl[1]
                # detect literal types
                if re.fullmatch(r"^-?[0-9]+$", lex):
                    symbols[varname] = ("NUMBR", lex)
                elif re.fullmatch(r"^-?[0-9]+\.[0-9]+$", lex):
                    symbols[varname] = ("NUMBAR", lex)
                elif re.fullmatch(r"^\"[^\"]*\"$", lex):
                    symbols[varname] = ("YARN", lex.strip('"'))
                elif re.fullmatch(r"^(WIN|FAIL)$", lex):
                    symbols[varname] = ("TROOF", lex)
                else:
                    # could be identifier assigned from another var
                    if lex in symbols:
                        symbols[varname] = symbols[lex]
                    else:
                        symbols[varname] = ("UNKNOWN", lex)
                # clear awaiting state
                awaiting_decl = None
                continue

            # safety: reset awaiting_decl if unknown flow
            if ttype.lower().startswith("variable declaration") is False and awaiting_decl and awaiting_decl is not True:
                # leave it alone; other logic handles
                pass

        # Convert to list of tuples
        sym_list = [(name, typ, val) for name, (typ, val) in symbols.items()]
        return sym_list

    def populate_symbol_table(self, sym_list):
        for i in self.sym_tree.get_children():
            self.sym_tree.delete(i)
        for name, typ, val in sym_list:
            self.sym_tree.insert("", tk.END, values=(name, typ, val))

    def status_message(self, msg):
        # put short feedback into terminal area top
        self.terminal.insert(tk.END, f"[Status] {msg}\n")
        self.terminal.see(tk.END)


if __name__ == "__main__":
    app = LOLGui()
    app.mainloop()
