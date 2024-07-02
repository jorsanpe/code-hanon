from collections import Counter
from time import perf_counter

from tabulate import tabulate


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
