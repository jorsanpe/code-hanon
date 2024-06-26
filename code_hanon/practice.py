#!/usr/bin/env python3
import random
import re
import sys
import termios
import tty
from collections import Counter
from time import perf_counter
from termcolor import colored
from tabulate import tabulate


class SessionStatistics:
    def __init__(self):
        self.valid_strokes = 0
        self.invalid_strokes = 0
        self.total_time = 0.0
        self.challenge_start = perf_counter()
        self.challenge_end = 0
        self.before = perf_counter()
        self.ok_chars = []
        self.failed_3grams = Counter()
        self.failed_expressions = Counter()
        self.challenge_string = None
        self.generator_expression = None
        self.previous_input_ok = True

    def start(self, generator_expression, challenge_string):
        self.challenge_start = perf_counter()
        self.before = perf_counter()
        self.challenge_string = challenge_string
        self.generator_expression = generator_expression
        self.ok_chars = [False] * len(challenge_string)

    def valid_input(self, pos):
        now = perf_counter()
        elapsed_time = now - self.before
        self.total_time += elapsed_time
        self.before = now
        self.valid_strokes += 1
        self.previous_input_ok = True

    def invalid_input(self, pos):
        now = perf_counter()
        elapsed_time = now - self.before
        self.total_time += elapsed_time
        self.before = now
        self.invalid_strokes += 1
        if self.previous_input_ok:
            self.failed_3grams[(self.at(pos), self.at(pos - 1), self.at(pos-2))] += 1
        self.previous_input_ok = False

    def at(self, pos):
        return self.challenge_string[pos] if pos > 0 else "$"

    def challenge_failed(self):
        self.challenge_end = perf_counter()
        self.failed_3grams[self.generator_expression] += 1

    def print(self):
        print("Statistics")
        total_strokes = self.valid_strokes + self.invalid_strokes
        worst_sequences = ["".join(ngram[0]) for ngram in self.failed_3grams.most_common(2)]
        rows = [
            [" Strokes per minute", "%.2f" % ((total_strokes * 60) / self.total_time)],
            [" Accuracy", "%.2f %%" % ((float(self.valid_strokes) * 100) / total_strokes)],
            [" Total strokes", "%d" % total_strokes],
            [" Valid strokes", "%d" % self.valid_strokes],
            [" Invalid strokes", "%d" % self.invalid_strokes],
            [" Worst sequences", f"{"|".join(worst_sequences)}"],
            [" Total time (s)", "%.2f" % self.total_time],
        ]
        print(tabulate(rows))


class PracticeSession:
    def __init__(self, input_directory):
        self.before = perf_counter()
        self.valid_strokes = 0
        self.invalid_strokes = 0
        self.total_time = 0.0
        self.generator_expressions = self.read_generator_file(f"{input_directory}/expressions.txt")
        self.generator_words = self.read_generator_file(f"{input_directory}/words.txt")
        self.generator_names = self.read_generator_file(f"{input_directory}/names.txt")
        self.statistics = SessionStatistics()

    def read_generator_file(self, filename):
        try:
            with open(filename, "r") as stream:
                lines = stream.readlines()
                return [line.strip() for line in lines if not line.startswith("#")]
        except FileNotFoundError:
            print(f"Error: The file '{filename}' was not found in the input directory")
            sys.exit(1)

    def generate_challenge_string(self):
        generator_expression = random.sample(self.generator_expressions, 1)[0]
        challenge_string = re.sub(r'W', lambda x: random.sample(self.generator_words, 1)[0], generator_expression)
        challenge_string = re.sub(r'N', lambda x: random.sample(self.generator_names, 1)[0], challenge_string)
        challenge_string = re.sub(r'1', lambda x: str(random.randint(0, 99)), challenge_string)
        self.statistics.start(generator_expression, challenge_string)
        return challenge_string

    def challenge_failed(self):
        self.statistics.challenge_failed()

    def valid_input(self, pos):
        self.statistics.valid_input(pos)

    def invalid_input(self, pos):
        self.statistics.invalid_input(pos)

    def print(self):
        self.statistics.print()
        # print("Statistics")
        # total_strokes = self.valid_strokes + self.invalid_strokes
        # rows = [
        #     [" Strokes per minute", "%.2f" % ((total_strokes * 60) / self.total_time)],
        #     [" Accuracy", "%.2f %%" % ((float(self.valid_strokes) * 100) / total_strokes)],
        #     [" Total strokes", "%d" % total_strokes],
        #     [" Valid strokes", "%d" % self.valid_strokes],
        #     [" Invalid strokes", "%d" % self.invalid_strokes],
        #     [" Total time (s)", "%.2f" % self.total_time],
        # ]
        # print(tabulate(rows))


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def start(input_directory, count):
    session = PracticeSession(input_directory)

    for i in range(count):
        challenge_string = session.generate_challenge_string()
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
                session.valid_input(pos-1)
            else:
                sys.stdout.write(colored(challenge_string[pos], "red"))
                pos += 1
                session.invalid_input(pos-1)
            sys.stdout.flush()

            if pos == len(challenge_string):
                if all(st for st in ok_chars):
                    print(colored(" ✓", "green"))
                else:
                    session.challenge_failed()
                    print(colored(" x", "red"))
                break
    session.print()
