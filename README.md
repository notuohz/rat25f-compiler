# CPSC323-Project

A lexer and parser implementation for the **Rat25F** programming language, built as part of CPSC 323 (Compilers & Languages).

## Overview

This project implements two core components of a compiler:

- **Lexical Analyzer (`lexer.py`)** — tokenizes Rat25F source code into keywords, identifiers, integers, reals, operators, separators, and more.
- **Syntax Analyzer (`parser.py`)** — parses the token stream and validates it against the Rat25F grammar rules.

## Files

| File | Description |
|------|-------------|
| `lexer.py` | Lexical analyzer / tokenizer |
| `parser.py` | Syntax analyzer / parser |
| `Keywords.py` | Keyword definitions for Rat25F |
| `integer.py` | Integer handling logic |
| `input1-3.rat25f` | Sample Rat25F input files |
| `output1-3.txt` | Expected output files |

## Usage

Run the parser on a Rat25F source file:

```bash
python3 parser.py <input_file.rat25f>
```

Or use the provided executable (Windows):

```bash
./Rat25F_Parser.exe <input_file.rat25f>
```

## Requirements

- Python 3.x

## Contributors

- **Alex Zhou** ([@notuohz](https://github.com/notuohz))
- **Alex Trang** ([@alive-vrevre](https://github.com/alive-vrevre))
- **Andrew Rivera** ([@AndyCSUFStudent](https://github.com/AndyCSUFStudent))
