#!/usr/bin/env python3
import argparse
import random
import re
import sys
import termios
import tty
from termcolor import colored


def getch():
    fd = sys.stdin.fileno()
    old_settings = termios.tcgetattr(fd)
    try:
        tty.setraw(sys.stdin.fileno())
        ch = sys.stdin.read(1)
    except Exception as e:
        sys.stdout.write(e)
        sys.stdout.flush()
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
    return ch


def read_generator_file(filename):
    with open(filename, "r") as stream:
        lines = stream.readlines()
        return [line.strip() for line in lines if not line.startswith("#")]


def start(expressions_filename, words_filename):
    generator_expressions = read_generator_file(expressions_filename)
    generator_words = read_generator_file(words_filename)

    for i in range(10):
        challenge_string = generate_challenge_string(generator_expressions, generator_words)
        text = colored(challenge_string, "light_grey")
        sys.stdout.write(text + "\r")
        sys.stdout.flush()
        pos = 0
        while True:
            char = getch()
            print("")
            if isinstance(char, str):
                print(f"char is a str {char.encode("utf-8")}")
            if char.encode("utf-8") == "b'\x7f'":
                sys.stdout.write("\b")
                pos -= 1
            elif char == challenge_string[pos]:
                sys.stdout.write(colored(char, "green"))
                pos += 1
            else:
                sys.stdout.write(colored(challenge_string[pos], "red"))
                pos += 1
            sys.stdout.flush()


def generate_challenge_string(generator_expressions, generator_words):
    generator = random.sample(generator_expressions, 1)[0]
    expression = re.sub(r'v', lambda x: random.sample(generator_words, 1)[0], generator)
    return expression


options = argparse.ArgumentParser(description='practice coding based on generator expressions')
options.add_argument('-e', '--expressions-file', action='store')
options.add_argument('-w', '--words-file', action='store')

args = options.parse_args()
start(args.expressions_file, args.words_file)
