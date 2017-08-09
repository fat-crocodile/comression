"""Decode/encode prefix-code encoded symbols from/to bitstream"""

from collections import defaultdict, namedtuple


class Decoder(object):
    """Decode symbol from bitsream"""

    def __init__(self, lenghts):
        """Input: 
            - iterable or pairs (symbol, code lenght)
        """
        self.table = _table_from_lenghts(lenghts)

    def get(self, bs):
        """Read next encoded symbol from bitstream bs, return decoded symbol"""
        code = 0     # readed code
        index = 0    # current table record 
        readed = 0   # number of bits already readed

        while index < len(self.table):
            record = self.table[index]

            # read additional bits
            delta = record.length - readed
            code = (code << delta) + bs.get_be(delta)
            readed += delta

            if code < record.end_code:      # match
                return record.symbols[code - record.start_code]

            # looking for a record that seems good
            while index < len(self.table) and self.table[index].end_code <= (code << (self.table[index].length - readed)):
                index += 1 

        raise Exception('unknown code: value=%d, readed bits=%d' % (code, readed))


class Encoder(object):
    """Put symbol into bitstream""" 

    def __init__(self, lenghts):
        """Input: 
            - iterable or pairs (symbol, code lenght)"""
        table = _table_from_lenghts(lenghts)
        self.code = {}

        for l, start, _, symbols in table:
            for i, c in enumerate(symbols):
                self.code[c] = (start + i, l)

    def put(self, bs, c):
        """Put encoded symbol c into bitstream bs"""
        v, n = self.code[c]
        bs.put_be(v, n)


_TableRecord = namedtuple("_TableRecord", "length start_code end_code symbols")


def _table_from_lenghts(lenghts):
    """Make canonical prefix code table from list of code leghts.

    Input:  
        iterable of pairs (symbol, code length), ordered by these symbols alphabet
    Output: 
        list of tuples (length, start_code, end_code, [symbols in the same alphabet order])

    Tuples are sorted by length"""

    # make dict {lenght --> [list of symbols in alphabet order]}
    by_len = defaultdict(list)
    for a, l in lenghts:
        if l > 0:
            by_len[l].append(a)

    # lengths that exists in code
    actual_lenghts = by_len.keys()
    actual_lenghts.sort()

    table = []
    code = 0
    prev_len = 0

    # fill table
    for length in actual_lenghts:
        code *= 2**(length - prev_len)
        table.append(_TableRecord(length, code, code + len(by_len[length]), by_len[length]))
        code += len(by_len[length])
        prev_len = length

    return table

