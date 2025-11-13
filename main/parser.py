

class Parser:

    def __init__(self, tokens):
        self.tokens = tokens                 
        self.position = 0                     
        self.stack = []                      
        self.errors = []                      
    # ============= Tape Operations (Input Management) =============
    
    # Returns current token
    def current_token(self):
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None
    
    # Move to the next token
    def consume(self, expected_token=None):
        token = self.current_token()
        if token is None:
            return None  # FIXED: Added return None
        
        if expected_token and token[1] != expected_token:
            self.errors.append(f"Line {token[3]}: Expected '{expected_token}', got '{token[1]}'")
            return None
        
        self.position += 1
        return token
    
    # Look at the next token without moving
    def peek(self, offset=1):
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None
    
    # ============= PDA Stack Operations =============
    
    # Push new symbol in the stack
    def push_stack(self, symbol, line_num=0):
        self.stack.append((symbol, line_num))
        print(f"  [PUSH] Stack: {[s[0] for s in self.stack]}")
    
    # Pop the value symbol in the top of stack
    def pop_stack(self, expected_symbol=None):
        if not self.stack:
            self.errors.append(f"Stack underflow - unmatched closing")
            return None
        
        symbol, line_num = self.stack.pop()
        # FIXED: Print entire stack, handle empty stack case
        print(f"  [POP]  Stack: {[s[0] for s in self.stack] if self.stack else '[]'}")
        
        if expected_symbol and symbol != expected_symbol:
            self.errors.append(f"Mismatched structure: expected '{expected_symbol}', got '{symbol}' from line {line_num}")
            return None
        
        return symbol

    # Look at the value of the top of stack
    def peek_stack(self):
        if self.stack:
            return self.stack[-1][0]
        return None
    
    # ============= PDA State Transitions & Parsing =============
    
    # Main parser body
    def parse(self):
        print("\n================ START PARSING HERE ================\n")

        if not self.tokens:
            self.errors.append("No tokens to parse - empty program")
            return False

        # Check program start
        if not self.parse_program_start():
            return False

        while self.current_token() and self.current_token()[1] != 'KTHXBYE':
            token = self.current_token()

            # Variable declaration section
            if token[1] == 'WAZZUP':
                self.parse_variable_list()
            
            # Variable declaration
            elif token[1] == 'I HAS A':
                self.parse_variable_declaration()

            # Skip unknown tokens
            else:
                print(f"Line {token[3]}: Skipping unrecognized statement starting with '{token[1]}'")
                self.consume()

        # Now consume KTHXBYE
        if not self.parse_program_end():
            self.errors.append(f"Missing clossing argument 'KTNXBYE' for opening argument 'HAI' at line 2")
            return False

        # Final check: stack should be empty
        if self.stack:
            print(f"\n[ERROR] Stack not empty at end: {[s[0] for s in self.stack]}")
            self.errors.append("Unclosed structures remain")
            return False
        
        print("\n========== Parse Complete ==========\n")
        return len(self.errors) == 0

    # ============= Grammar Rules =============
    
    def parse_program_start(self):
        token = self.consume('HAI')
        if not token:
            return False
        
        self.push_stack('PROGRAM', token[3])
        print(f"  ✓ Program started at line {token[3]}\n")
        return True

    def parse_program_end(self):
        token = self.consume('KTHXBYE')
        if not token:
            return False
        
        self.pop_stack('PROGRAM')
        print(f"  ✓ Program ended at line {token[3]}\n")
        return True  

    def parse_variable_declaration(self):
        self.consume('I HAS A')
        
        var_token = self.current_token()
        if var_token and var_token[2] == 'IDENTIFIER':
            self.consume()
            print(f"  ✓ Declared variable: {var_token[1]}")
            
            if self.current_token() and self.current_token()[1] == 'ITZ':
                self.consume('ITZ')
                self.parse_expression()
        else:
            self.errors.append(f"Expected identifier after I HAS A")
        print()

    def parse_variable_list(self):
        token = self.consume('WAZZUP')  
        if not token:  
            return False
        
        self.push_stack('VAR_SECTION', token[3])
        print(f"  ✓ Variable section opened at line {token[3]}")
        line_opened = token[3]
        
        # Parse variable declarations
        while self.current_token() and self.current_token()[1] != 'BUHBYE':
            if self.current_token()[1] == 'I HAS A':
                self.parse_variable_declaration()
            else:
                self.consume()
        
        token = self.consume('BUHBYE')
        if token:
            self.pop_stack('VAR_SECTION')
            print(f"  ✓ Variable section closed at line {token[3]}\n")
        else:
            self.errors.append(f"Missing BUHBYE for WAZZUP at line {line_opened}")
        
        return True  

    def parse_expression(self):
        token = self.current_token()
        if not token:
            return
        
        # Literal values
        if token[2] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'IDENTIFIER']:
            self.consume()

        # Arithmetic operations
        elif token[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            self.consume()
            
            self.parse_expression()
            if self.current_token() and self.current_token()[1] == 'AN':
                self.consume('AN')
                self.parse_expression()

        # Boolean operations
        elif token[1] in ['BOTH OF', 'EITHER OF', 'WON OF']:
            self.consume()
            self.parse_expression()
            if self.current_token() and self.current_token()[1] == 'AN':
                self.consume('AN')
                self.parse_expression()
        
        # Comparison
        elif token[1] in ['BOTH SAEM', 'DIFFRINT']:
            self.consume()
            self.parse_expression()
            if self.current_token() and self.current_token()[1] == 'AN':
                self.consume('AN')
                self.parse_expression()
    
    # ============= Stub Methods (To Be Implemented Later) =============
    
    def parse_statement(self):
        pass
    
    def parse_conditional(self):
        pass
    
    def parse_loop(self):
        pass
    
    def parse_switch(self):
        pass
    
    # ============= Utility Methods =============
    
    def print_errors(self):
        if self.errors:
            print("\n========== PARSING ERRORS ==========")
            for error in self.errors:
                print(f"  ✗ {error}")
            print("====================================\n")
        else:
            print("\n✓ No parsing errors found!\n")
    
    def get_stack_state(self):
        return [s[0] for s in self.stack] if self.stack else []


# ============= Helper Function =============

def parse_lolcode(tokens):
    parser = Parser(tokens)
    success = parser.parse()
    parser.print_errors()
    return success, parser
