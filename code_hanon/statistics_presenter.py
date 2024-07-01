import itertools
from collections import deque
from tabulate import tabulate
from code_hanon import statistics_repository


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
    [ngrams, expressions, latencies] = statistics_repository.all_statistics()

    ngram_statuses = {}
    for ngram in ngrams:
        if ngram['ngram'] not in ngram_statuses:
            ngram_statuses[ngram['ngram']] = {'ok': 0, 'ko': 0, 'latencies': []}
        if ngram['status'] == "OK":
            ngram_statuses[ngram['ngram']]['ok'] += int(ngram['value'])
        if ngram['status'] == "KO":
            ngram_statuses[ngram['ngram']]['ko'] += int(ngram['value'])

    for latency in latencies:
        ngram_id = latency['ngram']
        if ngram_id not in ngram_statuses:
            ngram_statuses[ngram_id] = {'ok': 0, 'ko': 0, 'latencies': []}
        ngram_statuses[ngram_id]['latencies'].append(latency['value'])

    for _, ngram_stats in ngram_statuses.items():
        ngram_stats['error_rate'] = float(ngram_stats['ko']) / (ngram_stats['ok'] + ngram_stats['ko'])

    for _, ngram_stats in ngram_statuses.items():
        latencies = ngram_stats['latencies']
        if len(latencies) == 0:
            ngram_stats['latency'] = 0
            continue
        avg = list(moving_average(latencies, n=min(len(latencies), 3)))
        ngram_stats['latency'] = avg[-1]

    ngrams_sorted = sorted(ngram_statuses.keys(), key=lambda d: -ngram_statuses[d][sort])

    rows = []
    for ngram_id in ngrams_sorted[:20]:
        rows.append([
            f"•{ngram_id}•",
            ngram_statuses[ngram_id]['latency'],
            f"{int(ngram_statuses[ngram_id]['error_rate'] * 100)}% ({ngram_statuses[ngram_id]['ko']}/{ngram_statuses[ngram_id]['ok'] + ngram_statuses[ngram_id]['ko']})"
        ])

    print(tabulate([['N-Gram', "Latency (ms)", "Error rate"]] + rows, headers="firstrow", colalign=("right", "right", "right")))

    # print(avg_sorted)
    # print(tabulate([['N-Gram', "Latency (ms)"]] + avg_sorted[:20], headers="firstrow", colalign=("right", "left")))
