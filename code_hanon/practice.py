# Copyright (C) Jordi Sánchez 2024
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import random
import re
import sys
import termios
import tty
from collections import Counter
from time import perf_counter
from termcolor import colored
from tabulate import tabulate
from code_hanon import statistics_repository


class SessionStatistics:
    def __init__(self):
        self.valid_strokes = 0
        self.invalid_strokes = 0
        self.total_time_per_char = 0.0
        self.challenge_start = perf_counter()
        self.before = perf_counter()
        self.ok_chars = []
        self.latency_per_char = []
        self.failed_3grams = Counter()
        self.failed_patterns = Counter()
        self.valid_3grams = Counter()
        self.valid_patterns = Counter()
        self.latency_3grams = []
        self.challenge_string = None
        self.generator_pattern = None
        self.challenge_ok = True

    def start(self, generator_pattern, challenge_string):
        self.challenge_start = perf_counter()
        self.before = perf_counter()
        self.challenge_string = challenge_string
        self.generator_pattern = generator_pattern
        self.ok_chars = [None] * len(challenge_string)
        self.latency_per_char = [0] * len(challenge_string)
        self.challenge_ok = True

    def valid_input(self, pos):
        now = perf_counter()
        elapsed_time = now - self.before
        self.before = now
        self.total_time_per_char += elapsed_time
        self.latency_per_char[pos] = elapsed_time
        self.valid_strokes += 1
        if self.ok_chars[pos] is None:
            self.ok_chars[pos] = True
        if self.ok_including(pos):
            self.valid_3grams[self.ngram_key(pos)] += 1
            self.latency_3grams.append([self.ngram_key(pos), int(self.latency_at(pos) * 1000)])

    def invalid_input(self, pos):
        now = perf_counter()
        self.total_time_per_char += now - self.before
        self.before = now
        self.invalid_strokes += 1
        if self.ok_chars[pos] is None:
            self.ok_chars[pos] = False
        if self.ok_upto(pos):
            self.failed_3grams[self.ngram_key(pos)] += 1
        self.challenge_ok = False

    def ngram_key(self, pos):
        return tuple([self.ngram_at(pos), self.generator_pattern])

    def latency_upto(self, pos):
        return self.latency_at(pos-2) + self.latency_at(pos-1) + self.latency_at(pos)

    def latency_at(self, pos):
        return self.latency_per_char[pos] if pos > 0 else 0

    def ok_upto(self, pos):
        return self.ok_at(pos-2) and self.ok_at(pos-1)

    def ok_including(self, pos):
        return self.ok_at(pos-2) and self.ok_at(pos-1) and self.ok_at(pos)

    def ok_at(self, pos):
        return self.ok_chars[pos] if pos > 0 else True

    def ngram_at(self, pos):
        return tuple([self.at(pos - 2), self.at(pos - 1), self.at(pos)])

    def at(self, pos):
        return self.challenge_string[pos] if pos > 0 else "$"

    def challenge_end(self):
        if self.challenge_ok:
            self.valid_patterns[self.generator_pattern] += 1
        else:
            self.failed_patterns[self.generator_pattern] += 1

    def print(self):
        print("Statistics")
        total_strokes = self.valid_strokes + self.invalid_strokes
        worst_sequences = [f'"{"".join(ngram[0][0])}"' for ngram in self.failed_3grams.most_common(2)]
        worst_patterns = [f'"{"".join(pattern[0])}"' for pattern in self.failed_patterns.most_common(2)]
        rows = [
            [" Strokes per minute", "%.2f" % ((total_strokes * 60) / self.total_time_per_char)],
            [" Accuracy", "%.2f %%" % ((float(self.valid_strokes) * 100) / total_strokes)],
            [" Total strokes", "%d" % total_strokes],
            [" Valid strokes", "%d" % self.valid_strokes],
            [" Invalid strokes", "%d" % self.invalid_strokes],
            [" Worst sequences", f"{', '.join(worst_sequences)}"],
            [" Worst patterns", f"{', '.join(worst_patterns)}"],
            [" Total time (s)", "%.2f" % self.total_time_per_char],
        ]
        print(tabulate(rows))


class PracticeSession:
    def __init__(self, input_directory):
        self.before = perf_counter()
        self.valid_strokes = 0
        self.invalid_strokes = 0
        self.total_time = 0.0
        self.generator_patterns = self.read_generator_file(f"{input_directory}/patterns.txt")
        self.generator_words = self.read_generator_file(f"{input_directory}/words.txt")
        self.generator_names = self.read_generator_file(f"{input_directory}/names.txt")
        self.statistics = SessionStatistics()
        self.current_challenge = ""
        self.next_challenge = self.generate_challenge_string()

    def read_generator_file(self, filename):
        try:
            with open(filename, "r") as stream:
                lines = stream.readlines()
                return [line.strip() for line in lines]
        except FileNotFoundError:
            print(f"Error: The file '{filename}' was not found in the input directory")
            sys.exit(1)

    def next(self):
        self.current_challenge = self.next_challenge
        self.next_challenge = self.generate_challenge_string()
        return self.current_challenge

    def generate_challenge_string(self):
        generator_pattern = random.sample(self.generator_patterns, 1)[0]
        challenge_string = re.sub(r'W', lambda x: random.sample(self.generator_words, 1)[0], generator_pattern)
        challenge_string = re.sub(r'N', lambda x: random.sample(self.generator_names, 1)[0], challenge_string)
        challenge_string = re.sub(r'1', lambda x: str(random.randint(0, 99)), challenge_string)
        return generator_pattern, challenge_string

    def challenge_ok(self):
        return self.statistics.challenge_ok

    def challenge_end(self):
        self.statistics.challenge_end()

    def valid_input(self, pos):
        self.statistics.valid_input(pos)

    def invalid_input(self, pos):
        self.statistics.invalid_input(pos)

    def finish(self):
        self.statistics.print()
        statistics_repository.update_statistics(self.statistics)


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
    statistics_repository.migrate()
    session = PracticeSession(input_directory)

    for i in range(count):
        generator_pattern, challenge_string = session.next()
        session.statistics.start(generator_pattern, challenge_string)

        if i < (count-1):
            text = colored(f"{challenge_string}\n{session.next_challenge[1]}", "light_grey")
            sys.stdout.write(text + "\r\033[1A")
        else:
            text = colored(f"{challenge_string}", "light_grey")
            sys.stdout.write(text + "\r")

        sys.stdout.flush()
        ok_chars = [False] * len(challenge_string)
        pos = 0

        while True:
            char = getch()
            if is_ctrl_c(char):
                session.finish()
                sys.exit(1)
            if is_backspace(char):
                if pos > 0:
                    pos -= 1
                    sys.stdout.write(f"\b{colored(challenge_string[pos], 'light_grey')}\b")
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
                if session.challenge_ok():
                    print(colored(" ✓", "green"))
                else:
                    print(colored(" x", "red"))
                session.challenge_end()
                break
    session.finish()


def is_backspace(char):
    return char == "\x7f"


def is_ctrl_c(char):
    return char == "\x03"
