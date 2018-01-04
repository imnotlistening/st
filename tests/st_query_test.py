#
# Simple test to make sure basic queries work.
#

from st_query import st_query_quote
import sys
import json

if len(sys.argv) < 2:
    print("Missing stocks!")
    exit(1)

for i in range(1, len(sys.argv)):
    obj = st_query_quote(sys.argv[i])

    for k in sorted(obj.keys()):
        print '%-20s  %s' % (k, obj[k])


print 'Done!'
