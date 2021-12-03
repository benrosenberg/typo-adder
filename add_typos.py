# add realistic typos to a piece of writing

# imports
import argparse
import random

# parsing
parser = argparse.ArgumentParser(description='Add typos to a file.', formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('filename', type=str, nargs=1, help='the file to process')
parser.add_argument('-m', '--messiness', type=int, default=5, help='percent of characters to substitute with a typo')
parser.add_argument('-w', '--whitespace', help='whether or not to include newlines and tabs in typos',
                    default=False, dest='whitespace', action='store_const', const=True)
parser.add_argument('-c', '--caps', help='whether or not to include left and right shift in typos',
                    default=True, dest='caps', action='store_const', const=False)
parser.add_argument('-s', '--space', help='whether or not to include spaces in typos',
                    default=True, dest='space', action='store_const', const=False)
parser.add_argument('-b', '--backspace', help='whether or not to include backspaces in typos',
                    default=True, dest='backspace', action='store_const', const=False)

args = parser.parse_args()

# US QWERTY keyboard as adjacency list thing
KB = {
    '`' : ['1', '\t'],
    '1' : ['`', 'q', '\t', '2'],
    '2' : ['1', '3', 'q', 'w'],
    '3' : ['2', '4', 'w', 'e'],
    '4' : ['3', '5', 'e', 'r'],
    '5' : ['4', '6', 'r', 't'],
    '6' : ['5', '7', 't', 'y'],
    '7' : ['6', '8', 'y', 'u'],
    '8' : ['7', '9', 'u', 'i'],
    '9' : ['8', '0', 'i', 'o'],
    '0' : ['9', '-', 'o', 'p'],
    '-' : ['0', '=', 'p', '['],
    '=' : ['-', '[', ']', '<BACKSPACE>'],
    '\t' : ['`', '1', 'q'],
    'q' : ['\t', '`', '1', '2', 'w', 's', 'a'],
    'w' : ['q', '2', '3', 'e','s'],
    'e' : ['3', '4', 'w', 'r', 's', 'd'],
    'r' : ['4', '5', 'e', 't', 'd', 'f'],
    't' : ['5', '6', 'r', 'y', 'f', 'g'],
    'y' : ['t', '6', '7', 'u', 'g', 'h'],
    'u' : ['y', '7', '8', 'i', 'h', 'j'],
    'i' : ['u', '8', '9', 'o', 'j', 'k'],
    'o' : ['i', '9', '0', 'p', 'k', 'l'],
    'p' : ['o', '0', '-', '[', 'l', ';'],
    '[' : ['p', '-', '=', ']', ';', '\''],
    ']' : ['[', '=', '\'', '\\', '<BACKSPACE>'],
    '\\': [']', '\n', '<BACKSPACE>'],
    'a' : ['\t', 'q', 'w', 's', 'z', '<LSHIFT>'],
    's' : ['a', 'w', 'd', 'z', 'x'],
    'd' : ['e', 'r', 's', 'f', 'x', 'c'],
    'f' : ['d', 'r', 't', 'g', 'c', 'v'],
    'g' : ['f', 't', 'y', 'h', 'v', 'b'],
    'h' : ['g', 'y', 'u', 'j', 'b', 'n'],
    'j' : ['h', 'u', 'i', 'k', 'n', 'm'],
    'k' : ['j', 'i', 'o', 'm', 'l', ','],
    'l' : ['k', 'o', 'p', ';', ',', '.'],
    ';' : ['l', 'p', '[', '\'', '.', '/'],
    '\'': [';', '[', ']', '\n', '/', '<RSHIFT>'],
    '\n' : ['\'', ']', '\\', '<RSHIFT>'],
    '<LSHIFT>' : ['a', 'z'],
    'z' : ['<LSHIFT>', 'a', 's', 'x'],
    'x' : ['z', 's', 'd', 'c'],
    'c' : ['x', 'd', 'f', 'v', ' '],
    'v' : ['c', 'f', 'g', 'b', ' '],
    'b' : ['v', 'g', 'h', 'n', ' '],
    'n' : ['b', 'h', 'j', 'm', ' '],
    'm' : ['n', 'j', 'k', ',', ' '],
    ',' : ['m', 'k', 'l', '.', ' '],
    '.' : [',', 'l', ';', '/'],
    '/' : ['.', ';', '\'', '<RSHIFT>'],
    '<RSHIFT>' : ['\n', '/'],
    ' ' : ['c', 'v', 'b', 'n', 'm', ',']
}

SHIFTS = {
    '`' : '~',
    '1' : '!',
    '2' : '@',
    '3' : '#',
    '4' : '$',
    '5' : '%',
    '6' : '^',
    '7' : '&',
    '8' : '*',
    '9' : '(',
    '0' : ')',
    '-' : '_',
    '=' : '+',
    '\t' : '\t',
    'q' : 'Q',
    'w' : 'W',
    'e' : 'E',
    'r' : 'R',
    't' : 'T',
    'y' : 'Y',
    'u' : 'U',
    'i' : 'I',
    'o' : 'O',
    'p' : 'P',
    '[' : '{',
    ']' : '}',
    '\\': '|',
    'a' : 'A',
    's' : 'S',
    'd' : 'D',
    'f' : 'F',
    'g' : 'G',
    'h' : 'H',
    'j' : 'J',
    'k' : 'K',
    'l' : 'L',
    ';' : ':',
    '\'': '"',
    '\n' : '\n',
    '<LSHIFT>' : '<LSHIFT>',
    'z' : 'Z',
    'x' : 'X',
    'c' : 'C',
    'v' : 'V',
    'b' : 'B',
    'n' : 'N',
    'm' : 'M',
    ',' : '<',
    '.' : '>',
    '/' : '?',
    '<RSHIFT>' : '<RSHIFT>',
    ' ' : ' ',
    '<BACKSPACE>' : '<BACKSPACE>'
}

# read file
filename = args.filename[0]
with open(filename) as f:
    contents = f.read()

def typo(character, change_case=False):
    uppercase = character not in KB and not change_case
    lowercase_char = character if character in KB else rSHIFTS[character]
    if uppercase:
        newchar = SHIFTS[random.choice(KB[lowercase_char])] 
    else:
        newchar = random.choice(KB[lowercase_char]) 

    return newchar

def revdict(d):
    return {v:k for (k,v) in d.items()}

rSHIFTS = revdict(SHIFTS)# rSHIFTS is dict of UPPERCASE : lowercase
out = ''
next_shift = False
for char in contents:
    if ((not args.space and char == ' ') or
        (not args.whitespace and char in ['\n', '\t'])):
        out += char
        continue

    chance = random.random() < (args.messiness / 100)
    if not chance: 
        out += char
        continue

    newchar = typo(char, next_shift)

    if newchar == '<BACKSPACE>':
        if not args.backspace:
            out += char
            continue
        if len(out) > 0:
            out = out[:-1]
    elif newchar in ['<LSHIFT>', '<RSHIFT>']:
        if args.caps:
            next_shift = True
    elif newchar in ['\n', '\t'] and not args.whitespace:
        out += char
        continue
    else:
        out += newchar
    
    if next_shift: next_shift = False

print(out)

