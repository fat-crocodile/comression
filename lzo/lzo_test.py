#! /usr/bin/env python

import sys
import lzo
from mylzo1x_d import lzo1x_decoder

# level 1   -- lzo1x_1
#       2-9 -- lzo1x_999
level = int(sys.argv[1]) if len(sys.argv) > 1 else 1

plain_text = sys.stdin.read()
compressed = lzo.compress(plain_text, level)

log = []
res = ''.join(lzo1x_decoder(compressed[5:], log.append))

# print some results
print "plain text len = %d, compressed len = %d, decopressed len = %d" % (len(plain_text), len(compressed), len(res))

if plain_text == ''.join(res):
    print 'OK'
else:
    # print first 10 errors
    count = 0
    for i in xrange(len(plain_text)):
        if plain_text[i] != res[i]:
            print 'error %d: at %d, %d vs. %d' % (count, i, ord(plain_text[i]), ord(res[i]))
            count += 1
            if count > 10: break

# print complete log in stderr
for r in log:
    print >>sys.stderr, r

