#!/usr/bin/env python3

"""
Rat25F Syntax Analyzer
CPSC323 Assignment 2
by  Andrew Rivera
    Alex Zhou
    Alex Trang
"""

import sys
import os

from lexer import (
    create_lexer, 
    Token,
    TOKEN_KEYWORD, 
    TOKEN_ID, 
    TOKEN_INT, 
    TOKEN_REAL, 
    TOKEN_OP, 
    TOKEN_SEP, 
    TOKEN_EOF,
    TOKEN_ERROR
)

class Rat25FParser:
    """Parser for Rat25F"""
    def __init__(self, lexer, output_file):
        self.lexer = lexer
        self.output_file = output_file
        self.current_token = None
        self.errors = []
        self.print_rules = True
        self.next_token()
    
    def next_token(self):
        """Move to next token"""
        self.current_token = self.lexer.get_next_token()

        # Skip over lexical errors
        while self.current_token.token_type == TOKEN_ERROR:
            self.error("Lexical error: " + self.current_token.lexeme)
            self.current_token = self.lexer.get_next_token()
    
    def write_output(self, text):
        """Write text to output file"""
        self.output_file.write(text + "\n")
    
    def print_token(self):
        """Print current token and lexeme to output file"""
        self.write_output("")
        token_part = "Token: " + self.current_token.token_type.ljust(15)
        lexeme_part = "Lexeme: " + self.current_token.lexeme
        output_line = token_part + " " + lexeme_part
        self.write_output(output_line)
    
    def print_production(self, production_rule):
        """Print production rule to output file if switch is on"""
        if self.print_rules:
            self.write_output("     " + production_rule)
    
    def match(self, exp_type, exp_lexeme=None):
        """
        Check if current token matches expected type/lexeme and consume it
        True if match is successful, false otherwise
        """
        if self.current_token.token_type == exp_type:
            if exp_lexeme is None or self.current_token.lexeme == exp_lexeme:
                self.print_token()
                self.next_token()
                return True
        return False
    
    def expect(self, exp_type, exp_lexeme=None):
        """
        Require current token to match expected type/lexeme
        Reports syntax error if match fails
        """
        if not self.match(exp_type, exp_lexeme):
            if exp_lexeme:
                self.error("Expected " + exp_type + " '" + exp_lexeme + "', got " + self.current_token.token_type + " '" + self.current_token.lexeme + "'")
            else:
                self.error("Expected " + exp_type + ", got " + self.current_token.token_type + " '" + self.current_token.lexeme + "'")
    
    def error(self, message):
        """Reports syntax error with line and column info"""
        err_msg = "Syntax error at line " + str(self.current_token.line_number) + ", column " + str(self.current_token.column_number) + ": " + message
        self.errors.append(err_msg)
        print(err_msg)
        self.write_output(err_msg)
    
# =============================== Grammar rule functions below ===============================
    def rat25f(self):
        """
        R1: <Rat25F> ::= <Opt Function Definitions> # <Opt Declaration List> <Statement List> #
        """
        self.print_production("<Rat25F> -> <Opt Function Definitions> # <Opt Declaration List> <Statement List> #")
        self.opt_function_definitions()
        self.expect(TOKEN_SEP, "#")
        self.opt_declaration_list()
        self.statement_list()
        self.expect(TOKEN_SEP, "#")
    
    def opt_function_definitions(self):
        """
        R2: <Opt Function Definitions> ::= <Function Definitions> | <Empty>
        """
        self.print_production("<Opt Function Definitions> -> <Function Definitions> | <Empty>")
        # Check if have 'function' keyword
        if self.current_token.token_type == TOKEN_KEYWORD and self.current_token.lexeme == "function":
            self.function_definitions()
        else:
            self.empty()
    
    def function_definitions(self):
        """
        R3: <Function Definitions> ::= <Function> | <Function> <Function Definitions>
        """
        self.print_production("<Function Definitions> -> <Function> <Function Definitions>")
        self.function()
        # Check if another function is after
        if self.current_token.token_type == TOKEN_KEYWORD and self.current_token.lexeme == "function":
            self.function_definitions()
    
    def function(self):
        """
        R4: <Function> ::= function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>
        """
        self.print_production("<Function> -> function <Identifier> ( <Opt Parameter List> ) <Opt Declaration List> <Body>")
        self.expect(TOKEN_KEYWORD, "function")
        self.expect(TOKEN_ID)
        self.expect(TOKEN_SEP, "(")
        self.opt_parameter_list()
        self.expect(TOKEN_SEP, ")")
        self.opt_declaration_list()
        self.body()
    
    def opt_parameter_list(self):
        """
        R5: <Opt Parameter List> ::= <Parameter List> | <Empty>
        """
        self.print_production("<Opt Parameter List> -> <Parameter List> | <Empty>")
        # Check if have an identifier (start of parameter)
        if self.current_token.token_type == TOKEN_ID:
            self.parameter_list()
        else:
            self.empty()
    
    def parameter_list(self):
        """
        R6: <Parameter List> ::= <Parameter> | <Parameter> , <Parameter List>
        """
        self.print_production("<Parameter List> -> <Parameter> , <Parameter List>")
        self.parameter()
        # Check if comma is after (more parameters)
        if self.current_token.token_type == TOKEN_SEP and self.current_token.lexeme == ",":
            self.match(TOKEN_SEP, ",")
            self.parameter_list()
    
    def parameter(self):
        """
        R7: <Parameter> ::= <IDs> <Qualifier>
        """
        self.print_production("<Parameter> -> <IDs> <Qualifier>")
        self.ids()
        self.qualifier()
    
    def qualifier(self):
        """
        R8: <Qualifier> ::= integer | boolean | real
        """
        self.print_production("<Qualifier> -> integer | boolean | real")
        if self.current_token.token_type == TOKEN_KEYWORD:
            if self.current_token.lexeme in ["integer", "boolean", "real"]:
                self.match(TOKEN_KEYWORD)
            else:
                self.error("Expected qualifier (integer, boolean, or real)")
        else:
            self.error("Expected qualifier")
    
    def body(self):
        """
        R9: <Body> ::= { <Statement List> }
        """
        self.print_production("<Body> -> { <Statement List> }")
        self.expect(TOKEN_SEP, "{")
        self.statement_list()
        self.expect(TOKEN_SEP, "}")
    
    def opt_declaration_list(self):
        """
        R10: <Opt Declaration List> ::= <Declaration List> | <Empty>
        """
        self.print_production("<Opt Declaration List> -> <Declaration List> | <Empty>")
        # Check if have a qualifier (start of declaration)
        if self.current_token.token_type == TOKEN_KEYWORD and self.current_token.lexeme in ["integer", "boolean", "real"]:
            self.declaration_list()
        else:
            self.empty()
    
    def declaration_list(self):
        """
        R11: <Declaration List> ::= <Declaration> ; | <Declaration> ; <Declaration List>
        """
        self.print_production("<Declaration List> -> <Declaration> ; <Declaration List>")
        self.declaration()
        self.expect(TOKEN_SEP, ";")
        # Check if another declaration is after
        if self.current_token.token_type == TOKEN_KEYWORD and self.current_token.lexeme in ["integer", "boolean", "real"]:
            self.declaration_list()
    
    def declaration(self):
        """
        R12: <Declaration> ::= <Qualifier> <IDs>
        """
        self.print_production("<Declaration> -> <Qualifier> <IDs>")
        self.qualifier()
        self.ids()
    
    def ids(self):
        """
        R13: <IDs> ::= <Identifier> | <Identifier> , <IDs>
        """
        self.print_production("<IDs> -> <Identifier> , <IDs>")
        self.expect(TOKEN_ID)
        # Check if comma is after (more identifiers)
        if self.current_token.token_type == TOKEN_SEP and self.current_token.lexeme == ",":
            self.match(TOKEN_SEP, ",")
            self.ids()
    
    def statement_list(self):
        """
        R14: <Statement List> ::= <Statement> | <Statement> <Statement List>
        """
        self.print_production("<Statement List> -> <Statement> <Statement List>")
        self.statement()
        # Check if another statement is after, look for statement starting tokens
        if self.current_token.token_type == TOKEN_SEP and self.current_token.lexeme == "{":
            self.statement_list()
        elif self.current_token.token_type == TOKEN_ID:
            self.statement_list()
        elif self.current_token.token_type == TOKEN_KEYWORD:
            if self.current_token.lexeme in ["if", "return", "put", "get", "while"]:
                self.statement_list()
    
    def statement(self):
        """
        R15: <Statement> ::= <Compound> | <Assign> | <If> | <Return> | <Print> | <Scan> | <While>
        """
        self.print_production("<Statement> -> <Compound> | <Assign> | <If> | <Return> | <Print> | <Scan> | <While>")
        
        # Determine which statement type based on current token
        if self.current_token.token_type == TOKEN_SEP and self.current_token.lexeme == "{":
            self.compound()
        elif self.current_token.token_type == TOKEN_KEYWORD:
            if self.current_token.lexeme == "if":
                self.if_statement()
            elif self.current_token.lexeme == "return":
                self.return_statement()
            elif self.current_token.lexeme == "put":
                self.print_statement()
            elif self.current_token.lexeme == "get":
                self.scan()
            elif self.current_token.lexeme == "while":
                self.while_statement()
            else:
                self.error("Unknown keyword in statement")
        elif self.current_token.token_type == TOKEN_ID:
            self.assign()
        else:
            self.error("Expected statement")
    
    def compound(self):
        """
        R16: <Compound> ::= { <Statement List> }
        """
        self.print_production("<Compound> -> { <Statement List> }")
        self.expect(TOKEN_SEP, "{")
        self.statement_list()
        self.expect(TOKEN_SEP, "}")
    
    def assign(self):
        """
        R17: <Assign> ::= <Identifier> = <Expression> ;
        """
        self.print_production("<Assign> -> <Identifier> = <Expression> ;")
        self.expect(TOKEN_ID)
        self.expect(TOKEN_OP, "=")
        self.expression()
        self.expect(TOKEN_SEP, ";")
    
    def if_statement(self):
        """
        R18: <If> ::= if ( <Condition> ) <Statement> <If'>
        """
        self.print_production("<If> -> if ( <Condition> ) <Statement> <If'>")
        self.expect(TOKEN_KEYWORD, "if")
        self.expect(TOKEN_SEP, "(")
        self.condition()
        self.expect(TOKEN_SEP, ")")
        self.statement()
        self.if_prime()
    
    def if_prime(self):
        """
        R19: <If'> ::= fi | else <Statement> fi
        """
        if self.current_token.token_type == TOKEN_KEYWORD and self.current_token.lexeme == "else":
            self.print_production("<If'> -> else <Statement> fi")
            self.match(TOKEN_KEYWORD, "else")
            self.statement()
            self.expect(TOKEN_KEYWORD, "fi")
        else:
            self.print_production("<If'> -> fi")
            self.expect(TOKEN_KEYWORD, "fi")
    
    def return_statement(self):
        """
        R20: <Return> ::= return <Return'>
        """
        self.print_production("<Return> -> return <Return'>")
        self.expect(TOKEN_KEYWORD, "return")
        self.return_prime()
    
    def return_prime(self):
        """
        R21: <Return'> ::= ; | <Expression> ;
        """
        if self.current_token.token_type == TOKEN_SEP and self.current_token.lexeme == ";":
            self.print_production("<Return'> -> ;")
            self.match(TOKEN_SEP, ";")
        else:
            self.print_production("<Return'> -> <Expression> ;")
            self.expression()
            self.expect(TOKEN_SEP, ";")
    
    def print_statement(self):
        """
        R22: <Print> ::= put ( <Expression> );
        """
        self.print_production("<Print> -> put ( <Expression> );")
        self.expect(TOKEN_KEYWORD, "put")
        self.expect(TOKEN_SEP, "(")
        self.expression()
        self.expect(TOKEN_SEP, ")")
        self.expect(TOKEN_SEP, ";")
    
    def scan(self):
        """
        R23: <Scan> ::= get ( <IDs> );
        """
        self.print_production("<Scan> -> get ( <IDs> );")
        self.expect(TOKEN_KEYWORD, "get")
        self.expect(TOKEN_SEP, "(")
        self.ids()
        self.expect(TOKEN_SEP, ")")
        self.expect(TOKEN_SEP, ";")
    
    def while_statement(self):
        """
        R24: <While> ::= while ( <Condition> ) <Statement>
        """
        self.print_production("<While> -> while ( <Condition> ) <Statement>")
        self.expect(TOKEN_KEYWORD, "while")
        self.expect(TOKEN_SEP, "(")
        self.condition()
        self.expect(TOKEN_SEP, ")")
        self.statement()
    
    def condition(self):
        """
        R25: <Condition> ::= <Expression> <Relop> <Expression>
        """
        self.print_production("<Condition> -> <Expression> <Relop> <Expression>")
        self.expression()
        self.relop()
        self.expression()
    
    def relop(self):
        """
        R26: <Relop> ::= == | != | > | < | <= | =>
        """
        self.print_production("<Relop> -> == | != | > | < | <= | =>")
        if self.current_token.token_type == TOKEN_OP:
            if self.current_token.lexeme in ["==", "!=", ">", "<", "<=", "=>"]:
                self.match(TOKEN_OP)
            else:
                self.error("Expected relational operator")
        else:
            self.error("Expected relational operator")
    
    def expression(self):
        """
        R27: <Expression> ::= <Term> <Expression'>
        """
        self.print_production("<Expression> -> <Term> <Expression'>")
        self.term()
        self.expression_prime()
    
    def expression_prime(self):
        """
        R28: <Expression'> ::= + <Term> <Expression'> | - <Term> <Expression'> | ε
        """
        if self.current_token.token_type == TOKEN_OP and self.current_token.lexeme in ["+", "-"]:
            self.print_production("<Expression'> -> + <Term> <Expression'> | - <Term> <Expression'>")
            self.match(TOKEN_OP)
            self.term()
            self.expression_prime()
        else:
            self.print_production("<Expression'> -> ε")
    
    def term(self):
        """
        R29: <Term> ::= <Factor> <Term'>
        """
        self.print_production("<Term> -> <Factor> <Term'>")
        self.factor()
        self.term_prime()
    
    def term_prime(self):
        """
        R30: <Term'> ::= * <Factor> <Term'> | / <Factor> <Term'> | ε
        """
        if self.current_token.token_type == TOKEN_OP and self.current_token.lexeme in ["*", "/"]:
            self.print_production("<Term'> -> * <Factor> <Term'> | / <Factor> <Term'>")
            self.match(TOKEN_OP)
            self.factor()
            self.term_prime()
        else:
            self.print_production("<Term'> -> ε")
    
    def factor(self):
        """
        R31: <Factor> ::= - <Primary> | <Primary>
        """
        if self.current_token.token_type == TOKEN_OP and self.current_token.lexeme == "-":
            self.print_production("<Factor> -> - <Primary>")
            self.match(TOKEN_OP, "-")
            self.primary()
        else:
            self.print_production("<Factor> -> <Primary>")
            self.primary()
    
    def primary(self):
        """
        R32: <Primary> ::= <Identifier> <Primary'> | <Integer> | ( <Expression> ) | <Real> | true | false
        """
        self.print_production("<Primary> -> <Identifier> <Primary'> | <Integer> | ( <Expression> ) | <Real> | true | false")
        
        if self.current_token.token_type == TOKEN_ID:
            self.match(TOKEN_ID)
            self.primary_prime()
        elif self.current_token.token_type == TOKEN_INT:
            self.match(TOKEN_INT)
        elif self.current_token.token_type == TOKEN_REAL:
            self.match(TOKEN_REAL)
        elif self.current_token.token_type == TOKEN_SEP and self.current_token.lexeme == "(":
            self.match(TOKEN_SEP, "(")
            self.expression()
            self.expect(TOKEN_SEP, ")")
        elif self.current_token.token_type == TOKEN_KEYWORD and self.current_token.lexeme in ["true", "false"]:
            self.match(TOKEN_KEYWORD)
        else:
            self.error("Expected primary expression")
    
    def primary_prime(self):
        """
        R33: <Primary'> ::= ( <IDs> ) | ε
        """
        if self.current_token.token_type == TOKEN_SEP and self.current_token.lexeme == "(":
            self.print_production("<Primary'> -> ( <IDs> )")
            self.match(TOKEN_SEP, "(")
            self.ids()
            self.expect(TOKEN_SEP, ")")
        else:
            self.print_production("<Primary'> -> ε")

    def empty(self):
        """
        R34: <Empty> ::= ε
        """
        self.print_production("<Empty> -> ε")
    
# =============================== End of grammar rule functions ===============================

    def parse(self):
        """Main parsing method (starts from the start symbol)"""
        print("Starting syntax analysis...")
        
        self.rat25f()
        
        # Make sure all tokens were consumed
        if self.current_token.token_type != TOKEN_EOF:
            self.error("Unexpected tokens after end of program")
        
        # Report results
        if len(self.errors) == 0:
            print("Syntax analysis complete: no errors found")
            self.write_output("\nSyntax analysis complete: no errors found")
            return True
        else:
            print("\nSyntax analysis complete - " + str(len(self.errors)) + " error(s) found")
            self.write_output("\nSyntax analysis complete - " + str(len(self.errors)) + " error(s) found")
            return False


def main():
    """
    Main program for syntax analyzer
    Prompts user for input and output files
    """
    print("Rat25F Syntax Analyzer")
    print("CPSC323 Assignment 2")
    print("by Andrew Rivera, Alex Trang, Alex Zhou")
    print()
    
    # Prompt input file
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
    
    # Prompt output file
    while True:
        output_file_name = input("Enter output file name: ").strip()
        if output_file_name:
            break
        else:
            print("Enter a valid output filename.")
    
    # Create lexer
    lexer = create_lexer(input_file_name)
    if lexer is None:
        return
    
    # Try to open output file
    try:
        output_file = open(output_file_name, 'w', encoding='utf-8')
    except:
        print("Couldn't create output file: " + output_file_name)
        print("Check if you have permission to write to this location")
        lexer.input_file.close()
        return
    
    # Create parser and run syntax analysis
    parser = Rat25FParser(lexer, output_file)
    parser.parse()
    
    # Clean up files
    lexer.input_file.close()
    output_file.close()
    
    print("Output written to " + output_file_name)

    input("\nPress Enter to exit...")

if __name__ == "__main__":
    main()