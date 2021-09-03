import argparse
import os
import subprocess as sub
from enum import Enum
from collections import defaultdict
from os import error
from typing import Dict, Iterable, List, overload
import sys
import time
from math import sin, cos
from lexer import *
from sparser import Parser
from runtime import State

########################################
# DRIVER CLASSES
########################################

ind = 0
current_state = State()

# Builtins
def get_state():
    return current_state.vals

def delete(variable):
    current_state.unbind(variable)
    return None

def array_(*args):
    return list(args)

def test(x, y, z):
    return x, y, z

def append(l, x):
    return l.append(x)

def grab(l, position):
    return l[position]

def insert(l, item, position):
    return l.insert(item, position)

def remove(l, item):
    return l.remove(item)

def pop(l, position):
    return l.pop(position)

def split(l, val):
    return l.split(val)

def clear(l):
    return l.clear()

def sys_open():
    return open(sys.argv[1], "r")

def read(file):
    return file.read()

def close(file):
    return file.close()

def write(file, text):
    return file.write(text)

def exit():
    return sys.exit()

def print_s(value):
    print(value, end=" ")

def dd(value):
    return defaultdict(lambda: value)

def is_digit(value):
    return value.isdigit()

def is_alpha(value):
    return value.isalpha()

def is_ident(value):
    return value.isidentifier()

def is_space(value):
    return value.isspace()

def sep_enum(name, value):
    x = Enum(name, value)
    return current_state.bind(f"{name}.{value}", str(helper(*x)))

def helper(*args):
    return str(args)

def dict_(key, value):
    return {key: value}

def next_(x):
    return next(x)

def read_source_file(path):
    # Try reading the path directly
    if os.path.isfile(path):
        return open(path, 'r').read()
    # Try with implied extension
    if os.path.isfile(path + '.soul'):
        return open(path + '.soul', 'r').read()
    # No such file
    raise Exception(f'No source file named {path} could be found!')

def transpile_to_nim(path):
    start = time.time()
    # Read file
    source = read_source_file(path)
    # Parse into AST
    ast = Parser(Lexer(source)).parse_statements()
    # Generate the .nim file name
    name_base = os.path.splitext(path)[0]
    output_name = name_base + '.nim'
    # Write the generated code
    output = open(output_name, 'w')
    output.write(ast.compile(current_state, source, ind)) # NOTE: Why is source needed here?
    print(f'Compiled in: {time.time()-start} seconds')
    return output_name

def parse_cli_args():
    # Build the argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', help='Transpile to Nim', action='store_true')
    parser.add_argument('-r', help='Immediately run transpiled Nim', action='store_true')
    parser.add_argument('sourcefile', help='The source file to transpile or run', nargs='?')
    # Do the parse
    return parser.parse_args()

def assert_source_file_in_cli_args(args):
    if args.sourcefile == None:
        raise Exception(f'No source file provided in the command line arguments!')

def main():
    args = parse_cli_args()
    print(args.sourcefile)
    if args.r:
        # We want to run with the Nim compiler
        assert_source_file_in_cli_args(args)
        output = transpile_to_nim(args.sourcefile)
        sub.Popen(['cmd', '/K', f'nim c -r {output}'])
    elif args.c:
        # We want to transpile to Nim
        assert_source_file_in_cli_args(args)
        transpile_to_nim(args.sourcefile)
    elif args.sourcefile != None:
        # There is a source file to execute
        source = read_source_file(args.sourcefile)
        start = time.time()
        print(Parser(Lexer(source)).parse_statements().eval(current_state, Lexer(source))) # NOTE: Why is a Lexer needed twice?
        print(f'Executed in: {time.time()-start} seconds')
    else:
        # REPL
        while True:
            source = input('>>> ')
            print(Parser(Lexer(source)).parse_statements().eval(current_state, Lexer(source))) # NOTE: Why is a Lexer needed twice?

if __name__ == '__main__':
    main()
