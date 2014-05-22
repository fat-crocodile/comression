"""Decode/encode Huffman-encoded symbols from/to bitstream"""

from collections import defaultdict, namedtuple

_HuffmanRecord = namedtuple("_HuffmanRecord", "length start_code end_code symbols")

class Decoder(object):
    """Decode symbol from bitsream"""

    def __init__(self, lens):
        """Input: 
        - list or pairs (symbol, code lenght)
        - OR list or code lenghts; in this case symbols are just integers"""
        if isinstance(lens[0], int):
            lens = [(n, l) for n,l in enumerate(lens)]

        self.tables = _tables_from_lenghts(lens)

    def get(self, bs):
        """Read next Huffman-encoded symbol from bitstream bs, return decoded symbol"""
        code = 0     # readed code
        index = 0    # current huffman record 
        readed = 0   # number of bits already readed

        while index < len(self.tables):
            record = self.tables[index]

            # read additional bits
            delta = record.length - readed
            i = bs.get_be(delta)
            code += i
            readed += delta

            if code < record.end_code:      # match
                return record.symbols[code - record.start_code]

            # looking for a record that seems good
            while index < len(self.tables) and self.tables[index].end_code <= code:
                index += 1 
                code <<= (self.tables[index].length - self.tables[index-1].length)

        raise Exception('unknown code: %d, %d' % (code, readed))

class Encoder(object):
    """Put symbol into bitstream""" 

    def __init__(self, lens):
        """Input: 
        - list or pairs (symbol, code lenght)
        - OR list or code lenghts; in this case symbols are just integers"""
        if isinstance(lens[0], int):
            lens = [(n, l) for n,l in enumerate(lens)]

        tables = _tables_from_lenghts(lens)
        self.code = {}

        for l, start, _, symbols in tables:
            for i, c in enumerate(symbols):
                self.code[c] = (start + i, l)

    def put(self, bs, c):
        """Put Huffman-encoded symbol c into bitstream bs"""
        v, n = self.code[c]
        bs.put_be(v, n)

def _tables_from_lenghts(lens):
    """Make canonical huffman code tables from list of code leghts.
    Input:  list of pairs (symbol, code length), ordered by alphabet
    Output: list of tuples (length, start_code, end_code, [symbols in alphabet order])
    Tuples are sorted by length"""

    # make dict {len --> [list of symbols in alphabet order]}
    by_len = defaultdict(list)
    for a, l in lens:
        if l > 0:
            by_len[l].append(a)

    # lengths that exists in code
    actual_lens = by_len.keys()
    actual_lens.sort()

    tables = []
    code = 0
    prev_len = 0

    # fill table
    for l in actual_lens:
        code *= 2**(l-prev_len)
        tables.append(_HuffmanRecord(l, code, code + len(by_len[l]), by_len[l]))
        code += len(by_len[l])
        prev_len = l

    return tables

