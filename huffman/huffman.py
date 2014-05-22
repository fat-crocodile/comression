"""Implement classical Huffman alghorithm"""

def make_code_symbols(weights):
    """Input:
        - list of pairs (symbol, weight), simbols with weight 0 are allowed
       Output:
        - list of pairs (symbol, code lenght) in the same order"""
    res = make_code([w for _,w in weights])
    return [(s, l) for (s,_),l in zip(weights, res)]

def make_code(weights):
    """Input:
        - list of symbols weights; simbols with weight 0 are allowed
       Output:
        - list of symbols code lenghts in the same order"""

    # each items is:
    # (weight, [(symbol1, len1), (symbol2, len2), ...  ])
    codes = [(w, [(i, 0)]) for i,w in enumerate(weights) if w > 0]
    codes.sort(key=lambda x: x[0], reverse=True)

    while len(codes) > 1:
        # get two least popular symbols
        m1 = codes.pop()
        m2 = codes.pop()

        # merge them in one
        s = (m1[0] + m2[0], [(i, l+1) for i,l in m1[1] + m2[1]])
        
        # insert new meta-symbol in list
        i = len(codes)
        while i > 0 and codes[i-1][0] < s[0]: i -= 1

        codes.insert(i, s)
    
    # now all pairs (symbol, code_len) are contained in codes[0][1]
    res = [0] * len(weights)

    for i,l in codes[0][1]:
        res[i] = l

    return res
