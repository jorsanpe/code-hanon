from pathlib import Path
from collections import Counter
import re
from nltk import ngrams
from tabulate import tabulate
from itertools import groupby


def _analyze(payload, expressions, words):
    lines = payload.split('\n')
    for line in lines:
        compressed_line = line.strip()
        compressed_line = re.sub(r'\d', "1", compressed_line)
        compressed_line = re.sub(r'([A-Z]\w+)+', "C", compressed_line)
        compressed_line = re.sub(r'[a-z_]\w+', lambda x: replace_string(x, words), compressed_line)
        compressed_line = re.sub(r"\'[\w \t]*\'", "'v'", compressed_line)
        compressed_line = "".join([key for key, _group in groupby(compressed_line)])

        if syntax_relevant(compressed_line):
            expressions[compressed_line] += 1


def replace_string(match, words):
    string = match.group()
    reserved_words = ["class", "module", "do", "map", "expect", "to", "eq", "def", "end"]
    if string in reserved_words:
        return string
    words[string] += 1
    return "v"


def syntax_relevant(gram):
    return not all(char in ["a", " ", "\t", "\n"] for char in gram) and len(gram) > 3


def analyze(directories):
    expressions = Counter()
    words = Counter()
    for directory in directories:
        files = list(Path(directory).rglob('*.rb'))
        for path in files:
            with open(path, 'r') as stream:
                payload = stream.read()
            _analyze(payload, expressions, words)
    present(expressions, words)
    return expressions


def present(expressions, words):
    present_counter(expressions, "ruby-expressions.txt", 25)
    present_counter(words, "ruby-words.txt", 100)


def present_counter(counter, filename, amount):
    rows = []
    for count in counter.most_common(amount):
        rows.append(["".join(count[0]), as_percent(count[1] / counter.total())])
    print(tabulate(rows))
    with open(filename, "w") as stream:
        for count in counter.most_common(amount):
            stream.write("".join(count[0]) + "\n")


def as_percent(value):
    return "%.2f %%" % (value * 100)
