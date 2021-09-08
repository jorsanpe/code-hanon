import pprint

from collections import Counter
from pathlib import Path
from collections import Counter
import nltk
from nltk import bigrams


def _analyze(payload, characters, symbols, ngrams):
    lines = payload.split('\n')
    for line in lines:
        for char in line:
            if char != ' ':
                if char.isalpha() or char.isnumeric():
                    characters[char] += 1
                else:
                    symbols[char] += 1
        for gram in bigrams(line):
            if not any(char.isalpha() for char in gram) and not any(char == ' ' for char in gram):
                ngrams[gram] += 1

def analyze(directories):
    characters = Counter()
    symbols = Counter()
    ngrams = Counter()
    for directory in directories:
        files = list(Path(directory).rglob('*.rb'))
        for path in files:
            with open(path, 'r') as stream:
                payload = stream.read()
            _analyze(payload, characters, symbols, ngrams)
    print(pprint.pformat(symbols.most_common()))
    print(pprint.pformat(characters.most_common()))
    print(pprint.pformat(ngrams.most_common()))
