import re
from parser import Parser

class SemanticAnalyzer(Parser):
    def __init__(self, tokens, symbol_table, function_dictionary):
        super().__init__(tokens)
        self.errors = []
        self.symbol_table = symbol_table
        self.function_dictionary = function_dictionary
        self.boolean_typecast = {}
        self.function_line = []
        self.inside_function = False  # Track if we're inside a function definition
    
    def analyze(self):
        """Main analysis entry point"""
        print("\n==================== START ANALYZE HERE ================\n")
        
        while self.current_token()[1] != 'KTHXBYE':
            self.analyze_statement()
            
    def analyze_statement(self):
        """Analyze a single statement and advance tokens"""
        token = self.current_token()

        if token[1] == 'HOW IZ I':
            self.inside_function = True  # Enter function definition
            self.consume('HOW IZ I')
            
            # Function name
            func_name_token = self.current_token()
            func_name = func_name_token[1]
            self.consume()  # consume function name

            # Extract parameters
            params = self.extract_function_params()
            
            # Save function signature
            self.function_scopes[func_name] = {
                "params": params
            }

            # Enter function scope
            self.push_scope()

            # Insert parameters into local scope
            for p in params:
                self.add_to_scope(p, "NOOB", "NOOB")
                print(f"  Added parameter '{p}' to scope")

            return        

        elif token[1] == 'IF U SAY SO':
            # Exit function scope
            self.inside_function = False  # Exit function definition
            self.pop_scope()
            self.consume('IF U SAY SO')
            print(f"  Exited function scope")
            return
        
        # Skip semantic checks if we're inside a function definition
        if self.inside_function:
            self.consume()
            return
        
        # Handle variable assignment that might contain function calls
        if token[1] == 'I HAS A':
            self.consume('I HAS A')
            self.consume()  # variable name
            if self.current_token()[1] == 'ITZ':
                self.consume('ITZ')
                # Check if the value is a function call
                if self.current_token()[1] == 'I IZ':
                    self.analyze_function_call()
                    # Consume MKAY if present
                    if self.current_token()[1] == 'MKAY':
                        self.consume('MKAY')
                    return
            return
        
        # Handle standalone function calls
        if token[1] == 'I IZ':
            self.analyze_function_call()
            return
            
        # Check for arithmetic expressions
        elif token[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            self.analyze_arithmetic_expr()

        elif token[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
            self.analyze_boolean_expr()

        elif token[1] in ['BOTH SAEM', 'DIFFRINT', 'BIGGR OF', 'SMALLR OF']:
            self.analyze_comparison_expr()
        else:
            # For any unhandled token, consume it to avoid infinite loop
            self.consume()
    
    def analyze_function_call(self):
        """Analyze function call and validate argument types"""
        self.consume('I IZ')  # Consume 'I IZ'
        
        func_name = self.current_token()[1]
        line_num = self.current_token()[3]
        self.consume()  # Consume function name
        
        # Check if function exists
        if func_name not in self.function_dictionary:
            self.errors.append(f"Error: Function '{func_name}' is not defined on line {line_num}")
            return
        
        # Print BEFORE function call
        print(f"\n=== BEFORE FUNCTION CALL '{func_name}' on line {line_num} ===")
        print(f"Function Dictionary for '{func_name}': {self.function_dictionary[func_name]}")
        
        # Get function parameters
        func_params = self.function_dictionary[func_name]
        arguments = []
        
        # Extract arguments
        # First argument always starts with YR
        if self.current_token()[1] == 'YR':
            self.consume('YR')
            
            arg_token = self.current_token()
            print(f"  DEBUG: Processing argument 1 - token: {arg_token}")
            
            # Handle string literals
            if arg_token[1] == '"':
                self.consume('"')
                arg_token = self.current_token()
                arg_value = arg_token[1]
                arg_type = 'YARN'
                self.consume()
                if self.current_token()[1] == '"':
                    self.consume('"')
            else:
                arg_value = arg_token[1]
                arg_type = self.get_argument_type(arg_token)
                print(f"  DEBUG: get_argument_type returned: {arg_type}")
                self.consume()
            
            arguments.append((arg_value, arg_type, arg_token[3]))
        
        # Remaining arguments start with AN YR
        while self.current_token() and self.current_token()[1] == 'AN':
            self.consume('AN')  # Consume AN
            
            if self.current_token()[1] == 'YR':
                self.consume('YR')  # Consume YR
                
                arg_token = self.current_token()
                print(f"  DEBUG: Processing argument {len(arguments) + 1} - token: {arg_token}")
                
                # Handle string literals
                if arg_token[1] == '"':
                    self.consume('"')
                    arg_token = self.current_token()
                    arg_value = arg_token[1]
                    arg_type = 'YARN'
                    self.consume()
                    if self.current_token()[1] == '"':
                        self.consume('"')
                else:
                    arg_value = arg_token[1]
                    arg_type = self.get_argument_type(arg_token)
                    print(f"  DEBUG: get_argument_type returned: {arg_type}")
                    self.consume()
                
                arguments.append((arg_value, arg_type, arg_token[3]))
        
        # Update function dictionary with actual argument types
        updated_params = []
        for i, ((arg_value, arg_type, arg_line), (param_name, param_type)) in enumerate(zip(arguments, func_params)):
            print(f"  Argument {i+1}: '{arg_value}' (type: {arg_type}) -> Parameter '{param_name}' (was: {param_type})")
            
            # Update parameter type based on argument type
            updated_params.append((param_name, arg_type))
            
            # If parameter has a specific type requirement (not NOOB), validate it
            if param_type != 'NOOB':
                if not self.types_compatible(arg_type, param_type):
                    self.errors.append(f"Error: Argument '{arg_value}' of type '{arg_type}' cannot be used for parameter '{param_name}' expecting type '{param_type}' on line {arg_line}")
        
        # Update the function dictionary with new types
        self.function_dictionary[func_name] = updated_params
        
        # Print AFTER function call
        print(f"\n=== AFTER FUNCTION CALL '{func_name}' ===")
        print(f"Updated Function Dictionary for '{func_name}': {self.function_dictionary[func_name]}")
        print()
    
    def get_argument_type(self, token):
        """Determine the type of an argument token"""
        print(f"    DEBUG get_argument_type: token = {token}")
        
        # Check if it's a literal type first
        if token[2] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'NOOB']:
            print(f"    DEBUG: Returning literal type: {token[2]}")
            return token[2]
        
        # Check if it's an identifier
        if token[2] == 'IDENTIFIER':
            if token[1] in self.symbol_table:
                var_type = self.symbol_table[token[1]][3]
                print(f"    DEBUG: Found identifier '{token[1]}' in symbol_table with type: {var_type}")
                return var_type
            else:
                print(f"    DEBUG: Identifier '{token[1]}' not found in symbol_table")
                return 'UNKNOWN'
        
        print(f"    DEBUG: Could not determine type, returning UNKNOWN")
        return 'UNKNOWN'
    
    def types_compatible(self, arg_type, param_type):
        """Check if argument type is compatible with parameter type"""
        # Same type is always compatible
        if arg_type == param_type:
            return True
        
        # NUMBR and NUMBAR are compatible
        if {arg_type, param_type} <= {'NUMBR', 'NUMBAR'}:
            return True
        
        # Check if YARN can be typecast to numeric
        if param_type in ['NUMBR', 'NUMBAR'] and arg_type == 'YARN':
            # Would need the actual value to check, return True for now
            return True
        
        return False
          
    def analyze_arithmetic_expr(self):
        """Check arithmetic expression operands for type compatibility"""
        operand_token = self.consume()
        op_type = "arithmetic"
        
        # Check first operand
        if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            self.analyze_arithmetic_expr()
        else:
            if self.current_token()[1] == '"':
                self.consume('"')
            
            if not self.is_valid_operand(op_type, self.current_token(), operand_token):
                return
            
            self.consume()
            
            if self.current_token()[1] == '"':
                self.consume('"')
        
        self.consume('AN')
        
        # Check second operand
        if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            self.analyze_arithmetic_expr()
        else:
            if self.current_token()[1] == '"':
                self.consume('"')
            
            if not self.is_valid_operand(op_type, self.current_token(), operand_token):
                return
            
            self.consume()
            
            if self.current_token()[1] == '"':
                self.consume('"')

    def analyze_boolean_expr(self):
        boolean_token = self.consume()
        op_type = 'boolean'

        if self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
            self.analyze_boolean_expr()
        else:
            if self.current_token()[1] == '"':
                self.consume('"')

            if not self.is_valid_operand(op_type, self.current_token(), boolean_token):
                return
            
            self.consume()

            if self.current_token()[1] == '"':
                self.consume('"')

        self.consume('AN')

        if self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT']:
            self.analyze_boolean_expr()
        else:
            if self.current_token()[1] == '"':
                self.consume('"')

            if not self.is_valid_operand(op_type, self.current_token(), boolean_token):
                return

            self.consume()

            if self.current_token()[1] == '"':
                self.consume('"')

    def analyze_comparison_expr(self):
        operand_token = self.consume()
        
        if self.current_token()[1] == '"':
            self.consume('"')

        if self.current_token()[2] == 'IDENTIFIER':
            if self.current_token()[1] not in self.symbol_table:
                return True

            if self.symbol_table[self.current_token()[1]][3] not in ['NUMBR', 'NUMBAR']:
                self.errors.append(f"Error: The operand '{self.current_token()[1]}' cannot be used in {operand_token[1]} operation on line {self.current_token()[3]}")
                return
        elif self.current_token()[2] not in ['NUMBR', 'NUMBAR']:
            self.errors.append(f"Error: The operand '{self.current_token()[1]}' cannot be used in {operand_token[1]} operation on line {self.current_token()[3]}")
            return
            
        self.consume()
       
        if self.current_token()[1] == '"':
            self.consume('"')
        
        self.consume('AN')
        
        if self.current_token()[1] in ['BOTH SAEM', 'DIFFRINT', 'BIGGR OF', 'SMALLR OF']:
            self.analyze_comparison_expr()
        else:
            if self.current_token()[1] == '"':
                self.consume('"')

            if self.current_token()[2] == 'IDENTIFIER':
                if self.current_token()[1] not in self.symbol_table and self.current_token()[3] not in self.function_line:
                    return True
                
                if self.symbol_table[self.current_token()[1]][3] not in ['NUMBR', 'NUMBAR']:
                    self.errors.append(f"Error: The operand '{self.current_token()[1]}' cannot be used in {operand_token[1]} operation on line {self.current_token()[3]}")
                    return
            elif self.current_token()[2] not in ['NUMBR', 'NUMBAR']:
                self.errors.append(f"Error: The operand '{self.current_token()[1]}' cannot be used in {operand_token[1]} operation on line {self.current_token()[3]}")
                return
            
            self.consume()
            
            if self.current_token()[1] == '"':
                self.consume('"')

    def extract_function_params(self):
        params = []

        while self.current_token() and self.current_token()[1] in ['YR', 'AN']:
            self.consume()
            if self.current_token()[2] == 'IDENTIFIER':
                params.append(self.current_token()[1])
                self.consume()

        return params

    def is_valid_operand(self, type, token, operation_token):
        """Check if a token is a valid operand for the given operation type"""
        
        if token[2] == 'YARN':
            if type == 'arithmetic':
                is_numbr = re.match(r'^-?[0-9]+$', token[1])
                is_numbar = re.match(r'^-?[0-9]+\.[0-9]+$', token[1])

                if is_numbr or is_numbar:
                    print("TYPECAST ARITHMETIC")
                    return True
                else:
                    self.errors.append(f"Error: '{token[1]}' cannot be typecasted to NUMBR or NUMBAR for {operation_token[1]} operation on line {token[3]}")
                    return False

            elif type == 'boolean':
                if token[1] in ['0', '1', '0.0', '1.0', 'WIN', 'FAIL']:
                    print("TYPECAST BOOLEAN")
                    return True
                else:
                    self.errors.append(f"Error: '{token[1]}' cannot be typecasted to TROOF for {operation_token[1]} operation on line {token[3]}")
                    return False
            
        elif token[2] == 'IDENTIFIER':
            if token[1] not in self.symbol_table and token[3] not in self.function_line:
                self.errors.append(f"Error: Variable name '{token[1]}' does not exist on line {token[3]}")
                return True

            if self.symbol_table[token[1]][3] == 'YARN':
                if type == 'arithmetic':
                    is_numbr = re.match(r'^-?[0-9]+$', self.symbol_table[token[1]][0])
                    is_numbar = re.match(r'^-?[0-9]+\.[0-9]+$', self.symbol_table[token[1]][0])

                    if is_numbr or is_numbar:
                        print("TYPECAST ARITHMETIC")
                        return True
                    else:
                        self.errors.append(f"Error: '{token[1]}' cannot be typecasted to NUMBR or NUMBAR for {operation_token[1]} operation on line {token[3]}")
                        return False

                elif type == 'boolean':
                    if self.symbol_table[token[1]][0] in ['0', '1', '0.0', '1.0', 'WIN', 'FAIL', 'NOOB']:
                        print("TYPECAST BOOLEAN")
                        return True
                    else:
                        self.errors.append(f"Error: '{token[1]}' cannot be typecasted to TROOF for {operation_token[1]} operation on line {token[3]}")
                        return False

            if type == 'boolean':
                if self.symbol_table[token[1]][3] == 'TROOF':
                    return True

                if self.symbol_table[token[1]][3] == 'NUMBR' and self.symbol_table[token[1]][0] in ["1", "0"]:
                    print("TYPECAST BOOLEAN")
                    return True

                elif self.symbol_table[token[1]][3] == 'NUMBAR' and self.symbol_table[token[1]][0] in ["1.0", "0.0"]:
                    print("TYPECAST BOOLEAN")
                    return True

                elif self.symbol_table[token[1]][3] == 'NOOB':
                    print("TYPECAST BOOLEAN")
                    return True

                else:
                    self.errors.append(f"Error: '{token[1]}' cannot be typecasted to TROOF for {operation_token[1]} operation on line {token[3]}")
                    return False

            elif type == 'arithmetic':
                if self.symbol_table[token[1]][3] not in ['NUMBR', 'NUMBAR']:
                    self.errors.append(f"Error: Invalid data type '{self.symbol_table[token[1]][3]}' for {operation_token[1]} operation on line {token[3]}. Expected NUMBR or NUMBAR.")
                    return False
        else:
            if type == 'arithmetic':
                if token[2] in ['NUMBR', 'NUMBAR']:
                    print("NO TYPECAST NEEDED")
                    return True
                else:
                    self.errors.append(f"Error: Invalid data type '{token[2]}' for {operation_token[1]} operation on line {token[3]}. Expected NUMBR or NUMBAR.")
                    return False

            elif type == 'boolean':
                if token[2] == 'NUMBR' and token[1] in ["1","0"]:
                    print("TYPECAST BOOLEAN")
                    return True
                elif token[2] == 'NUMBAR' and token[1] in ["1.0", "0.0"]:
                    print("TYPECAST BOOLEAN")
                    return True
                elif token[2] == "NOOB":
                    print("TYPECAST BOOLEAN")
                    return True
                elif token[2] == "TROOF":
                    print("NO TYPECAST NEEDED")
                    return True
                else:
                    self.errors.append(f"Error: Invalid value of {token[1]} for data type {token[2]} for {operation_token[1]} operation on line {token[3]}. Expected 1 or 0")
                    return False
        
        return True


def analyze_lolcode(tokens, symbol_table, function_dictionary):
    """Entry point for semantic analysis"""
    semantic = SemanticAnalyzer(tokens, symbol_table, function_dictionary)
    semantic.analyze()
    
    if semantic.errors:
        print("\n=== SEMANTIC ERRORS FOUND ===")
        for error in semantic.errors:
            print(error)
        return semantic.errors
    else:
        print("\n=== NO SEMANTIC ERRORS ===")
        return []
