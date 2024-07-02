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

import sys
import itertools
import statistics
from collections import deque
from tabulate import tabulate
from code_hanon import statistics_repository
from sparklines import sparklines


def moving_average(iterable, n=3):
    it = iter(iterable)
    d = deque(itertools.islice(it, n - 1))
    d.appendleft(0)
    s = sum(d)
    for elem in it:
        s += elem - d.popleft()
        d.append(elem)
        yield int(s / n)


def present(sort='error_rate'):
    [ngrams, latencies] = statistics_repository.all_statistics()

    ngram_statuses, strokes_per_minute = parse_statistics(latencies, ngrams)
    ngrams_sorted = sort_ngrams(ngram_statuses, sort)
    if len(ngrams_sorted) == 0:
        return

    rows = []
    for ngram_id in ngrams_sorted[:20]:
        rows.append([
            ngram_id[1],
            f"•{ngram_id[0]}•",
            ngram_statuses[ngram_id]['latency'],
            f"{int(ngram_statuses[ngram_id]['error_rate'] * 100)}% ({ngram_statuses[ngram_id]['ko']}/{ngram_statuses[ngram_id]['ok'] + ngram_statuses[ngram_id]['ko']})"
        ])
    print(tabulate([["Expression", "N-Gram", f"Latency (ms) {latency_sorted_column_indicator(sort)}", f"Error rate {error_sorted_column_indicator(sort)}"]] + rows, headers="firstrow", colalign=("right", "right", "right", "right")))

    sys.stdout.write("SPM: ")
    for dp in sparklines(strokes_per_minute[-20:]):
        print(dp)


def latency_sorted_column_indicator(sort):
    if sort == "latency":
        return "▼"
    return ""


def error_sorted_column_indicator(sort):
    if sort == "error_rate":
        return "▼"
    return ""


def sort_ngrams(ngram_statuses, sort):
    ngrams_filtered = filter(lambda d: ngram_statuses[d]['total'] >= 3, ngram_statuses.keys())
    ngrams_sorted = sorted(ngrams_filtered, key=lambda d: -ngram_statuses[d][sort])
    return ngrams_sorted


def parse_statistics(latencies, ngrams):
    ngram_statuses = {}
    for ngram in ngrams:
        ngram_id = (ngram['ngram'], ngram['pattern'])
        if ngram_id not in ngram_statuses:
            ngram_statuses[ngram_id] = {'ok': 0, 'ko': 0, 'latencies': []}
        if ngram['status'] == "OK":
            ngram_statuses[ngram_id]['ok'] += int(ngram['value'])
        if ngram['status'] == "KO":
            ngram_statuses[ngram_id]['ko'] += int(ngram['value'])

    for latency in latencies:
        ngram_id = (latency['ngram'], latency['pattern'])
        if ngram_id not in ngram_statuses:
            ngram_statuses[ngram_id] = {'ok': 0, 'ko': 0, 'latencies': []}
        ngram_statuses[ngram_id]['latencies'].append(latency['value'])

    for _, ngram_stats in ngram_statuses.items():
        ngram_stats['total'] = ngram_stats['ok'] + ngram_stats['ko']
        ngram_stats['error_rate'] = float(ngram_stats['ko']) / (ngram_stats['total'])

    for _, ngram_stats in ngram_statuses.items():
        ngram_latencies = ngram_stats['latencies']
        if len(ngram_latencies) == 0:
            ngram_stats['latency'] = 0
            continue
        avg = list(moving_average(ngram_latencies, n=min(len(ngram_latencies), 3)))
        ngram_stats['latency'] = avg[-1]

    latency_per_timestamp = {}
    for latency in latencies:
        timestamp = latency['timestamp']
        if timestamp not in latency_per_timestamp:
            latency_per_timestamp[timestamp] = [latency['value']]
        else:
            latency_per_timestamp[timestamp].append(latency['value'])
    strokes_per_minute = [int(60000 / statistics.mean(latency_per_timestamp[timestamp])) for timestamp in sorted(latency_per_timestamp.keys())]

    return ngram_statuses, strokes_per_minute
