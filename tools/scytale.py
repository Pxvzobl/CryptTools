#!/usr/bin/python3.6
# -*- coding: utf-8 -*-

import sys
sys.path.insert(0, "../lib")
from utils import *
from validator import *
import argparse
import numpy as np
import enchant

FILL_CHARACTER = ' '

def set_args():
    global args
    parser = argparse.ArgumentParser()
    parser.add_argument("-t", "--text", help="text to read from. If not specified the program will read from standard input")
    parser.add_argument("-k", "--key", help="key used to encrypt. If no key is provided the program will try to crack and decrypt using the specified language", type=int)
    parser.add_argument("-l", "--lang", help=f"available languages: {enchant.list_languages()} (default: en_US). Only useful if no key is provided", default='en_US')
    parser.add_argument("-V", "--verbose", action='store_true', help="show extra information")
    parser.add_argument("-A", "--all", action='store_true', help="show decrypted text for each tested key")
    parser.add_argument("-D", "--debug", action='store_true', help="show information about text validation")
    parser.add_argument("-T", "--threshold", help="valid word count percentage to mark the whole text as valid language (default: 50)", type=int, default=50)
    parser.add_argument("--beep", action='store_true', help="plays a beep sound when program finishes. May require SOX to be installed")
    args = parser.parse_args()

def key_to_matrix_bounds(key):
    rows = key
    cols = math.ceil(size/rows)
    return (rows, cols)

def scytale(text, rows, cols):
    """Encrypts/Decrypts a `text` using the scytale transposition cipher with specified `key`"""
    m = np.array(list(text.ljust(rows*cols, FILL_CHARACTER))).reshape((rows, cols))
    result = ''.join([''.join(row) for row in m.transpose()]).strip()
    if args.all and args.key is not None:
        print(f'Text to cipher: "{text}" ({len(text)})')
        print(m)
        print(f"Result size: {len(result)}")
    return result

def cipher(text):
    bounds = key_to_matrix_bounds(args.key)
    rows = bounds[0]
    cols = bounds[1]
    if args.verbose:
        print(f"Testing matrix: {rows}x{cols}")
    return scytale(text, rows, cols)

def test(text, rows, cols, terminal):
    dimensions = (rows, cols)
    if dimensions in testedKeys:
        return FAILED
    testedKeys.add(dimensions)
    decrypt = scytale(text, rows, cols)
    if args.verbose:
        sys.stdout.write("\r")
        sys.stdout.write(f"Testing matrix: {rows}x{cols}       ")
        sys.stdout.flush()
    if args.all:
        print(f'Testing decrypted text:\n"{decrypt}"')
    if args.verbose and args.debug:
        print()
    if validator.is_valid(decrypt):
        if args.verbose:
            validator.success()
        if terminal:
            print(decrypt)
        return ((rows, cols), decrypt)
    return FAILED

def testKeys(text, keys, terminal):
    for k in keys:
        bounds = key_to_matrix_bounds(k)
        rows = bounds[0]
        cols = bounds[1]
        decrypted = test(text, rows, cols, terminal)
        if decrypted == FAILED:
            decrypted = test(text, cols, rows, terminal)
            if decrypted != FAILED:
                return decrypted
        else:
            return decrypted
    return FAILED

def crack(text, terminal=True):
    """Cracks the text that must be encrypted with the scytale cipher"""
    global testedKeys
    testedKeys = set()
    if args.verbose:
        print(f'Text to crack: "{text}" ({size})')
    divs = list(divisors(size))
    decrypted = testKeys(text, divs, terminal)
    if decrypted == FAILED:
        keys = [x for x in range(2, size) if x not in divs]
        decrypted = testKeys(text, keys, terminal)
    if decrypted != FAILED:
        return decrypted
    if terminal:
        validator.fail()
    return FAILED

if __name__ == "__main__":
    set_args()

    validator = Validator(args.lang, args.threshold, args.debug, args.beep)
    text = read(args.text)
    size = len(text)

    if args.key is not None:
        if args.key not in range(1, size + 1):
            error(f"key must be between 1 and {size}")
        print(cipher(text))
    else:
        crack(text)
