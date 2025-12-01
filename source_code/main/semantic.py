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
            self.errors.append(f"Line {line_num}: Function '{func_name}' is not defined")
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
                    self.errors.append(
                        f"Line {arg_line}: Argument '{arg_value}' of type '{arg_type}' "
                        f"is incompatible with parameter '{param_name}' (expected '{param_type}')"
                    )
        
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
        if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
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
        if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF', 'BIGGR OF', 'SMALLR OF']:
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
        op = boolean_token[1]
        op_type = 'boolean'

        if op == 'NOT':
            if self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
                self.analyze_boolean_expr()
                return

            if self.current_token()[1] == '"':
                self.consume('"')

            if not self.is_valid_operand(op_type, self.current_token(), boolean_token):
                return
            
            self.consume()

            if self.current_token()[1] == '"':
                self.consume('"')

            return

        if op in ['ALL OF', 'ANY OF']:

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

            while self.current_token() and self.current_token()[1] == 'AN':
                self.consume('AN')

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

            if not self.current_token() or self.current_token()[1] != 'MKAY':
                self.errors.append(f"Line {boolean_token[3]}: {op} requires MKAY at the end")
                return
            
            self.consume('MKAY')
            return

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
    
    def analyze_comparison_expr(self):
        operand_token = self.consume()
        
        if self.current_token()[1] == '"':
            self.consume('"')

        if self.current_token()[2] == 'IDENTIFIER':
            if self.current_token()[1] not in self.symbol_table:
                return True

            if self.symbol_table[self.current_token()[1]][3] not in ['NUMBR', 'NUMBAR']:
                self.errors.append(
                    f"Line {arg_line}: Argument '{arg_value}' of type '{arg_type}' "
                    f"is incompatible with parameter '{param_name}' (expected '{param_type}')"
                )
                return
        elif self.current_token()[2] not in ['NUMBR', 'NUMBAR']:
            self.errors.append(
                f"Line {arg_line}: Argument '{arg_value}' of type '{arg_type}' "
                f"is incompatible with parameter '{param_name}' (expected '{param_type}')"
                )
            return
            
        self.consume()
       
        if self.current_token()[1] == '"':
            self.consume('"')
        
        self.consume('AN')
        
        if self.current_token()[1] in ['BOTH SAEM', 'DIFFRINT', 'BIGGR OF', 'SMALLR OF', 'SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            self.analyze_comparison_expr()
        else:
            if self.current_token()[1] == '"':
                self.consume('"')

            if self.current_token()[2] == 'IDENTIFIER':
                if self.current_token()[1] not in self.symbol_table and self.current_token()[3] not in self.function_line:
                    return True
                
                if self.symbol_table[self.current_token()[1]][3] not in ['NUMBR', 'NUMBAR']:
                    self.errors.append(
                        f"Line {arg_line}: Argument '{arg_value}' of type '{arg_type}' "
                        f"is incompatible with parameter '{param_name}' (expected '{param_type}')"
                    )
                    return
            elif self.current_token()[2] not in ['NUMBR', 'NUMBAR']:
                self.errors.append(
                    f"Line {arg_line}: Argument '{arg_value}' of type '{arg_type}' "
                    f"is incompatible with parameter '{param_name}' (expected '{param_type}')"
                )
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
                    self.errors.append(
                        f"Line {token[3]}: Value '{token[1]}' cannot be cast to NUMBR or NUMBAR "
                        f"for '{operation_token[1]}' operation"
                    )

                    return False

            elif type == 'boolean':
                if token[1] in ['0', '1', '0.0', '1.0', 'WIN', 'FAIL']:
                    print("TYPECAST BOOLEAN")
                    return True
                else:
                    self.errors.append(
                        f"Line {token[3]}: Value '{token[1]}' cannot be cast to TROOF "
                        f"for '{operation_token[1]}' operation"
                    )

                    return False
            
        elif token[2] == 'IDENTIFIER':
            if token[1] not in self.symbol_table and token[3] not in self.function_line:
                self.errors.append(f"Line {token[3]}: Variable '{token[1]}' does not exist")
                return True

            if self.symbol_table[token[1]][3] == 'YARN':
                if type == 'arithmetic':
                    is_numbr = re.match(r'^-?[0-9]+$', self.symbol_table[token[1]][0])
                    is_numbar = re.match(r'^-?[0-9]+\.[0-9]+$', self.symbol_table[token[1]][0])

                    if is_numbr or is_numbar:
                        print("TYPECAST ARITHMETIC")
                        return True
                    else:
                        self.errors.append(
                            f"Line {token[3]}: Value '{token[1]}' cannot be cast to NUMBR or NUMBAR "
                            f"for '{operation_token[1]}' operation"
                        )

                        return False

                elif type == 'boolean':
                    if self.symbol_table[token[1]][0] in ['0', '1', '0.0', '1.0', 'WIN', 'FAIL', 'NOOB']:
                        print("TYPECAST BOOLEAN")
                        return True
                    else:
                        self.errors.append(
                            f"Line {token[3]}: Value '{token[1]}' cannot be cast to TROOF "
                            f"for '{operation_token[1]}' operation"
                        )
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
                    self.errors.append(
                        f"Line {token[3]}: Value '{token[1]}' cannot be cast to TROOF "
                        f"for '{operation_token[1]}' operation"
                    )

                    return False

            elif type == 'arithmetic':
                if self.symbol_table[token[1]][3] not in ['NUMBR', 'NUMBAR']:
                    self.errors.append(
                        f"Line {token[3]}: Invalid operand type '{self.symbol_table[token[1]][3]}' "
                        f"for '{operation_token[1]}' operation (expected NUMBR or NUMBAR)"
                    )
        else:
            if type == 'arithmetic':
                if token[2] in ['NUMBR', 'NUMBAR']:
                    print("NO TYPECAST NEEDED")
                    return True
                else:
                    self.errors.append(f"Error: Invalid data type '{token[2]}' for {operation_token[1]} operation on line {token[3]}. Expected NUMBR or NUMBAR.")
                    return False

            elif type == 'boolean':
                if token[2] == 'NUMBR' and token[1] in ["1",1,"0",0]:
                    print("TYPECAST BOOLEAN")
                    return True
                elif token[2] == 'NUMBAR' and token[1] in ["1.0",1.0, "0.0",0.0]:
                    print("TYPECAST BOOLEAN")
                    return True
                elif token[2] == "NOOB":
                    print("TYPECAST BOOLEAN")
                    return True
                elif token[2] == "TROOF":
                    print("NO TYPECAST NEEDED")
                    return True
                else:
                    self.errors.append(
                    f"Line {token[3]}: Invalid value '{token[1]}' for type '{token[2]}' "
                    f"in '{operation_token[1]}' operation (expected 0 or 1)"
                )

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
        return False, semantic.errors
    else:
        print("\n=== NO SEMANTIC ERRORS ===")
        return True, semantic.errors


# import re
# from parser import Parser

# class SemanticAnalyzer(Parser):
#     def __init__(self, tokens, symbol_table, function_dictionary):
#         super().__init__(tokens)
#         self.errors = []
#         self.symbol_table = symbol_table
#         self.function_dictionary = function_dictionary
#         self.boolean_typecast = {}
#         self.function_line = []
#         self.inside_function = False  # Track if we're inside a function definition
    
#     def analyze(self):
#         """Main analysis entry point"""
#         print("\n==================== START ANALYZE HERE ================\n")
        
#         while self.current_token()[1] != 'KTHXBYE':
#             self.analyze_statement()
            
#     def analyze_statement(self):
#         """Analyze a single statement and advance tokens"""
#         token = self.current_token()

#         if token[1] == 'HOW IZ I':
#             self.inside_function = True  # Enter function definition
#             self.consume('HOW IZ I')
            
#             # Function name
#             func_name_token = self.current_token()
#             func_name = func_name_token[1]
#             self.consume()  # consume function name

#             # Extract parameters
#             params = self.extract_function_params()
            
#             # Save function signature
#             self.function_scopes[func_name] = {
#                 "params": params
#             }

#             # Enter function scope
#             self.push_scope()

#             # Insert parameters into local scope
#             for param_name in params:
#                 self.declare_variable(param_name, 'NOOB')

#             # Analyze function body
#             while self.current_token()[1] != 'IF U SAY SO':
#                 if self.current_token()[1] == 'GTFO':
#                     self.consume('GTFO') # Allow GTFO inside function
#                 elif self.current_token()[1] == 'FOUND YR':
#                     self.consume('FOUND YR')
#                     self.analyze_expression() # Validate return value
#                 else:
#                     self.analyze_statement()

#             self.consume('IF U SAY SO')
#             self.pop_scope() # Exit function scope
#             self.inside_function = False # Exit function definition

#         elif token[1] == 'I IZ':
#             self.consume('I IZ')
#             func_name = self.current_token()[1]
#             self.consume() # Consume function name

#             if func_name not in self.function_scopes:
#                 self.errors.append(f"Error: Function '{func_name}' not defined.")
#             else:
#                 # Check arguments
#                 expected_params = self.function_scopes[func_name]["params"]
#                 if self.current_token()[1] == 'YR':
#                     while self.current_token()[1] == 'YR':
#                         self.consume('YR')
#                         self.analyze_expression() # Validate argument expression
#                         if self.current_token()[1] == 'AN':
#                             self.consume('AN')
                
#                 self.consume('MKAY')

#         # Check for arithmetic expressions
#         elif token[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
#             self.analyze_arithmetic_expr()
        
#         # Check for boolean expressions
#         elif token[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
#             self.analyze_boolean_expr()

#         # Check for comparison expressions
#         elif token[1] in ['BOTH SAEM', 'DIFFRINT']:
#             self.analyze_comparison_expr()

#         # Check for concatenation
#         elif token[1] == 'SMOOSH':
#             self.analyze_concatenation_expr()

#         # Check for explicit typecasting
#         elif token[1] == 'MAEK':
#             self.analyze_typecast_expr()
        
#         # Check for other statement types (VISIBLE, variable declarations, etc.)
#         elif token[1] == 'VISIBLE':
#             self.consume('VISIBLE')
#             # The next token might be an expression or literal
#             if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
#                 self.analyze_arithmetic_expr()
#             elif self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
#                 self.analyze_boolean_expr()
#             elif self.current_token()[1] in ['BOTH SAEM', 'DIFFRINT']:
#                 self.analyze_comparison_expr()
#             elif self.current_token()[1] == 'SMOOSH':
#                 self.analyze_concatenation_expr()
#             elif self.current_token()[1] == 'MAEK':
#                 self.analyze_typecast_expr()
#             else:
#                 self.consume()  # Consume the literal/variable being displayed
#                 # Handle infinite arity for VISIBLE
#                 while self.current_token()[1] == '+':
#                     self.consume('+')
#                     if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
#                         self.analyze_arithmetic_expr()
#                     elif self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
#                         self.analyze_boolean_expr()
#                     elif self.current_token()[1] in ['BOTH SAEM', 'DIFFRINT']:
#                         self.analyze_comparison_expr()
#                     elif self.current_token()[1] == 'SMOOSH':
#                         self.analyze_concatenation_expr()
#                     elif self.current_token()[1] == 'MAEK':
#                         self.analyze_typecast_expr()
#                     else:
#                         self.consume()

#         elif token[1] == 'GIMMEH':
#             self.consume('GIMMEH')
#             if self.current_token()[2] == 'IDENTIFIER':
#                 var_name = self.current_token()[1]
#                 if var_name not in self.symbol_table:
#                      self.errors.append(f"Line {token[3]}: Variable '{var_name}' not declared before GIMMEH.")
#                 self.consume()
#             else:
#                  self.errors.append(f"Line {token[3]}: Expected variable after GIMMEH.")

#         # Variable Declaration (I HAS A)
#         elif token[1] == 'I HAS A':
#             self.consume('I HAS A')
#             if self.current_token()[2] == 'IDENTIFIER':
#                 var_name = self.current_token()[1]
#                 # Check for re-declaration in the same scope (if scope handling is added)
#                 self.consume()
#                 if self.current_token()[1] == 'ITZ':
#                     self.consume('ITZ')
#                     # Validate initialization expression/value
#                     if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
#                         self.analyze_arithmetic_expr()
#                     elif self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
#                         self.analyze_boolean_expr()
#                     elif self.current_token()[1] in ['BOTH SAEM', 'DIFFRINT']:
#                         self.analyze_comparison_expr()
#                     elif self.current_token()[1] == 'SMOOSH':
#                         self.analyze_concatenation_expr()
#                     elif self.current_token()[1] == 'MAEK':
#                         self.analyze_typecast_expr()
#                     else:
#                         self.consume()

#         # Variable Assignment (variable R value)
#         elif token[2] == 'IDENTIFIER' and self.peek_token()[1] == 'R':
#             var_name = token[1]
#             if var_name not in self.symbol_table:
#                  self.errors.append(f"Line {token[3]}: Variable '{var_name}' not declared before assignment.")
#             self.consume() # consume variable
#             self.consume('R')
            
#             # Validate assignment expression/value
#             if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
#                 self.analyze_arithmetic_expr()
#             elif self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
#                 self.analyze_boolean_expr()
#             elif self.current_token()[1] in ['BOTH SAEM', 'DIFFRINT']:
#                 self.analyze_comparison_expr()
#             elif self.current_token()[1] == 'SMOOSH':
#                 self.analyze_concatenation_expr()
#             elif self.current_token()[1] == 'MAEK':
#                 self.analyze_typecast_expr()
#             else:
#                 self.consume()

#         # Implicit Variable Assignment (IS NOW A) - Typecasting
#         elif token[2] == 'IDENTIFIER' and self.peek_token()[1] == 'IS NOW A':
#             var_name = token[1]
#             if var_name not in self.symbol_table:
#                  self.errors.append(f"Line {token[3]}: Variable '{var_name}' not declared before IS NOW A.")
#             self.consume()
#             self.consume('IS NOW A')
#             target_type = self.current_token()[1]
#             if target_type not in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF']:
#                  self.errors.append(f"Line {token[3]}: Invalid target type '{target_type}' for IS NOW A.")
#             self.consume()

#         # Flow Control: O RLY? (If-Else)
#         elif token[1] == 'O RLY?':
#             self.consume('O RLY?')
#             if self.current_token()[1] == 'YA RLY':
#                 self.consume('YA RLY')
#                 while self.current_token()[1] not in ['NO WAI', 'OIC']:
#                     self.analyze_statement()
                
#                 if self.current_token()[1] == 'NO WAI':
#                     self.consume('NO WAI')
#                     while self.current_token()[1] != 'OIC':
#                         self.analyze_statement()
                
#                 if self.current_token()[1] == 'OIC':
#                     self.consume('OIC')
#                 else:
#                     self.errors.append(f"Line {token[3]}: Expected OIC to close O RLY block.")

#         # Flow Control: WTF? (Switch-Case)
#         elif token[1] == 'WTF?':
#             self.consume('WTF?')
#             while self.current_token()[1] == 'OMG':
#                 self.consume('OMG')
#                 self.consume() # consume literal
#                 while self.current_token()[1] not in ['OMG', 'OMGWTF', 'OIC', 'GTFO']:
#                     self.analyze_statement()
#                 if self.current_token()[1] == 'GTFO':
#                     self.consume('GTFO')

#             if self.current_token()[1] == 'OMGWTF':
#                 self.consume('OMGWTF')
#                 while self.current_token()[1] != 'OIC':
#                     self.analyze_statement()
            
#             if self.current_token()[1] == 'OIC':
#                 self.consume('OIC')
#             else:
#                 self.errors.append(f"Line {token[3]}: Expected OIC to close WTF block.")

#         # Loops
#         elif token[1] == 'IM IN YR':
#             self.consume('IM IN YR')
#             label = self.current_token()[1]
#             self.consume() # loop label
#             op = self.current_token()[1] # UPPIN/NERFIN
#             self.consume()
#             self.consume('YR')
#             var = self.current_token()[1]
#             self.consume() # loop var
            
#             if self.current_token()[1] in ['TIL', 'WILE']:
#                 self.consume() # TIL/WILE
#                 # condition expression
#                 if self.current_token()[1] in ['BOTH SAEM', 'DIFFRINT']:
#                     self.analyze_comparison_expr()
#                 else:
#                     self.analyze_expression() # General expression check

#             while self.current_token()[1] != 'IM OUTTA YR':
#                 if self.current_token()[1] == 'GTFO':
#                     self.consume('GTFO') # Valid inside loop
#                 else:
#                     self.analyze_statement()
            
#             self.consume('IM OUTTA YR')
#             if self.current_token()[1] == label:
#                 self.consume()
#             else:
#                 self.errors.append(f"Line {token[3]}: Loop label mismatch in IM OUTTA YR.")

#         # Add more statement types as needed
#         else:
#             # For any unhandled token, consume it to avoid infinite loop
#             self.consume()
          
#     def analyze_arithmetic_expr(self):
#         """Check arithmetic expression operands for type compatibility"""
#         operation_token = self.consume()
        
#         # Check first operand
#         if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
#             self.analyze_arithmetic_expr()  # Recurse for nested operation
#         else:
#             if not self.is_valid_numeric_operand(self.current_token(), operation_token):
#                 pass # Error added in helper
#             self.consume()  # Consume the operand value
        
#         # Expect AN keyword
#         if self.current_token()[1] == 'AN':
#             self.consume('AN')
#         else:
#              self.errors.append(f"Line {self.current_token()[3]}: Expected 'AN' in arithmetic expression.")

#         # Check second operand
#         if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
#             self.analyze_arithmetic_expr()  # Recurse for nested operation
#         else:
#             if not self.is_valid_numeric_operand(self.current_token(), operation_token):
#                 pass # Error added in helper
#             self.consume()  # Consume the operand value

#     def analyze_boolean_expr(self):
#         """Check boolean expression operands"""
#         operation_token = self.consume() # Consume boolean operator
        
#         # Unary NOT
#         if operation_token[1] == 'NOT':
#             if self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
#                 self.analyze_boolean_expr()
#             else:
#                 self.consume() # Consume operand (can be anything castable to TROOF)
#             return

#         # Infinite Arity (ALL OF, ANY OF)
#         if operation_token[1] in ['ALL OF', 'ANY OF']:
#             while self.current_token()[1] != 'MKAY':
#                 if self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
#                     self.analyze_boolean_expr()
#                 else:
#                     self.consume()
                
#                 if self.current_token()[1] == 'AN':
#                     self.consume('AN')
#                 elif self.current_token()[1] != 'MKAY':
#                      # Optional MKAY check or implicit end
#                      break
#             if self.current_token()[1] == 'MKAY':
#                 self.consume('MKAY')
#             return

#         # Binary Boolean (BOTH OF, EITHER OF, WON OF)
#         # Operand 1
#         if self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
#             self.analyze_boolean_expr()
#         else:
#             self.consume()

#         # AN
#         if self.current_token()[1] == 'AN':
#             self.consume('AN')
#         else:
#              self.errors.append(f"Line {self.current_token()[3]}: Expected 'AN' in boolean expression.")

#         # Operand 2
#         if self.current_token()[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
#             self.analyze_boolean_expr()
#         else:
#             self.consume()

#     def analyze_comparison_expr(self):
#         """Check comparison expression operands"""
#         operation_token = self.consume() # BOTH SAEM or DIFFRINT
        
#         # Operand 1
#         arg1_token = self.current_token()
#         arg_line = arg1_token[3] # Initialize arg_line from the first operand
        
#         if arg1_token[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
#             self.analyze_arithmetic_expr()
#         else:
#             self.consume()

#         # AN
#         if self.current_token()[1] == 'AN':
#             self.consume('AN')
#         else:
#              self.errors.append(f"Line {self.current_token()[3]}: Expected 'AN' in comparison expression.")

#         # Operand 2
#         arg2_token = self.current_token()
#         # You could update arg_line here if needed for the second argument error context
        
#         if arg2_token[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
#             self.analyze_arithmetic_expr()
#         else:
#             self.consume()

#     def analyze_concatenation_expr(self):
#         """Check concatenation expression (SMOOSH)"""
#         self.consume('SMOOSH')
        
#         # Accepts list of strings separated by AN
#         while True:
#             self.consume() # Consume string/var
#             if self.current_token()[1] == 'AN':
#                 self.consume('AN')
#             else:
#                 break

#     def analyze_typecast_expr(self):
#         """Check typecast expression (MAEK)"""
#         self.consume('MAEK')
#         self.consume() # operand
#         if self.current_token()[1] == 'A': # Optional A
#             self.consume('A')
        
#         target_type = self.current_token()[1]
#         if target_type not in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF']:
#              self.errors.append(f"Line {self.current_token()[3]}: Invalid type '{target_type}' in MAEK.")
#         self.consume()

#     # Helper function for arithmetic validation
#     def is_valid_numeric_operand(self, token, operation_token):
#         """
#         Check if a token is a valid numeric operand for arithmetic operations.
#         Returns True if valid, False otherwise (and adds error).
#         """
#         # Check if it's a YARN that cannot be typecast to numeric
#         if token[2] == 'YARN Literal' or (token[2] == 'IDENTIFIER' and self.symbol_table.get(token[1], [None, None, None, 'NOOB'])[3] == 'YARN'):
#             val = token[1]
#             if token[2] == 'IDENTIFIER':
#                 val = self.symbol_table[token[1]][0] # Get value from symbol table
            
#             # Remove quotes for literal
#             if token[2] == 'YARN Literal':
#                 val = val.strip('"')

#             # Check if YARN can be typecast to NUMBR (integer) or NUMBAR (float)
#             is_numbr = re.match(r'^-?[0-9]+$', str(val))
#             is_numbar = re.match(r'^-?[0-9]+\.[0-9]+$', str(val))
            
#             if not (is_numbr or is_numbar):
#                 self.errors.append(
#                     f"Error: '{token[1]}' cannot be typecasted to NUMBR or NUMBAR "
#                     f"for {operation_token[1]} operation on line {token[3]}"
#                 )
#                 return False

#         # Check identifiers
#         elif token[2] == 'IDENTIFIER':
#              if token[1] in self.symbol_table:
#                  dtype = self.symbol_table[token[1]][3]
#                  if dtype not in ['NUMBR', 'NUMBAR', 'YARN']: # YARN handled above
#                       self.errors.append(
#                         f"Error: Invalid data type '{dtype}' for {operation_token[1]} "
#                         f"operation on line {token[3]}. Expected NUMBR or NUMBAR."
#                     )
#                       return False
#              else:
#                  self.errors.append(f"Error: Variable '{token[1]}' not defined on line {token[3]}")
#                  return False

#         # Check literals
#         elif token[2] not in ['NUMBR Literal', 'NUMBAR Literal', 'YARN Literal']: # YARN handled above
#             self.errors.append(
#                 f"Error: Invalid operand '{token[1]}' of type '{token[2]}' for {operation_token[1]} "
#                 f"operation on line {token[3]}. Expected NUMBR or NUMBAR."
#             )
#             return False
        
#         return True

#     def extract_function_params(self):
#         """Parses function parameters from HOW IZ I declaration"""
#         params = []
#         if self.current_token()[1] == 'YR':
#             while self.current_token()[1] == 'YR':
#                 self.consume('YR')
#                 if self.current_token()[2] == 'IDENTIFIER':
#                     params.append(self.current_token()[1])
#                     self.consume()
#                 if self.current_token()[1] == 'AN':
#                     self.consume('AN')
#         return params

#     def push_scope(self):
#         """Creates a new scope for function variables"""
#         # In a simple implementation, you might copy symbol_table or use a stack of dicts
#         # For now, we can just denote a scope change if the parser supports it structure
#         pass

#     def pop_scope(self):
#         """Exits current function scope"""
#         pass

#     def declare_variable(self, name, value):
#         """Helper to declare variable in symbol table"""
#         # This would need to interact with the symbol table structure properly
#         # For now, simplified:
#         if name not in self.symbol_table:
#              self.symbol_table[name] = (value, 'NOOB', None, 'NOOB')

#     def peek_token(self):
#         """Returns the next token without moving the pointer."""
#         if self.position + 1 < len(self.tokens):
#             return self.tokens[self.position + 1]
#         return None

#     def analyze_expression(self):
#         """Helper to route to specific expression analyzers based on current token"""
#         token = self.current_token()
#         if token[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
#             self.analyze_arithmetic_expr()
#         elif token[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
#             self.analyze_boolean_expr()
#         elif token[1] in ['BOTH SAEM', 'DIFFRINT']:
#             self.analyze_comparison_expr()
#         elif token[1] == 'SMOOSH':
#             self.analyze_concatenation_expr()
#         elif token[1] == 'MAEK':
#             self.analyze_typecast_expr()
#         else:
#             self.consume()


# def analyze_lolcode(tokens, symbol_table, function_dictionary):
#     """Entry point for semantic analysis"""
#     semantic = SemanticAnalyzer(tokens, symbol_table, function_dictionary)
#     semantic.analyze()
    
#     if semantic.errors:
#         print("\n=== SEMANTIC ERRORS FOUND ===")
#         for error in semantic.errors:
#             print(error)
#         return False, semantic.errors
#     else:
#         print("\n=== NO SEMANTIC ERRORS ===")
#         return True, semantic.errors