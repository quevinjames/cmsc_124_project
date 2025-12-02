from parser import Parser
import re

class Execute(Parser):
    def __init__(self, tokens, symbol_table, function_dictionary):
        super().__init__(tokens)
        self.errors = []
        self.symbol_table = symbol_table
        self.function_dictionary = function_dictionary
        self.op_stack = []
        self.it_var = []
        self.outputs = []

        self.function_bodies = {}

    def get_value(self, token):
        """Extract value and datatype from a token"""
        if token[2] == 'IDENTIFIER':
            value = self.symbol_table[token[1]][0]
            dtype = self.symbol_table[token[1]][3]
            
            # If the identifier holds a YARN, try to convert it to numeric
            if dtype == 'YARN':
                # Try to cast YARN to NUMBR or NUMBAR
                if re.match(r'^-?[0-9]+$', str(value)):
                    value = float(value)
                    dtype = 'NUMBAR'
                elif re.match(r'^-?[0-9]+\.[0-9]+$', str(value)):
                    value = float(value)
                    dtype = 'NUMBAR'
                elif value == 'WIN':
                    value = 1.0
                    dtype = 'NUMBAR'
                elif value == 'FAIL':
                    value = 0.0
                    dtype = 'NUMBAR'
                    
        elif token[2] == 'NUMBR':
            value = int(token[1])
            dtype = 'NUMBR'
        elif token[2] == 'NUMBAR':
            value = float(token[1])
            dtype = 'NUMBAR'
        elif token[2] == 'YARN':
            # Implicit typecasting for YARN literals
            yarn_val = token[1]
            if re.match(r'^-?[0-9]+$', yarn_val):
                value = int(yarn_val)
                dtype = 'NUMBR'
            elif re.match(r'^-?[0-9]+\.[0-9]+$', yarn_val):
                value = float(yarn_val)
                dtype = 'NUMBAR'
            elif yarn_val == 'WIN':
                value = 1.0
                dtype = 'NUMBAR'
            elif yarn_val == 'FAIL':
                value = 0.0
                dtype = 'NUMBAR'
            else:
                value = yarn_val
                dtype = 'YARN'
        elif token[2] == 'TROOF':
            # Convert TROOF to numeric for arithmetic
            if token[1] == 'WIN':
                value = 1.0
                dtype = 'NUMBAR'
            else:  # FAIL
                value = 0.0
                dtype = 'NUMBAR'
        else:
            value = token[1]
            dtype = token[2]
        
        return value, dtype

    def get_bool_value(self, token):
        """Extract boolean value from a token"""
        if token[2] == 'IDENTIFIER':
            val, _, _, dtype = self.symbol_table[token[1]]

            if dtype == 'YARN':
                if val in ['0', '0.0', 'FAIL', 'NOOB', '']:
                    return 'FAIL'
                elif val in ['1', '1.0', 'WIN']:
                    return 'WIN'
                else:
                    # Non-empty string that's not explicitly false
                    return 'WIN'

            elif dtype == 'TROOF':
                return 'FAIL' if val == 'FAIL' else 'WIN'

            elif dtype == 'NUMBR':
                return 'FAIL' if val in ['0', 0] else 'WIN'

            elif dtype == 'NUMBAR':
                return 'FAIL' if val in ['0.0', 0.0] else 'WIN'
            
            elif dtype == 'NOOB':
                return 'FAIL'

        elif token[2] == 'TROOF':
            return token[1]  # Already 'WIN' or 'FAIL'

        elif token[2] == 'YARN':
            if token[1] in ['0', '0.0', 'FAIL', 'NOOB', '']:
                return 'FAIL'
            else:
                return 'WIN'

        elif token[2] == 'NUMBR':
            return 'FAIL' if token[1] in [0, '0'] else 'WIN'

        elif token[2] == 'NUMBAR':
            return 'FAIL' if token[1] in [0.0, '0.0'] else 'WIN'

        elif token[2] == 'NOOB':
            return 'FAIL'
        
        # Default to FAIL for unknown types
        return 'FAIL'

    def perform_operation(self, operator, left_val, left_dtype, right_val, right_dtype):
        """Perform the arithmetic operation and determine result type"""
        # Determine result datatype
        if left_dtype == 'NUMBAR' or right_dtype == 'NUMBAR':
            result_dtype = 'NUMBAR'
        else:
            result_dtype = 'NUMBR'

        if left_val == 'NOOB':
            left_val = 0 

        if right_val == 'NOOB':
            right_val = 0
        
        # Convert values to proper numeric types
        left = float(left_val) if left_dtype == 'NUMBAR' else int(left_val)
        right = float(right_val) if right_dtype == 'NUMBAR' else int(right_val)
        
        
        # Perform operation
        match operator:
            case 'SUM OF':
                result = left + right
            case 'DIFF OF':
                result = left - right
            case 'PRODUKT OF':
                result = left * right
            case 'QUOSHUNT OF':
                result = left / right
                result_dtype = 'NUMBAR'  # Division always returns float
            case 'MOD OF':
                result = left % right
            case 'BIGGR OF':
                result = left if left > right else right
            case 'SMALLR OF':
                result = left if left < right else right
            case _:
                raise ValueError(f"Unknown operator: {operator}")
        
        # Convert result to appropriate type
        if result_dtype == 'NUMBR' and operator != 'QUOSHUNT OF':
            result = int(result)
        
        return result, result_dtype

    def perform_bool_operation(self, operator, left_val, right_val=None):
        """Perform boolean operation and return result"""
        result_dtype = 'TROOF'

        # Convert WIN/FAIL to boolean
        left_bool = True if left_val == 'WIN' else False
        
        if right_val is not None:
            right_bool = True if right_val == 'WIN' else False


        match operator:
            case 'BOTH OF':
                result = left_bool and right_bool

            case 'EITHER OF':
                result = left_bool or right_bool

            case 'WON OF':
                result = left_bool ^ right_bool

            case 'NOT':
                result = not left_bool
            
            case _:
                raise ValueError(f"Unknown boolean operator: {operator}")

        # Convert boolean back to WIN/FAIL
        result_val = 'WIN' if result else 'FAIL'

        return result_val, result_dtype

    def perform_comparison_operation(self, operator, left_val, left_dtype, right_val, right_dtype):
        """Perform comparison operation and return TROOF result"""
        
        # Convert values to proper numeric types for comparison
        left = float(left_val) if left_dtype == 'NUMBAR' else int(left_val)
        right = float(right_val) if right_dtype == 'NUMBAR' else int(right_val)
        
        # Perform operation
        match operator:
            case 'BOTH SAEM':
                result = 'WIN' if left == right else 'FAIL'
            case 'DIFFRINT':
                result = 'WIN' if left != right else 'FAIL'
            case _:
                raise ValueError(f"Unknown comparison operator: {operator}")
        
        result_dtype = 'TROOF'
        
        return result, result_dtype

    def perform_infinite_arity_operation(self, operator, operands):
        """Perform infinite arity boolean operation (ALL OF, ANY OF)"""
        result_dtype = 'TROOF'
        
        # Convert all operands to boolean
        bool_values = []
        for operand in operands:
            if operand[2] == 'TROOF':
                bool_val = operand[1]
            elif operand[2] == 'result' and operand[3] == 'TROOF':
                bool_val = operand[1]
            else:
                bool_val = self.get_bool_value(operand)
            
            bool_values.append(True if bool_val == 'WIN' else False)
        
        # Perform operation
        if operator == 'ALL OF':
            # ALL OF: returns WIN if all operands are WIN
            result = all(bool_values)
        elif operator == 'ANY OF':
            # ANY OF: returns WIN if at least one operand is WIN
            result = any(bool_values)
        else:
            raise ValueError(f"Unknown infinite arity operator: {operator}")
        
        # Convert boolean back to WIN/FAIL
        result_val = 'WIN' if result else 'FAIL'
        
        return result_val, result_dtype

    def perform_concat_operation(self, operands):
        """Perform string concatenation on all operands"""
        result_parts = []
        
        for operand in operands:
            # Get the string value of each operand
            if operand[2] == 'YARN':
                result_parts.append(operand[1])
            elif operand[2] == 'result':
                # Already evaluated result
                result_parts.append(str(operand[1]))
            elif operand[2] == 'IDENTIFIER':
                value, dtype = self.get_value(operand)
                result_parts.append(str(value))
            elif operand[2] in ['NUMBR', 'NUMBAR', 'TROOF']:
                result_parts.append(str(operand[1]))
            else:
                result_parts.append(str(operand[1]))
        
        # Concatenate all parts
        result = ''.join(result_parts)
        result_dtype = 'YARN'
        
        return result, result_dtype

    def manage_stack(self):
        """Process stack when we have operator and operands"""
        
        # Handle NOT operator (unary - only needs 2 items on stack)
        if len(self.op_stack) >= 2:
            tos = self.op_stack[-1]      # Operand
            tos1 = self.op_stack[-2]     # Operator
            
            if (isinstance(tos1, tuple) and tos1[1] == 'NOT' and isinstance(tos, tuple)):
                
                # Get boolean value
                if tos[2] == 'TROOF':
                    operand_val = tos[1]
                elif tos[2] in ['result'] and tos[3] == 'TROOF':
                    operand_val = tos[1]
                elif tos[2] == 'IDENTIFIER':
                    operand_val = self.get_bool_value(tos)
                else:
                    operand_val = self.get_bool_value(tos)
                result, result_dtype = self.perform_bool_operation(tos1[1], operand_val, None)
                # Pop the two items
                self.op_stack.pop()
                self.op_stack.pop()
                # Push result back
                new_token = ('NONE', result, 'result', result_dtype)
                self.op_stack.append(new_token)
                return True
        
        # Handle binary operators (need 3 items on stack)
        if len(self.op_stack) < 3:
            return False
            
        tos = self.op_stack[-1]      # Right operand
        tos1 = self.op_stack[-2]     # Left operand  
        tos2 = self.op_stack[-3]     # Operator
        
        # Check if tos2 is an operator and tos/tos1 are values
        if (isinstance(tos2, tuple) and tos2[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF'] and isinstance(tos, tuple) and isinstance(tos1, tuple)):
            
            # Get values and datatypes using get_value for proper conversion
            right_val, right_dtype = self.get_value(tos)
            left_val, left_dtype = self.get_value(tos1)
            
            # Perform the operation
            result, result_dtype = self.perform_operation(
                tos2[1], left_val, left_dtype, right_val, right_dtype
            )
            
            # Pop the three items
            self.op_stack.pop()
            self.op_stack.pop()
            self.op_stack.pop()
            
            # Push result back
            new_token = ('NONE', result, 'result', result_dtype)
            self.op_stack.append(new_token)
            
            return True
        
        elif (isinstance(tos2, tuple) and tos2[1] in ['BOTH OF', 'EITHER OF', 'WON OF'] and isinstance(tos, tuple) and isinstance(tos1, tuple)):
            
            # Get boolean values
            if tos[2] == 'TROOF':
                right_val = tos[1]
            elif tos[2] in ['result'] and tos[3] == 'TROOF':
                right_val = tos[1]
            elif tos[2] == 'IDENTIFIER':
                right_val = self.get_bool_value(tos)
            else:
                # Try to convert other types to boolean
                right_val = self.get_bool_value(tos)

            if tos1[2] == 'TROOF':
                left_val = tos1[1]
            elif tos1[2] in ['result'] and tos1[3] == 'TROOF':
                left_val = tos1[1]
            elif tos1[2] == 'IDENTIFIER':
                left_val = self.get_bool_value(tos1)
            else:
                # Try to convert other types to boolean
                left_val = self.get_bool_value(tos1)

            # Perform boolean operation
            result, result_dtype = self.perform_bool_operation(tos2[1], left_val, right_val)

            # Pop the three items
            self.op_stack.pop()
            self.op_stack.pop()
            self.op_stack.pop()

            # Push result back
            new_token = ('NONE', result, 'result', result_dtype)
            self.op_stack.append(new_token)

            return True

        elif (isinstance(tos2, tuple) and tos2[1] in ['BOTH SAEM', 'DIFFRINT', 'BIGGR OF', 'SMALLR OF'] and isinstance(tos, tuple) and isinstance(tos1, tuple)):

            if tos[2] in ['NUMBR', 'NUMBAR', 'result']:
                right_val = tos[1]
                right_dtype = tos[2] if tos[2] != 'result' else tos[3]
            elif tos[2] == 'IDENTIFIER':
                right_val, right_dtype = self.get_value(tos)
            else:
                return False
            
            if tos1[2] in ['NUMBR', 'NUMBAR', 'result']:
                left_val = tos1[1]
                left_dtype = tos1[2] if tos1[2] != 'result' else tos1[3]
            elif tos1[2] == 'IDENTIFIER':
                left_val, left_dtype = self.get_value(tos1)
            else:
                return False
            
            # Perform the operation
            result, result_dtype = self.perform_comparison_operation(
                tos2[1], left_val, left_dtype, right_val, right_dtype
            )
            
            # Pop the three items
            self.op_stack.pop()
            self.op_stack.pop()
            self.op_stack.pop()
            
            # Push result back
            new_token = ('NONE', result, 'result', result_dtype)
            self.op_stack.append(new_token)
            
            return True

        return False

    def execute_arithmetic_expr(self):
        """Execute arithmetic expression"""
        # Push the operator first
        operator_token = self.consume()
        self.op_stack.append(operator_token)
        
        # Process first operand
        if self.current_token()[1] == '"':
            self.consume()
        
        if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
            # Nested expression
            self.execute_arithmetic_expr()
        else:
            # Simple operand
            self.op_stack.append(self.current_token())
            self.consume()
        
        if self.current_token()[1] == '"':
            self.consume()
        
        # Consume 'AN'
        if self.current_token()[1] == 'AN':
            self.consume()
        
        # Process second operand
        if self.current_token()[1] == '"':
            self.consume()
        
        if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
            # Nested expression
            self.execute_arithmetic_expr()
        else:
            # Simple operand
            self.op_stack.append(self.current_token())
            self.consume()
        
        if self.current_token()[1] == '"':
            self.consume()

        # Try to reduce the stack
        self.manage_stack()

    def execute(self):
        """Main execute entry point"""

        while self.current_token()[1] != 'KTHXBYE':
            self.execute_statement()


    def execute_statement(self):
        """Execute a single statement and advance tokens"""
        token = self.current_token()
        if token[1] == 'VISIBLE':
            # Handle output statement
            self.consume()  # Consume VISIBLE

            self.outputs = []  # Collect all values to print
            no_newline = False  # Track if ending with '!'

            while True:
                current = self.current_token()

                # Check for arithmetic expression
                if current[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF',
                                  'MOD OF', 'BIGGR OF', 'SMALLR OF']:
                    self.execute_arithmetic_expr()
                    while len(self.op_stack) > 1:
                        if not self.manage_stack():
                            break
                    if len(self.op_stack) == 1:
                        result = self.op_stack.pop()
                        self.outputs.append(str(result[1]))

                # Boolean
                elif current[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT']:
                    self.execute_boolean_expr()
                    while len(self.op_stack) > 1:
                        if not self.manage_stack():
                            break
                    if len(self.op_stack) == 1:
                        result = self.op_stack.pop()
                        self.outputs.append(str(result[1]))

                # Infinite-arity boolean
                elif current[1] in ['ALL OF', 'ANY OF']:
                    self.execute_infinite_arity_expr()
                    if len(self.op_stack) == 1:
                        result = self.op_stack.pop()
                        self.outputs.append(str(result[1]))

                # Comparisons
                elif current[1] in ['BOTH SAEM', 'DIFFRINT']:
                    self.execute_comparison_expr()
                    while len(self.op_stack) > 1:
                        if not self.manage_stack():
                            break
                    if len(self.op_stack) == 1:
                        result = self.op_stack.pop()
                        self.outputs.append(str(result[1]))

                # Concatenation
                elif current[1] == 'SMOOSH':
                    self.execute_concat_expr()
                    if len(self.op_stack) == 1:
                        result = self.op_stack.pop()
                        self.outputs.append(str(result[1]))

                elif current[1] == 'IT':
                    self.outputs.append(str(self.it_var))

                # Simple value
                else:
                    value, dtype = self.get_value(current)
                    self.outputs.append(str(value))
                    self.consume()

                # Check for "+"
                if self.current_token() and self.current_token()[1] == '+':
                    self.consume()
                    continue

                break

            # FINAL CHECK: Does it end with "!"?
            if self.current_token() and self.current_token()[1] == '!':
                no_newline = True
                self.consume()  # Consume '!'

            # Output logic
            if no_newline:
                print(f"{''.join(self.outputs)}", end='')
            else:
                print(f"{''.join(self.outputs)}")
        elif token[2] == 'IDENTIFIER' and self.peek()[1] == 'R' and self.peek(2)[1] != 'MAEK':
            self.execute_reassignment()

        elif token[2] == 'IDENTIFIER' and self.peek()[1] == 'IS NOW A':
            self.execute_recast(1)
        
        elif token[2] in ['IDENTIFIER', 'NUMBR', 'NUMBAR', 'YARN', 'TROOF']:
            value, dtype = self.get_value(token)
            self.it_var = value  # IMPORTANT: Update IT variable
            self.consume()
        # ----------------------

        elif token[1] == 'MAEK':
            self.execute_recast(3)

        elif token[1] == 'I HAS A':
            self.execute_declaration()

        elif token[2] == 'IDENTIFIER' and self.peek()[1] == 'IS NOW A':
            self.execute_recast(1)

        elif token[2] == 'IDENTIFIER' and self.peek()[1] == 'R' and self.peek(2)[1] == 'MAEK':
            self.execute_recast(2)

        elif token[1] == 'MAEK':
            self.execute_recast(3)

        elif token[1] == 'GIMMEH':
            self.execute_input()

        elif token[1] == 'O RLY?':
            self.execute_conditional()

        elif token[1] == 'WTF?':
            self.execute_switch()

        elif token[1] == 'IM IN YR':
            self.execute_loop()

        elif token[1] == 'HOW IZ I':
            self.execute_function_definition()

        elif token[1] == 'I IZ':
            self.execute_function()

              
        elif token[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
            self.execute_arithmetic_expr()
            
            # Keep reducing stack until no more reductions possible
            while len(self.op_stack) > 1:
                if not self.manage_stack():
                    break
            
            if len(self.op_stack) == 1:
                final_result = self.op_stack.pop()
                self.it_var.append((final_result[1], final_result[0], final_result[2], final_result[3]))
                return final_result

        elif token[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT']:
            self.execute_boolean_expr()
            
            # Keep reducing stack
            while len(self.op_stack) > 1:
                if not self.manage_stack():
                    break
            
            if len(self.op_stack) == 1:
                final_result = self.op_stack.pop()
                self.it_var.append((final_result[1], final_result[0], final_result[2], final_result[3]))
                return final_result

        elif token[1] in ['ALL OF', 'ANY OF']:
            self.execute_infinite_arity_expr()
            
            if len(self.op_stack) == 1:
                final_result = self.op_stack.pop()
                self.it_var.append((final_result[1], final_result[0], final_result[2], final_result[3]))
                return final_result

        elif token[1] in ['BOTH SAEM', 'DIFFRINT']:
            self.execute_comparison_expr()
            
            # Keep reducing stack
            while len(self.op_stack) > 1:
                if not self.manage_stack():
                    break
            
            if len(self.op_stack) == 1:
                final_result = self.op_stack.pop()
                self.it_var.append((final_result[1], final_result[0], final_result[2], final_result[3]))
                return final_result
        
        elif token[1] == 'SMOOSH':
            self.execute_concat_expr()
            
            if len(self.op_stack) == 1:
                final_result = self.op_stack.pop()
                self.it_var.append((final_result[1], final_result[0], final_result[2], final_result[3]))
                return final_result
        
        else:
            # Unknown token - consume to avoid infinite loop
            self.consume()
        
        # Consume newline if present
        if self.current_token()[2] == 'NEWLINE':
            self.consume()

    def execute_boolean_expr(self):
        """Execute boolean expression"""
        operator_token = self.consume()
        self.op_stack.append(operator_token)

        if self.current_token()[1] == '"':
            self.consume()
        
        if self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT']:
            # Nested expression
            self.execute_boolean_expr()
        else:
            # Simple operand
            self.op_stack.append(self.current_token())
            self.consume()
        
        if self.current_token()[1] == '"':
            self.consume()
        
        # For NOT, we don't need a second operand
        if operator_token[1] == 'NOT':
            self.manage_stack()
            return
        
        # Consume 'AN' for binary operators
        if self.current_token()[1] == 'AN':
            self.consume()
        
        # Process second operand
        if self.current_token()[1] == '"':
            self.consume()
        
        if self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT']:
            # Nested expression
            self.execute_boolean_expr()
        else:
            self.op_stack.append(self.current_token())
            self.consume()
        
        if self.current_token()[1] == '"':
            self.consume()
        
        self.manage_stack()

    def execute_comparison_expr(self):
        """Execute comparison expression"""
        
        operator_token = self.consume()
        self.op_stack.append(operator_token)

        # Handle first operand (left side)
        if self.current_token()[1] == '"':
            self.consume()

        # Check if first operand is a nested expression
        if self.current_token()[1] in ['BOTH SAEM', 'DIFFRINT']:
            self.execute_comparison_expr()
        elif self.current_token()[1] in ['BIGGR OF', 'SMALLR OF', 'SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            self.execute_arithmetic_expr()
        else:
            self.op_stack.append(self.current_token())
            self.consume()

        if self.current_token()[1] == '"':
            self.consume()

        # Consume 'AN' separator
        if self.current_token()[1] == 'AN':
            self.consume()

        # Handle second operand (right side)
        if self.current_token()[1] == '"':
            self.consume()

        # Check if second operand is a nested expression
        if self.current_token()[1] in ['BOTH SAEM', 'DIFFRINT']:
            self.execute_comparison_expr()
        elif self.current_token()[1] in ['BIGGR OF', 'SMALLR OF', 'SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            self.execute_arithmetic_expr()
        else:
            self.op_stack.append(self.current_token())
            self.consume()

        if self.current_token()[1] == '"':
            self.consume()

        self.manage_stack()

    def execute_infinite_arity_expr(self):
        """Execute infinite arity boolean expression (ALL OF, ANY OF)"""
        operator_token = self.consume()
        operator = operator_token[1]
        
        operands = []
        
        # Collect all operands until MKAY
        while self.current_token()[1] != 'MKAY':
            # Skip quotes if present
            if self.current_token()[1] == '"':
                self.consume()
            
            # Skip AN separator
            if self.current_token()[1] == 'AN':
                self.consume()
                continue
            
            # Check for nested boolean expressions
            if self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT']:
                self.execute_boolean_expr()
                
                # Reduce the stack to get the result
                while len(self.op_stack) > 1:
                    if not self.manage_stack():
                        break
                
                if len(self.op_stack) >= 1:
                    operands.append(self.op_stack.pop())
            
            # Check for nested infinite arity expressions
            elif self.current_token()[1] in ['ALL OF', 'ANY OF']:
                self.execute_infinite_arity_expr()
                
                if len(self.op_stack) >= 1:
                    operands.append(self.op_stack.pop())
            
            # Simple operand
            else:
                operands.append(self.current_token())
                self.consume()
            
            # Skip quotes if present
            if self.current_token()[1] == '"':
                self.consume()
        
        # Consume MKAY
        if self.current_token()[1] == 'MKAY':
            self.consume()
        
        # Perform the infinite arity operation
        result, result_dtype = self.perform_infinite_arity_operation(operator, operands)
        
        # Push result to stack
        new_token = ('NONE', result, 'result', result_dtype)
        self.op_stack.append(new_token)


    def execute_concat_expr(self):
        """Execute string concatenation expression (SMOOSH)"""
        self.consume()  # Consume SMOOSH
        
        operands = []
        
        # Collect all operands until we hit a token that's not part of the expression
        while True:
            current = self.current_token()
            
            # Check for end of expression (newline, +, or other statement keywords)
            if current[2] == 'NEWLINE' or current[1] in ['VISIBLE', 'KTHXBYE', '+']:
                break
            
            # Skip quotes if present
            if current[1] == '"':
                self.consume()
                continue
            
            # Skip AN separator
            if current[1] == 'AN':
                self.consume()
                continue
            
            # Check for nested arithmetic expressions
            if current[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
                self.execute_arithmetic_expr()
                
                # Reduce the stack to get the result
                while len(self.op_stack) > 1:
                    if not self.manage_stack():
                        break
                
                if len(self.op_stack) >= 1:
                    operands.append(self.op_stack.pop())
            
            # Check for nested boolean expressions
            elif current[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT']:
                self.execute_boolean_expr()
                
                # Reduce the stack to get the result
                while len(self.op_stack) > 1:
                    if not self.manage_stack():
                        break
                
                if len(self.op_stack) >= 1:
                    operands.append(self.op_stack.pop())
            
            # Check for infinite arity boolean expressions
            elif current[1] in ['ALL OF', 'ANY OF']:
                self.execute_infinite_arity_expr()
                
                if len(self.op_stack) >= 1:
                    operands.append(self.op_stack.pop())
            
            # Check for comparison expressions
            elif current[1] in ['BOTH SAEM', 'DIFFRINT']:
                self.execute_comparison_expr()
                
                # Reduce the stack to get the result
                while len(self.op_stack) > 1:
                    if not self.manage_stack():
                        break
                
                if len(self.op_stack) >= 1:
                    operands.append(self.op_stack.pop())
            
            # Check for nested SMOOSH
            elif current[1] == 'SMOOSH':
                self.execute_concat_expr()
                
                if len(self.op_stack) >= 1:
                    operands.append(self.op_stack.pop())
            
            # Simple operand (literal or identifier)
            else:
                operands.append(current)
                self.consume()
            
            # Skip quotes if present
            if self.current_token()[1] == '"':
                self.consume()
        
        # Perform the concatenation
        result, result_dtype = self.perform_concat_operation(operands)
        
        # Push result to stack
        new_token = ('NONE', result, 'result', result_dtype)
        self.op_stack.append(new_token)

    def execute_declaration(self):
        self.consume()
        var_token = self.consume()
        self.consume()

        current = self.current_token()

        if current[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
            self.execute_arithmetic_expr()
            
            # Keep reducing stack until fully reduced
            while len(self.op_stack) > 1:
                if not self.manage_stack():
                    break
            
            if len(self.op_stack) == 1:
                result = self.op_stack.pop()  # ('NONE', value, 'result', dtype)
                self.symbol_table[var_token[1]] = (result[1], 'IDENTIFIER', var_token[3], result[3])
        
        # Handle boolean expressions
        elif current[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT']:
            self.execute_boolean_expr()
            
            while len(self.op_stack) > 1:
                if not self.manage_stack():
                    break
            
            if len(self.op_stack) == 1:
                result = self.op_stack.pop()  # ('NONE', value, 'result', dtype)
                self.symbol_table[var_token[1]] = (result[1], 'IDENTIFIER', var_token[3], result[3])
        
        # Handle infinite arity boolean expressions
        elif current[1] in ['ALL OF', 'ANY OF']:
            self.execute_infinite_arity_expr()

            if len(self.op_stack) == 1:
                result = self.op_stack.pop()  # ('NONE', value, 'result', dtype)
                self.symbol_table[var_token[1]] = (result[1], 'IDENTIFIER', var_token[3], result[3])
        
        # Handle comparison expressions
        elif current[1] in ['BOTH SAEM', 'DIFFRINT']:
            self.execute_comparison_expr()
            
            while len(self.op_stack) > 1:
                if not self.manage_stack():
                    break
            
            if len(self.op_stack) == 1:
                result = self.op_stack.pop()  # ('NONE', value, 'result', dtype)
                self.symbol_table[var_token[1]] = (result[1], 'IDENTIFIER', var_token[3], result[3])
        
        # Handle string concatenation
        elif current[1] == 'SMOOSH':
            self.execute_concat_expr()
            
            if len(self.op_stack) == 1:
                result = self.op_stack.pop()  # ('NONE', value, 'result', dtype)
                self.symbol_table[var_token[1]] = (result[1], 'IDENTIFIER', var_token[3], result[3])




    def execute_reassignment(self):
        """Execute variable reassignment: <var> R <expr>"""
        var_token = self.consume()  # Get variable name
        self.consume()  # Consume 'R'
        
        current = self.current_token()
        
        # Handle arithmetic expressions
        if current[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
            self.execute_arithmetic_expr()
            
            # Keep reducing stack until fully reduced
            while len(self.op_stack) > 1:
                if not self.manage_stack():
                    break
            
            if len(self.op_stack) == 1:
                result = self.op_stack.pop()  # ('NONE', value, 'result', dtype)
                old_entry = self.symbol_table[var_token[1]]
                self.symbol_table[var_token[1]] = (result[1], old_entry[1], old_entry[2], result[3])
        
        # Handle boolean expressions
        elif current[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT']:
            self.execute_boolean_expr()
            
            while len(self.op_stack) > 1:
                if not self.manage_stack():
                    break
            
            if len(self.op_stack) == 1:
                result = self.op_stack.pop()
                old_entry = self.symbol_table[var_token[1]]
                self.symbol_table[var_token[1]] = (result[1], old_entry[1], old_entry[2], result[3])
        
        # Handle infinite arity boolean expressions
        elif current[1] in ['ALL OF', 'ANY OF']:
            self.execute_infinite_arity_expr()
            
            if len(self.op_stack) == 1:
                result = self.op_stack.pop()
                old_entry = self.symbol_table[var_token[1]]
                self.symbol_table[var_token[1]] = (result[1], old_entry[1], old_entry[2], result[3])
        
        # Handle comparison expressions
        elif current[1] in ['BOTH SAEM', 'DIFFRINT']:
            self.execute_comparison_expr()
            
            while len(self.op_stack) > 1:
                if not self.manage_stack():
                    break
            
            if len(self.op_stack) == 1:
                result = self.op_stack.pop()
                old_entry = self.symbol_table[var_token[1]]
                self.symbol_table[var_token[1]] = (result[1], old_entry[1], old_entry[2], result[3])
        
        # Handle string concatenation
        elif current[1] == 'SMOOSH':
            self.execute_concat_expr()
            
            if len(self.op_stack) == 1:
                result = self.op_stack.pop()
                old_entry = self.symbol_table[var_token[1]]
                self.symbol_table[var_token[1]] = (result[1], old_entry[1], old_entry[2], result[3])
        
        # Handle variable assignment: <variable> R <variable>
        elif current[2] == 'IDENTIFIER':
            if current[1] in self.symbol_table:
                # Get value from the source variable
                source_value = self.symbol_table[current[1]][0]
                source_dtype = self.symbol_table[current[1]][3]
                
                old_entry = self.symbol_table[var_token[1]]
                self.symbol_table[var_token[1]] = (source_value, old_entry[1], old_entry[2], source_dtype)
                self.consume()
        
        # Handle literal assignment: <variable> R <literal>
        elif current[2] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF']:
            value = current[1]
            dtype = current[2]
            
            # Convert to proper type
            if dtype == 'NUMBR':
                value = int(value)
            elif dtype == 'NUMBAR':
                value = float(value)
            
            old_entry = self.symbol_table[var_token[1]]
            self.symbol_table[var_token[1]] = (value, old_entry[1], old_entry[2], dtype)
            self.consume()
        
        else:
            self.consume()
        
        # Consume newline if present
        if self.current_token() and self.current_token()[2] == 'NEWLINE':
            self.consume()

 
    def execute_recast(self, type):
        """Execute type recasting: <variable> IS NOW A <type>"""

        if type == 3:
            self.consume()

        var_token = self.consume()
        var_name = var_token[1]

        
        # Check if variable exists in symbol table
        if var_name not in self.symbol_table:
            self.errors.append(f"Error: Variable '{var_name}' not declared")
            return
        
              
        # Consume 'IS NOW A'
        if self.current_token()[1] == 'IS NOW A' and type == 1:
            self.consume()

        elif self.current_token()[1] == 'R' and self.peek()[1] == 'MAEK' and type == 2:
            self.consume()
            self.consume()
            var_assign = self.consume()

        elif self.current_token()[1] == 'A' and type == 3:
            self.consume()


        if type == 1 or type == 3:
            # Get current variable info
            current_value, old1, old2, current_type = self.symbol_table[var_name]

        elif type == 2:
            current_value, old1, old2, current_type = self.symbol_table[var_assign[1]]




        # Get the target type
        new_type_token = self.current_token()
        new_type = new_type_token[1]
        self.consume()
        
        new_value = None
        
        # ============= NOOB TYPE CASTING =============
        if current_type == 'NOOB':
            if new_type == 'TROOF':
                new_value = 'FAIL'
            elif new_type == 'NUMBR':
                new_value = 0
            elif new_type == 'NUMBAR':
                new_value = 0.0
            elif new_type == 'YARN':
                new_value = ''
            else:
                self.errors.append(f"Error: Cannot cast NOOB to {new_type}")
                return
        
        # ============= TROOF TYPE CASTING =============
        elif current_type == 'TROOF':
            if new_type == 'NUMBR':
                # WIN -> 1, FAIL -> 0
                new_value = 1 if current_value == 'WIN' else 0
            elif new_type == 'NUMBAR':
                # WIN -> 1.0, FAIL -> 0.0
                new_value = 1.0 if current_value == 'WIN' else 0.0
            elif new_type == 'YARN':
                # Convert to string
                new_value = str(current_value)
            elif new_type == 'TROOF':
                # Same type, no change
                new_value = current_value
            else:
                self.errors.append(f"Error: Cannot cast TROOF to {new_type}")
                return
        
        # ============= NUMBAR TYPE CASTING =============
        elif current_type == 'NUMBAR':
            if new_type == 'NUMBR':
                # Truncate decimal portion
                new_value = int(current_value)
            elif new_type == 'YARN':
                # Truncate to 2 decimal places
                new_value = f"{current_value:.2f}"
            elif new_type == 'TROOF':
                # 0.0 -> FAIL, others -> WIN
                new_value = 'FAIL' if current_value == 0.0 else 'WIN'
            elif new_type == 'NUMBAR':
                # Same type, no change
                new_value = current_value
            else:
                self.errors.append(f"Error: Cannot cast NUMBAR to {new_type}")
                return
        
        # ============= NUMBR TYPE CASTING =============
        elif current_type == 'NUMBR':
            if new_type == 'NUMBAR':
                # Convert to floating point
                new_value = float(current_value)
            elif new_type == 'YARN':
                # Convert to string
                new_value = str(current_value)
            elif new_type == 'TROOF':
                # 0 -> FAIL, others -> WIN
                new_value = 'FAIL' if current_value == 0 else 'WIN'
            elif new_type == 'NUMBR':
                # Same type, no change
                new_value = current_value
            else:
                self.errors.append(f"Error: Cannot cast NUMBR to {new_type}")
                return
        
        # ============= YARN TYPE CASTING =============
        elif current_type == 'YARN':
            if new_type == 'NUMBAR':
                # Try to convert to float
                try:
                    # Check if string contains only valid characters (digits, hyphen, period)
                    if all(c.isdigit() or c in '.-' for c in str(current_value)):
                        new_value = float(current_value)
                    else:
                        self.errors.append(f"Error: Cannot cast YARN '{current_value}' to NUMBAR - contains non-numerical characters")
                        return
                except ValueError:
                    self.errors.append(f"Error: Cannot cast YARN '{current_value}' to NUMBAR")
                    return
            
            elif new_type == 'NUMBR':
                # Try to convert to int
                try:
                    # Check if string contains only valid characters (digits, hyphen)
                    if all(c.isdigit() or c == '-' for c in str(current_value)):
                        new_value = int(float(current_value))  # Convert via float to handle "5.0" -> 5
                    else:
                        self.errors.append(f"Error: Cannot cast YARN '{current_value}' to NUMBR - contains non-numerical characters")
                        return
                except ValueError:
                    self.errors.append(f"Error: Cannot cast YARN '{current_value}' to NUMBR")
                    return
            
            elif new_type == 'TROOF':
                # Empty string or "0" or "0.0" -> FAIL, others -> WIN
                if current_value in ['', '0', '0.0', 'FAIL', 'NOOB']:
                    new_value = 'FAIL'
                else:
                    new_value = 'WIN'
            
            elif new_type == 'YARN':
                # Same type, no change
                new_value = current_value
            
            else:
                self.errors.append(f"Error: Cannot cast YARN to {new_type}")
                return
        
        else:
            self.errors.append(f"Error: Unknown source type {current_type}")
            return 

        
        if type == 1:
            # Update symbol table with new value and type
            self.symbol_table[var_name] = (new_value, old1, old2, new_type)

        elif type == 2:
            self.symbol_table[var_name] =  (new_value, old1, old2, new_type)

        elif type == 3:
            self.it_var.append((new_value, old1, old2, new_type))


        
        # Consume newline if present
        if self.current_token() and self.current_token()[2] == 'NEWLINE':
            self.consume()

    def execute_input(self):
        self.consume()

        var_token = self.consume()
        var_name = var_token[1]

        current_value, old1, old2, current_type = self.symbol_table[var_name]

        try:
            import tkinter as tk
            from tkinter import simpledialog
            # GUI mode
            root = tk.Tk()
            root.withdraw()  # Hide the main window
            new_value = simpledialog.askstring("Input", f"Enter value for {var_name}:")
            if new_value is None:  # User cancelled
                new_value = ""
        except:
        # CLI mode
            new_value = input()
    

        self.symbol_table[var_name] = (new_value, old1, old2, 'YARN')

    def execute_conditional(self):
        # Consume 'O RLY?'
        self.consume()
        
        # Skip all newlines after O RLY?
        while self.current_token() and self.current_token()[2] == 'NEWLINE':
            self.position += 1
        
        # Check if IT is truthy
        it_value = self.it_var[-1][0] if self.it_var else None
        is_truthy = it_value in ['WIN', 1, '1', 1.0, '1.0', True]
        
        # Consume 'YA RLY'
        self.consume()
        
        # Skip newlines after YA RLY
        while self.current_token() and self.current_token()[2] == 'NEWLINE':
            self.position += 1
        
        if is_truthy:
            # Execute YA RLY block
            while self.current_token() and self.current_token()[1] not in ['NO WAI', 'OIC']:
                self.execute_statement()
        else:
            # Skip YA RLY block
            while self.current_token() and self.current_token()[1] not in ['NO WAI', 'OIC']:
                self.consume()
        
        # NO WAI block (optional)
        if self.current_token() and self.current_token()[1] == 'NO WAI':
            self.consume()  # Consume 'NO WAI'
            
            # Skip newlines after NO WAI
            while self.current_token() and self.current_token()[2] == 'NEWLINE':
                self.position += 1
            
            if not is_truthy:
                # Execute NO WAI block (only if condition was false)
                while self.current_token() and self.current_token()[1] != 'OIC':
                    self.execute_statement()
            else:
                # Skip NO WAI block (condition was true)
                while self.current_token() and self.current_token()[1] != 'OIC':
                    self.consume()

        
        if self.current_token()[1] == 'OIC':
            self.consume()

    def execute_switch(self):
        # Consume 'WTF?'
        self.consume()
        
        # Skip newlines after WTF?
        while self.current_token() and self.current_token()[2] == 'NEWLINE':
            self.position += 1
        
        it_value = self.it_var[-1][0] if self.it_var else None
        case_matched = False
        
        # Process OMG cases
        while self.current_token() and self.current_token()[1] == 'OMG':
            self.consume()  # Consume 'OMG'
            
            # Get the case literal value
            token = self.current_token()
            if token[2] == 'NUMBR':  # Integer literal
                case_value = int(token[1])
            elif token[2] == 'NUMBAR':  # Float literal
                case_value = float(token[1])
            elif token[2] == 'YARN':  # String literal
                case_value = token[1]
            elif token[1] == 'WIN':  # Boolean literal
                case_value = 'WIN'
            elif token[1] == 'FAIL':  # Boolean literal
                case_value = 'FAIL'
            else:
                case_value = token[1]
            
            self.consume()  # Consume the literal
            
            # Skip newlines after case value
            while self.current_token() and self.current_token()[2] == 'NEWLINE':
                self.position += 1
            
            # Check if this case matches AND we haven't matched a case yet
            if case_value == it_value and not case_matched:
                case_matched = True
                
                # Execute THIS case block only
                while self.current_token() and self.current_token()[1] not in ['OMG', 'OMGWTF', 'OIC']:
                    if self.current_token()[1] == 'GTFO':
                        self.consume()  # Consume 'GTFO'
                        
                        # Skip newlines after GTFO
                        while self.current_token() and self.current_token()[2] == 'NEWLINE':
                            self.position += 1
                        break
                    
                    self.execute_statement()
            else:
                # Skip this case block
                while self.current_token() and self.current_token()[1] not in ['OMG', 'OMGWTF', 'OIC']:
                    if self.current_token()[1] == 'GTFO':
                        self.consume()
                        while self.current_token() and self.current_token()[2] == 'NEWLINE':
                            self.position += 1
                        break
                    self.consume()
        
        # Process OMGWTF (default case)
        if self.current_token() and self.current_token()[1] == 'OMGWTF':
            self.consume()  # Consume 'OMGWTF'
            
            # Skip newlines after OMGWTF
            while self.current_token() and self.current_token()[2] == 'NEWLINE':
                self.position += 1
            
            # Execute default case only if no case matched
            if not case_matched:
                while self.current_token() and self.current_token()[1] != 'OIC':
                    self.execute_statement()
            else:
                # Skip default case
                while self.current_token() and self.current_token()[1] != 'OIC':
                    self.consume()
        
        # Consume 'OIC'
        if self.current_token() and self.current_token()[1] == 'OIC':
            self.consume()

    def execute_loop(self):
        """Execute loop: IM IN YR <label> UPPIN/NERFIN YR <var> TIL/WILE <condition>"""

       
        first = self.current_token()[1]

        if first == "IM IN YR":      # merged
            self.consume()
        else:                       # split
            self.consume()  # IM
            self.consume()  # IN
            self.consume()  # YR

        
        label_token = self.consume()
        label = label_token[1]

        
        operation = self.consume()[1]


        if self.current_token() and self.current_token()[1] == "YR":
            self.consume()

   
        loop_var = self.consume()[1]

     
        condition_type = self.consume()[1]

 
        condition_start_pos = self.position

        # Skip condition expression
        self.skip_condition()

        # Skip newlines after condition
        while self.current_token() and self.current_token()[2] == "NEWLINE":
            self.consume()

        # Store body start
        body_start_pos = self.position

   
        loop_end_pos = self.find_loop_end()
        if loop_end_pos is None:
            raise Exception(f"Syntax Error: Missing 'IM OUTTA YR {label}' for loop '{label}'")


    
        iteration = 0
        max_iterations = 10000

        while iteration < max_iterations:

         
            self.position = condition_start_pos
            condition_result = self.evaluate_loop_condition()

            if condition_type == 'WILE':
                should_continue = (condition_result == 'WIN')
            else:  # TIL
                should_continue = (condition_result == 'FAIL')

            if not should_continue:
                break

         
            self.position = body_start_pos
            broke_out = False

            while self.position < loop_end_pos:
                current = self.current_token()

                # look for split IM OUTTA (to break early)
                if current[1] == 'IM':
                    next_tok = self.peek()
                    if next_tok and next_tok[1] == 'OUTTA':
                        break

                # GTFO handler
                if current[1] == 'GTFO':
                    self.consume()
                    broke_out = True
                    break

                self.execute_statement()

            if broke_out:
                break

           
            
            dtype = self.symbol_table[loop_var][3]
            old_entry = self.symbol_table[loop_var]

            if dtype == 'NUMBR':
                current_val = int(self.symbol_table[loop_var][0])
                if operation == 'UPPIN':
                    new_val = current_val + 1
                else:
                    new_val = current_val - 1
                # Store as integer, not string
                self.symbol_table[loop_var] = (new_val,
                                               old_entry[1],
                                               old_entry[2],
                                               dtype)
            else:  # NUMBAR
                current_val = float(self.symbol_table[loop_var][0])
                if operation == 'UPPIN':
                    new_val = current_val + 1
                else:
                    new_val = current_val - 1
                # Store as float
                self.symbol_table[loop_var] = (new_val,
                                               old_entry[1],
                                               old_entry[2],
                                               dtype)

            iteration += 1

        self.position = loop_end_pos

        end_token = self.current_token()[1]

        # Handle merged "IM OUTTA YR"
        if end_token == "IM OUTTA YR":
            self.consume()
        else:
            # Split version: IM OUTTA YR
            self.consume()
            self.consume()
            self.consume()

        # Consume the loop label
        self.consume()


        # Optional newline
        if self.current_token() and self.current_token()[2] == 'NEWLINE':
            self.consume()



    def skip_condition(self):
        """Skip past the condition expression, supporting merged tokens."""
        depth = 0

        while self.current_token():
            token = self.current_token()[1]

            if token in ("ALL OF", "ANY OF"):
                depth += 1
            elif token == "MKAY" and depth > 0:
                depth -= 1

            if self.current_token()[2] == "NEWLINE" and depth == 0:
                break

            self.consume()


    def find_loop_end(self):
        """Find position of 'IM OUTTA YR', supporting merged and split tokens."""
        saved = self.position
        depth = 1

        while self.position < len(self.tokens):
            tok = self.tokens[self.position][1]

            # merged start
            if tok == "IM IN YR":
                depth += 1

            # merged end
            elif tok == "IM OUTTA YR":
                depth -= 1
                if depth == 0:
                    end = self.position
                    self.position = saved
                    return end

            # split version
            elif tok == "IM":
                if self.position + 2 < len(self.tokens):
                    n1 = self.tokens[self.position + 1][1]
                    n2 = self.tokens[self.position + 2][1]

                    if n1 == "IN" and n2 == "YR":
                        depth += 1
                    elif n1 == "OUTTA" and n2 == "YR":
                        depth -= 1
                        if depth == 0:
                            end = self.position
                            self.position = saved
                            return end

            self.position += 1

        self.position = saved
        return None


    def evaluate_loop_condition(self):
        """Evaluate condition expression and return WIN or FAIL"""

        current = self.current_token()

        # comparisons
        if current[1] in ('BOTH SAEM', 'DIFFRINT'):
            self.execute_comparison_expr()
            while len(self.op_stack) > 1:
                self.manage_stack()
            return self.op_stack.pop()[1] if self.op_stack else 'FAIL'

        # boolean
        elif current[1] in ('BOTH OF', 'EITHER OF', 'WON OF', 'NOT'):
            self.execute_boolean_expr()
            while len(self.op_stack) > 1:
                self.manage_stack()
            return self.op_stack.pop()[1] if self.op_stack else 'FAIL'

        # infinite arity
        elif current[1] in ('ALL OF', 'ANY OF'):
            self.execute_infinite_arity_expr()
            return self.op_stack.pop()[1] if self.op_stack else 'FAIL'

        # direct TROOF literal
        elif current[2] == 'TROOF':
            val = current[1]
            self.consume()
            return val

        # variable boolean
        elif current[2] == 'IDENTIFIER':
            val = self.get_bool_value(current)
            self.consume()
            return val

        return 'FAIL'   

    def store_function_bodies(self):
        """
        Scan through all tokens and store complete function definitions.
        Stores tokens from 'HOW IZ I' to 'IF U SAY SO' (inclusive) for each function.
        Key: function name
        Value: list of tokens for that function
        """
        pos = 0
        
        while pos < len(self.tokens):
            token = self.tokens[pos]
            
            # Check if we found a function definition
            if token[1] == 'HOW IZ I':
                # Get function name (next token after HOW IZ I)
                if pos + 1 < len(self.tokens):
                    func_name = self.tokens[pos + 1][1]
                    
                    # Find the end of this function (IF U SAY SO)
                    start_pos = pos
                    end_pos = pos
                    
                    # Search for IF U SAY SO
                    while end_pos < len(self.tokens):
                        if self.tokens[end_pos][1] == 'IF U SAY SO':
                            # Include IF U SAY SO in the stored tokens
                            end_pos += 1
                            break
                        end_pos += 1
                    
                    # Store the complete function (from HOW IZ I to IF U SAY SO inclusive)
                    self.function_bodies[func_name] = self.tokens[start_pos:end_pos]
                    
                    
                    # Move position past this function
                    pos = end_pos
                    continue
            
            pos += 1
        

                    
    def execute_function_definition(self):
        """Skip function definition during normal execution"""
        token = self.consume('HOW IZ I')
       
        while self.current_token() and self.current_token()[1] != 'IF U SAY SO':
            self.consume()

    def execute_function(self):
        """
        Executes: I IZ <func_name> [YR <arg1> [AN YR <arg2> ...]] MKAY
        """
        if self.current_token()[1] == 'I':
            self.consume(); self.consume() # I, IZ
        else:
            self.consume() # I IZ (merged)

        func_name = self.consume()[1]

        if func_name not in self.function_bodies:
            raise Exception(f"Runtime Error: Function '{func_name}' not defined.")

        expected_params = self.function_dictionary.get(func_name, [])
        args_values = []

        # Parse Arguments
        while self.current_token():
            tok = self.current_token()[1]
            if tok == 'MKAY' or self.current_token()[2] == 'NEWLINE':
                break
                
            if tok == 'YR':
                self.consume()
                args_values.append(self.evaluate_expression())
            elif tok == 'AN':
                self.consume()
                if self.current_token()[1] == 'YR': self.consume()
                args_values.append(self.evaluate_expression())
            else:
                break
        
        if self.current_token()[1] == 'MKAY': self.consume()

        if len(args_values) != len(expected_params):
            raise Exception(f"Function '{func_name}' expects {len(expected_params)} args, got {len(args_values)}")

        old_tokens = self.tokens
        old_position = self.position
        old_symbol_table = self.symbol_table
        
        # Copy global scope so we don't pollute it, but can still read globals if needed
        local_symbol_table = old_symbol_table.copy()
        
        # Bind arguments
        for i, (param_name, _) in enumerate(expected_params):
            # Storing as (value, type, subtype, internal_type)
            local_symbol_table[param_name] = (args_values[i], None, None, 'NOOB')

        self.tokens = self.function_bodies[func_name]
        self.position = 0
        self.symbol_table = local_symbol_table
        
        # Skip the definition line (HOW IZ I ...)
        while self.position < len(self.tokens):
            if self.current_token()[2] == 'NEWLINE':
                self.consume()
                break
            self.consume()

        
        # Default return is NOOB (represented as None in Python)
        return_value = None 

        while self.position < len(self.tokens):
            current = self.current_token()
            token_type = current[1]

            if token_type == 'FOUND YR':
                self.consume()
                return_value = self.evaluate_expression()
                break 
            
            elif token_type == 'GTFO':
                self.consume()
                return_value = 'NOOB' # Explicitly NOOB
                break

            elif token_type == 'IF U SAY SO':
                break

            # CASE D: Execute Statement
            else:
                self.execute_statement()

        self.tokens = old_tokens
        self.position = old_position
        self.symbol_table = old_symbol_table
        
        # Update IT variable
        self.it_var = return_value
        
        # Return for nested calls
        return return_value
    def evaluate_expression(self):
        """Helper to evaluate literal, variable, or arithmetic expression"""
        # You likely already have this logic. 
        # This is just a placeholder to ensure the code above runs.
        current = self.current_token()
        
        # Arithmetic/Logic start
        if current[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'BOTH SAEM']: 
            self.execute_arithmetic_expr() # This should push result to stack
            return self.op_stack.pop()[1] # Return the value
            
        # Literal
        elif current[2] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF']:
            self.consume()
            return current[1]
            
        # Variable
        elif current[2] == 'IDENTIFIER':
            var_name = current[1]
            self.consume()
            return self.symbol_table[var_name][0]
            
        return None

   
def execute_lolcode(tokens, symbol_table, function_dictionary):
    """Entry point for code execution"""
    executor = Execute(tokens, symbol_table, function_dictionary)
    executor.store_function_bodies()
    executor.execute()
    new_symbol_table = executor.symbol_table
    new_function_dictionary = executor.function_dictionary
    new_errors = executor.errors
    new_outputs = executor.outputs
    
   
    return new_symbol_table, new_function_dictionary, new_errors

