from collections import defaultdict


def list_duplicates(seq):
    tally = defaultdict(list)
    for i, item in enumerate(seq):
        tally[item].append(i)
    return ((key, locs) for key, locs in tally.items()
            if len(locs) > 1)


def indices_matches(a, b):
    b_set = set(b)
    return [i for i, j in enumerate(a) if j in b_set]
