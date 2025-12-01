"""
LOLCODE Parser
Pushdown Automaton (PDA) inspired parser for syntax analysis
"""

class Parser:
    def __init__(self, tokens):
        self.tokens = tokens                 
        self.position = 0                     
        self.errors = []         
        self.symbol_table = {}

    # ================================================================
    # ======================= UTILITIES ==============================
    # ================================================================
    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    def advance(self):
        self.position += 1

    def peek(self):
        if self.position + 1 < len(self.tokens):
            return self.tokens[self.position + 1]
        return None

    # ================================================================
    # ======================= CORE PARSING ===========================
    # ================================================================
    def parse(self):
        """Main parsing loop"""
        # 1. Check for HAI
        if not self.current_token() or self.current_token()[1] != 'HAI':
            line = self.current_token()[3] if self.current_token() else "Unknown"
            self.errors.append(f"Error on line {line}: Expected 'HAI' at start of program")
            return False
        
        self.advance() # Eat HAI

        # 2. Process Statements until KTHXBYE
        while self.current_token() and self.current_token()[1] != 'KTHXBYE':
            self.parse_statement()
            
        # 3. Check for KTHXBYE
        if not self.current_token() or self.current_token()[1] != 'KTHXBYE':
            # Get line of last token if current is None
            line = self.tokens[-1][3] if self.tokens else "Unknown"
            self.errors.append(f"Error on line {line}: Expected 'KTHXBYE' to end the program")
            return False
            
        return len(self.errors) == 0

    def parse_statement(self):
        token = self.current_token()
        if not token: return

        val = token[1]
        # We grab the line number here for cleaner code, but use token[3] in errors as requested
        line = token[3]

        # --- Variable Declaration ---
        if val == 'I HAS A':
            self.advance()
            # Expect Identifier
            if not self.current_token() or self.current_token()[0] != 'Identifier':
                self.errors.append(f"Error on line {self.current_token()[3]}: Expected variable name after 'I HAS A'")
                return
            
            var_name = self.current_token()[1]
            
            # Add to symbol table (semantics will handle values, we just register existence)
            if var_name not in self.symbol_table:
                # Format: (Value, Type, Line, Origin)
                self.symbol_table[var_name] = ("NOOB", "NOOB", line, "Variable Declaration")
            
            self.advance()
            
            # Optional Initialization
            if self.current_token() and self.current_token()[1] == 'ITZ':
                self.advance()
                self.parse_expression()

        # --- Output ---
        elif val == 'VISIBLE':
            self.advance()
            # Parse infinite arguments
            while self.current_token() and self.current_token()[0] != 'Code Delimiter':
                if self.current_token()[1] in ['VISIBLE', 'GIMMEH', 'I HAS A', 'KTHXBYE']:
                    break
                self.parse_expression()
                # Optional '+' separator (not standard but common)
                if self.current_token() and self.current_token()[1] == '+':
                    self.advance()

        # --- Input ---
        elif val == 'GIMMEH':
            self.advance()
            if not self.current_token() or self.current_token()[0] != 'Identifier':
                # FIX: Explicitly using current_token()[3]
                self.errors.append(f"Error on line {self.current_token()[3]}: Expected variable name for GIMMEH")
            self.advance()

        # --- Operations (Expression start) ---
        elif val in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 
                     'BIGGR OF', 'SMALLR OF', 'BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'SMOOSH']:
            self.parse_expression()

        else:
            # Skip unhandled tokens (newlines, comments handled by lexer usually)
            self.advance()

    def parse_expression(self):
        token = self.current_token()
        if not token: return

        val = token[1]
        
        # Binary Operations
        if val in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF', 'BOTH OF', 'EITHER OF', 'WON OF']:
            self.advance()
            self.parse_expression() # Operand 1
            
            # Check for AN
            if self.current_token() and self.current_token()[1] == 'AN':
                self.advance()
            else:
                # FIX: Explicitly using current_token()[3]
                line_ref = self.current_token()[3] if self.current_token() else "Unknown"
                self.errors.append(f"Error on line {line_ref}: Expected 'AN' separator in operation")
            
            self.parse_expression() # Operand 2

        # Unary Operation
        elif val == 'NOT':
            self.advance()
            self.parse_expression()

        # Infinite Arity (SMOOSH)
        elif val == 'SMOOSH':
            self.advance()
            self.parse_expression()
            while self.current_token() and self.current_token()[1] == 'AN':
                self.advance()
                self.parse_expression()

        # Literals and Identifiers
        elif token[0] in ['Identifier', 'Integer Literal', 'Float Literal', 'String Literal', 'TROOF Literal', 'NUMBR Literal', 'NUMBAR Literal', 'YARN Literal']:
            self.advance()
        
        else:
            # Not an expression start
            pass

    def adjust_dictionary(self):
        """Returns the symbol table for the Semantic Analyzer"""
        return self.symbol_table

# ======================= ENTRY POINT =======================
def parse_lolcode(tokens):
    parser = Parser(tokens)
    success = parser.parse()
    # Return tuple: (success_bool, parser_instance, symbol_table)
    return success, parser, parser.adjust_dictionary()