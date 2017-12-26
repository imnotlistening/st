#!/usr/bin/python

from portfolio import *

portfolio_file = 'portfolios/my-assets.txt'

print 'Loading porfolio: %s' % portfolio_file

portfolio = Portfolio(portfolio_file)

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
        
