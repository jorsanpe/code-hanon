#!/usr/bin/env python
import argparse
from collections import namedtuple

import python
import c


Language = namedtuple('Language', ['name', 'analyze'])

languages = {
    'c': Language('C', c.analyze),
    'python': Language('Python',  python.analyze)
}


options = argparse.ArgumentParser(description='placa: source code character frequency analysis')
options.add_argument('-l', '--language', action='store', choices=languages.keys())
options.add_argument('directories', nargs=argparse.REMAINDER)

args = options.parse_args()
language = languages[args.language]

print(f'Analyzing {language.name} files from {", ".join(args.directories)}')

languages[args.language].analyze(args.directories)
