
from lexer import Lexer
from parser import parse_lolcode
import gui  # import the GUI module

def run_cli():
    input_file = "input.txt"

    with open(input_file, 'r') as file:
        text = file.read()
        
    lexer = Lexer()
    tokens = lexer.tokenize(text)

    print("====================== All Tokens ======================\n")
    for i in tokens:
        print(f"Token:\t{i}\n")
    print("========================================================\n")

    lexer.print_tokens(tokens)
    lexer.print_statistics()

    print("=============== PARSER HERE ===============")
    success, parser, symbol_table = parse_lolcode(tokens)
    if success:
        print("\n===========================\nParsing success\n===========================\n")
    else:
        print("\n===========================\nParsing failed, check errors above\n===========================\n")

def main():
    choice = input("Run in GUI mode? (y/n): ").strip().lower()
    if choice == "y":
        gui.start_gui()
    else:
        run_cli()

if __name__ == "__main__":
    main()
