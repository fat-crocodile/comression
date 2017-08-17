import sys
sys.path.insert(0, '../src')

from prefix_code import Encoder, Decoder
from huffman import make_code_symbols as make_code 
from bounded_huffman import make_code_symbols as make_ll_code  # ll for lenght-limited


class DummyInputStream(object):
    def __init__(self, data):
        self.data = iter(data)
    def get_be(self, n):
        res = 0
        for _ in xrange(n):
            b = self.data.next()
            res *= 2
            if b == '1': res += 1
            elif b == '0': pass
            else: raise Exception('Wrong input format')
        return res


class DummyOutputStream(object):
    def __init__(self):
        self.buffer = []
    def put_be(self, v, n):
        res = []
        for _ in xrange(n):
            res.append('1' if v % 2 else '0')
            v /= 2
        res.reverse()
        self.buffer.extend(res)         


def display_char(c):
    code = ord(c)
    if c == '\n': return '\\n'
    if c == '\t': return '\\t'
    if c == '\r': return '\\r'
    if c == ' ': return "' '"
    if code > 32 and code < 128:
        return c
    return '0x%02x' % code


def display_list(l):
    columns = 4
    items = ['%s --> %3s' % (display_char(c), i) for c,i in l if i > 0]
    rows = [[] for _ in range((len(items) + columns - 1) / columns)]

    try:
        ii = iter(items)
        while True:
            for r in rows:
                r.append(ii.next())
    except StopIteration:
        pass

    res = ['\t'.join(r) for r in rows] 
    return '\n'.join(res)


def test_coder(name, data, code):
    encoder = Encoder(code)
    dos = DummyOutputStream()

    for x in data:
        encoder.put(dos, x)

    print name
    print ''.join(dos.buffer)
    print len(dos.buffer)

    dis = DummyInputStream(dos.buffer)
    decoder = Decoder(code)

    res = []
    try:
        while True:
            res.append(decoder.get(dis))
    except StopIteration:
        pass

    if ''.join(res) == data:
        print 'Decoded'
    else:
        print 'Error!'

data = sys.stdin.read()

counts = dict.fromkeys([chr(i) for i in range(256)], 0)
for x in data:
    counts[x] += 1

counts = sorted(counts.iteritems())

print 'Counts:\n%s' % display_list(counts)

symbols = sum((c for _,c in counts), 0)
weights = [c * 1.0 / symbols for _,c in counts]

codeu  = make_code(counts)
code16 = make_ll_code(counts, 16)
code10 = make_ll_code(counts, 10)
code8  = make_ll_code(counts, 8)
code6  = make_ll_code(counts, 6)

print 'Unlimited code (weighted lenght %s):\n%s' % (sum((w * l for w,(_,l) in zip(weights, codeu)), 0), display_list(codeu))
print 'code-16 (weighted lenght %s):\n%s' % (sum((w * l for w,(_,l) in zip(weights, code16)), 0), display_list(code16))
print 'code-10 (weighted lenght %s):\n%s' % (sum((w * l for w,(_,l) in zip(weights, code10)), 0), display_list(code10))
print 'code-8 (weighted lenght %s):\n%s' %  (sum((w * l for w,(_,l) in zip(weights, code8)), 0), display_list(code8))
print 'code-6 (weighted lenght %s):\n%s' %  (sum((w * l for w,(_,l) in zip(weights, code6)), 0), display_list(code6))

test_coder('unlimited', data, codeu)
test_coder('code-16', data, code16)
test_coder('code-10', data, code10)
test_coder('code-8', data, code8)
test_coder('code-6', data, code6)
 
