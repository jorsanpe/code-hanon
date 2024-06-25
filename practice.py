#!/usr/bin/env python3
import argparse
import random
import re
import sys
import termios
import tty
from time import perf_counter
from termcolor import colored


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


def start(expressions_filename, words_filename, challenges=5):
    generator_expressions = read_generator_file(expressions_filename)
    generator_words = read_generator_file(words_filename)

    valid_strokes = 0
    invalid_strokes = 0
    time_between_strokes = 0
    previous_time = perf_counter()

    for i in range(challenges):
        challenge_string = generate_challenge_string(generator_expressions, generator_words)
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
                valid_strokes += 1
            else:
                sys.stdout.write(colored(challenge_string[pos], "red"))
                pos += 1
                invalid_strokes += 1
            sys.stdout.flush()

            next_time = perf_counter()
            elapsed_time = next_time - previous_time
            time_between_strokes += elapsed_time
            previous_time = next_time

            if pos == len(challenge_string):
                if all(st for st in ok_chars):
                    print(colored(" ✓", "green"))
                else:
                    print(colored(" x", "red"))
                break
    print("# Statistics")
    print(" Time between strokes: %.2f" % (time_between_strokes / (valid_strokes + invalid_strokes)))
    print(" Accuracy: %.2f %%" % ((float(valid_strokes) * 100) / (valid_strokes - invalid_strokes)))


def generate_challenge_string(generator_expressions, generator_words):
    generator = random.sample(generator_expressions, 1)[0]
    expression = re.sub(r'v', lambda x: random.sample(generator_words, 1)[0], generator)
    return expression


options = argparse.ArgumentParser(description='practice coding based on generator expressions')
options.add_argument('-e', '--expressions-file', action='store')
options.add_argument('-w', '--words-file', action='store')

args = options.parse_args()
start(args.expressions_file, args.words_file)
