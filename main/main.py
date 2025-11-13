from lexer import Lexer
from parser import Parser, parse_lolcode

def start():
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

    #print("\n====================== Sample Syntax Analyzer======================\n")
    #
    #if tokens[0][1] != 'HAI':
    #print("Invalid Program Start")
    #
    #elif tokens[len(tokens)-1][1] != 'KTHXBYE':
    #print("Invalid Program End")
    #
    #else:
    #print("Valid Program Start and End\n")
    #
    #closed = False
    #for token in range(0, len(tokens) - 1):
    #if tokens[token][1] == "WAZZUP":
    #for i in range (token, len(tokens) - 1):
    #
    #if tokens[i][1] == "BUHBYE":
    #closed = True:
    #
    #if closed == True:
    #print("List Declaration Properly Closed")
    #
    #else:
    #print("List Declaration IS NOT Properly Closed")
    #
    #
    #
    #print("======================================================================\n")

    print("\n\n")


    print("\n\n")

    print("=============== PARSER HERE ===============")

    success, parser = parse_lolcode(tokens)

    if success:
        print("\n===========================\n")
        print("parsing success")
        print("\n===========================\n")


    else:
        print("\n===========================\n")
        print("parsing failed, check errors above")
        print("\n===========================\n")

    
    return 0


start()
