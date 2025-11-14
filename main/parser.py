
"""
LOLCODE Parser
Pushdown Automaton (PDA) inspired parser for syntax analysis
"""

class Parser:
    """
    Pushdown Automaton (PDA) inspired parser for LOLCODE
    """
    
    def __init__(self, tokens):
        self.tokens = tokens                 
        self.position = 0                     
        self.stack = []                      
        self.errors = []         
        self.variables = {}
    
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
            return None
        
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
            
            # Function declaration
            elif token[1] == 'HOW IZ I':
                self.parse_function()
            
            # Variable declaration
            elif token[1] == 'I HAS A':
                self.parse_variable_declaration()
            
            # Other statements
            else:
                self.parse_statement()

        # Now consume KTHXBYE
        if not self.parse_program_end():
            # FIXED: Get the line number from HAI token (first token)
            self.errors.append(f"Missing closing argument 'KTHXBYE' for opening argument 'HAI' at line {self.tokens[0][3]}")
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
                self.parse_expression(var_token)

            else:
                self.variables[var_token] = "NOOB"
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

    def parse_expression(self, var_token=None):
        token = self.current_token()
        if not token:
            return
        
        # Literal values
        if token[2] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'IDENTIFIER']:
            self.variables[var_token] = token[1]
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
    
    def parse_output(self):
        self.consume('VISIBLE')
        self.parse_expression()
        print(f"  ✓ Output statement\n")

    def parse_input(self):
        self.consume('GIMMEH')
        if self.current_token() and self.current_token()[2] == 'IDENTIFIER':
            var = self.consume()
            print(f"  ✓ Input to {var[1]}\n")

    def parse_assignment(self):
        var_token = self.consume()
        self.consume('R')
        self.parse_expression()
        print(f"  ✓ Assignment to {var_token[1]}\n")

    def parse_typecast(self, cast_type):
        """
        Parse type casting operations
        Type 1: <variable> R MAEK <variable> <type>
        Type 2: <variable> IS NOW A <type>
        """
        var_token = self.consume()
        
        if cast_type == 1:
            self.consume('R')
            self.consume('MAEK')
            
            # Get the variable to cast (can be same or different variable)
            cast_var = self.current_token()
            if cast_var and cast_var[2] == 'IDENTIFIER':
                self.consume()
            
            # Get the target type
            type_token = self.current_token()
            if type_token and type_token[2] == 'TYPE':
                target_type = type_token[1]
                self.consume()
                print(f"  ✓ Typecast: {var_token[1]} R MAEK {cast_var[1] if cast_var else '?'} {target_type}")
            else:
                self.errors.append(f"Line {var_token[3]}: Expected type after MAEK")
        
        elif cast_type == 2:
            # Format: variable IS NOW A type
            self.consume('IS NOW A')
            
            # Get the target type
            type_token = self.current_token()
            if type_token and type_token[2] == 'TYPE':
                target_type = type_token[1]
                self.consume()
                print(f"  ✓ Typecast: {var_token[1]} IS NOW A {target_type}")
            else:
                self.errors.append(f"Line {var_token[3]}: Expected type after IS NOW A")
        
        print()

    def parse_function(self):
        """
        Parse function declaration
        Format: HOW IZ I <function_name> [YR <param1> [AN YR <param2> ...]]
                  <function_body>
                IF U SAY SO
        """
        token = self.consume('HOW IZ I')
        if not token:
            return False
        
        # Get function name
        func_name_token = self.current_token()
        if func_name_token and func_name_token[2] == 'IDENTIFIER':
            func_name = func_name_token[1]
            self.consume()
            self.push_stack(f'FUNCTION:{func_name}', token[3])
            print(f"  ✓ Function '{func_name}' declared at line {token[3]}")
            
            # Parse parameters (optional)
            params = []
            if self.current_token() and self.current_token()[1] == 'YR':
                self.consume('YR')
                param_token = self.current_token()
                if param_token and param_token[2] == 'IDENTIFIER':
                    params.append(param_token[1])
                    self.consume()
                    
                    # Additional parameters with AN YR
                    while self.current_token() and self.current_token()[1] == 'AN':
                        self.consume('AN')
                        if self.current_token() and self.current_token()[1] == 'YR':
                            self.consume('YR')
                            param_token = self.current_token()
                            if param_token and param_token[2] == 'IDENTIFIER':
                                params.append(param_token[1])
                                self.consume()
            
            if params:
                print(f"    Parameters: {', '.join(params)}")
            
            # Parse function body
            while self.current_token() and self.current_token()[1] != 'IF U SAY SO':
                if self.current_token()[1] == 'FOUND YR':
                    # Parse return statement
                    self.consume('FOUND YR')
                    self.parse_expression()
                    print(f"    ✓ Return statement")
                else:
                    self.parse_statement()
            
            # Close function
            token = self.consume('IF U SAY SO')
            if token:
                self.pop_stack(f'FUNCTION:{func_name}')
                print(f"  ✓ Function '{func_name}' closed at line {token[3]}\n")
            else:
                self.errors.append(f"Missing 'IF U SAY SO' for function '{func_name}'")
        else:
            self.errors.append(f"Expected function name after HOW IZ I")
        
        return True

    def parse_statement(self):
        token = self.current_token()
        if not token:
            return
        
        if token[1] == 'I HAS A':
            self.parse_variable_declaration()
        
        # FIXED: Check for IS NOW A before R (order matters!)
        elif token[2] == 'IDENTIFIER' and self.peek() and self.peek()[1] == 'IS NOW A':
            self.parse_typecast(2)
        
        # FIXED: Check if next two tokens are R and MAEK
        elif token[2] == 'IDENTIFIER' and self.peek() and self.peek()[1] == 'R':
            if self.peek(2) and self.peek(2)[1] == 'MAEK':
                self.parse_typecast(1)
            else:
                self.parse_assignment()
        
        elif token[1] == 'VISIBLE':
            self.parse_output()
        elif token[1] == 'GIMMEH':
            self.parse_input()
        elif token[1] == 'O RLY?':
            self.parse_conditional()
        elif token[1] == 'WTF?':
            self.parse_switch()
        elif token[1] == 'IM IN YR':
            self.parse_loop()
        # FIXED: Added function call support
        elif token[1] == 'I IZ':
            self.parse_function_call()
        else:
            # FIXED: Don't print skip message, just consume
            self.consume()

    def parse_function_call(self):
        """
        Parse function call
        Format: I IZ <function_name> [YR <arg1> [AN YR <arg2> ...]] MKAY
        """
        self.consume('I IZ')
        
        func_name_token = self.current_token()
        if func_name_token and func_name_token[2] == 'IDENTIFIER':
            func_name = func_name_token[1]
            self.consume()
            print(f"  ✓ Calling function: {func_name}")
            
            # Parse arguments (optional)
            args = []
            if self.current_token() and self.current_token()[1] == 'YR':
                self.consume('YR')
                self.parse_expression()
                args.append(1)
                
                # Additional arguments with AN YR
                while self.current_token() and self.current_token()[1] == 'AN':
                    self.consume('AN')
                    if self.current_token() and self.current_token()[1] == 'YR':
                        self.consume('YR')
                        self.parse_expression()
                        args.append(1)
            
            # Optional MKAY to end function call
            if self.current_token() and self.current_token()[1] == 'MKAY':
                self.consume('MKAY')
            
            if args:
                print(f"    with {len(args)} argument(s)\n")
            else:
                print()

    def parse_conditional(self):
        token = self.consume('O RLY?')
        self.push_stack('CONDITIONAL', token[3])
        print(f"  ✓ Conditional opened at line {token[3]}")
        
        # YA RLY block
        if self.current_token() and self.current_token()[1] == 'YA RLY':
            self.consume('YA RLY')
            self.push_stack('YA_RLY', self.tokens[self.position-1][3])
            
            # Parse statements until NO WAI or OIC
            while self.current_token() and self.current_token()[1] not in ['NO WAI', 'MEBBE', 'OIC']:
                self.parse_statement()
            
            self.pop_stack('YA_RLY')
        
        # Optional NO WAI block
        if self.current_token() and self.current_token()[1] == 'NO WAI':
            self.consume('NO WAI')
            self.push_stack('NO_WAI', self.tokens[self.position-1][3])
            
            while self.current_token() and self.current_token()[1] != 'OIC':
                self.parse_statement()
            
            self.pop_stack('NO_WAI')
        
        # Close conditional
        token = self.consume('OIC')
        if token:
            self.pop_stack('CONDITIONAL')
            print(f"  ✓ Conditional closed at line {token[3]}\n")

    def parse_loop(self):
        self.consume('IM IN YR')
        
        label_token = self.current_token()
        if label_token and label_token[2] == 'IDENTIFIER':
            label = label_token[1]
            self.consume()
            self.push_stack(f'LOOP:{label}', label_token[3])
            print(f"  ✓ Loop '{label}' opened at line {label_token[3]}")
            
            # Parse loop body
            while self.current_token() and self.current_token()[1] != 'IM OUTTA YR':
                if self.current_token()[1] == 'GTFO':
                    self.consume('GTFO')
                    print(f"    ✓ Break statement")
                else:
                    self.parse_statement()
            
            # Close loop
            if self.current_token() and self.current_token()[1] == 'IM OUTTA YR':
                self.consume('IM OUTTA YR')
                exit_label = self.current_token()
                if exit_label and exit_label[2] == 'IDENTIFIER':
                    if exit_label[1] == label:
                        self.consume()
                        self.pop_stack(f'LOOP:{label}')
                        print(f"  ✓ Loop '{label}' closed\n")
                    else:
                        self.errors.append(f"Loop label mismatch: '{label}' vs '{exit_label[1]}'")

    def parse_switch(self):
        token = self.consume('WTF?')
        self.push_stack('SWITCH', token[3])
        print(f"  ✓ Switch opened at line {token[3]}")
        
        # Parse OMG cases
        while self.current_token() and self.current_token()[1] == 'OMG':
            self.consume('OMG')
            self.parse_expression()  # Case value
            print(f"    ✓ Case statement")
            
            # Parse case body
            while self.current_token() and self.current_token()[1] not in ['OMG', 'OMGWTF', 'OIC']:
                if self.current_token()[1] == 'GTFO':
                    self.consume('GTFO')
                    print(f"      ✓ Break from case")
                    break
                self.parse_statement()
        
        # Optional default case
        if self.current_token() and self.current_token()[1] == 'OMGWTF':
            self.consume('OMGWTF')
            print(f"    ✓ Default case")
            while self.current_token() and self.current_token()[1] != 'OIC':
                self.parse_statement()
        
        token = self.consume('OIC')
        if token:
            self.pop_stack('SWITCH')
            print(f"  ✓ Switch closed at line {token[3]}\n")

    # ============= Utility Methods =============
    
    def print_errors(self):
        if self.errors:
            print("\n========== PARSING ERRORS ==========")
            for error in self.errors:
                print(f"  ✗ {error}")
            print("====================================\n")
        else:
            print("\n✓ No parsing errors found!\n")

    def print_variables(self):
        symbol_table = {}
        self.variables.pop(None, None)
        if self.variables:
            print("\n========== ALL VARIABLES LIST ==========")
            for variable in self.variables:
                symbol_table[variable[1]] = self.variables[variable]
                print(f"{variable[1]}:\t {self.variables[variable]}\n")
            print("====================================\n")
            return symbol_table
        else:
            print("\n✓ No parsing errors found!\n")

    
    def get_stack_state(self):
        return [s[0] for s in self.stack] if self.stack else []


# ============= Helper Function =============

def parse_lolcode(tokens):
    parser = Parser(tokens)
    success = parser.parse()
    parser.print_errors()
    symbol_table = parser.print_variables()
    return success, parser, symbol_table
