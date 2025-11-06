import re

class LOLCODELexer:
    def __init__(self):
        # Token counters
        self.keyword_count = 0
        self.identifier_count = 0
        self.numbr_literal_count = 0
        self.numbar_literal_count = 0
        self.yarn_literal_count = 0
        self.troof_literal_count = 0
        self.operator_count = 0
        self.other_symbol_count = 0
        
        # Define token patterns
        self.patterns = self._create_patterns()
    
    def _create_patterns(self):
        patterns = []
        
        # Multi-word keywords
        multi_word = [
            ('I HAS A', 'Variable Declaration'),
            ('IS NOW A', 'Typecasting'),
            ('SUM OF', 'Arithmetic Operator'),
            ('DIFF OF', 'Arithmetic Operator'),
            ('PRODUKT OF', 'Arithmetic Operator'),
            ('QUOSHUNT OF', 'Arithmetic Operator'),
            ('MOD OF', 'Arithmetic Operator'),
            ('BIGGR OF', 'Arithmetic Operator'),
            ('SMALLR OF', 'Arithmetic Operator'),
            ('BOTH OF', 'Boolean Operator'),
            ('EITHER OF', 'Boolean Operator'),
            ('WON OF', 'Boolean Operator'),
            ('ANY OF', 'Boolean Operator'),
            ('ALL OF', 'Boolean Operator'),
            ('BOTH SAEM', 'Comparison Operator'),
            ('DIFFRINT', 'Comparison Operator'),
            (r'O RLY\?', 'Conditional Statement'),
            ('YA RLY', 'Conditional Statement'),
            ('NO WAI', 'Conditional Statement'),
            (r'WTF\?', 'Switch-Case Statement'),
            ('IM IN YR', 'Loop Statement'),
            ('IM OUTTA YR', 'Loop Statement'),
            ('HOW IZ I', 'Function Declaration'),
            ('IF U SAY SO', 'Function Declaration'),
            ('FOUND YR', 'Return Statement'),
            ('I IZ', 'Function Call'),
        ]
        
        for keyword, desc in multi_word:
            patterns.append((re.compile(r'\b' + keyword + r'\b'), desc, 'KEYWORD'))
        
        # Single-word keywords
        single_word = [
            ('HAI', 'Code Delimiter'),
            ('KTHXBYE', 'Code Delimiter'),
            ('WAZZUP', 'Variable List Delimiter'),
            ('BUHBYE', 'Variable List Delimiter'),
            ('ITZ', 'Variable Assignment (following I HAS A)'),
            ('R', 'Variable Assignment'),
            ('NOT', 'Boolean Operator'),
            ('SMOOSH', 'String Operation'),
            ('MAEK', 'Typecasting'),
            ('A', 'Typecasting'),
            ('VISIBLE', 'Output Statement'),
            ('GIMMEH', 'Input Statement'),
            ('MEBBE', 'Conditional Statement'),
            ('OIC', 'Conditional Statement'),
            ('OMG', 'Switch-Case Statement'),
            ('OMGWTF', 'Switch-Case Statement'),
            ('UPPIN', 'Loop Operation'),
            ('NERFIN', 'Loop Operation'),
            ('YR', 'Loop Parameter'),
            ('TIL', 'Loop Condition'),
            ('WILE', 'Loop Condition'),
            ('GTFO', 'Break Statement'),
            ('MKAY', 'End of Expression'),
        ]
        
        for keyword, desc in single_word:
            patterns.append((re.compile(r'\b' + keyword + r'\b'), desc, 'KEYWORD'))
        
        # Type keywords
        type_keywords = [
            ('NOOB', 'Type Literal'),
            ('NUMBR', 'Type Literal'),
            ('NUMBAR', 'Type Literal'),
            ('YARN', 'Type Literal'),
            ('TROOF', 'Type Literal'),
        ]
        
        for keyword, desc in type_keywords:
            patterns.append((re.compile(r'\b' + keyword + r'\b'), desc, 'TYPE'))
        
        # Boolean literals
        patterns.append((re.compile(r'\bWIN\b'), 'Boolean Value (True)', 'TROOF'))
        patterns.append((re.compile(r'\bFAIL\b'), 'Boolean Value (False)', 'TROOF'))
        
        # String delimiter 
        patterns.append((re.compile(r'"'), 'String Delimiter', 'STRING_DELIM'))
        
        # Operators
        patterns.append((re.compile(r'\bAN\b'), 'Multiple Parameter Separator', 'OPERATOR'))
        
        # Numbers 
        patterns.append((re.compile(r'-?[0-9]+\.[0-9]+'), 'Float Literal', 'NUMBAR'))
        patterns.append((re.compile(r'-?[0-9]+'), 'Integer Literal', 'NUMBR'))
        
        # Identifiers 
        patterns.append((re.compile(r'\b[A-Za-z][A-Za-z0-9_]*\b'), 'Variable Identifier', 'IDENTIFIER'))
        
        # Other symbols 
        patterns.append((re.compile(r'[,!?]'), 'Delimiter', 'OTHER'))
        
        return patterns
    
    def remove_comments(self, text):
        lines = text.split('\n')
        cleaned_lines = []
        in_multiline = False
        
        for line in lines:
                        
            # Handle single-line comments
            if 'BTW' in line:
                before_btw = line.split('BTW', 1)[0].strip()
                if before_btw:
                    cleaned_lines.append(before_btw)
            else:
                cleaned_lines.append(line)
        
        return '\n'.join(cleaned_lines)
    
    def tokenize_line(self, line):
        tokens = []
        pos = 0
        in_string = False
        string_content = ""
        
        while pos < len(line):
            # Handle string literals
            if line[pos] == '"':
                if in_string:
                    # End of string
                    tokens.append(('String Literal', string_content, 'YARN'))
                    tokens.append(('String Delimiter', '"', 'STRING_DELIM'))
                    in_string = False
                    string_content = ""
                else:
                    # Start of string
                    tokens.append(('String Delimiter', '"', 'STRING_DELIM'))
                    in_string = True
                pos += 1
                continue
            
            # Accumulate string content
            if in_string:
                string_content += line[pos]
                pos += 1
                continue
            
            # Skip whitespace outside strings
            if line[pos] in ' \t':
                pos += 1
                continue
            
            # Try to match a token pattern
            matched = False
            for regex, description, token_type in self.patterns:
                match = regex.match(line, pos)
                if match:
                    token_text = match.group(0)
                    tokens.append((description, token_text, token_type))
                    pos = match.end()
                    matched = True
                    break
            
            # Skip unknown characters
            if not matched:
                pos += 1
        
        return tokens
    
    def update_counters(self, tokens):
        for _, _, token_type in tokens:
            if token_type == 'KEYWORD' or token_type == 'TYPE':
                self.keyword_count += 1
            elif token_type == 'IDENTIFIER':
                self.identifier_count += 1
            elif token_type == 'NUMBR':
                self.numbr_literal_count += 1
            elif token_type == 'NUMBAR':
                self.numbar_literal_count += 1
            elif token_type == 'YARN':
                self.yarn_literal_count += 1
            elif token_type == 'TROOF':
                self.troof_literal_count += 1
            elif token_type == 'OPERATOR':
                self.operator_count += 1
            elif token_type == 'OTHER' or token_type == 'STRING_DELIM':
                self.other_symbol_count += 1
    
    def tokenize(self, text):
        # Remove comments first
        text = self.remove_comments(text)
        
        # Tokenize each line
        all_tokens = []
        for line in text.split('\n'):
            line = line.strip()
            if line:
                tokens = self.tokenize_line(line)
                all_tokens.extend(tokens)
        
        # Update counters
        self.update_counters(all_tokens)
        
        return all_tokens
    
    def print_tokens(self, tokens):
        for description, token, _ in tokens:
            print(f"{description} {token}")
    
    def print_statistics(self):
        print("\n===========================================")
        print(f"\nKeywords: {self.keyword_count}")
        print(f"Identifiers: {self.identifier_count}")
        print(f"NUMBR Literals: {self.numbr_literal_count}")
        print(f"NUMBAR Literals: {self.numbar_literal_count}")
        print(f"YARN Literals: {self.yarn_literal_count}")
        print(f"TROOF Literals: {self.troof_literal_count}")
        print(f"Operators: {self.operator_count}")
        print(f"Other Symbols: {self.other_symbol_count}\n")
        print("===========================================\n")


def main():
    input_file = "input.txt"
    
    
    with open(input_file, 'r') as file:
        text = file.read()
        
    # Create lexer and analyze
    lexer = LOLCODELexer()
    tokens = lexer.tokenize(text)

    print("====================== All Tokens ======================\n")
    for i in tokens:
        print(f"Token:\t{i}\n")
    print("========================================================\n")


    
    # Display results
    lexer.print_tokens(tokens)
    lexer.print_statistics()

    print("\n====================== Sample Syntax Analyzer======================\n")
    
    if tokens[0][1] != 'HAI':
        print("Invalid Program Start")
    
    elif tokens[len(tokens)-1][1] != 'KTHXBYE':
        print("Invalid Program End")
    
    else:
        print("Valid Program Start and End\n")
    
    
    for token in range(0, len(tokens) - 1):
        if tokens[token][1] == "WAZZUP":
            closed = False
            for i in range (token, len(tokens) - 1):
        
                if tokens[i][1] == "BUHBYE":
                    closed = True
        
            if closed == True:
                print("List Declaration Properly Closed")
    
            else:
                print("List Declaration IS NOT Properly Closed")
    
    
    
    print("======================================================================\n")

    
    return 0


main()


