from parser import Parser

class Execute(Parser):
    def __init__(self, tokens, symbol_table, function_dictionary):
        super().__init__(tokens)
        self.errors = []
        self.symbol_table = symbol_table
        self.function_dictionary = function_dictionary
        self.op_stack = []

    def get_value(self, token):
        """Extract value and datatype from a token"""
        if token[2] == 'IDENTIFIER':
            value = self.symbol_table[token[1]][0]
            dtype = self.symbol_table[token[1]][3]
        elif token[2] == 'NUMBR':
            value = int(token[1])
            dtype = 'NUMBR'
        elif token[2] == 'NUMBAR':
            value = float(token[1])
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
            
            # Get values and datatypes
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
        print("\n================= START EXECUTE HERE =================\n")
        
        while self.current_token()[1] != 'KTHXBYE':
            self.execute_statement()

    def execute_statement(self):
        """Execute a single statement and advance tokens"""
        token = self.current_token()

        if token[1] == 'VISIBLE':
            # Handle output statement
            self.consume()  # Consume VISIBLE
            
            outputs = []  # Collect all values to print
            
            while True:
                current = self.current_token()
                
                # Check for arithmetic expression
                if current[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
                    self.execute_arithmetic_expr()
                    
                    # Keep reducing stack until no more reductions possible
                    while len(self.op_stack) > 1:
                        if not self.manage_stack():
                            break
                    
                    if len(self.op_stack) == 1:
                        result = self.op_stack.pop()
                        outputs.append(str(result[1]))
                    else:
                        print(f"Error: Stack not fully reduced. Remaining: {self.op_stack}")
                
                # Check for boolean expression
                elif current[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT']:
                    self.execute_boolean_expr()
                    
                    # Keep reducing stack until no more reductions possible
                    while len(self.op_stack) > 1:
                        if not self.manage_stack():
                            break
                    
                    if len(self.op_stack) == 1:
                        result = self.op_stack.pop()
                        outputs.append(str(result[1]))
                    else:
                        print(f"Error: Stack not fully reduced. Remaining: {self.op_stack}")
                
                # Check for infinite arity boolean expression
                elif current[1] in ['ALL OF', 'ANY OF']:
                    self.execute_infinite_arity_expr()
                    
                    if len(self.op_stack) == 1:
                        result = self.op_stack.pop()
                        outputs.append(str(result[1]))
                    else:
                        print(f"Error: Stack not fully reduced. Remaining: {self.op_stack}")

                elif current[1] in ['BOTH SAEM', 'DIFFRINT']:
                    self.execute_comparison_expr()

                    while len(self.op_stack) > 1:
                        if not self.manage_stack():
                            break

                    if len(self.op_stack) == 1:
                        result = self.op_stack.pop()
                        outputs.append(str(result[1]))

                    else:
                        print(f"Error: Stack not fully reduced. Remaining: {self.op_stack}")
                else:
                    # Simple value to print
                    value, dtype = self.get_value(current)
                    outputs.append(str(value))
                    self.consume()
                
                # Check if there's a + separator for more expressions
                if self.current_token() and self.current_token()[1] == '+':
                    self.consume()  # Consume the +
                    continue
                else:
                    break  # No more expressions to process
            
            # Print all collected outputs concatenated
            print(f"OUTPUT: {''.join(outputs)}")
        
        elif token[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
            self.execute_arithmetic_expr()
            
            # Keep reducing stack until no more reductions possible
            while len(self.op_stack) > 1:
                if not self.manage_stack():
                    break
            
            if len(self.op_stack) == 1:
                print(f"Arithmetic successful: {self.op_stack[0]}")
                final_result = self.op_stack.pop()
                return final_result
            else:
                print(f"Error: Stack not fully reduced. Remaining: {self.op_stack}")

        elif token[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT']:
            self.execute_boolean_expr()
            
            # Keep reducing stack
            while len(self.op_stack) > 1:
                if not self.manage_stack():
                    break
            
            if len(self.op_stack) == 1:
                print(f"Boolean successful: {self.op_stack[0]}")
                final_result = self.op_stack.pop()
                return final_result
            else:
                print(f"Error: Stack not fully reduced. Remaining: {self.op_stack}")

        elif token[1] in ['ALL OF', 'ANY OF']:
            self.execute_infinite_arity_expr()
            
            if len(self.op_stack) == 1:
                print(f"Infinite arity boolean successful: {self.op_stack[0]}")
                final_result = self.op_stack.pop()
                return final_result
            else:
                print(f"Error: Stack not fully reduced. Remaining: {self.op_stack}")

        elif token[1] in ['BOTH SAEM', 'DIFFRINT']:
            self.execute_comparison_expr()
        
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

   
   

def execute_lolcode(tokens, symbol_table, function_dictionary):
    """Entry point for code execution"""
    executor = Execute(tokens, symbol_table, function_dictionary)
    executor.execute()
    
    if executor.errors:
        print("\n=== EXECUTION ERRORS FOUND ===")
        for error in executor.errors:
            print(error)
        return False, executor.errors
    else:
        print("\n=== EXECUTION COMPLETE ===")
        return True, executor.errors
