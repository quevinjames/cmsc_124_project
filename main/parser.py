"""
LOLCODE Parser
Pushdown Automaton (PDA) inspired parser for syntax analysis
"""

class Parser:
    """
    Pushdown Automaton (PDA) inspired parser for LOLCODE
    """

    # ================================================================
    # ======================= INITIALIZATION =========================
    # ================================================================
    def __init__(self, tokens):
        """================ __init__ ================"""
        # Tokens and position
        self.tokens = tokens                 
        self.position = 0                     
        # PDA stack
        self.stack = []                      
        # Errors
        self.errors = []         
        # Variables and symbol table
        self.variables = {}
        self.symbol_table = {}

    # ================================================================
    # ======================= TAPE OPERATIONS ========================
    # ================================================================

    # ------------------------------------------------
    # Function: current_token
    # Description:
    #     Returns the current token without moving the pointer.
    # ------------------------------------------------
    def current_token(self):
        """================ current_token ================"""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

    # ------------------------------------------------
    # Function: consume
    # Description:
    #     Move to the next token, optionally verifying it matches an expected value.
    # ------------------------------------------------
    def consume(self, expected_token=None):
        """================ consume ================"""
        token = self.current_token()
        if token is None:
            return None
        
        if expected_token and token[1] != expected_token:
            self.errors.append(f"Line {token[3]}: Expected '{expected_token}', got '{token[1]}'")
            return None
        
        self.position += 1
        return token

    # ------------------------------------------------
    # Function: peek
    # Description:
    #     Look ahead at upcoming tokens without advancing the pointer.
    # ------------------------------------------------
    def peek(self, offset=1):
        """================ peek ================"""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None

    # ================================================================
    # ======================= PDA STACK OPERATIONS ===================
    # ================================================================

    # ------------------------------------------------
    # Function: push_stack
    # Description:
    #     Push a symbol onto the parser stack, optionally with a line number.
    # ------------------------------------------------    # ------------------------------------------------
    def push_stack(self, symbol, line_num=0):
        """================ push_stack ================"""
        self.stack.append((symbol, line_num))
        print(f"  [PUSH] Stack: {[s[0] for s in self.stack]}")

    # ------------------------------------------------
    # Function: pop_stack
    # Description:
    #     Pop symbol from top of the PDA stack; optionally check expected symbol.
    # ------------------------------------------------
    def pop_stack(self, expected_symbol=None):
        """================ pop_stack ================"""
        if not self.stack:
            self.errors.append(f"Stack underflow - unmatched closing")
            return None
        
        symbol, line_num = self.stack.pop()
        print(f"  [POP]  Stack: {[s[0] for s in self.stack] if self.stack else '[]'}")
        
        if expected_symbol and symbol != expected_symbol:
            self.errors.append(f"Mismatched structure: expected '{expected_symbol}', got '{symbol}' from line {line_num}")
            return None
        
        return symbol

    # ------------------------------------------------
    # Function: peek_stack
    # Description:
    #     Return the top symbol of the stack without popping it.
    # ------------------------------------------------
    def peek_stack(self):
        """================ peek_stack ================"""
        if self.stack:
            return self.stack[-1][0]
        return None


    def determine_data_type(value):
        """Helper function to determine data type of a value"""
        if isinstance(value, str):
            if value in ('WIN', 'FAIL'):
                return 'TROOF'
            elif re.match(r'^-?[0-9]+$', value):
                return 'NUMBR'
            elif re.match(r'^-?[0-9]+\.[0-9]+$', value):
                return 'NUMBAR'
            else:
                return 'YARN'
        return 'NOOB'

    # ================================================================
    # ======================= PDA PARSING BODY =======================
    # ================================================================

    # ------------------------------------------------
    # Function: parse
    # Description:
    #     Main parser body; drives parsing of entire LOLCODE program.
    # ------------------------------------------------
    def parse(self):
        """================ parse ================"""
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
            self.errors.append(f"Missing closing argument 'KTHXBYE' for opening argument 'HAI' at line {self.tokens[0][3]}")
            return False

        # Final check: stack should be empty
        if self.stack:
            print(f"\n[ERROR] Stack not empty at end: {[s[0] for s in self.stack]}")
            self.errors.append("Unclosed structures remain")
            return False
        
        print("\n========== Parse Complete ==========\n")
        return len(self.errors) == 0

    # ================================================================
    # ======================= GRAMMAR RULES ==========================
    # ================================================================

    # ------------------------------------------------
    # Function: parse_program_start
    # Description:
    #     Parse the 'HAI' token and start the program.
    # ------------------------------------------------
    def parse_program_start(self):
        """================ parse_program_start ================"""
        token = self.consume('HAI')
        if not token:
            return False
        
        self.push_stack('PROGRAM', token[3])
        print(f"  ✓ Program started at line {token[3]}\n")
        return True

    # ------------------------------------------------
    # Function: parse_program_end
    # Description:
    #     Parse the 'KTHXBYE' token and end the program.
    # ------------------------------------------------
    def parse_program_end(self):
        """================ parse_program_end ================"""
        token = self.consume('KTHXBYE')
        if not token:
            return False
        
        self.pop_stack('PROGRAM')
        print(f"  ✓ Program ended at line {token[3]}\n")
        return True  

    # ------------------------------------------------
    # Function: parse_variable_declaration
    # Description:
    #     Parse a variable declaration (I HAS A ... ITZ ...).
    # ------------------------------------------------
    def parse_variable_declaration(self):
        """================ parse_variable_declaration ================"""
        self.consume('I HAS A')
        
        var_token = self.current_token()
        if var_token and var_token[2] == 'IDENTIFIER':
            var_name = var_token[1]
            self.consume()
            
            if self.current_token() and self.current_token()[1] == 'ITZ':
                self.consume('ITZ')
                value, data_type = self.parse_expression(var_token)
                self.variables[var_token] = (value, data_type)
                self.symbol_table[var_name] = (value, data_type)
                print(f"  ✓ Declared variable: {var_name} with value {value} (type: {data_type})")
            else:
                self.variables[var_token] = ('NOOB', 'NOOB')
                self.symbol_table[var_name] = ('NOOB', 'NOOB')
                print(f"  ✓ Declared variable: {var_name} (default: NOOB)")
        else:
            self.errors.append(f"Expected identifier after I HAS A")
        print()
    # ------------------------------------------------
    # Function: parse_variable_list
    # Description:
    #     Parse a WAZZUP ... BUHBYE section containing variable declarations.
    # ------------------------------------------------
    def parse_variable_list(self):
        """================ parse_variable_list ================"""
        token = self.consume('WAZZUP')  
        if not token:  
            return False
        
        self.push_stack('VAR_SECTION', token[3])
        print(f"  ✓ Variable section opened at line {token[3]}")
        line_opened = token[3]
        
        while self.current_token() and self.current_token()[1] != 'BUHBYE':
            if self.current_token()[1] == 'I HAS A':
                self.parse_variable_declaration()
            else:
                curr = self.current_token()
                if curr and curr[2] == 'IDENTIFIER' and self.peek() and self.peek()[1] == 'R':
                    if curr[1] not in self.symbol_table:
                        self.errors.append(f"Variable '{curr[1]}' is not declared on line {curr[3]}")
                    self.consume()  # consume identifier
                    if self.current_token() and self.current_token()[1] == 'R':
                        self.consume('R')
                        self.parse_expression()
                else:
                    self.consume()
        
        token = self.consume('BUHBYE')
        if token:
            self.pop_stack('VAR_SECTION')
            print(f"  ✓ Variable section closed at line {token[3]}\n")
        else:
            self.errors.append(f"Missing BUHBYE for WAZZUP at line {line_opened}")
        
        return True

    # ------------------------------------------------
    # Function: parse_expression
    # Description:
    #     Parse expressions including literals, arithmetic, boolean, and comparison operations.
    # ------------------------------------------------
    def parse_expression(self, var_token=None):
        """================ parse_expression ================"""
        token = self.current_token()
        if not token:
            return (None, None)
        
        if token[2] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'IDENTIFIER']:
            if token[2] == 'IDENTIFIER' and token[1] not in self.symbol_table:
                self.errors.append(f"Variable '{token[1]}' undeclared on line {token[3]}")
                return (None, None)

            if token[2] == 'IDENTIFIER':
                # Get value and type from symbol table
                stored = self.symbol_table.get(token[1])
                if isinstance(stored, tuple):
                    value, data_type = stored
                else:
                    value = stored
                    data_type = determine_data_type(value)
            else:
                value = token[1]
                data_type = token[2]  # Use the token's data type directly

            if var_token is not None:
                self.variables[var_token] = (value, data_type)
                self.symbol_table[var_token[1]] = (value, data_type)

            self.consume()
            return (value, data_type)

        elif token[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            op = token[1]
            self.consume()
            left, left_type = self.parse_expression()
            if self.current_token() and self.current_token()[1] == 'AN':
                self.consume('AN')
                right, right_type = self.parse_expression()
                # Result of arithmetic operations is numeric
                result_type = 'NUMBAR' if (left_type == 'NUMBAR' or right_type == 'NUMBAR') else 'NUMBR'
                return (f"({left} {op} {right})", result_type)
            return (left, left_type)

        elif token[1] in ['BOTH OF', 'EITHER OF', 'WON OF']:
            op = token[1]
            self.consume()
            left, _ = self.parse_expression()
            if self.current_token() and self.current_token()[1] == 'AN':
                self.consume('AN')
                right, _ = self.parse_expression()
                return (f"({left} {op} {right})", 'TROOF')  # Boolean operations return TROOF
            return (left, 'TROOF')
        
        elif token[1] in ['BOTH SAEM', 'DIFFRINT']:
            op = token[1]
            self.consume()
            left, _ = self.parse_expression()
            if self.current_token() and self.current_token()[1] == 'AN':
                self.consume('AN')
                right, _ = self.parse_expression()
                return (f"({left} {op} {right})", 'TROOF')  # Comparison operations return TROOF
            return (left, 'TROOF')
        
        return (None, None)

    # ================================================================
    # ======================= STATEMENT PARSING ======================
    # ================================================================

    # ------------------------------------------------
    # Function: parse_statement
    # Description:
    #     Parse a single statement based on the current token.
    #     Handles variable declarations, assignments, typecasts, I/O,
    #     conditionals, loops, function calls, and unknown tokens.
    # ------------------------------------------------
    def parse_statement(self):
        """================ parse_statement ================"""
        token = self.current_token()
        if not token:
            return
        
        # Variable declaration
        if token[1] == 'I HAS A':
            self.parse_variable_declaration()
        
        # Typecast: IS NOW A (typecast type 2)
        elif token[2] == 'IDENTIFIER' and self.peek() and self.peek()[1] == 'IS NOW A':
            self.parse_typecast(2)
        
        # Typecast: R MAEK (typecast type 1) or assignment
        elif token[2] == 'IDENTIFIER' and self.peek() and self.peek()[1] == 'R':
            if self.peek(2) and self.peek(2)[1] == 'MAEK':
                self.parse_typecast(1)
            else:
                self.parse_assignment()
        
        # Output statement
        elif token[1] == 'VISIBLE':
            self.parse_output()
        
        # Input statement
        elif token[1] == 'GIMMEH':
            self.parse_input()
        
        # Conditional statements
        elif token[1] == 'O RLY?':
            self.parse_conditional()
        
        # Switch/case statement
        elif token[1] == 'WTF?':
            self.parse_switch()
        
        # Loop statement
        elif token[1] == 'IM IN YR':
            self.parse_loop()
        
        # Function call
        elif token[1] == 'I IZ':
            self.parse_function_call()
        
        # Unknown token: consume silently
        else:
            self.consume()


    # ================================================================
    # ===================== STATEMENTS & I/O =========================
    # ================================================================

    # ------------------------------------------------
    # Function: parse_output
    # Description:
    #     Parse a VISIBLE statement to output values.
    # ------------------------------------------------
    def parse_output(self):
        """================ parse_output ================"""
        self.consume('VISIBLE')
        self.parse_expression()
        print(f"  ✓ Output statement\n")

    # ------------------------------------------------
    # Function: parse_input
    # Description:
    #     Parse a GIMMEH statement to take user input into a variable.
    # ------------------------------------------------
    def parse_input(self):
        """================ parse_input ================"""
        self.consume('GIMMEH')
        if self.current_token() and self.current_token()[2] == 'IDENTIFIER':
            var = self.consume()
            print(f"  ✓ Input to {var[1]}\n")

    # ------------------------------------------------
    # Function: parse_assignment
    # Description:
    #     Parse variable assignment (IDENTIFIER R expression).
    # ------------------------------------------------
    def parse_assignment(self):
        """================ parse_assignment ================"""
        var_token = self.consume()
        if var_token[2] == 'IDENTIFIER' and var_token[1] not in self.symbol_table:
            self.errors.append(f"Variable '{var_token[1]}' is not declared on line {var_token[3]}")
            if self.current_token() and self.current_token()[1] == 'R':
                self.consume('R')
                self.parse_expression()
        else:
            self.consume('R')
            value, data_type = self.parse_expression()
            if value is not None:
                # Update all matching variable keys
                for var_key in list(self.variables.keys()):
                    if var_key[1] == var_token[1]:
                        self.variables[var_key] = (value, data_type)
                        break
                self.symbol_table[var_token[1]] = (value, data_type)
                print(f"  ✓ Assignment: {var_token[1]} = {value} (type: {data_type})\n")
            else:
                print(f"  ✓ Assignment attempted, but no value was parsed\n") 

    # ------------------------------------------------
    # Function: parse_typecast
    # Description:
    #     Parse typecasting operations of two forms:
    #     Type 1: <variable> R MAEK <variable> <type>
    #     Type 2: <variable> IS NOW A <type>
    # ------------------------------------------------
    def parse_typecast(self, cast_type):
        """================ parse_typecast ================"""
        var_token = self.consume()
        
        if cast_type == 1:
            self.consume('R')
            self.consume('MAEK')
            cast_var = self.current_token()
            if cast_var and cast_var[2] == 'IDENTIFIER':
                self.consume()
            type_token = self.current_token()
            if type_token and type_token[2] == 'TYPE':
                target_type = type_token[1]
                self.consume()
                print(f"  ✓ Typecast: {var_token[1]} R MAEK {cast_var[1] if cast_var else '?'} {target_type}")
            else:
                self.errors.append(f"Line {var_token[3]}: Expected type after MAEK")
        
        elif cast_type == 2:
            self.consume('IS NOW A')
            type_token = self.current_token()
            if type_token and type_token[2] == 'TYPE':
                target_type = type_token[1]
                self.consume()
                print(f"  ✓ Typecast: {var_token[1]} IS NOW A {target_type}")
            else:
                self.errors.append(f"Line {var_token[3]}: Expected type after IS NOW A")
        
        print()

    # ================================================================
    # ======================= FUNCTIONS =============================
    # ================================================================

    # ------------------------------------------------
    # Function: parse_function
    # Description:
    #     Parse function declaration (HOW IZ I ... IF U SAY SO)
    # ------------------------------------------------
    def parse_function(self):
        """================ parse_function ================"""
        token = self.consume('HOW IZ I')
        if not token:
            return False
        
        func_name_token = self.current_token()
        if func_name_token and func_name_token[2] == 'IDENTIFIER':
            func_name = func_name_token[1]
            self.consume()
            self.push_stack(f'FUNCTION:{func_name}', token[3])
            print(f"  ✓ Function '{func_name}' declared at line {token[3]}")
            
            params = []
            if self.current_token() and self.current_token()[1] == 'YR':
                self.consume('YR')
                param_token = self.current_token()
                if param_token and param_token[2] == 'IDENTIFIER':
                    params.append(param_token[1])
                    self.consume()
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
            
            while self.current_token() and self.current_token()[1] != 'IF U SAY SO':
                if self.current_token()[1] == 'FOUND YR':
                    self.consume('FOUND YR')
                    self.parse_expression()
                    print(f"    ✓ Return statement")
                else:
                    self.parse_statement()
            
            token = self.consume('IF U SAY SO')
            if token:
                self.pop_stack(f'FUNCTION:{func_name}')
                print(f"  ✓ Function '{func_name}' closed at line {token[3]}\n")
            else:
                self.errors.append(f"Missing 'IF U SAY SO' for function '{func_name}'")
        else:
            self.errors.append(f"Expected function name after HOW IZ I")
        
        return True

    # ------------------------------------------------
    # Function: parse_function_call
    # Description:
    #     Parse function calls (I IZ <func_name> [YR ...] MKAY)
    # ------------------------------------------------
    def parse_function_call(self):
        """================ parse_function_call ================"""
        self.consume('I IZ')
        func_name_token = self.current_token()
        if func_name_token and func_name_token[2] == 'IDENTIFIER':
            func_name = func_name_token[1]
            self.consume()
            print(f"  ✓ Calling function: {func_name}")
            
            args = []
            if self.current_token() and self.current_token()[1] == 'YR':
                self.consume('YR')
                self.parse_expression()
                args.append(1)
                while self.current_token() and self.current_token()[1] == 'AN':
                    self.consume('AN')
                    if self.current_token() and self.current_token()[1] == 'YR':
                        self.consume('YR')
                        self.parse_expression()
                        args.append(1)
            
            if self.current_token() and self.current_token()[1] == 'MKAY':
                self.consume('MKAY')
            
            if args:
                print(f"    with {len(args)} argument(s)\n")
            else:
                print()

    # ================================================================
    # ======================= CONDITIONALS ===========================
    # ================================================================

    # ------------------------------------------------
    # Function: parse_conditional
    # Description:
    #     Parse O RLY? ... YA RLY / NO WAI ... OIC
    # ------------------------------------------------
    def parse_conditional(self):
        """================ parse_conditional ================"""
        token = self.consume('O RLY?')
        self.push_stack('CONDITIONAL', token[3])
        print(f"  ✓ Conditional opened at line {token[3]}")
        
        if self.current_token() and self.current_token()[1] == 'YA RLY':
            self.consume('YA RLY')
            self.push_stack('YA_RLY', self.tokens[self.position-1][3])
            while self.current_token() and self.current_token()[1] not in ['NO WAI', 'MEBBE', 'OIC']:
                self.parse_statement()
            self.pop_stack('YA_RLY')
        
        if self.current_token() and self.current_token()[1] == 'NO WAI':
            self.consume('NO WAI')
            self.push_stack('NO_WAI', self.tokens[self.position-1][3])
            while self.current_token() and self.current_token()[1] != 'OIC':
                self.parse_statement()
            self.pop_stack('NO_WAI')
        
        token = self.consume('OIC')
        if token:
            self.pop_stack('CONDITIONAL')
            print(f"  ✓ Conditional closed at line {token[3]}\n")

    # ================================================================
    # ======================= LOOPS ==================================
    # ================================================================

    # ------------------------------------------------
    # Function: parse_loop
    # Description:
    #     Parse loops (IM IN YR ... IM OUTTA YR)
    # ------------------------------------------------
    def parse_loop(self):
        """================ parse_loop ================"""
        self.consume('IM IN YR')
        label_token = self.current_token()
        if label_token and label_token[2] == 'IDENTIFIER':
            label = label_token[1]
            self.consume()
            self.push_stack(f'LOOP:{label}', label_token[3])
            print(f"  ✓ Loop '{label}' opened at line {label_token[3]}")
            
            while self.current_token() and self.current_token()[1] != 'IM OUTTA YR':
                if self.current_token()[1] == 'GTFO':
                    self.consume('GTFO')
                    print(f"    ✓ Break statement")
                else:
                    self.parse_statement()
            
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

    # ================================================================
    # ======================= SWITCH/CASE ============================
    # ================================================================

    # ------------------------------------------------
    # Function: parse_switch
    # Description:
    #     Parse WTF? ... OMG ... OMGWTF ... OIC switch-case structure
    # ------------------------------------------------
    def parse_switch(self):
        """================ parse_switch ================"""
        token = self.consume('WTF?')
        self.push_stack('SWITCH', token[3])
        print(f"  ✓ Switch opened at line {token[3]}")
        
        while self.current_token() and self.current_token()[1] == 'OMG':
            self.consume('OMG')
            self.parse_expression()
            print(f"    ✓ Case statement")
            while self.current_token() and self.current_token()[1] not in ['OMG', 'OMGWTF', 'OIC']:
                if self.current_token()[1] == 'GTFO':
                    self.consume('GTFO')
                    print(f"      ✓ Break from case")
                    break
                self.parse_statement()
        
        if self.current_token() and self.current_token()[1] == 'OMGWTF':
            self.consume('OMGWTF')
            print(f"    ✓ Default case")
            while self.current_token() and self.current_token()[1] != 'OIC':
                self.parse_statement()
        
        token = self.consume('OIC')
        if token:
            self.pop_stack('SWITCH')
            print(f"  ✓ Switch closed at line {token[3]}\n")

    # ================================================================
    # ======================= UTILITY METHODS ========================
    # ================================================================

    # ------------------------------------------------
    # Function: print_errors
    # Description:
    #     Print all parsing errors accumulated.
    # ------------------------------------------------
    def print_errors(self):
        """================ print_errors ================"""
        if self.errors:
            print("\n========== PARSING ERRORS ==========")
            for error in self.errors:
                print(f"  ✗ {error}")
            print("====================================\n")
        else:
            print("\n✓ No parsing errors found!\n")

    # ------------------------------------------------
    # Function: print_variables
    # Description:
    #     Print all declared variables and their values.
    # ------------------------------------------------
    def print_variables(self):
        """================ print_variables ================"""
        symbol_table = {}
        self.variables.pop(None, None)
        if self.variables:
            print("\n========== ALL VARIABLES LIST ==========")
            for variable in self.variables:
                symbol_table[variable[1]] = self.variables[variable]
            print("====================================\n")
            return symbol_table
        else:
            print("\n✓ No variables found!\n")

    # ------------------------------------------------
    # Function: get_stack_state
    # Description:
    #     Return current stack state for debugging.
    # ------------------------------------------------
    def get_stack_state(self):
        """================ get_stack_state ================"""
        return [s[0] for s in self.stack] if self.stack else []


    
    # ------------------------------------------------
    # Function: adjust_dictionary
    # Description:
    #     adjust the key value pair of the dict 
    #     from key = tuple (Type, Literal, Element, Line)
    #          value = data type
    #   
    #     to key = Literal
    #        value = (data type, element, line)
    # ------------------------------------------------
    def adjust_dictionary(self):
        """================ adjust_dictionary ================"""
        final_variables = {}

        for var_token in self.variables:
            stored = self.variables[var_token]
            
            # Handle tuple storage (value, data_type)
            if isinstance(stored, tuple):
                value, data_type = stored
            else:
                # Fallback for old string-only storage
                value = stored
                data_type = determine_data_type(value)

            # Store as: variable_name -> (value, token_type, line_num, data_type)
            final_variables[var_token[1]] = (value, var_token[2], var_token[3], data_type)

        return final_variables

# ================================================================
# ======================= HELPER FUNCTION ========================
# ================================================================

def parse_lolcode(tokens):
    """================ parse_lolcode ================"""
    parser = Parser(tokens)
    success = parser.parse()
    parser.print_errors()
    symbol_table = parser.adjust_dictionary()
    print("Dictionary")
    for i in symbol_table:
        print(f"{i} : {symbol_table[i]}\n")
    return success, parser, symbol_table
