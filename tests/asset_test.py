#
# Simple tests for the query API.
#

from stock          import Stock
from cryptocurrency import CryptoCurrency

import sys
import json

print 'Testing query API!'

assets = [ 'NVDA', 'AAPL', '.INX', 'GOOGL' ]
cryptos = [ 'BTC', 'ETH' ]

for ticker in cryptos:
    crypto = CryptoCurrency(ticker, 'USD')

    crypto.refresh()

    (p, c, o, v) = crypto.get_price()

    if c > 0:
        arrow = u'\u25b2'
    elif c < 0:
        arrow = u'\u25bc'
    else:
        arrow = ' '
    
    print '%6s: $%-8.2f  %s%6.2f%%   | $%-8.2f  vol %d' % (crypto.ticker,
                                                           p,
                                                           arrow, c,
                                                           o,
                                                           v)

for ticker in assets:
    s = Stock(ticker)

    s.refresh()
    (p, c, o, v) = s.get_price()

    if c > 0:
        arrow = u'\u25b2'
    elif c < 0:
        arrow = u'\u25bc'
    else:
        arrow = ' '
    
    print '%6s: $%-8.2f  %s%6.2f%%   | $%-8.2f  vol %d' % (s.ticker,
                                                           p,
                                                           arrow, c,
                                                           o,
                                                           v)
    
    
