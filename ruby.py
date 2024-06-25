from pathlib import Path
from collections import Counter
import re
from nltk import bigrams, trigrams
from tabulate import tabulate
from itertools import groupby


def _analyze(payload, grams_2, grams_3):
    lines = payload.split('\n')
    for line in lines:
        line = re.sub(r'\d', "1", line)
        line = "".join([key for key, _group in groupby(line)])
        for gram in bigrams(line):
            if not any(char.isalpha() for char in gram) and not any(char == ' ' for char in gram):
                grams_2[gram] += 1
        for gram in trigrams(line):
            if not any(char.isalpha() for char in gram) and not any(char == ' ' for char in gram):
                grams_3[gram] += 1

def analyze(directories):
    grams_2 = Counter()
    grams_3 = Counter()
    for directory in directories:
        files = list(Path(directory).rglob('*.rb'))
        for path in files:
            with open(path, 'r') as stream:
                payload = stream.read()
            _analyze(payload, grams_2, grams_3)
    # print(pprint.pformat(symbols.most_common(25)))
    # print(pprint.pformat(characters.most_common(25)))
    # print(pprint.pformat(ngrams.most_common(25)))
    present(grams_2, grams_3, n=25)


def present(grams_2, grams_3, n=25):
    grams_2_rows = []
    for count in grams_2.most_common(n):
        grams_2_rows.append(["".join(count[0]), as_percent(count[1]/grams_2.total())])
    print(tabulate(grams_2_rows))

    grams_3_rows = []
    for count in grams_3.most_common(n):
        grams_3_rows.append(["".join(count[0]), as_percent(count[1]/grams_3.total())])
    print(tabulate(grams_3_rows))


def as_percent(value):
    return "%.2f %%" % (value * 100)
