#
# Simple tests for the query API.
#

import st_query
import equity

import sys
import json

print 'Testing query API!'

for ticker in sys.argv[1:]:
    s = equity.Stock(ticker)

    s.refresh()
    (p, c, o, v) = s.get_price()

    if c > 0:
        arrow = u'\u25b2'
    elif c < 0:
        arrow = u'\u25bc'
    else:
        arrow = ' '
    
    print '%s: $%-8.2f  %s%6.2f%%   | $%-8.2f  vol %d' % (s.ticker,
                                                          p,
                                                          arrow, c,
                                                          o,
                                                          v)
