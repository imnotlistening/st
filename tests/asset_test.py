#
# Simple tests for the query API.
#

import sys
from stock import Stock

print 'Testing query API!'

if len(sys.argv) < 2:
    print "Missing stocks to query!"
    exit(1)

for i in range(1, len(sys.argv)):
    s = Stock(sys.argv[i])

    print unicode(s)
