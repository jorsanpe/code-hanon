import os
from pathlib import Path
from collections import Counter
import re
from tabulate import tabulate
from itertools import groupby
from code_hanon import languages
import functools


class Analysis:
    def __init__(self, language):
        self.expressions = Counter()
        self.words = Counter()
        self.names = Counter()
        self.extensions = languages.supported[language]["extensions"]
        self.reserved_words = languages.supported[language]["reserved_words"]


def analyze(language, directories, output):
    print(f'Analyzing {language} files from {", ".join(directories)}')

    analysis = Analysis(language)
    for directory in directories:
        files = functools.reduce(lambda v, e: v + list(Path(directory).rglob(e)), analysis.extensions, [])
        for path in files:
            try:
                with open(path, 'r', errors='ignore') as stream:
                    payload = stream.read()
                _analyze(payload, language, analysis)
            except UnicodeError as error:
                print(f"error while decoding file `{path}`")
    _present(analysis, output)


def _analyze(payload, language, analysis):
    payload = _remove_comments(payload, language)
    lines = payload.split('\n')
    for line in lines:
        compressed_line = line.strip()
        compressed_line = re.sub(r'([A-Z]\w+)+', lambda x: _replace_name(x, analysis), compressed_line)
        compressed_line = re.sub(r'[a-z_]\w+', lambda x: _replace_word(x, analysis), compressed_line)
        compressed_line = re.sub(r"\'[\w \t]*\'", "'W'", compressed_line)
        compressed_line = re.sub(r'\d', "1", compressed_line)
        compressed_line = "".join([key for key, _group in groupby(compressed_line)])
        compressed_line = compressed_line.replace("clas", "class")

        if _syntax_relevant(compressed_line):
            analysis.expressions[compressed_line] += 1


def _remove_comments(payload, language):
    def replacer(match):
        s = match.group(0)
        if s.startswith('/'):
            return " "
        else:
            return s

    lang = languages.supported[language]
    if "comments" not in lang:
        return payload

    pattern = re.compile(lang["comments"], re.DOTALL | re.MULTILINE)
    return re.sub(pattern, replacer, payload)


def _replace_word(match, analysis):
    string = match.group()
    reserved_words = analysis.reserved_words
    if string in reserved_words:
        return string
    analysis.words[string] += 1
    return "W"


def _replace_name(match, analysis):
    string = match.group()
    analysis.names[string] += 1
    return "N"


def _syntax_relevant(gram):
    return not all(char in ["a", " ", "\t", "\n"] for char in gram) and len(gram) > 3


def _present(analysis, output):
    os.makedirs(output, exist_ok=True)
    _present_counter(analysis.expressions, f"{output}/expressions.txt", 25)
    _present_counter(analysis.words, f"{output}/words.txt", 100)
    _present_counter(analysis.names, f"{output}/names.txt", 100)


def _present_counter(counter, filename, amount):
    rows = []
    for count in counter.most_common(10):
        rows.append(["".join(count[0]), _as_percent(count[1] / counter.total())])
    print(tabulate(rows))
    with open(filename, "w") as stream:
        for count in counter.most_common(amount):
            stream.write("".join(count[0]) + "\n")


def _as_percent(value):
    return "%.2f %%" % (value * 100)
