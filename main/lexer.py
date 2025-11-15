
import re

class Lexer:
    """
    Lexer for LOLCODE
    Responsible for tokenizing input source code, removing comments,
    assigning line numbers, and maintaining token statistics.
    """

    # ================================================================
    # ======================= INITIALIZATION =========================
    # ================================================================
    def __init__(self):
        """================ __init__ ================"""
        # Token counters
        self.keyword_count = 0
        self.identifier_count = 0
        self.numbr_literal_count = 0
        self.numbar_literal_count = 0
        self.yarn_literal_count = 0
        self.troof_literal_count = 0
        self.operator_count = 0
        self.other_symbol_count = 0
        
        # Compile token patterns
        self.patterns = self._create_patterns()

    # ================================================================
    # ======================= PATTERN CREATION =======================
    # ================================================================
    def _create_patterns(self):
        """================ _create_patterns ================"""
        patterns = []

        # ----------------- Multi-word keywords -----------------
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

        # ----------------- Single-word keywords -----------------
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

        # ----------------- Type keywords -----------------
        type_keywords = [
            ('NOOB', 'Type Literal'),
            ('NUMBR', 'Type Literal'),
            ('NUMBAR', 'Type Literal'),
            ('YARN', 'Type Literal'),
            ('TROOF', 'Type Literal'),
        ]
        for keyword, desc in type_keywords:
            patterns.append((re.compile(r'\b' + keyword + r'\b'), desc, 'TYPE'))

        # ----------------- Boolean literals -----------------
        patterns.append((re.compile(r'\bWIN\b'), 'Boolean Value (True)', 'TROOF'))
        patterns.append((re.compile(r'\bFAIL\b'), 'Boolean Value (False)', 'TROOF'))

        # ----------------- Operators -----------------
        patterns.append((re.compile(r'\bAN\b'), 'Multiple Parameter Separator', 'OPERATOR'))

        # ----------------- Numbers -----------------
        patterns.append((re.compile(r'-?[0-9]+\.[0-9]+'), 'Float Literal', 'NUMBAR'))
        patterns.append((re.compile(r'-?[0-9]+'), 'Integer Literal', 'NUMBR'))

        # ----------------- Identifiers -----------------
        patterns.append((re.compile(r'\b[A-Za-z][A-Za-z0-9_]*\b'), 'Variable Identifier', 'IDENTIFIER'))

        # ----------------- Other symbols -----------------
        patterns.append((re.compile(r'[,!?]'), 'Delimiter', 'OTHER'))

        return patterns

    # ================================================================
    # ======================= LINE NUMBERING =========================
    # ================================================================
    def assign_linenum(self, text):
        """================ assign_linenum ================"""
        lines = text.split('\n')
        new_lines = []

        line_count = 1
        for line in lines:
            new_line = (f"{line_count:<3}| ") + line
            new_lines.append(new_line)
            line_count += 1

        return new_lines

    # ================================================================
    # ======================= COMMENT HANDLING ======================
    # ================================================================
    def remove_comments(self, text):
        """================ remove_comments ================"""
        lines = text
        cleaned_lines = []

        for line in lines:
            # Single-line comments
            if 'BTW' in line:
                before_btw = line.split('BTW', 1)[0].strip()
                if before_btw:
                    cleaned_lines.append(before_btw)
            else:
                cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    # ================================================================
    # ======================= TOKENIZATION ==========================
    # ================================================================
    def tokenize_line(self, line):
        """================ tokenize_line ================"""
        tokens = []
        pos = 4  # Skip line number prefix
        in_string = False
        string_content = ""
        final_line_num = int(line[:3].strip())  # Extract line number

        while pos < len(line):

            # Handle string literals
            if line[pos] == '"':
                if in_string:
                    tokens.append(('String Literal', string_content, 'YARN', final_line_num))
                    in_string = False
                    string_content = ""
                else:
                    in_string = True
                pos += 1
                continue

            # Accumulate string content
            if in_string:
                string_content += line[pos]
                pos += 1
                continue

            # Skip whitespace
            if line[pos] in ' \t':
                pos += 1
                continue

            # Match token patterns
            matched = False
            for regex, description, token_type in self.patterns:
                match = regex.match(line, pos)
                if match:
                    token_text = match.group(0)
                    tokens.append((description, token_text, token_type, final_line_num))
                    pos = match.end()
                    matched = True
                    break

            if not matched:
                pos += 1

        return tokens

    # ================================================================
    # ======================= TOKEN COUNTERS =========================
    # ================================================================
    def update_counters(self, tokens):
        """================ update_counters ================"""
        for token in tokens:
            token_type = token[2]
            if token_type in ['KEYWORD', 'TYPE']:
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
            elif token_type in ['OTHER', 'STRING_DELIM']:
                self.other_symbol_count += 1

    # ================================================================
    # ======================= MAIN TOKENIZE ==========================
    # ================================================================
    def tokenize(self, text):
        """================ tokenize ================"""
        text_with_linenum = self.assign_linenum(text)
        final_text = self.remove_comments(text_with_linenum)
        
        all_tokens = []
        for line in final_text.split('\n'):
            line = line.strip()
            if line:
                tokens = self.tokenize_line(line)
                all_tokens.extend(tokens)

        self.update_counters(all_tokens)
        return all_tokens

    # ================================================================
    # ======================= UTILITIES =============================
    # ================================================================
    def print_tokens(self, tokens):
        """================ print_tokens ================"""
        for description, token, _, line_num in tokens:
            print(f"Line {line_num}: {description} {token}")

    def print_statistics(self):
        """================ print_statistics ================"""
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
