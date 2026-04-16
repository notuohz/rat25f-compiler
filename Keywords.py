import sys
import os 

"""
Rat25F Lexical Analyzer
CS323 Assignment 1
by  Andrew Rivera
    Alex Zhou
    Alex Trang
"""

class Tokens:
    def __init__(self):
        self.keywords = {'if', 'elif', 'else', 'repeat', 'write', 'until', 'int', 'return', 'void', 'while', 'float', 'real'}
        self.delimiters = {';', ',', '(', ')', '{', '}'}
        
    def is_letter(self, ch):
        return ch.isalpha()
    
    
    def tokenize(self, text):
        tokens_list = []
        i = 0
        
        while i < len(text):
            ch = text[i]
            
            #skip whitespace
            if ch.isspace():
                i += 1
                continue
            
            #keywords/identifier
            if self.is_letter(ch):
                start = i
                while i < len(text) and self.is_letter(text[i]):
                    i += 1
                lexeme = text[start:i]

                if lexeme in self.keywords:
                    token_type = 'KEYWORD'
                else:
                    token_type = 'IDENTIFIER'
                tokens_list.append((token_type, lexeme))
                    
            else:
                # Unknown or invalid character
                tokens_list.append(('UNKNOWN', ch))
                i += 1

        return tokens_list

code = input("Input test case: ")
lexer = Tokens()
tokens = lexer.tokenize(code)
print('Token           Lexeme')
print('-----           ------')
for token in tokens:
    print(f'{token[0]:<16}{token[1]}')