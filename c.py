import pprint

from collections import Counter
from pathlib import Path
from collections import Counter
import nltk
from nltk import ngrams


def _analyze(payload, characters, symbols, grams):
    lines = payload.split('\n')
    for line in lines:
        for char in line:
            if char != ' ':
                if char.isalpha():
                    characters[char] += 1
                else:
                    symbols[char] += 1
        for gram in ngrams(line, 3):
            if not any(char.isalpha() for char in gram) and not any(char == ' ' for char in gram):
                grams[gram] += 1


def analyze(directories):
    characters = Counter()
    symbols = Counter()
    grams = Counter()
    for directory in directories:
        files = list(Path(directory).rglob('*.c')) + list(Path(directory).rglob('*.cc')) + list(Path(directory).rglob('*.cpp'))
        for path in files:
            with open(path, 'r') as stream:
                payload = stream.read()
            _analyze(payload, characters, symbols, grams)
    print(pprint.pformat(symbols.most_common()))
    print(pprint.pformat(characters.most_common()))
    print(pprint.pformat(grams.most_common()))
