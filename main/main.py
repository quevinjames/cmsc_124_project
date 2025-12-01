
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
    input_file = "input.txt"
    with open(input_file, 'r') as file:
        text = file.read()

    # ----------------- Tokenization -----------------
    lexer = Lexer()
    tokens = lexer.tokenize(text)
    lexer.print_errors()

    print("====================== All Tokens ======================\n")
    for i in tokens:
        print(f"Token:\t{i}\n")
    print("========================================================\n")


        # ----------------- Parsing -----------------
    print("=============== PARSER HERE ===============")
    success, parser, symbol_table, function_dictionary = parse_lolcode(tokens)
    if success:
        print("\n===========================\nParsing success\n===========================\n")

        semantic_success, semantic_errors = analyze_lolcode(tokens, symbol_table, function_dictionary)

        if semantic_success:
            print("\n=======================\n Semantic Success\n===========================\n")

            final_symbol_table, final_function_table, final_errors = execute_lolcode(tokens, symbol_table, function_dictionary)
    else:
        print("\n===========================\nParsing failed, check errors above\n===========================\n")

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
