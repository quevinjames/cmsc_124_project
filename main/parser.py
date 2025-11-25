"""
LOLCODE Parser
Pushdown Automaton (PDA) inspired parser for syntax analysis
"""

class Parser:
    """
    Pushdown Automaton (PDA) inspired parser for LOLCODE
    """

    def __init__(self, tokens):
        """================ __init__ ================"""
        self.tokens = tokens                 
        self.position = 0                     
        self.stack = []                      
        self.errors = []         
        self.variables = {}
        self.symbol_table = {}
        self.function_line = []
        self.scope_stack = [{}]  
        self.current_function_params = []
        self.function_scopes = {}  




    def current_token(self):
        """================ current_token ================"""
        if self.position < len(self.tokens):
            return self.tokens[self.position]
        return None

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

    def peek(self, offset=1):
        """================ peek ================"""
        pos = self.position + offset
        if pos < len(self.tokens):
            return self.tokens[pos]
        return None


    def push_stack(self, symbol, line_num=0):
        """================ push_stack ================"""
        self.stack.append((symbol, line_num))
        print(f"  [PUSH] Stack: {[s[0] for s in self.stack]}")

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

    def peek_stack(self):
        """================ peek_stack ================"""
        if self.stack:
            return self.stack[-1][0]
        return None


    def push_scope(self):
        """================ push_scope ================"""
        self.scope_stack.append({})
        print(f"  [SCOPE] Pushed new scope (depth: {len(self.scope_stack)})")

    def pop_scope(self):
        """================ pop_scope ================"""
        if len(self.scope_stack) > 1:  # Keep global scope
            self.scope_stack.pop()
            print(f"  [SCOPE] Popped scope (depth: {len(self.scope_stack)})")

    def add_to_scope(self, var_name, value='NOOB', data_type='NOOB'):
        """================ add_to_scope ================"""
        self.scope_stack[-1][var_name] = (value, data_type)
        self.symbol_table[var_name] = (value, data_type, None, None)

    def lookup_variable(self, var_name):
        """================ lookup_variable ================"""
        for scope in reversed(self.scope_stack):
            if var_name in scope:
                return scope[var_name]
        return None

    def variable_exists(self, var_name):
        """================ variable_exists ================"""
        for scope in reversed(self.scope_stack):
            if var_name in scope:
                return True
        return False


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

    def expect_end_of_statement(self, statement_name, line_num):
        """
        Validates that a statement ends properly (NEWLINE or end of tokens).
        Reports error if unexpected tokens appear after the statement.
        """
        token = self.current_token()
        
        if not token:
            return True  # End of file is acceptable
        
        if token[2] == 'NEWLINE':
            return True  # Proper end of statement
        
        # Found unexpected token after statement
        self.errors.append(
            f"Line {line_num}: Unexpected token '{token[1]}' after {statement_name}"
        )
        
        # Consume all tokens until newline to prevent cascading errors
        while token and token[2] != 'NEWLINE':
            self.consume()
            token = self.current_token()
        
        return False


    def parse(self):
        """================ parse ================"""
        print("\n================ START PARSING HERE ================\n")

        if not self.tokens:
            self.errors.append("No tokens to parse - empty program")
            return False

        while self.current_token()[2] == "NEWLINE":
            self.consume()



        if not self.parse_program_start():
            return False

        while self.current_token()[2] == "NEWLINE":
            self.consume()

        if self.current_token()[1] != 'WAZZUP' and ('Variable List Delimiter', 'WAZZUP', 'KEYWORD', 5) in self.tokens:
            self.errors.append(f"Error: Variable declaration block should be right after the HAI")
            return False


        while self.current_token() and self.current_token()[1] != 'KTHXBYE':
            token = self.current_token()

            if token[1] == 'WAZZUP':
                self.parse_variable_list()
            
            elif token[1] == 'HOW IZ I':
                self.parse_function()

            elif token[1] == 'I HAS A':
                self.errors.append(f"Error: I HAS A variable declaration must be inside the WAZZUP block on line {token[3]}")
                return False
            
            else:
                self.parse_statement()

        if not self.parse_program_end():
            self.errors.append(f"Missing closing argument 'KTHXBYE' for opening argument 'HAI' at line {self.tokens[0][3]}")
            return False

        if self.stack:
            print(f"\n[ERROR] Stack not empty at end: {[s[0] for s in self.stack]}")
            self.errors.append("Unclosed structures remain")
            return False
        
        print("\n========== Parse Complete ==========\n")
        return len(self.errors) == 0


    def parse_program_start(self):
        """================ parse_program_start ================"""
        token = self.consume('HAI')
        if not token:
            return False
        
        self.push_stack('PROGRAM', token[3])
        print(f"  ✓ Program started at line {token[3]}\n")
        return True

    def parse_program_end(self):
        """================ parse_program_end ================"""
        token = self.consume('KTHXBYE')
        if not token:
            return False
        
        self.pop_stack('PROGRAM')
        print(f"  ✓ Program ended at line {token[3]}\n")
        return True  

    def parse_variable_declaration(self):
        """================ parse_variable_declaration ================"""
        self.consume('I HAS A')
        
        var_token = self.current_token()
        if var_token and var_token[2] == 'IDENTIFIER':
            var_name = var_token[1]
            if var_name in self.symbol_table:
                self.errors.append(f"Error: Variable name {var_name} is already taken on line {var_token[3]}")
                return False
            self.consume()
            
            if self.current_token() and self.current_token()[1] == 'ITZ':
                self.consume('ITZ')
                value, data_type = self.parse_expression(var_token)
                self.variables[var_token] = (value, data_type, None, None)
                self.symbol_table[var_name] = (value, data_type, None, None)
                print(f"  ✓ Declared variable: {var_name} with value {value} (type: {data_type})")


                self.expect_end_of_statement(f"variable declaration '{var_name}'", {var_token[3]})
            else:
                self.variables[var_token] = ('NOOB', 'NOOB', None, None)
                self.symbol_table[var_name] = ('NOOB', 'NOOB', None, None)
                print(f"  ✓ Declared variable: {var_name} (default: NOOB)")

                
                self.expect_end_of_statement(f"variable declaration '{var_name}'", {var_token[3]})
        else:
            self.errors.append(f"Expected identifier after I HAS A")
            return False
        print()

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
                    if curr[1] not in self.symbol_table and curr[3] not in self.function_line:
                        return False
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
            return False
        
        return True

    
    def parse_expression(self, var_token=None):
        token = self.current_token()
        if not token:
            return (None, None)

        # ===== Literals / Identifiers =====
        if token[2] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'IDENTIFIER']:
            if token[2] == 'IDENTIFIER' and token[1] not in self.symbol_table:
                self.errors.append(f"Variable '{token[1]}' undeclared on line {token[3]} {self.function_line}")
                return (None, None not in self.function_line)

            if token[2] == 'IDENTIFIER':
                stored = self.symbol_table.get(token[1])
                if isinstance(stored, tuple):
                    value, data_type, _, _ = stored
                else:
                    value = stored
                    data_type = determine_data_type(value)
            else:
                value = token[1]
                data_type = token[2]

            if var_token is not None:
                self.variables[var_token] = (value, data_type, None, None)
                self.symbol_table[var_token[1]] = (value, data_type, None, None)

            self.consume()
            return (value, data_type)

        # ===== Math Ops =====
        elif token[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            op = token[1]
            op_token = token
            self.consume()
            left, left_type = self.parse_expression()

            if not self.current_token() or self.current_token()[1] != 'AN':
                self.errors.append(f"Line {op_token[3]}: {op} requires AN keyword and second operand")
                return (None, None)

            self.consume('AN')
            
            if not self.current_token():
                self.errors.append(f"Line {op_token[3]}: {op} requires second operand after AN")
                return (None, None)
            
            right, right_type = self.parse_expression()
            
            if right is None:
                self.errors.append(f"Line {op_token[3]}: {op} missing second operand")
                return (None, None)
            
            result_type = 'NUMBAR' if (left_type == 'NUMBAR' or right_type == 'NUMBAR') else 'NUMBR'
            return (f"({left} {op} {right})", result_type)

        # ===== Boolean Ops (fixed) =====
       
        elif token[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
            op = token[1]
            op_token = token
            self.consume()

            #
            # ==== Special Case: NOT ====
            #
            if op == 'NOT':
                left, _ = self.parse_expression()
                if left is None:
                    self.errors.append(f"Line {op_token[3]}: NOT requires one operand")
                    return (None, None)
                return (f"(NOT {left})", 'TROOF')


            #
            # ===== Variadic Boolean Ops: ALL OF / ANY OF =====
            #
            if op in ['ALL OF', 'ANY OF']:
                operands = []

                # ---- Parse first operand ----
                left, _ = self.parse_expression()
                if left is None:
                    self.errors.append(f"Line {op_token[3]}: {op} requires operands")
                    return (None, None)
                operands.append(left)

                # ---- Expect AN next ----
                if not self.current_token() or self.current_token()[1] != 'AN':
                    self.errors.append(f"Line {op_token[3]}: {op} requires AN between operands")
                    return (None, None)
                self.consume('AN')

                # ---- Parse second operand ----
                right, _ = self.parse_expression()
                if right is None:
                    self.errors.append(f"Line {op_token[3]}: {op} requires second operand")
                    return (None, None)
                operands.append(right)

                # ---- Keep parsing AN <expr> until MKAY ----
                while True:
                    tok = self.current_token()
                    if tok and tok[1] == 'MKAY':
                        self.consume('MKAY')
                        break

                    if not tok or tok[1] != 'AN':
                        self.errors.append(f"Line {op_token[3]}: {op} expects AN or MKAY")
                        return (None, None)

                    self.consume('AN')

                    nxt, _ = self.parse_expression()
                    if nxt is None:
                        self.errors.append(f"Line {op_token[3]}: {op} missing operand after AN")
                        return (None, None)

                    operands.append(nxt)

                # Build final expression
                expr = f"({op} " + " ".join(operands) + ")"
                return (expr, 'TROOF')



            #
            # ===== Binary Boolean Ops: BOTH OF, EITHER OF, WON OF =====
            #
            left, _ = self.parse_expression()

            # require AN
            if not self.current_token() or self.current_token()[1] != 'AN':
                self.errors.append(f"Line {op_token[3]}: {op} requires AN keyword and second operand")
                return (None, None)

            self.consume('AN')

            if not self.current_token():
                self.errors.append(f"Line {op_token[3]}: {op} missing second operand")
                return (None, None)

            right, _ = self.parse_expression()

            if right is None:
                self.errors.append(f"Line {op_token[3]}: {op} missing second operand")
                return (None, None)

            return (f"({op} {left} {right})", 'TROOF')

        # ===== Comparison Ops =====
        elif token[1] in ['BOTH SAEM', 'DIFFRINT', 'BIGGR OF', 'SMALLR OF']:
            op = token[1]
            op_token = token
            self.consume()
            left, _ = self.parse_expression()
            
            if not self.current_token() or self.current_token()[1] != 'AN':
                self.errors.append(f"Line {op_token[3]}: {op} requires AN keyword and second operand")
                return (None, None)
            
            self.consume('AN')

            if not self.current_token():
                self.errors.append(f"Line {op_token[3]}: {op} requires second operand after AN")
                return (None, None)
            
            right, _ = self.parse_expression()
            
            if right is None:
                self.errors.append(f"Line {op_token[3]}: {op} missing second operand")
                return (None, None)
            
            return (f"({left} {op} {right})", 'TROOF')

        # ===== SMOOSH =====
        elif token[1] == 'SMOOSH':
            return self.parse_concat()

        return (None, None)

    def parse_statement(self):
        """================ parse_statement ================"""
        token = self.current_token()
        if not token:
            return
        
        if token[2] == 'IDENTIFIER' and self.peek() and self.peek()[1] == 'IS NOW A':
            self.parse_typecast(2)
        
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
        
        elif token[1] == 'I IZ':
            self.parse_function_call()

        elif token[1] == 'SMOOSH':
            self.parse_concat()

        elif token[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            self.parse_expression()

        elif token[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
            self.parse_expression()

        elif token[1] in ['BOTH SAEM', 'DIFFRINT', 'BIGGR OF', 'SMALLR OF']:
            self.parse_expression()

        else:
            self.consume()

    def parse_output(self):
        """================ parse_output ================"""
        self.consume('VISIBLE')
        
        expressions = []
        
        # Parse first expression
        expr, expr_type = self.parse_expression()
        if expr is not None:
            expressions.append((expr, expr_type))
        
        # Parse additional expressions separated by '+'
        while self.current_token() and self.current_token()[1] == '+':
            plus_token = self.current_token()
            self.consume('+')
            
            # Check if there's an expression after '+'
            if not self.current_token():
                self.errors.append(f"Line {plus_token[3]}: Expected expression after '+'")
                return False
            
            expr, expr_type = self.parse_expression()
            if expr is None:
                self.errors.append(f"Line {plus_token[3]}: Expected expression after '+'")
                return False
            
            expressions.append((expr, expr_type))
        
        print(f"  ✓ Output statement with {len(expressions)} expression(s)\n")

        self.expect_end_of_statement(f"VISIBLE statement line {self.current_token()[3]}", self.current_token()[3])
        return expressions

    def parse_input(self):
        """================ parse_input ================"""
        self.consume('GIMMEH')
        if self.current_token() and self.current_token()[2] == 'IDENTIFIER':
            var = self.consume()
            print(f"  ✓ Input to {var[1]}\n")

            self.expect_end_of_statement(f"GIMMEH statement line: {self.current_token()[3]}", self.current_token()[3])

    def parse_assignment(self):
        """================ parse_assignment ================"""
        var_token = self.consume()
        if var_token[2] == 'IDENTIFIER' and var_token[1] not in self.symbol_table and var_token[3] not in self.function_line:
            self.errors.append(f"Variable '{var_token[1]}' is not declared on line {var_token[3]}")
            if self.current_token() and self.current_token()[1] == 'R':
                self.consume('R')
                self.parse_expression()
            return False
        else:
            self.consume('R')
            # Only validate the expression syntax, don't evaluate it
            value, data_type = self.parse_expression()
            
            # Don't store the value yet - let the executor handle it
            # Just validate that the expression is syntactically correct
            print(f"  ✓ Assignment syntax valid: {var_token[1]} R <expression>\n")
            self.expect_end_of_statement(f"assignment to '{var_token[1]}' line: {var_token[3]}", self.current_token()[3])
            return True

    def parse_typecast(self, cast_type):
        """================ parse_typecast ================"""
        var_token = self.consume()

        if var_token[1] not in self.symbol_table:
            self.errors.append(f"Error: variable {var_token[1]} is not declared on line {var_token[3]}")
            return False
        
        if cast_type == 1:
            self.consume('R')
            self.consume('MAEK')
            cast_var = self.current_token()
            if cast_var and cast_var[2] == 'IDENTIFIER' and cast_var[1] not in self.symbol_table:
                self.errors.append(f"Error: variable {cast_var[1]} is not declared on line {cast_var[3]}")
                return False
            elif cast_var and cast_var[2] == 'IDENTIFIER' and cast_var[1] in self.symbol_table:
                self.consume()

            type_token = self.current_token()
            if type_token and type_token[2] == 'TYPE':
                target_type = type_token[1]
                self.consume()
                print(f"  ✓ Typecast: {var_token[1]} R MAEK {cast_var[1] if cast_var else '?'} {target_type}")

                self.expect_end_of_statement(f"typecast line: {self.current_token()[3]}", self.current_token()[3])
            else:
                self.errors.append(f"Line {var_token[3]}: Expected type after MAEK")
                return False
        
        elif cast_type == 2:
            self.consume('IS NOW A')
            type_token = self.current_token()
            if type_token and type_token[2] == 'TYPE':
                target_type = type_token[1]
                self.consume()
                print(f"  ✓ Typecast: {var_token[1]} IS NOW A {target_type}")

                self.expect_end_of_statement(f"typecast line: {self.current_token()[3]}", self.current_token()[3])
            else:
                self.errors.append(f"Line {var_token[3]}: Expected type after IS NOW A")
                return False
        
        print()


    def parse_function(self):
        """================ parse_function ================"""
        token = self.consume('HOW IZ I')
        if not token:
            return False
        
        func_name_token = self.current_token()
        if func_name_token and func_name_token[2] == 'IDENTIFIER':
            func_start_line = token[3]
            func_name = func_name_token[1]
            self.consume()
            self.push_stack(f'FUNCTION:{func_name}', token[3])
            
            self.push_scope()
            print(f"  ✓ Function '{func_name}' declared at line {token[3]}")
            
            params = []
            if self.current_token() and self.current_token()[1] == 'YR':
                self.consume('YR')
                param_token = self.current_token()
                if param_token and param_token[2] == 'IDENTIFIER':
                    params.append(param_token[1])
                    self.add_to_scope(param_token[1], 'NOOB', 'NOOB')
                    self.consume()
                while self.current_token() and self.current_token()[1] == 'AN':
                    self.consume('AN')
                    if self.current_token() and self.current_token()[1] == 'YR':
                        self.consume('YR')
                        param_token = self.current_token()
                        if param_token and param_token[2] == 'IDENTIFIER':
                            params.append(param_token[1])
                            self.add_to_scope(param_token[1], 'NOOB', 'NOOB')
                            self.consume()
            
            if params:
                print(f"    Parameters: {', '.join(params)}")


            func_end_line = func_start_line
            while self.current_token() and self.current_token()[1] != 'IF U SAY SO':
                if self.current_token()[1] == 'FOUND YR':
                    self.consume('FOUND YR')
                    self.parse_expression()
                    print(f"    ✓ Return statement")
                else:
                    self.parse_statement()

            self.function_scopes[func_name] = {
                'start_line': func_start_line,
                'end_line': func_end_line,
                'params': params
            }
            
            token = self.consume('IF U SAY SO')
            if token:
                self.pop_stack(f'FUNCTION:{func_name}')
                self.pop_scope()
                print(f"  ✓ Function '{func_name}' closed at line {token[3]}\n")
            else:
                self.errors.append(f"Missing 'IF U SAY SO' for function '{func_name}'")
                self.pop_scope()  # Still pop scope even on error
                return False
        else:
            self.errors.append(f"Expected function name after HOW IZ I")
            return False
        
        return True
    def parse_function_call(self):
        """================ parse_function_call ================"""
        self.consume('I IZ')
        func_name_token = self.current_token()

        if func_name_token[1] not in self.function_scopes:
            self.errors.append(f"Error: function name {func_name_token[1]} does not exist on line {func_name_token[3]}" )
            return False

        self.consume()

        args_count = 0

        if self.current_token()[1] == 'YR':
            args_count+=1
            self.consume('YR')
            self.parse_expression()

            while self.current_token()[1] == 'AN':
                self.consume('AN')
                if self.current_token()[1] == 'YR':
                    args_count+=1
                    self.consume('YR')
                    self.parse_expression()

        if self.current_token()[1] == 'MKAY':
            self.consume('MKAY')

        if args_count == len(self.function_scopes[func_name_token[1]]['params']):
            return True

        else:
            self.errors.append(f"Error: Invalid number of parameters, expected {len(self.function_scopes[func_name_token[1]]['params'])} but got {args_count} on line {func_name_token[3]}")
            return False


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
                        return False


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

    def parse_concat(self):
        """================ parse_concat ================"""
        smoosh_token = self.consume('SMOOSH')
        
        # Parse first operand
        if self.current_token() and self.current_token()[1] == '"':
            self.consume('"')
        first_val, _ = self.parse_expression()
        if self.current_token() and self.current_token()[1] == '"':
            self.consume('"')
        
        # Must have at least one AN keyword (requires at least 2 operands)
        if not self.current_token() or self.current_token()[1] != 'AN':
            self.errors.append(f"Line {smoosh_token[3]}: SMOOSH requires at least 2 operands")
            return (None, None)
        
        # Parse remaining operands (AN operand)+
        while self.current_token() and self.current_token()[1] == 'AN':
            an_token = self.consume('AN')
            
            # Check if there's actually a valid operand after AN
            if not self.current_token():
                self.errors.append(f"Line {an_token[3]}: Expected operand after AN in SMOOSH")
                return (None, None)
            
            # Check if next token is a newline, terminator, or end marker (no operand present)
            next_token_type = self.current_token()[0]  # Access token type (first element)
            if next_token_type == 'Newline' or self.current_token()[1] in ['MKAY', 'KTHXBYE']:
                self.errors.append(f"Line {an_token[3]}: Expected operand after AN in SMOOSH")
                return (None, None)
            
            # Parse the operand
            if self.current_token() and self.current_token()[1] == '"':
                self.consume('"')
            next_val, _ = self.parse_expression()
            if self.current_token() and self.current_token()[1] == '"':
                self.consume('"')
            
            # Check if parse_expression failed
            if next_val is None:
                self.errors.append(f"Line {an_token[3]}: Invalid operand after AN in SMOOSH")
                return (None, None)
        
        # Optional MKAY terminator
        if self.current_token() and self.current_token()[1] == 'MKAY':
            self.consume('MKAY')
        
        print(f"  ✓ String concatenation\n")
        return (None, None)


    def print_errors(self):
        """================ print_errors ================"""
        if self.errors:
            print("\n========== PARSING ERRORS ==========")
            for error in self.errors:
                print(f"  ✗ {error}")
            print("====================================\n")
        else:
            print("\n✓ No parsing errors found!\n")

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

    def get_stack_state(self):
        """================ get_stack_state ================"""
        return [s[0] for s in self.stack] if self.stack else []


    
    def adjust_dictionary(self):
        """================ adjust_dictionary ================"""
        final_variables = {}

        for var_token in self.variables:
            stored = self.variables[var_token]
            
            if isinstance(stored, tuple):
                value, data_type, _, _ = stored
            else:
                value = stored
                data_type = determine_data_type(value)

            final_variables[var_token[1]] = (value, var_token[2], var_token[3], data_type)

        return final_variables

    def normalize_symbol(self, entry):
            """Normalize symbol-table entries into a 4-tuple."""
            if len(entry) == 4:
                return entry

            if len(entry) == 2:
                value, dtype = entry
                return (value, dtype, None, dtype)

            if len(entry) == 1:
                return (entry[0], None, None, None)

            return (None, None, None, None)


def parse_lolcode(tokens):
    """================ parse_lolcode ================"""
    parser = Parser(tokens)
    success = parser.parse()
    parser.print_errors()
    symbol_table = parser.adjust_dictionary()
    function_dictionary = {}
    print("Dictionary")
    for i in symbol_table:
        print(f"{i} : {symbol_table[i]}\n")


    print(parser.function_scopes)

    print("\n========== FUNCTION SCOPES ==========")
    for func_name, func_info in parser.function_scopes.items():
        function_dictionary[func_name] = [(param, 'NOOB') for param in func_info['params']]
    print("======================================\n")

    for i in function_dictionary:
        print(f"{i} : {function_dictionary[i]}\n")



    return success, parser, symbol_table, function_dictionary
