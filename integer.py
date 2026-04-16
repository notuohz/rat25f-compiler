#!/usr/bin/env python3
"""
Rat25F Lexical Analyzer
CS323 Assignment 1
by  Andrew Rivera
    Alex Zhou
    Alex Trang
"""

import sys
import os

# Token type constants
TOKEN_KEYWORD = "keyword"
TOKEN_ID = "identifier" 
TOKEN_INT = "integer"
TOKEN_REAL = "real"
TOKEN_OP = "operator"
TOKEN_SEP = "separator"
TOKEN_EOF = "EOF"
TOKEN_ERR = "error"

# Character for easy checking **Check if any missing**
OPERATOR_CHARS = '=!<>+-*/'
SEPARATOR_CHARS = '(){}#;,'


class Token:
    """Token data structure"""
    def __init__(self, token_type, lexeme, line_number=1, column_number=1):
        self.token_type = token_type
        self.lexeme = lexeme
        self.line_number = line_number
        self.column_number = column_number

class Rat25FLexer:
    """Lexer for Rat25F"""
    def __init__(self, input_file):
        self.input_file = input_file
        self.current_char = None
        self.line_number = 1
        self.column_number = 0
        self.eof_reached = False
        
        # Keywords for Rat25F language
        self.keywords = {
            'while', 'if', 'else', 'endif', 'do', 'doend', 'for', 'and', 'or', 'function',
            'integer', 'boolean', 'real', 'true', 'false', 'return', 'put', 'get',
            'begin', 'end', 'var', 'const', 'procedure', 'call'
        }
        
        # Get first character to start
        self.next_char()
    
    def skip_whitespace(self):
        """Skip over spaces, tabs and newlines"""
        while self.current_char and self.current_char.isspace():
            self.next_char()
    
    def peek(self):
        """Look at next character without moving forward"""
        pos = self.input_file.tell()
        next_char = self.input_file.read(1)
        self.input_file.seek(pos)
        if next_char:
            return next_char
        else:
            return None
    
    def next_char(self):
        """Move to next character in input file"""
        self.current_char = self.input_file.read(1)
        if not self.current_char:
            self.eof_reached = True
            self.current_char = None
        else:
            self.column_number += 1
            if self.current_char == '\n':
                self.line_number += 1
                self.column_number = 0
    
    def get_next_token(self):
        """Main token-finding function"""
    
        while not self.eof_reached:
            # Skip over whitespace
            self.skip_whitespace()
            
            if self.eof_reached:
                break
                
            # Remember position for error messages
            tok_line = self.line_number
            tok_col = self.column_number
            
            # Decipher type of token
            current = self.current_char

            # Letter = identifier or keyword
            if current.isalpha():   
                return self.process_identifier_keyword(tok_line, tok_col)
            
            # Digit = number 
            elif current.isdigit():
                return self.process_number(tok_line, tok_col)
            
            # Dot = real number
            elif current == '.':
                return self.process_real(tok_line, tok_col)
            
            # Operator symbols
            elif current in OPERATOR_CHARS:
                return self.process_operator(tok_line, tok_col)
            
            # Separator symbols
            elif current in SEPARATOR_CHARS:
                return self.process_separator(tok_line, tok_col)
            
            # Quote = comment
            elif current == '"':
                return self.process_comment(tok_line, tok_col)
            
            # Unknown = error
            else:
                bad_char = self.current_char
                self.next_char()
                return Token(TOKEN_ERR, bad_char, tok_line, tok_col)
        
        # End of file
        return Token(TOKEN_EOF, "", self.line_number, self.column_number)
    

    def process_number(self, line, column):
        """
        Process integers and real numbers using FSM approach
        Handles patterns: [0-9]+ (integer) and [0-9]+.[0-9]+ (real)
        Alex Zhou implementation
        """
        lexeme = ""
        
        # FSM states for number recognition
        # State 0: Start (must accept digit)
        # State 1: Integer part (accepting state for integer) 
        # State 2: After decimal point(must have digit)
        # State 3: Fractional part (accepting state for real)
        
        state = 0
        
        # State 0: Start state - must have digit
        if state == 0:

            if self.current_char and self.current_char.isdigit():
                lexeme += self.current_char
                self.next_char()
                state = 1
            else:
                # Invalid start - should not happen since we check isdigit() before calling
                return Token(TOKEN_ERR, "Invalid number", line, column)
        
        # State 1: Reading integer part
        while state == 1 and self.current_char and self.current_char.isdigit():
            lexeme += self.current_char
            self.next_char()
        
        # Check if we have a decimal point (transition to real number)
        if state == 1 and self.current_char == '.':
            # Look ahead to see if there's a digit after the decimal point
            next_char = self.peek()
            if next_char and next_char.isdigit():
                lexeme += self.current_char  # Add the decimal point
                self.next_char()
                state = 2
            else:
                # Decimal point without following digit - return integer and let decimal be processed separately
                return Token(TOKEN_INT, lexeme, line, column)
        
        # State 2: After decimal point - must have at least one digit
        if state == 2:
            if self.current_char and self.current_char.isdigit():
                lexeme += self.current_char
                self.next_char()
                state = 3
            else:
                # This shouldn't happen since we checked with peek()
                return Token(TOKEN_ERR, lexeme, line, column)
        
        # State 3: Reading fractional part - continue reading digits
        while state == 3 and self.current_char and self.current_char.isdigit():
            lexeme += self.current_char
            self.next_char()
        
        # Determine final token type based on final state
        if state == 1:
            # Ended in integer state
            return Token(TOKEN_INT, lexeme, line, column)
        elif state == 3:
            # Ended in real number state
            return Token(TOKEN_REAL, lexeme, line, column)
        else:
            # Should not reach here with valid input
            return Token(TOKEN_ERR, lexeme, line, column)
    
    def process_real(self, line, column):
        """
        Process real numbers starting with decimal point
        Handles pattern: .[0-9]+ 
        Alex Zhou implementation
        """
        lexeme = ""
        
        # FSM states for real number starting with decimal point
        # State 0: Start with decimal point
        # State 1: After decimal point (must have digit)
        # State 2: Reading fractional digits (accepting state)
        
        state = 0
        
        # State 0: Must start with decimal point
        if state == 0 and self.current_char == '.':
            lexeme += self.current_char
            self.next_char()
            state = 1
        else:
            # Should not happen since we check for '.' before calling
            return Token(TOKEN_ERR, "Expected decimal point", line, column)
        
        # State 1: After decimal point - must have at least one digit
        if state == 1:
            if self.current_char and self.current_char.isdigit():
                lexeme += self.current_char
                self.next_char()
                state = 2
            else:
                # Decimal point without following digit is invalid
                return Token(TOKEN_ERR, lexeme, line, column)
        
        # State 2: Continue reading fractional digits
        while state == 2 and self.current_char and self.current_char.isdigit():
            lexeme += self.current_char
            self.next_char()
        
        # Check final state
        if state == 2:
            # Valid real number starting with decimal point
            return Token(TOKEN_REAL, lexeme, line, column)
        else:
            # Invalid real number
            return Token(TOKEN_ERR, lexeme, line, column)
    
    def process_operator(self, line, column):
        """Handle all operators"""
        first_char = self.current_char
        self.next_char()
        
        # Handle multi-character operators first
        next_char = self.current_char
        
        if first_char == '=' and next_char == '=':
            self.next_char()
            return Token(TOKEN_OP, "==", line, column)
        
        if first_char == '!' and next_char == '=':
            self.next_char()
            return Token(TOKEN_OP, "!=", line, column)
        
        if first_char == '<' and next_char == '=':
            self.next_char()
            return Token(TOKEN_OP, "<=", line, column)
        
        if first_char == '>' and next_char == '=':
            self.next_char()
            return Token(TOKEN_OP, ">=", line, column)
        
        # Handle error case, ! by itself is invalid
        if first_char == '!' and next_char != '=':
            return Token(TOKEN_ERR, first_char, line, column)
        
        # Must be single character operator
        return Token(TOKEN_OP, first_char, line, column)
    
    def process_separator(self, line, column):
        """Handle single character separators"""
        sep_char = self.current_char
        self.next_char()
        return Token(TOKEN_SEP, sep_char, line, column)
    
    def process_comment(self, line, column):
        """Handle quoted comments by skipping over them entirely"""
        # Skip opening quote
        self.next_char() 
        
        # Read everything until closing quote
        while self.current_char and self.current_char != '"':
            self.next_char()
        
        # Check for unterminated comment
        if not self.current_char:
            return Token(TOKEN_ERR, "Unterminated comment", line, column)
        
        # Skip closing quote
        self.next_char() 
        
        # Get next real token
        return self.get_next_token()


def main():
    """
    Main program: process Rat25F source file and output tokens
    Usage: python lexer.py <input_file> <output_file>
    """
    # Need script name + input file + output file = 3 args required
    num_args = len(sys.argv)
    if num_args != 3:
        print("Need both input and output files. Usage: python lexer.py <input_file> <output_file>")
        print("Example: python lexer.py test.rat25f results.txt")
        return
    
    input_file_name = sys.argv[1]
    output_file_name = sys.argv[2]
    
    # Make sure input file exists
    if not os.path.exists(input_file_name):
        print("Unable to find file: " + input_file_name)
        print("Make sure you typed the filename correctly and the file exists")
        return
    
    # Try to open input file
    try:
        input_file = open(input_file_name, 'r')
    except:
        print("Couldn't open input file: " + input_file_name)
        print("Check file permissions or if it's being used by another program")
        return
    
    # Create lexer
    lexer = Rat25FLexer(input_file)
    
    # Output to output file 
    try:
        output_file = open(output_file_name, 'w')
    except:
        print("Couldn't create output file: " + output_file_name)
        print("Check if you have permission to write to this location")
        input_file.close()
        return
    
    # Output header for results
    output_file.write("Token           Lexeme\n")
    output_file.write("-----           ------\n")
    
    # Process all tokens from the input file
    try:
        while True:
            token = lexer.get_next_token()
            
            if token.token_type == TOKEN_EOF:
                break
            elif token.token_type == TOKEN_ERR:
                # Format & write error messages
                error_line = "ERROR           " + token.lexeme + " (Line " + str(token.line_number) + ", Column " + str(token.column_number) + ")"
                output_file.write(error_line + "\n")
            else:
                # Format & write valid tokens
                token_part = token.token_type.ljust(15)
                lexeme_part = token.lexeme
                output_line = token_part + " " + lexeme_part
                output_file.write(output_line + "\n")
        
        # Let user know we're done
        print("Analysis complete. Tokens written to " + output_file_name)
            
    except Exception as error:
        print("Something went wrong while analyzing: " + str(error))
        print("Check input file format and try again")
    
    # Clean up files
    input_file.close()
    output_file.close()


if __name__ == "__main__":  
    main()
