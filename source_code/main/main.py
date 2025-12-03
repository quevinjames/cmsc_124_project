
"""
LOLCODE CLI & GUI Launcher
Handles command-line interface for tokenizing and parsing LOLCODE,
or launching the GUI version of the interpreter.
"""

# ================================================================
# ======================= IMPORTS =================================
# ================================================================
from lexer import Lexer
from parser import parse_lolcode
from semantic import analyze_lolcode
from execute import execute_lolcode
import gui  # GUI module

# ================================================================
# ======================= CLI RUNNER =============================
# ================================================================
def run_cli():
    """================ run_cli ================"""
    # ----------------- Load source code -----------------
    input_file = "10_functions.lol"
    with open(input_file, 'r') as file:
        text = file.read()

    # ----------------- Tokenization -----------------
    lexer = Lexer()
    tokens = lexer.tokenize(text)

    if len(lexer.errors) == 0:
        lexer_success = True

    else:
        lexer_success = False


        # ----------------- Parsing --------        ---------
    if lexer_success:
            # ----------------- Parsing -----------------
        success, parser, symbol_table, function_dictionary, parse_errors = parse_lolcode(tokens)
        if success:
            semantic_success, semantic_errors = analyze_lolcode(tokens, symbol_table, function_dictionary)
            if semantic_success:
                final_symbol_table, final_function_table, final_errors = execute_lolcode(tokens, symbol_table, function_dictionary)
            else:
                for i in semantic_errors:
                    print(i)
        else:
            for i in parse_errors:
                print(i)
                        
    else:
        for i in lexer.errors:
            print(i)

# ================================================================
# ======================= MAIN ENTRY ============================
# ================================================================
def main():
    """================ main ================"""
    choice = input("Run in GUI mode? (y/n): ").strip().lower()
    if choice == "y":
        gui.start_gui()
    else:
        run_cli()

# ================================================================
# ======================= SCRIPT EXECUTION =======================
# ================================================================
if __name__ == "__main__":
    main()
