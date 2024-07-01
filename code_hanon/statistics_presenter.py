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
    [ngrams, latencies] = statistics_repository.all_statistics()

    ngram_statuses = parse_statistics(latencies, ngrams)
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

    print(tabulate([["Expression", "N-Gram", "Latency (ms)", "Error rate"]] + rows, headers="firstrow", colalign=("right", "right", "right", "right")))


def sort_ngrams(ngram_statuses, sort):
    ngrams_filtered = filter(lambda d: ngram_statuses[d]['total'] > 5, ngram_statuses.keys())
    ngrams_sorted = sorted(ngrams_filtered, key=lambda d: -ngram_statuses[d][sort])
    return ngrams_sorted


def parse_statistics(latencies, ngrams):
    ngram_statuses = {}
    for ngram in ngrams:
        ngram_id = (ngram['ngram'], ngram['expression'])
        if ngram_id not in ngram_statuses:
            ngram_statuses[ngram_id] = {'ok': 0, 'ko': 0, 'latencies': []}
        if ngram['status'] == "OK":
            ngram_statuses[ngram_id]['ok'] += int(ngram['value'])
        if ngram['status'] == "KO":
            ngram_statuses[ngram_id]['ko'] += int(ngram['value'])

    for latency in latencies:
        ngram_id = (latency['ngram'], latency['expression'])
        if ngram_id not in ngram_statuses:
            ngram_statuses[ngram_id] = {'ok': 0, 'ko': 0, 'latencies': []}
        ngram_statuses[ngram_id]['latencies'].append(latency['value'])

    for _, ngram_stats in ngram_statuses.items():
        ngram_stats['total'] = ngram_stats['ok'] + ngram_stats['ko']
        ngram_stats['error_rate'] = float(ngram_stats['ko']) / (ngram_stats['total'])

    for _, ngram_stats in ngram_statuses.items():
        latencies = ngram_stats['latencies']
        if len(latencies) == 0:
            ngram_stats['latency'] = 0
            continue
        avg = list(moving_average(latencies, n=min(len(latencies), 3)))
        ngram_stats['latency'] = avg[-1]
    return ngram_statuses
