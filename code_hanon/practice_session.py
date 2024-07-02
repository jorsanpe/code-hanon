import random
import re
import sys
from collections import namedtuple
from time import perf_counter
from code_hanon.session_statistics import SessionStatistics
from code_hanon import statistics_repository


Challenge = namedtuple('Challenge', ['pattern', 'string'])


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
        self.next_challenge = self.generate_challenge()

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
        self.next_challenge = self.generate_challenge()
        self.statistics.start(self.current_challenge.pattern, self.current_challenge.string)
        return self.current_challenge.string

    def generate_challenge(self):
        generator_pattern = random.sample(self.generator_patterns, 1)[0]
        challenge_string = re.sub(r'W', lambda x: random.sample(self.generator_words, 1)[0], generator_pattern)
        challenge_string = re.sub(r'N', lambda x: random.sample(self.generator_names, 1)[0], challenge_string)
        challenge_string = re.sub(r'1', lambda x: str(random.randint(0, 99)), challenge_string)
        return Challenge(generator_pattern, challenge_string)

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
