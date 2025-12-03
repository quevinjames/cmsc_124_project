import re

"""
LOLCODE Parser
Pushdown Automaton (PDA) inspired parser for syntax analysis
"""
import re

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

    # ---------- New helper to standardize errors ----------
    def add_error(self, line, message):
        """Append an error in the standard format."""
        try:
            lineno = int(line)
        except Exception:
            # fallback if line is None or not int
            lineno = 0
        self.errors.append(f"Error on line {lineno}: {message}")

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
            # use token's line number if available
            line = token[3] if token and len(token) > 3 else 0
            self.add_error(line, f"Expected '{expected_token}', got '{token[1]}'")
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

    def pop_stack(self, expected_symbol=None):
        """================ pop_stack ================"""
        if not self.stack:
            # try to use current token line if available
            ct = self.current_token()
            line = ct[3] if ct and len(ct) > 3 else 0
            self.add_error(line, "Stack underflow - unmatched closing")
            return None

        symbol, line_num = self.stack.pop()

        if expected_symbol and symbol != expected_symbol:
            self.add_error(line_num, f"Mismatched structure: expected '{expected_symbol}', got '{symbol}'")
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

    def pop_scope(self):
        """================ pop_scope ================"""
        if len(self.scope_stack) > 1:  # Keep global scope
            self.scope_stack.pop()

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
        ln = line_num if isinstance(line_num, int) else (token[3] if token and len(token) > 3 else 0)
        self.add_error(ln, f"Unexpected token '{token[1]}' after {statement_name}")

        # Consume all tokens until newline to prevent cascading errors
        while token and token[2] != 'NEWLINE':
            self.consume()
            token = self.current_token()

        return False

    def parse(self):
        """================ parse ================"""

        if not self.tokens:
            self.add_error(0, "No tokens to parse - empty program")
            return False

        # skip initial newlines
        while self.current_token() and self.current_token()[2] == "NEWLINE":
            self.consume()

        if not self.parse_program_start():
            return False

        while self.current_token() and self.current_token()[2] == "NEWLINE":
            self.consume()

        # if WAZZUP exists but not right after HAI, report error at current token line
        ct = self.current_token()
        if ct and ct[1] != 'WAZZUP' and ('Variable List Delimiter', 'WAZZUP', 'KEYWORD', 5) in self.tokens:
            line = ct[3] if len(ct) > 3 else 0
            self.add_error(line, "Variable declaration block should be right after the HAI")
            return False

        while self.current_token() and self.current_token()[1] != 'KTHXBYE':
            token = self.current_token()

            # if token[1] == ',':
            #     self.consume()
            #     continue
            # # ======================

            # self.parse_statement()

            if token[1] == 'WAZZUP':
                self.parse_variable_list()

            elif token[1] == 'HOW IZ I':
                self.parse_function()

            elif token[1] == 'I HAS A':
                line = token[3] if len(token) > 3 else 0
                self.add_error(line, "I HAS A variable declaration must be inside the WAZZUP block")
                return False

            else:
                self.parse_statement()

        if not self.parse_program_end():
            first_line = self.tokens[0][3] if self.tokens and len(self.tokens[0]) > 3 else 0
            self.add_error(first_line, "Missing closing argument 'KTHXBYE' for opening argument 'HAI'")
            return False

        while self.current_token() and self.current_token()[2] == "NEWLINE":
            self.consume()

        if self.current_token():
            ct = self.current_token()
            ln = ct[3] if len(ct) > 3 else 0
            self.add_error(ln, f"Unexpected token {ct[1]} after KTHXBYE")

        if self.stack:
            ct = self.current_token()
            ln = ct[3] if ct and len(ct) > 3 else 0
            self.add_error(ln, "Unclosed structures remain")
            return False

        return len(self.errors) == 0

    def parse_program_start(self):
        """================ parse_program_start ================"""
        token = self.consume('HAI')
        if not token:
            return False

        self.push_stack('PROGRAM', token[3])
        return True

    def parse_program_end(self):
        """================ parse_program_end ================"""
        token = self.consume('KTHXBYE')
        if not token:
            return False

        self.pop_stack('PROGRAM')
        return True

    def parse_variable_declaration(self):
        """================ parse_variable_declaration ================"""
        self.consume('I HAS A')

        var_token = self.current_token()
        if var_token and var_token[2] == 'IDENTIFIER':
            var_name = var_token[1]
            if var_name in self.symbol_table:
                line = var_token[3] if len(var_token) > 3 else 0
                self.add_error(line, f"Variable name {var_name} is already taken")
                return False
            self.consume()

            if self.current_token() and self.current_token()[1] == 'ITZ':
                self.consume('ITZ')
                value, data_type = self.parse_expression(var_token)
                self.variables[var_token] = (value, data_type, None, None)
                self.symbol_table[var_name] = (value, data_type, None, None)

                # expect_end_of_statement accepts a line_num; ensure it's an int
                ln = var_token[3] if len(var_token) > 3 else 0
                self.expect_end_of_statement(f"variable declaration '{var_name}'", ln)
            else:
                self.variables[var_token] = ('NOOB', 'NOOB', None, None)
                self.symbol_table[var_name] = ('NOOB', 'NOOB', None, None)

                ln = var_token[3] if len(var_token) > 3 else 0
                self.expect_end_of_statement(f"variable declaration '{var_name}'", ln)
        else:
            ct = self.current_token()
            ln = ct[3] if ct and len(ct) > 3 else 0
            self.add_error(ln, "Expected identifier after I HAS A")
            return False

    def parse_variable_list(self):
        """================ parse_variable_list ================"""
        token = self.consume('WAZZUP')
        if not token:
            return False

        self.push_stack('VAR_SECTION', token[3])
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
        else:
            self.add_error(line_opened, "Missing BUHBYE for WAZZUP")
            return False

        return True

    def parse_expression(self, var_token=None):
        token = self.current_token()
        if not token:
            return (None, None)

        # ===== Literals / Identifiers =====
        if token[2] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'IDENTIFIER']:
            if token[2] == 'IDENTIFIER' and token[1] not in self.symbol_table:
                ln = token[3] if len(token) > 3 else 0
                msg = f"Variable '{token[1]}' undeclared"
                # preserve any function_line info if present (append)
                if self.function_line:
                    msg = msg + f" {self.function_line}"
                self.add_error(ln, msg)
                return (None, None)

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
                ln = op_token[3] if len(op_token) > 3 else 0
                self.add_error(ln, f"{op} requires AN keyword and second operand")
                return (None, None)

            self.consume('AN')

            if not self.current_token():
                ln = op_token[3] if len(op_token) > 3 else 0
                self.add_error(ln, f"{op} requires second operand after AN")
                return (None, None)

            right, right_type = self.parse_expression()

            if right is None:
                ln = op_token[3] if len(op_token) > 3 else 0
                self.add_error(ln, f"{op} missing second operand")
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
                    ln = op_token[3] if len(op_token) > 3 else 0
                    self.add_error(ln, "NOT requires one operand")
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
                    ln = op_token[3] if len(op_token) > 3 else 0
                    self.add_error(ln, f"{op} requires operands")
                    return (None, None)
                operands.append(left)

                # ---- Expect AN next ----
                if not self.current_token() or self.current_token()[1] != 'AN':
                    ln = op_token[3] if len(op_token) > 3 else 0
                    self.add_error(ln, f"{op} requires AN between operands")
                    return (None, None)
                self.consume('AN')

                # ---- Parse second operand ----
                right, _ = self.parse_expression()
                if right is None:
                    ln = op_token[3] if len(op_token) > 3 else 0
                    self.add_error(ln, f"{op} requires second operand")
                    return (None, None)
                operands.append(right)

                # ---- Keep parsing AN <expr> until MKAY ----
                while True:
                    tok = self.current_token()
                    if tok and tok[1] == 'MKAY':
                        self.consume('MKAY')
                        break

                    if not tok or tok[1] != 'AN':
                        ln = op_token[3] if len(op_token) > 3 else 0
                        self.add_error(ln, f"{op} expects AN or MKAY")
                        return (None, None)

                    self.consume('AN')

                    nxt, _ = self.parse_expression()
                    if nxt is None:
                        ln = op_token[3] if len(op_token) > 3 else 0
                        self.add_error(ln, f"{op} missing operand after AN")
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
                ln = op_token[3] if len(op_token) > 3 else 0
                self.add_error(ln, f"{op} requires AN keyword and second operand")
                return (None, None)

            self.consume('AN')

            if not self.current_token():
                ln = op_token[3] if len(op_token) > 3 else 0
                self.add_error(ln, f"{op} missing second operand")
                return (None, None)

            right, _ = self.parse_expression()

            if right is None:
                ln = op_token[3] if len(op_token) > 3 else 0
                self.add_error(ln, f"{op} missing second operand")
                return (None, None)

            return (f"({op} {left} {right})", 'TROOF')

        # ===== Comparison Ops =====
        elif token[1] in ['BOTH SAEM', 'DIFFRINT', 'BIGGR OF', 'SMALLR OF']:
            op = token[1]
            op_token = token
            self.consume()
            left, _ = self.parse_expression()

            if not self.current_token() or self.current_token()[1] != 'AN':
                ln = op_token[3] if len(op_token) > 3 else 0
                self.add_error(ln, f"{op} requires AN keyword and second operand")
                return (None, None)

            self.consume('AN')

            if not self.current_token():
                ln = op_token[3] if len(op_token) > 3 else 0
                self.add_error(ln, f"{op} requires second operand after AN")
                return (None, None)

            right, _ = self.parse_expression()

            if right is None:
                ln = op_token[3] if len(op_token) > 3 else 0
                self.add_error(ln, f"{op} missing second operand")
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

        elif token[1] == 'OIC' and 'CONDITIONAL' not in self.stack:
            ln = token[3] if len(token) > 3 else 0
            self.add_error(ln, "Invalid keyword OIC, O RLY? not found")
            self.consume()

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
                ln = plus_token[3] if len(plus_token) > 3 else 0
                self.add_error(ln, "Expected expression after '+'")
                return False

            expr, expr_type = self.parse_expression()
            if expr is None:
                ln = plus_token[3] if len(plus_token) > 3 else 0
                self.add_error(ln, "Expected expression after '+'")
                return False

            expressions.append((expr, expr_type))


        # If current token exists use its line, else 0
        ct = self.current_token()
        ln = ct[3] if ct and len(ct) > 3 else 0
        if self.current_token()[1] == '!':
            pass 
        else:
            self.expect_end_of_statement(f"VISIBLE statement line {ln}", ln)
        return expressions

    def parse_input(self):
        """================ parse_input ==============="""
        self.consume('GIMMEH')
        ct = self.current_token()
        if ct and ct[2] == 'IDENTIFIER':
            if ct[1] not in self.symbol_table:
                ln = ct[3] if len(ct) > 3 else 0
                self.add_error(ln, f"Variable identifier {ct[1]} does not yet exist")
                return False

            var = self.consume()
            ct2 = self.current_token()
            ln2 = ct2[3] if ct2 and len(ct2) > 3 else 0
            self.expect_end_of_statement(f"GIMMEH statement line: {ln2}", ln2)

        else:
            ct = self.current_token()
            ln = ct[3] if ct and len(ct) > 3 else 0
            self.add_error(ln, "Expecting an identifier after GIMMEH statement")
            return False

    def parse_assignment(self):
        """================ parse_assignment ==============="""
        var_token = self.consume()
        if var_token is None:
            # nothing to do
            return False

        if var_token[2] == 'IDENTIFIER' and var_token[1] not in self.symbol_table and var_token[3] not in self.function_line:
            ln = var_token[3] if len(var_token) > 3 else 0
            self.add_error(ln, f"Variable '{var_token[1]}' is not declared")
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
            ct = self.current_token()
            ln = ct[3] if ct and len(ct) > 3 else 0
            self.expect_end_of_statement(f"assignment to '{var_token[1]}' line: {var_token[3]}", ln)
            return True

    def parse_typecast(self, cast_type):
        """================ parse_typecast ================"""
        var_token = self.consume()

        if var_token is None:
            return False

        if var_token[1] not in self.symbol_table:
            ln = var_token[3] if len(var_token) > 3 else 0
            self.add_error(ln, f"variable {var_token[1]} is not declared")
            return False

        if cast_type == 1:
            self.consume('R')
            self.consume('MAEK')
            cast_var = self.current_token()
            if cast_var and cast_var[2] == 'IDENTIFIER' and cast_var[1] not in self.symbol_table:
                ln = cast_var[3] if len(cast_var) > 3 else 0
                self.add_error(ln, f"variable {cast_var[1]} is not declared")
                return False
            elif cast_var and cast_var[2] == 'IDENTIFIER' and cast_var[1] in self.symbol_table:
                self.consume()

            type_token = self.current_token()
            if type_token and type_token[2] == 'TYPE':
                target_type = type_token[1]
                self.consume()

                ct = self.current_token()
                ln = ct[3] if ct and len(ct) > 3 else 0
                self.expect_end_of_statement(f"typecast line: {ln}", ln)
            else:
                ln = var_token[3] if len(var_token) > 3 else 0
                self.add_error(ln, "Expected type after MAEK")
                return False

        elif cast_type == 2:
            self.consume('IS NOW A')
            type_token = self.current_token()
            if type_token and type_token[2] == 'TYPE':
                target_type = type_token[1]
                self.consume()

                ct = self.current_token()
                ln = ct[3] if ct and len(ct) > 3 else 0
                self.expect_end_of_statement(f"typecast line: {ln}", ln)
            else:
                ln = var_token[3] if len(var_token) > 3 else 0
                self.add_error(ln, "Expected type after IS NOW A")
                return False


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


            func_end_line = func_start_line
            while self.current_token() and self.current_token()[1] != 'IF U SAY SO':
                if self.current_token()[1] == 'FOUND YR':
                    self.consume('FOUND YR')
                    self.parse_expression()
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
            else:
                self.add_error(func_start_line, f"Missing 'IF U SAY SO' for function '{func_name}'")
                self.pop_scope()  # Still pop scope even on error
                return False
        else:
            ct = self.current_token()
            ln = ct[3] if ct and len(ct) > 3 else 0
            self.add_error(ln, "Expected function name after HOW IZ I")
            return False

        return True

    def parse_function_call(self):
        """================ parse_function_call ================"""
        self.consume('I IZ')
        func_name_token = self.current_token()

        if func_name_token is None:
            self.add_error(0, "Expected function name after I IZ")
            return False

        if func_name_token[1] not in self.function_scopes:
            ln = func_name_token[3] if len(func_name_token) > 3 else 0
            self.add_error(ln, f"function name {func_name_token[1]} does not exist")
            return False

        self.consume()

        args_count = 0

        if self.current_token() and self.current_token()[1] == 'YR':
            args_count += 1
            self.consume('YR')
            self.parse_expression()

            while self.current_token() and self.current_token()[1] == 'AN':
                self.consume('AN')
                if self.current_token() and self.current_token()[1] == 'YR':
                    args_count += 1
                    self.consume('YR')
                    self.parse_expression()

        if self.current_token() and self.current_token()[1] == 'MKAY':
            self.consume('MKAY')

        expected = len(self.function_scopes[func_name_token[1]]['params'])
        if args_count == expected:
            return True
        else:
            ln = func_name_token[3] if len(func_name_token) > 3 else 0
            self.add_error(ln, f"Invalid number of parameters, expected {expected} but got {args_count}")
            return False

    def parse_conditional(self):
        """================ parse_conditional ================"""
        token = self.consume('O RLY?')
        if not token:
            return
        self.push_stack('CONDITIONAL', token[3])

        # Validate end of O RLY? statement
        if not self.expect_end_of_statement('O RLY?', token[3]):
            self.pop_stack('CONDITIONAL')
            return

        # Consume newline after O RLY?
        while self.current_token() and self.current_token()[2] == 'NEWLINE':
            self.position += 1

        # YA RLY is mandatory
        if not self.current_token() or self.current_token()[1] != 'YA RLY':
            self.add_error(token[3], "Expected YA RLY after O RLY?")
            self.pop_stack('CONDITIONAL')
            return

        ya_rly_token = self.consume('YA RLY')
        self.push_stack('YA_RLY', ya_rly_token[3])

        # Validate end of YA RLY statement
        if not self.expect_end_of_statement('YA RLY', ya_rly_token[3]):
            self.pop_stack('YA_RLY')
            self.pop_stack('CONDITIONAL')
            return

        # Consume newline after YA RLY
        while self.current_token() and self.current_token()[2] == 'NEWLINE':
            self.position += 1

        # Parse YA RLY block
        while self.current_token() and self.current_token()[1] not in ['NO WAI', 'OIC']:
            self.parse_statement()

        self.pop_stack('YA_RLY')

        # NO WAI is optional
        if self.current_token() and self.current_token()[1] == 'NO WAI':
            no_wai_token = self.consume('NO WAI')
            self.push_stack('NO_WAI', no_wai_token[3])

            # Validate end of NO WAI statement
            if not self.expect_end_of_statement('NO WAI', no_wai_token[3]):
                self.pop_stack('NO_WAI')
                self.pop_stack('CONDITIONAL')
                return

            # Consume newline after NO WAI
            while self.current_token() and self.current_token()[2] == 'NEWLINE':
                self.position += 1

            # Parse NO WAI block
            while self.current_token() and self.current_token()[1] != 'OIC':
                self.parse_statement()

            self.pop_stack('NO_WAI')

        # OIC is mandatory
        if not self.current_token() or self.current_token()[1] != 'OIC':
            self.add_error(token[3], "Expected OIC to close conditional")
            self.pop_stack('CONDITIONAL')
            return

        oic_token = self.consume('OIC')
        self.pop_stack('CONDITIONAL')

    def parse_loop(self):
        """================ parse_loop ================"""
        self.consume('IM IN YR')
        label_token = self.current_token()
        
        # Validate Label
        if label_token and label_token[2] == 'IDENTIFIER':
            label = label_token[1]
            self.consume()
            self.push_stack(f'LOOP:{label}', label_token[3])
        else:
            self.add_error(self.current_token()[3], "Expected loop label after IM IN YR")
            return False

        #  Validate Operation (UPPIN / NERFIN)
        if self.current_token()[1] in ['UPPIN', 'NERFIN']:
            self.consume()
        else:
            self.add_error(self.current_token()[3], "Expected UPPIN or NERFIN operation")
            self.pop_stack(f'LOOP:{label}')  # Fix: Clean stack on error
            return False

        #  Validate 'YR'
        if self.current_token()[1] == 'YR':
            self.consume('YR')
        else:
            self.add_error(self.current_token()[3], "Expected YR after operation")
            self.pop_stack(f'LOOP:{label}')
            return False

        #  Validate Loop Variable
        if self.current_token()[2] == 'IDENTIFIER':
            if self.current_token()[1] not in self.symbol_table:
                self.add_error(self.current_token()[3], f"Variable {self.current_token()[1]} not found")
                self.pop_stack(f'LOOP:{label}')
                return False
            self.consume()
        else:
            self.add_error(self.current_token()[3], "Expected identifier after YR")
            self.pop_stack(f'LOOP:{label}')
            return False

        #  Validate TIL / WILE (Fixed Logic)
        if self.current_token()[1] in ['TIL', 'WILE']:
            self.consume()
            #  Parse Expression (Relaxed Logic: allow any expression)
            expr_val, expr_type = self.parse_expression()
            if expr_val is None:
                self.pop_stack(f'LOOP:{label}')
                return False
        else:
            self.add_error(self.current_token()[3], "Expected TIL or WILE")
            self.pop_stack(f'LOOP:{label}')
            return False

        #  Consume Newlines before body
        while self.current_token() and self.current_token()[2] == 'NEWLINE':
            self.consume()

        #  Loop Body
        while self.current_token() and self.current_token()[1] != 'IM OUTTA YR':
            if self.current_token()[1] == 'KTHXBYE':
                self.add_error(self.current_token()[3], "Unexpected end of file in loop (missing IM OUTTA YR)")
                self.pop_stack(f'LOOP:{label}')
                return False
            
            if self.current_token()[1] == 'GTFO':
                gtfo_token = self.consume('GTFO')
                # Handle GTFO if needed, usually just continue parsing syntax
            else:
                self.parse_statement()

        # Loop End
        if self.current_token() and self.current_token()[1] == 'IM OUTTA YR':
            self.consume('IM OUTTA YR')
            exit_label = self.current_token()
            if exit_label and exit_label[2] == 'IDENTIFIER':
                if exit_label[1] == label:
                    self.consume()
                    self.pop_stack(f'LOOP:{label}')
                else:
                    self.add_error(exit_label[3], f"Loop label mismatch: '{label}' vs '{exit_label[1]}'")
                    self.pop_stack(f'LOOP:{label}')
                    return False
            else:
                self.add_error(exit_label[3], "Expected label after IM OUTTA YR")
                self.pop_stack(f'LOOP:{label}')
                return False
        else:
            self.add_error(self.current_token()[3], "Expected IM OUTTA YR")
            self.pop_stack(f'LOOP:{label}')
            return False

        return True


    def parse_switch(self):
        """================ parse_switch ================"""
        token = self.consume('WTF?')
        if not token:
            return
        self.push_stack('SWITCH', token[3])

        # Validate end of WTF? statement
        if not self.expect_end_of_statement('WTF?', token[3]):
            self.pop_stack('SWITCH')
            return

        # Consume all newlines after WTF?
        while self.current_token() and self.current_token()[2] == 'NEWLINE':
            self.position += 1

        # Parse OMG cases
        while self.current_token() and self.current_token()[1] == 'OMG':
            omg_token = self.consume('OMG')
            self.parse_expression()

            # Validate end of OMG statement
            if not self.expect_end_of_statement('OMG', omg_token[3]):
                self.pop_stack('SWITCH')
                return


            # Consume all newlines after OMG
            while self.current_token() and self.current_token()[2] == 'NEWLINE':
                self.position += 1

            # Parse case block
            while self.current_token() and self.current_token()[1] not in ['OMG', 'OMGWTF', 'OIC']:
                if self.current_token()[1] == 'GTFO':
                    gtfo_token = self.consume('GTFO')

                    # Validate end of GTFO statement
                    if not self.expect_end_of_statement('GTFO', gtfo_token[3]):
                        self.pop_stack('SWITCH')
                        return


                    # Consume all newlines after GTFO
                    while self.current_token() and self.current_token()[2] == 'NEWLINE':
                        self.position += 1

                    break
                self.parse_statement()

        # Parse OMGWTF (default case)
        if self.current_token() and self.current_token()[1] == 'OMGWTF':
            omgwtf_token = self.consume('OMGWTF')

            # Validate end of OMGWTF statement
            if not self.expect_end_of_statement('OMGWTF', omgwtf_token[3]):
                self.pop_stack('SWITCH')
                return


            # Consume all newlines after OMGWTF
            while self.current_token() and self.current_token()[2] == 'NEWLINE':
                self.position += 1

            # Parse default case block
            while self.current_token() and self.current_token()[1] != 'OIC':
                self.parse_statement()

        # Consume OIC
        token = self.consume('OIC')
        if token:
            self.pop_stack('SWITCH')

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
            ln = smoosh_token[3] if len(smoosh_token) > 3 else 0
            self.add_error(ln, "SMOOSH requires at least 2 operands")
            return (None, None)

        # Parse remaining operands (AN operand)+
        while self.current_token() and self.current_token()[1] == 'AN':
            an_token = self.consume('AN')

            # Check if there's actually a valid operand after AN
            if not self.current_token():
                ln = an_token[3] if len(an_token) > 3 else 0
                self.add_error(ln, "Expected operand after AN in SMOOSH")
                return (None, None)

            # Check if next token is a newline, terminator, or end marker (no operand present)
            next_token_type = self.current_token()[0]  # Access token type (first element)
            if next_token_type == 'Newline' or (self.current_token() and self.current_token()[1] in ['MKAY', 'KTHXBYE']):
                ln = an_token[3] if len(an_token) > 3 else 0
                self.add_error(ln, "Expected operand after AN in SMOOSH")
                return (None, None)

            # Parse the operand
            if self.current_token() and self.current_token()[1] == '"':
                self.consume('"')
            next_val, _ = self.parse_expression()
            if self.current_token() and self.current_token()[1] == '"':
                self.consume('"')

            # Check if parse_expression failed
            if next_val is None:
                ln = an_token[3] if len(an_token) > 3 else 0
                self.add_error(ln, "Invalid operand after AN in SMOOSH")
                return (None, None)

        # Optional MKAY terminator
        if self.current_token() and self.current_token()[1] == 'MKAY':
            self.consume('MKAY')

        return (None, None)

   
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
    symbol_table = parser.adjust_dictionary()
    parser_errors = parser.errors
    function_dictionary = {}


    return success, parser, symbol_table, function_dictionary, parser_errors
