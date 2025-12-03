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

            return        

        elif token[1] == 'IF U SAY SO':
            # Exit function scope
            self.inside_function = False  # Exit function definition
            self.pop_scope()
            self.consume('IF U SAY SO')
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

    def analyze_operand(self, token):
        """
        Helper to check if an operand is valid.
        Used by analyze_expression to validate variables and literals.
        """
        
        # 1. Allow 'IT' keyword
        if token[1] == 'IT':
            return True

        # 2. Check Variables (Identifiers)
        if token[2] == 'IDENTIFIER':
            # Check if variable is declared in the symbol table
            if token[1] not in self.symbol_table:
                self.errors.append(f"Error on line {token[3]}: Variable '{token[1]}' used before declaration.")
                return False
            return True
            
        # 3. Allow Literals
        elif token[2] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF']:
            return True
        
        # 4. Handle invalid types
        else:
            self.errors.append(f"Error on line {token[3]}: Invalid operand '{token[1]}'")
            return False
    
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
        
        # Get function parameters
        func_params = self.function_dictionary[func_name]
        arguments = []
        
        # Extract arguments
        # First argument always starts with YR
        if self.current_token()[1] == 'YR':
            self.consume('YR')
            
            arg_token = self.current_token()
            
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
                self.consume()
            
            arguments.append((arg_value, arg_type, arg_token[3]))
        
        # Remaining arguments start with AN YR
        while self.current_token() and self.current_token()[1] == 'AN':
            self.consume('AN')  # Consume AN
            
            if self.current_token()[1] == 'YR':
                self.consume('YR')  # Consume YR
                
                arg_token = self.current_token()
                
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
                    self.consume()
                
                arguments.append((arg_value, arg_type, arg_token[3]))
        
        # Update function dictionary with actual argument types
        updated_params = []
        for i, ((arg_value, arg_type, arg_line), (param_name, param_type)) in enumerate(zip(arguments, func_params)):
            
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
    
    def get_argument_type(self, token):
        """Determine the type of an argument token"""
        
        # Check if it's a literal type first
        if token[2] in ['NUMBR', 'NUMBAR', 'YARN', 'TROOF', 'NOOB']:
            return token[2]
        
        # Check if it's an identifier
        if token[2] == 'IDENTIFIER':
            if token[1] in self.symbol_table:
                var_type = self.symbol_table[token[1]][3]
                return var_type
            else:
                return 'UNKNOWN'
        
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

        # Check first operand
        if self.current_token()[2] == 'IDENTIFIER':
            if self.current_token()[1] not in self.symbol_table:
                return True

            var_type = self.symbol_table[self.current_token()[1]][3]
            if var_type not in ['NUMBR', 'NUMBAR', 'NOOB']:  # Allow NOOB for runtime assignment
                self.errors.append(
                    f"Line {self.current_token()[3]}: Variable '{self.current_token()[1]}' of type '{var_type}' "
                    f"cannot be used in '{operand_token[1]}' operation (expected NUMBR or NUMBAR)"
                )
                return

        if self.current_token()[1] in ['BOTH SAEM', 'DIFFRINT', 'BIGGR OF', 'SMALLR OF', 'SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            self.analyze_comparison_expr()
        else:
            if self.current_token()[1] == '"':
                self.consume('"')

            # Check second operand
            if self.current_token()[2] == 'IDENTIFIER':
                if self.current_token()[1] not in self.symbol_table and self.current_token()[3] not in self.function_line:
                    return True
                
                var_type = self.symbol_table[self.current_token()[1]][3]
                if var_type not in ['NUMBR', 'NUMBAR', 'NOOB']:  # Allow NOOB for runtime assignment
                    self.errors.append(
                        f"Line {self.current_token()[3]}: Variable '{self.current_token()[1]}' of type '{var_type}' "
                        f"cannot be used in '{operand_token[1]}' operation (expected NUMBR or NUMBAR)"
                    )
                    return
            elif self.current_token()[2] not in ['NUMBR', 'NUMBAR']:
                self.errors.append(
                    f"Line {self.current_token()[3]}: Invalid operand type '{self.current_token()[2]}' "
                    f"for '{operand_token[1]}' operation (expected NUMBR or NUMBAR)"
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
                # Allow WIN/FAIL in arithmetic operations
                is_troof = token[1] in ['WIN', 'FAIL']

                if is_numbr or is_numbar or is_troof:
                    return True
                else:
                    self.errors.append(
                        f"Line {token[3]}: Value '{token[1]}' cannot be cast to NUMBR or NUMBAR "
                        f"for '{operation_token[1]}' operation"
                    )

                    return False

            elif type == 'boolean':
                if token[1] in ['0', '1', '0.0', '1.0', 'WIN', 'FAIL']:
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

            # NOOB variables are allowed - they might be assigned at runtime (e.g., via GIMMEH)
            if self.symbol_table[token[1]][3] == 'NOOB':
                return True

            if self.symbol_table[token[1]][3] == 'YARN':
                if type == 'arithmetic':
                    is_numbr = re.match(r'^-?[0-9]+$', self.symbol_table[token[1]][0])
                    is_numbar = re.match(r'^-?[0-9]+\.[0-9]+$', self.symbol_table[token[1]][0])
                    # Allow WIN/FAIL in arithmetic operations
                    is_troof = self.symbol_table[token[1]][0] in ['WIN', 'FAIL']

                    if is_numbr or is_numbar or is_troof:
                        return True
                    else:
                        self.errors.append(
                            f"Line {token[3]}: Value '{token[1]}' cannot be cast to NUMBR or NUMBAR "
                            f"for '{operation_token[1]}' operation"
                        )

                        return False

                elif type == 'boolean':
                    if self.symbol_table[token[1]][0] in ['0', '1', '0.0', '1.0', 'WIN', 'FAIL', 'NOOB']:
                        return True
                    else:
                        self.errors.append(
                            f"Line {token[3]}: Value '{token[1]}' cannot be cast to TROOF "
                            f"for '{operation_token[1]}' operation"
                        )
                        return False

            # Allow TROOF type in arithmetic operations (WIN=1, FAIL=0)
            if type == 'arithmetic':
                if self.symbol_table[token[1]][3] in ['NUMBR', 'NUMBAR', 'TROOF']:
                    return True
                else:
                    self.errors.append(
                        f"Line {token[3]}: Invalid operand type '{self.symbol_table[token[1]][3]}' "
                        f"for '{operation_token[1]}' operation (expected NUMBR, NUMBAR, or TROOF)"
                    )
                    return False

            if type == 'boolean':
                if self.symbol_table[token[1]][3] == 'TROOF':
                    return True

                if self.symbol_table[token[1]][3] == 'NUMBR' and self.symbol_table[token[1]][0] in ["1", "0"]:
                    return True

                elif self.symbol_table[token[1]][3] == 'NUMBAR' and self.symbol_table[token[1]][0] in ["1.0", "0.0"]:
                    return True

                else:
                    self.errors.append(
                        f"Line {token[3]}: Value '{token[1]}' cannot be cast to TROOF "
                        f"for '{operation_token[1]}' operation"
                    )

                    return False

        else:
            if type == 'arithmetic':
                # Allow TROOF literals (WIN/FAIL) in arithmetic operations
                if token[2] in ['NUMBR', 'NUMBAR', 'TROOF']:
                    return True
                else:
                    self.errors.append(f"Error: Invalid data type '{token[2]}' for {operation_token[1]} operation on line {token[3]}. Expected NUMBR, NUMBAR, or TROOF.")
                    return False

            elif type == 'boolean':
                if token[2] == 'NUMBR' and token[1] in ["1",1,"0",0]:
                    return True
                elif token[2] == 'NUMBAR' and token[1] in ["1.0",1.0, "0.0",0.0]:
                    return True
                elif token[2] == "NOOB":
                    return True
                elif token[2] == "TROOF":
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
        return False, semantic.errors
    else:
        return True, semantic.errors

