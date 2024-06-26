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
class PracticeSession:
    before: float
    valid_strokes: int = 0
    invalid_strokes: int = 0
    total_time: float = 0

    def __init__(self, input_directory):
        self.before = perf_counter()
        self.generator_expressions = self.read_generator_file(f"{input_directory}/expressions.txt")
        self.generator_words = self.read_generator_file(f"{input_directory}/words.txt")
        self.generator_names = self.read_generator_file(f"{input_directory}/names.txt")

    def read_generator_file(self, filename):
        try:
            with open(filename, "r") as stream:
                lines = stream.readlines()
                return [line.strip() for line in lines if not line.startswith("#")]
        except FileNotFoundError:
            print(f"Error: The file '{filename}' was not found in the input directory")
            sys.exit(1)

    def generate_challenge_string(self):
        generator = random.sample(self.generator_expressions, 1)[0]
        expression = re.sub(r'W', lambda x: random.sample(self.generator_words, 1)[0], generator)
        expression = re.sub(r'N', lambda x: random.sample(self.generator_names, 1)[0], expression)
        expression = re.sub(r'1', lambda x: str(random.randint(0, 99)), expression)
        return expression

    def valid_input(self):
        now = perf_counter()
        elapsed_time = now - self.before
        self.total_time += elapsed_time
        self.before = now
        self.valid_strokes += 1

    def invalid_input(self):
        now = perf_counter()
        elapsed_time = now - self.before
        self.total_time += elapsed_time
        self.before = now
        self.invalid_strokes += 1

    def print(self):
        print("Statistics")
        total_strokes = self.valid_strokes + self.invalid_strokes
        rows = [
            [" Strokes per minute", "%.2f" % ((total_strokes * 60) / self.total_time)],
            [" Accuracy", "%.2f %%" % ((float(self.valid_strokes) * 100) / total_strokes)],
            [" Total strokes", "%d" % total_strokes],
            [" Valid strokes", "%d" % self.valid_strokes],
            [" Invalid strokes", "%d" % self.invalid_strokes],
            [" Total time (s)", "%.2f" % self.total_time],
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
                session.valid_input()
            else:
                sys.stdout.write(colored(challenge_string[pos], "red"))
                pos += 1
                session.invalid_input()
            sys.stdout.flush()

            if pos == len(challenge_string):
                if all(st for st in ok_chars):
                    print(colored(" ✓", "green"))
                else:
                    print(colored(" x", "red"))
                break
    session.print()
