#!/usr/bin/python

import sys

from portfolio import *

if len(sys.argv) < 2:
    print "Missing portfolio files!"
    exit(1)

for i in range(1, len(sys.argv)):
    print 'Loading porfolio: %s' % sys.argv[i]

    portfolio = Portfolio(sys.argv[i])

    # for tr in portfolio.transactions:
    #     if tr.tr_type == Transaction.BUY or tr.tr_type == Transaction.SELL:
    #         print '%-12s | %-12s %s @ %-8.2f (nr=%d)' % (tr.tr_date,
    #                                                      tr.tr_type,
    #                                                      repr(tr.stock),
    #                                                      tr.price,
    #                                                      tr.quantity)
    #     else:
    #         print '%-12s | %-12s %-8.2f' % (tr.tr_date,
    #                                         tr.tr_type,
    #                                         tr.quantity)

    print unicode(portfolio)
