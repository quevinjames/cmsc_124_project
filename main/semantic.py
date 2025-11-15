import re
from parser import Parser

class SemanticAnalyzer(Parser):
    def __init__(self, tokens, symbol_table):
        super().__init__(tokens)
        self.errors = []
        self.symbol_table = symbol_table
    
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
        # Check for other statement types (VISIBLE, variable declarations, etc.)
        elif token[1] == 'VISIBLE':
            self.consume('VISIBLE')
            # The next token might be an expression or literal
            if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
                self.analyze_arithmetic_expr()
            else:
                self.consume()  # Consume the literal/variable being displayed
        # Add more statement types as needed
        else:
            # For any unhandled token, consume it to avoid infinite loop
            self.consume()
          
    def analyze_arithmetic_expr(self):
        """Check arithmetic expression operands for type compatibility"""
        operand_token = self.consume()
        
        # Check first operand
        # Check for nested operation FIRST
        if self.current_token()[1] in ['SUM OF', 'DIFF OF', 'PRODUKT OF', 'QUOSHUNT OF', 'MOD OF']:
            self.analyze_arithmetic_expr()  # Recurse for nested operation
        else:
            # Handle string delimiters if present
            if self.current_token()[1] == '"':
                self.consume('"')  # Consume opening delimiter
            
            if not self.is_valid_numeric_operand(self.current_token(), operand_token):
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
            
            if not self.is_valid_numeric_operand(self.current_token(), operand_token):
                return
            
            self.consume()  # Consume the operand value
            
            # Consume closing delimiter if present
            if self.current_token()[1] == '"':
                self.consume('"')
    
    def is_valid_numeric_operand(self, token, operation_token):
        """
        Check if a token is a valid numeric operand for arithmetic operations.
        Returns True if valid, False otherwise (and adds error).
        """
        
        # Check if it's a YARN that cannot be typecast to numeric
        if token[2] == 'YARN':
            # Check if YARN can be typecast to NUMBR (integer) or NUMBAR (float)
            is_numbr = re.match(r'^-?[0-9]+$', token[1])
            is_numbar = re.match(r'^-?[0-9]+\.[0-9]+$', token[1])
            
            if not (is_numbr or is_numbar):
                self.errors.append(
                    f"Error: '{token[1]}' cannot be typecasted to NUMBR or NUMBAR "
                    f"for {operation_token[1]} operation on line {token[3]}"
                )
                return False

        # Check if the operand is an identifier
        elif token[2] == 'IDENTIFIER':

            # Check if it's a YARN that cannot be typecast to numeric
            if self.symbol_table[token[1]][3] == 'YARN':
                # Check if YARN can be typecast to NUMBR (integer) or NUMBAR (float)
                is_numbr = re.match(r'^-?[0-9]+$', self.symbol_table[token[1]][0])
                is_numbar = re.match(r'^-?[0-9]+\.[0-9]+$', self.symbol_table[token[1]][0])
                
                if not (is_numbr or is_numbar):
                    self.errors.append(
                        f"Error: '{token[1]}' cannot be typecasted to NUMBR or NUMBAR "
                        f"for {operation_token[1]} operation on line {token[3]}"
                    )
                    return False


            elif self.symbol_table[token[1]][3] not in ['NUMBR', 'NUMBAR']:
                self.errors.append(
                f"Error: Invalid data type '{self.symbol_table[token[1]][1]}' for {operation_token[1]} "
                f"operation on line {token[3]}. Expected NUMBR or NUMBAR."
            )
                return False

        # Check if it's a valid numeric type
        elif token[2] not in ['NUMBR', 'NUMBAR']:
            self.errors.append(
                f"Error: Invalid data type '{token[2]}' for {operation_token[1]} "
                f"operation on line {token[3]}. Expected NUMBR or NUMBAR."
            )
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
