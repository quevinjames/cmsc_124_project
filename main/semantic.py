import re
from parser import Parser

class SemanticAnalyzer(Parser):
    def __init__(self, tokens, symbol_table):
        super().__init__(tokens)
        self.errors = []
        self.symbol_table = symbol_table
        self.boolean_typecast = {}
    
    def analyze(self):
        """Main analysis entry point"""
        print("\n==================== START ANALYZE HERE ================\n")
        
        while self.current_token()[1] != 'KTHXBYE':
            self.analyze_statement()
            
    def analyze_statement(self):
        """Analyze a single statement and advance tokens"""
        token = self.current_token()
        
        # Check for arithmetic expressions
        if token[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            self.analyze_arithmetic_expr()

        elif token[1] in ['BOTH OF', 'EITHER OF', 'WON OF', 'NOT', 'ALL OF', 'ANY OF']:
            self.analyze_boolean_expr()

        elif token[1] in ['BOTH SAEM', 'DIFFRINT', 'BIGGR OF', 'SMALLR OF']:
            self.analyze_comparison_expr()
        else:
            # For any unhandled token, consume it to avoid infinite loop
            self.consume()
          
    def analyze_arithmetic_expr(self):
        """Check arithmetic expression operands for type compatibility"""
        operand_token = self.consume()
        op_type = "arithmetic"
        
        # Check first operand
        # Check for nested operation FIRST
        if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            self.analyze_arithmetic_expr()  # Recurse for nested operation
        else:
            # Handle string delimiters if present
            if self.current_token()[1] == '"':
                self.consume('"')  # Consume opening delimiter
            
            if not self.is_valid_operand(op_type, self.current_token(), operand_token):
                return
            
            self.consume()  # Consume the operand value
            
            # Consume closing delimiter if present
            if self.current_token()[1] == '"':
                self.consume('"')
        
        # Expect AN keyword
        self.consume('AN')
        
        # Check second operand
        # Check for nested operation FIRST
        if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            self.analyze_arithmetic_expr()  # Recurse for nested operation
        else:
            # Handle string delimiters if present
            if self.current_token()[1] == '"':
                self.consume('"')  # Consume opening delimiter
            
            if not self.is_valid_operand(op_type, self.current_token(), operand_token):
                return
            
            self.consume()  # Consume the operand value
            
            # Consume closing delimiter if present
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
            self.consume('"')  # Consume opening delimiter

        if self.current_token()[2] == 'IDENTIFIER':

            if self.symbol_table[self.current_token()[1]][3] not in ['NUMBR', 'NUMBAR']:
                self.errors.append(f"Error: The opperand '{self.current_token()[1]}' cannot be used in {operand_token[1]} operation on line {self.current_token()[3]}")
                return

            
        elif self.current_token()[2] not in ['NUMBR', 'NUMBAR']:
            self.errors.append(f"Error: The opperand '{self.current_token()[1]}' cannot be used in {operand_token[1]} operation on line {self.current_token()[3]}")
            return
            
        self.consume()  # Consume the operand value
            
       
        if self.current_token()[1] == '"':
            self.consume('"')

        
        self.consume('AN')
        
        # Check second operand
        # Check for nested operation FIRST
        if self.current_token()[1] in ['BOTH SAEM', 'DIFFRINT', 'BIGGR OF', 'SMALLR OF']:
            self.analyze_comparison_expr_expr()  # Recurse for nested operation
        else:

            # Handle string delimiters if present
            if self.current_token()[1] == '"':
                self.consume('"')  # Consume opening delimiter

            if self.current_token()[2] == 'IDENTIFIER':
                print("IDENTIFIER DITO SA BOTH SAEM")

                if self.symbol_table[self.current_token()[1]][3] not in ['NUMBR', 'NUMBAR']:
                    self.errors.append(f"Error: The opperand '{self.current_token()[1]}' cannot be used in {operand_token[1]} operation on line {self.current_token()[3]}")
                    return
            
            elif token[2] not in ['NUMBR', 'NUMBAR']:
                self.errors.append(f"Error: The opperand '{self.current_token()[1]}' cannot be used in {operand_token[1]} operation on line {self.current_token()[3]}")
                return
            
            self.consume()  # Consume the operand value
            
            # Consume closing delimiter if present
            if self.current_token()[1] == '"':
                self.consume('"')




    def is_valid_operand(self, type, token, operation_token):
        """
        Check if a token is a valid numeric operand for arithmetic operations.
        Returns True if valid, False otherwise (and adds error).
        """
        
        # Check if it's a YARN that cannot be typecast to numeric
        if token[2] == 'YARN':
            # Check if YARN can be typecast to NUMBR (integer) or NUMBAR (float)

            if type == 'arithmetic':
                is_numbr = re.match(r'^-?[0-9]+$', token[1])
                is_numbar = re.match(r'^-?[0-9]+\.[0-9]+$', token[1])

                if is_numbr:
                    print("TYPECAST ARITHMETIC")
                    return True

                elif is_numbar:
                    print("TYPECAST ARITHMETIC")
                    return True

                else:
                    self.errors.append(f"Error: '{token[1]}' cannot be typecasted to NUMBR or NUMBAR for {operation_token[1]} operation on line {token[3]}")
                    return False


            elif type == 'boolean':

                if token[1] in ['0', '1']:
                    print("TYPECAST BOOLEAN")
                    return True

                elif token[1] in ['0.0', '1.0']:
                    print("TYPECASE BOOLEAN")
                    return True

                elif token[1]  in ['WIN', 'FAIL']:
                    print("TYPECAST BOOLEAN")
                    return True
                
                else:
                    self.errors.append(f"Error: '{token[1]}' cannot be typecasted to TROOF for {operation_token[1]} operation on line {token[3]}")
                    return False

            
            
        # Check if the operand is an identifier
        elif token[2] == 'IDENTIFIER':

            # Check if it's a YARN that cannot be typecast to numeric
            if self.symbol_table[token[1]][3] == 'YARN':
                
                if type == 'arithmetic':
                    is_numbr = re.match(r'^-?[0-9]+$', self.symbol_table[token[1]][0])
                    is_numbar = re.match(r'^-?[0-9]+\.[0-9]+$', self.symbol_table[token[1]][0])

                    if is_numbr:
                        print("TYPECAST ARITHMETIC")
                        return True

                    elif is_numbar:
                        print("TYPECAST ARITHMETIC")
                        return True

                    else:
                        self.errors.append(f"Error: '{token[1]}' cannot be typecasted to NUMBR or NUMBAR for {operation_token[1]} operation on line {token[3]}")
                        return False

                elif type == 'boolean':

                    if self.symbol_table[token[1]][0] in ['0', '1']:
                        print("TYPECAST BOOLEAN")
                        return True

                    elif self.symbol_table[token[1]][0] in ['0.0', '1.0']:
                        print("TYPECASE BOOLEAN")
                        return True

                    elif self.symbol_table[token[1]][0] in ['WIN', 'FAIL']:
                        print("TYPECAST BOOLEAN")
                        return True

                    elif self.symbol_table[token[1]][0] == 'NOOB':
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
                    self.errors.append(
                    f"Error: Invalid data type '{self.symbol_table[token[1]][1]}' for {operation_token[1]} "
                    f"operation on line {token[3]}. Expected NUMBR or NUMBAR."
                )
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
                    print("TYPECASE BOOLEAN")
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


def analyze_lolcode(tokens, symbol_table):
    """Entry point for semantic analysis"""
    semantic = SemanticAnalyzer(tokens, symbol_table)
    semantic.analyze()
    
    if semantic.errors:
        print("\n=== SEMANTIC ERRORS FOUND ===")
        for error in semantic.errors:
            print(error)
        return semantic.errors
    else:
        print("\n=== NO SEMANTIC ERRORS ===")
        return []
