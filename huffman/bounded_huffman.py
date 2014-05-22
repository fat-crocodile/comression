"""Implement algorithm from 

LAWRENCE L. LARMORE, DANIEL S. HIRSCHBERG
"A Fast Algorithm for Optimal Length-Limited Huffman Codes"
Journal of the Association for Computing Machinery, Vol. 37, No. 3, July 1990"""

def make_code_symbols(weights, limit):
    """Input: 
        - list of pairs (symbol, weight); symbols with weight 0 allowed
        - code lenght limit
        Output:
        - list of pairs (symbol, code lenght) in the same order
    """
    res = make_code([w for _,w in weights], limit)
    return [(s, l) for (s,_),l in zip(weights, res)]

def make_code(weights, limit):
    """Input: 
        - symbols weights in alphabetical order (symbols with weight 0 allowed)
        - code lenght limit
        Output:
        - symbols code lenghts in alphabetical order
    """

    # sort by weight, exclude zero-weighted symbols and save original symbol position
    positioned_weights = sorted((w, n) for n,w in enumerate(weights) if w > 0)

    if len(positioned_weights) > 2**limit:
        raise Exception('there are no such code')

    coins = []

    for level in range(limit, 0, -1):
        # generate current level coins
        new_coins = [(w, {i:level}) for w,i in positioned_weights]
        # coins, merged from previous level coins
        prev_coins = [_merge_coins(coins[2*i], coins[2*i+1]) for i in range(len(coins) / 2)]
        # merge lists
        coins = list(_imerge(prev_coins, new_coins, lambda x,y: x[0] < y[0]))

    # got results
    res = [0] * len(weights)

    for i in range(len(positioned_weights) * 2 - 2):
        for k,v in coins[i][1].items():
            if res[k] < v: res[k] = v

    return res

def _merge_coins(c1, c2):
    """Merge two coins in one meta-coin. Each coin in pair (weight, {base coin id --> height in tree})"""
    w = c1[0] + c2[0]

    d = c1[1].copy()
    for k,v in c2[1].iteritems():
        if k not in d: d[k] = 0
        d[k] = max(d[k], v)

    return w, d

def _imerge(iter1, iter2, less_then = None):
    """Merge two sorted iterables in one sorted iterable"""
    i1,i2 = None, None
    iter1, iter2 = iter(iter1), iter(iter2)
    
    while True:
        if i1 is None:
            try: 
                i1 = iter1.next()
            except StopIteration:
                if i2 is not None: yield i2
                for x in iter2:
                    yield x
                return
        if i2 is None:
            try: 
                i2 = iter2.next()
            except StopIteration:
                if i1 is not None: yield i1
                for x in iter1:
                    yield x
                return

        if less_then(i1, i2):
            yield i1
            i1 = None
        else:
            yield i2
            i2 = None

