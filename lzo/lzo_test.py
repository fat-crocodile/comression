#! /usr/bin/env python

import sys
import lzo
from mylzo1x_d import lzo1x_decoder

plain_text = sys.stdin.read()
compressed = lzo.compress(plain_text)

log = []
res = ''.join(lzo1x_decoder(compressed[5:], log.append))

# print some results
print "plain text len = %d, compressed len = %d, decopressed len = %d" % (len(plain_text), len(compressed), len(res))

count = 0
for i in xrange(len(plain_text)):
    if plain_text[i] != res[i]:
        print 'error %d: at %d, %d vs. %d' % (count, i, ord(plain_text[i]), ord(res[i]))
        count += 1
        if count > 10: break

if count == 0:
    print 'OK'

# print complete log in stderr
for r in log:
    print >>sys.stderr, r

