import pprint

from pathlib import Path
from collections import Counter


def _analyze(payload, characters, symbols):
    lines = payload.split('\n')
    for line in lines:
        for char in line:
            if char != ' ':
                if char.isalpha() or char.isnumeric():
                    symbols[char] += 1
                else:
                    symbols[char] += 1


def analyze(directories):
    characters = Counter()
    symbols = Counter()
    for directory in directories:
        for path in Path(directory).rglob('*.py'):
            with open(path, 'r') as stream:
                payload = stream.read()
            _analyze(payload, characters, symbols)
    most_common = symbols.most_common(50)
    total_occurrences = sum([item[1] for item in most_common])
    print('symbol,occurrences,frequency')
    for item in most_common:
        print(f'"{item[0]}","{item[1]}","{item[1]*100/float(total_occurrences):.1f}"')
