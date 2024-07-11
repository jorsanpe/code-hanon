import random
import re
import sys
from collections import namedtuple
from code_hanon.session_statistics import SessionStatistics
from code_hanon import statistics_repository


Challenge = namedtuple('Challenge', ['pattern', 'string', 'display_string'])


class PracticeSession:
    def __init__(self, input_directory, config):
        self.valid_strokes = 0
        self.invalid_strokes = 0
        self.generator_patterns = self.read_generator_file(f"{input_directory}/patterns.txt")
        self.generator_words = self.read_generator_file(f"{input_directory}/words.txt")
        self.generator_names = self.read_generator_file(f"{input_directory}/names.txt")
        self.statistics = SessionStatistics()
        self.current_challenge = ""
        self.config = config
        self.repeat_failures = []

    def read_generator_file(self, filename):
        try:
            with open(filename, "r") as stream:
                lines = stream.readlines()
                return [line.strip() for line in lines]
        except FileNotFoundError:
            print(f"Error: The file '{filename}' was not found in the input directory")
            sys.exit(1)

    def challenges(self):
        challenges = list(map(
            lambda _: self.generate_challenge(),
            range(self.config['count'])
        ))
        for challenge, next_challenge in zip(challenges, challenges[1:] + [None]):
            yield from self._yield_challenge(challenge, next_challenge)
        for challenge, next_challenge in zip(self.repeat_failures, self.repeat_failures[1:] + [None]):
            yield from self._yield_challenge(challenge, next_challenge)

    def _yield_challenge(self, challenge, next_challenge):
        self.statistics.start(challenge.pattern, challenge.display_string)
        self.current_challenge = challenge
        yield challenge, next_challenge

    def generate_challenge(self):
        generator_pattern = random.sample(self.generator_patterns, 1)[0]
        challenge_string = re.sub(r'W', lambda x: random.sample(self.generator_words, 1)[0], generator_pattern)
        challenge_string = re.sub(r'N', lambda x: random.sample(self.generator_names, 1)[0], challenge_string)
        challenge_string = re.sub(r'1', lambda x: str(random.randint(0, 99)), challenge_string)
        if self.config['press_enter']:
            display_string = challenge_string + "↩"
            challenge_string += "\x0d"
        else:
            display_string = challenge_string
        return Challenge(generator_pattern, challenge_string, display_string)

    def challenge_ok(self):
        return self.statistics.challenge_ok

    def challenge_end(self):
        if not self.challenge_ok():
            for i in range(self.config['repeat_failures']):
                self.repeat_failures.append(self.current_challenge)
        self.statistics.challenge_end()

    def valid_input(self, pos):
        self.statistics.valid_input(pos)

    def invalid_input(self, pos):
        self.statistics.invalid_input(pos)

    def finish(self):
        self.statistics.print()
        statistics_repository.update_statistics(self.statistics)

