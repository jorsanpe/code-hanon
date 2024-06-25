#!/usr/bin/env python3
import argparse
import random
import re
import sys
import termios
import tty
from dataclasses import dataclass
from time import perf_counter
from termcolor import colored
from tabulate import tabulate


@dataclass
class Statistics:
    before: float
    valid_strokes: int = 0
    invalid_strokes: int = 0
    total_time: float = 0

    def __init__(self):
        self.before = perf_counter()

    def valid(self):
        now = perf_counter()
        elapsed_time = now - self.before
        self.total_time += elapsed_time
        self.before = now
        self.valid_strokes += 1

    def invalid(self):
        now = perf_counter()
        elapsed_time = now - self.before
        self.total_time += elapsed_time
        self.before = now
        self.invalid_strokes += 1

    def print(self):
        print("Statistics")
        total_strokes = self.valid_strokes + self.invalid_strokes
        rows = [
            [" Total time (s)", "%.2f" % self.total_time],
            [" Valid strokes", "%d" % self.valid_strokes],
            [" Invalid strokes", "%d" % self.invalid_strokes],
            [" Total strokes", "%d" % total_strokes],
            [" Time between strokes (s)", "%.2f" % (self.total_time / total_strokes)],
            [" Strokes per minute", "%.2f" % ((total_strokes * 60) / self.total_time)],
            [" Accuracy", "%.2f %%" % ((float(self.valid_strokes) * 100) / total_strokes)]
        ]
        print(tabulate(rows))


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def read_generator_file(filename):
    with open(filename, "r") as stream:
        lines = stream.readlines()
        return [line.strip() for line in lines if not line.startswith("#")]


def start(expressions_filename, words_filename, names_filename, challenges=5):
    generator_expressions = read_generator_file(expressions_filename)
    generator_words = read_generator_file(words_filename)
    generator_names = read_generator_file(names_filename)
    stats = Statistics()

    for i in range(challenges):
        challenge_string = generate_challenge_string(generator_expressions, generator_words, generator_names)
        text = colored(challenge_string, "light_grey")
        sys.stdout.write(text + "\r")
        sys.stdout.flush()
        ok_chars = [False] * len(challenge_string)
        pos = 0

        while True:
            char = getch()
            if char == "\x03":
                sys.exit(1)
            if char == "\x7f":
                if pos > 0:
                    pos -= 1
                sys.stdout.write(f"\b{colored(challenge_string[pos], "light_grey")}\b")
            elif char == challenge_string[pos]:
                sys.stdout.write(colored(char, "green"))
                ok_chars[pos] = True
                pos += 1
                stats.valid()
            else:
                sys.stdout.write(colored(challenge_string[pos], "red"))
                pos += 1
                stats.invalid()
            sys.stdout.flush()

            if pos == len(challenge_string):
                if all(st for st in ok_chars):
                    print(colored(" ✓", "green"))
                else:
                    print(colored(" x", "red"))
                break
    stats.print()


def generate_challenge_string(generator_expressions, generator_words, generator_names):
    generator = random.sample(generator_expressions, 1)[0]
    expression = re.sub(r'S', lambda x: random.sample(generator_words, 1)[0], generator)
    expression = re.sub(r'N', lambda x: random.sample(generator_names, 1)[0], expression)
    expression = re.sub(r'1', lambda x: str(random.randint(0, 99)), expression)
    return expression


options = argparse.ArgumentParser(description='practice coding based on generator expressions')
options.add_argument('-e', '--expressions-file', action='store')
options.add_argument('-w', '--words-file', action='store')
options.add_argument('-n', '--names-file', action='store')

args = options.parse_args()
start(args.expressions_file, args.words_file, args.names_file)
