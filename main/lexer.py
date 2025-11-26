
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
        
        # Error collector
        self.errors = []

        # Compile token patterns
        self.patterns = self._create_patterns()

        # Store all keywords for invalid keyword detection
        self.valid_keywords = set([
            'I', 'HAS', 'A', 'IS', 'NOW', 'SUM', 'OF', 'DIFF', 'PRODUKT', 'QUOSHUNT', 'MOD',
            'BIGGR', 'SMALLR', 'BOTH', 'SAEM', 'DIFFRINT', 'EITHER', 'WON', 'ANY', 'ALL',
            'O RLY?', 'YA', 'RLY', 'NO', 'WAI', 'WTF?', 'IM', 'IN', 'YR', 'OUTTA', 'HOW', 'IZ', 'IF',
            'U', 'SAY', 'SO', 'FOUND', 'ITZ', 'R', 'NOT', 'SMOOSH', 'VISIBLE', 'GIMMEH',
            'MEBBE', 'OIC', 'OMG', 'OMGWTF', 'UPPIN', 'NERFIN', 'TIL', 'WILE', 'GTFO', 'MKAY',
            'HAI', 'KTHXBYE', 'BUHBYE', 'WAZZUP'
        ])

    # ================================================================
    # ======================= PATTERN CREATION =======================
    # ================================================================
    def _create_patterns(self):
        """================ _create_patterns ================"""
        patterns = []
        patterns.append((re.compile(r'O RLY\?'), 'Conditional Statement', 'KEYWORD'))
        patterns.append((re.compile(r'WTF\?'), 'Switch-Case Statement', 'KEYWORD'))


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
            ('YA RLY', 'Conditional Statement'),
            ('NO WAI', 'Conditional Statement'),
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

        # ----------------- VISIBLE seperator -----------------
        patterns.append((re.compile(r'\+'), 'VISIBLE Separator', 'Separator'))


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
    def tokenize_line(self, raw_line):
        """================ tokenize_line ================"""
        tokens = []
        line = raw_line
        pos = 4  # Skip "3 | " prefix
        in_string = False
        string_content = ""
        final_line_num = int(raw_line[:3].strip())

        while pos < len(line):

            if line[pos] == '"':
                if in_string:
                    tokens.append(('String Literal', string_content, 'YARN', final_line_num))
                    in_string = False
                    string_content = ""
                else:
                    in_string = True
                pos += 1
                continue

            if in_string:
                string_content += line[pos]
                pos += 1
                continue

            if line[pos] in ' \t':
                pos += 1
                continue

            # INVALID IDENTIFIER STARTING WITH NUMBER
            invalid_identifier_match = re.match(r'-?[0-9]+[A-Za-z_][A-Za-z0-9_]*', line[pos:])
            if invalid_identifier_match:
                bad = invalid_identifier_match.group(0)
                self.errors.append(
                    f"Invalid identifier '{bad}' at line {final_line_num} "
                    "(identifiers cannot start with a digit)"
                )
                pos += len(bad)
                continue

            # TRY MATCHING TOKEN PATTERNS
            matched = False
            for regex, description, token_type in self.patterns:
                match = regex.match(line, pos)
                if match:
                    value = match.group(0)

                    # IDENTIFIER ——> check invalid keyword
                    if token_type == "IDENTIFIER":
                        upper = value.upper()
                        if upper in self.valid_keywords:
                            # This is a keyword but matched wrongly as identifier
                            self.errors.append(
                                f"Invalid use of keyword '{value}' at line {final_line_num}"
                            )
                        else:
                            # Check if identifier looks like a broken keyword
                            # RULE: if it's ALL CAPS and similar to a keyword, mark as invalid
                            if value.isupper():
                                # Compute similarity by prefix length
                                for kw in self.valid_keywords:
                                    if kw.startswith(value[0:2]):
                                        self.errors.append(
                                            f"Invalid keyword '{value}' at line {final_line_num}"
                                        )
                                        break

                    tokens.append((description, value, token_type, final_line_num))
                    pos = match.end()
                    matched = True
                    break

            # INVALID UNKNOWN TOKEN
            if not matched:
                if re.match(r'[A-Za-z]', line[pos]):
                    bad = re.match(r'[A-Za-z][A-Za-z0-9_]*', line[pos:]).group(0)
                    self.errors.append(f"Invalid token '{bad}' at line {final_line_num}")
                    pos += len(bad)
                else:
                    pos += 1  # Skip unknown char

        return tokens

    # ================================================================
    # ======================= TOKEN COUNTERS =========================
    # ================================================================
    def update_counters(self, tokens):
        for desc, tok, typ, ln in tokens:
            if typ in ['KEYWORD', 'TYPE']:
                self.keyword_count += 1
            elif typ == 'IDENTIFIER':
                self.identifier_count += 1
            elif typ == 'NUMBR':
                self.numbr_literal_count += 1
            elif typ == 'NUMBAR':
                self.numbar_literal_count += 1
            elif typ == 'YARN':
                self.yarn_literal_count += 1
            elif typ == 'TROOF':
                self.troof_literal_count += 1
            elif typ == 'OPERATOR':
                self.operator_count += 1
            elif typ in ['OTHER']:
                self.other_symbol_count += 1

    # ================================================================
    # ======================= MAIN TOKENIZE ==========================
    # ================================================================
    def tokenize(self, text):
        text_with_linenum = self.assign_linenum(text)
        final_text = self.remove_comments(text_with_linenum)
        
        all_tokens = []
        for raw_line in final_text.split('\n'):
            stripped = raw_line.strip()

            if stripped:
                line_tokens = self.tokenize_line(raw_line)
                all_tokens.extend(line_tokens)

            # Add NEWLINE token (parser needs it)
            line_num = int(raw_line[:3].strip())
            all_tokens.append(("Newline", "\\n", "NEWLINE", line_num))

        self.update_counters(all_tokens)
        return all_tokens


# ======================= ERROR HANDLING ==========================
    def print_errors(self):
        """Print all lexer errors collected during tokenization"""
        if not self.errors:
            print("No lexer errors found.")
            return

        print("\n========== LEXER ERRORS ==========")
        for err in self.errors:
            print(err)
        print("==================================\n")

    # ================================================================
    # ======================= UTILITIES =============================
    # ================================================================
    def print_tokens(self, tokens):
        for description, token, _, line_num in tokens:
            print(f"Line {line_num}: {description} {token}")

    def print_statistics(self):
        print("\n===========================================")
        print(f"Keywords: {self.keyword_count}")
        print(f"Identifiers: {self.identifier_count}")
        print(f"NUMBR Literals: {self.numbr_literal_count}")
        print(f"NUMBAR Literals: {self.numbar_literal_count}")
        print(f"YARN Literals: {self.yarn_literal_count}")
        print(f"TROOF Literals: {self.troof_literal_count}")
        print(f"Operators: {self.operator_count}")
        print(f"Other Symbols: {self.other_symbol_count}\n")
        print("===========================================\n")
