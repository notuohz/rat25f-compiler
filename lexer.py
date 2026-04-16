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
TOKEN_ERROR = "error"

# Character sets for fast checking of operator, separator
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
        
        # Keywords
        self.keywords = {
            'function', 'integer', 'boolean', 'real', 'if', 'else', 'fi',
            'return', 'put', 'get', 'while', 'true', 'false'
            }
        
        # Get first character to start
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
    
    def is_real_dot(self):
        """Check if dot starts a real number or is a separator"""
        return self.peek() and self.peek().isdigit()
    
    def get_next_token(self):
        """Main token-finding function"""
        
        # Skip whitespace
        while self.current_char and self.current_char.isspace():
            self.next_char()
        
        if self.eof_reached:
            return Token(TOKEN_EOF, "", self.line_number, self.column_number)
            
        # Remember position for error messages
        tok_line = self.line_number
        tok_col = self.column_number
        
        # Decipher type of token
        current = self.current_char

        # Digit first
        if current.isdigit():
            return self.process_number(tok_line, tok_col)
        
        # Letter = identifier or keyword
        elif current.isalpha():   
            return self.process_identifier_keyword(tok_line, tok_col)
        
        # Dot = real number or error
        elif current == '.':
            if self.is_real_dot():
                return self.process_real(tok_line, tok_col)
            else:
                # Dot alone is invalid
                invalid_char = self.current_char
                self.next_char()
                return Token(TOKEN_ERROR, invalid_char, tok_line, tok_col)
        
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
            invalid_char = self.current_char
            self.next_char()
            return Token(TOKEN_ERROR, invalid_char, tok_line, tok_col)
    
    def process_identifier_keyword(self, line, column):
        """
        Process identifiers and keywords using FSM approach
        RE: [a-zA-Z][a-zA-Z0-9$]*
        Alex Trang implementation
        """
        lexeme = ""
        
        # FSM states
        # Keyword checked in lookup table
        # State 0: Start (must accept letter)
        # State 1: Reading identifier chars (accepting state)

        # Check for proper first char format
        if not self.current_char or not self.current_char.isalpha():
            return Token(TOKEN_ERROR, "Identifier must start with letter", line, column)
        
        # Accept first char and move to State 1
        lexeme += self.current_char.lower()
        self.next_char()
        
        # State 1: Accept alphanumeric or $
        while self.current_char:
            if self.current_char.isalnum():
                lexeme += self.current_char.lower()
                self.next_char()
            elif self.current_char == '$':
                lexeme += self.current_char.lower()
                self.next_char()
            else:
                break
        
        # Return as keyword if found in lookup table for keywords
        if lexeme in self.keywords:
            return Token(TOKEN_KEYWORD, lexeme, line, column)
        
        # Return as identifier if not found in lookup table for keywords
        return Token(TOKEN_ID, lexeme, line, column)
        
    def process_number(self, line, column):
        """
        Process integers and real numbers using FSM approach
        RE: [0-9]+ (integer) and [0-9]+.[0-9]+ (real)
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
                return Token(TOKEN_ERROR, "Invalid number", line, column)
        
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
                return Token(TOKEN_ERROR, lexeme, line, column)
        
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
            return Token(TOKEN_ERROR, lexeme, line, column)
    
    def process_real(self, line, column):
        """
        Process real numbers starting with decimal point
        RE: .[0-9]+ 
        Alex Zhou implementation
        """
        lexeme = ""
        
        # FSM states
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
            return Token(TOKEN_ERROR, "Expected decimal point", line, column)
        
        # State 1: After decimal point - must have at least one digit
        if state == 1:
            if self.current_char and self.current_char.isdigit():
                lexeme += self.current_char
                self.next_char()
                state = 2
            else:
                # Decimal point without following digit is invalid
                return Token(TOKEN_ERROR, lexeme, line, column)
        
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
            return Token(TOKEN_ERROR, lexeme, line, column)
    
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
        
        if first_char == '=' and next_char == '>':
            self.next_char()
            return Token(TOKEN_OP, "=>", line, column)
        
        # Handle error case, ! by itself is invalid
        if first_char == '!' and next_char != '=':
            return Token(TOKEN_ERROR, first_char, line, column)
        
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
            return Token(TOKEN_ERROR, "Unterminated comment", line, column)
        
        # Skip closing quote
        self.next_char() 
        
        # Get next real token
        return self.get_next_token()
    
    def peek_token(self):
        """
        Look at next token without consuming it.
        Saves lexer state, gets next token, then restores state
        """
        # Save current lexer state
        saved_pos = self.input_file.tell()
        saved_line = self.line_number
        saved_col = self.column_number
        saved_char = self.current_char
        saved_eof = self.eof_reached
        
        # Get next token
        token = self.get_next_token()
        
        # Restore lexer state so token can be read again
        self.input_file.seek(saved_pos)
        self.line_number = saved_line
        self.column_number = saved_col
        self.current_char = saved_char
        self.eof_reached = saved_eof
        
        return token

def create_lexer(input_file_name):
    """
    Create and return a lexer for the given file.
    Returns Rat25FLexer instance if successful, none if file cannot be opened
    """
    try:
        input_file = open(input_file_name, 'r')
        return Rat25FLexer(input_file)
    except FileNotFoundError:
        print(f"Error: File not found - {input_file_name}")
        return None
    except PermissionError:
        print(f"Error: Permission denied - {input_file_name}")
        return None
    except Exception as e:
        print(f"Error opening file {input_file_name}: {str(e)}")
        return None
def main():
    """
    Main program: process Rat25F source file and output tokens
    Prompts user for input and output files
    """
    print("Rat25F Lexical Analyzer")
    print("CPSC323 Assignment 1")
    
    # Get input file name from user
    while True:
        input_file_name = input("Enter input file name: ").strip()
        if input_file_name:
            if os.path.exists(input_file_name):
                break
            else:
                print("Unable to find file: " + input_file_name)
                print("Check the filename and try again.")
        else:
            print("Enter a valid filename.")
    
    # Get output file name from user
    while True:
        output_file_name = input("Enter output file name: ").strip()
        if output_file_name:
            break
        else:
            print("Enter a valid output filename.")
    
    # Create lexer using helper function
    lexer = create_lexer(input_file_name)
    if lexer is None:
        return
    
    # Output to output file 
    try:
        output_file = open(output_file_name, 'w')
    except:
        print("Couldn't create output file: " + output_file_name)
        print("Check if you have permission to write to this location")
        lexer.input_file.close()
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
            elif token.token_type == TOKEN_ERROR:
                # Format & write error messages
                error_line = "ERROR           " + token.lexeme + " (Line " + str(token.line_number) + ", Column " + str(token.column_number) + ")"
                output_file.write(error_line + "\n")
            else:
                # Format & write valid tokens
                token_part = token.token_type.ljust(15)
                lexeme_part = token.lexeme
                output_line = token_part + " " + lexeme_part
                output_file.write(output_line + "\n")
        
        print("Analysis of file complete. Tokens written to " + output_file_name)
            
    except Exception as error:
        print("Something went wrong while analyzing: " + str(error))
    
    # Clean up files
    lexer.input_file.close()
    output_file.close()

if __name__ == "__main__":  
    main()