#
# A portfolio of stocks. Manage and track a list of equities, and how much they
# have made/lost, etc.
#

from datetime  import datetime
from termcolor import colored
from operator  import methodcaller

import curses

from stock     import Stock
from lot       import Lot
from lot       import LotAggregate

def no_color(s, color):
    return s

class Portfolio(object):
    """
    This wraps a list of lots. Each lot represents some stocks.
    """

    def __init__(self, file_path):
        """
        Load an portfolio from a file. The file format is as follows:

          # Lines that start with '#' are comment. Blank lines are ignored. For
          # each transaction, if there's a '#' at the end of the line, the
          # remaining string is considered a description of the transaction.
          <TR_DATE> | <TR_TYPE>: <quantity> [equity <acquired price>] [# desc]
          ...

        Where <TR_DATE> is the date of the transaction, formatted: YYYY-MM-DD
              <TR_TYPE> is {BUY, SELL, DEPOSIT, WITHDRAWL} (case insensitive)
              <quantity> is a floating point quantity.
              [equity <price>] When TYPE is buy or sell, then this must be
                               present: it is the equity ticker, f.e NVDA, and
                               the price at which the equity was bought/sold.
              [# msg] An optional message describing the transaction.
        """

        self.name         = file_path
        self.lots         = list()
        self.assets       = None     # Will be a list of stocks.
        self.asset_counts = dict()
        self.asset_lots   = dict()
        self.cash         = 0.0

        f = open(file_path)

        for line in f:
            self.parse_line(line)

        self.__compute_details()
        self.assets = self.asset_lots.keys()

    def __compute_details(self):
        """
        Compute an asset map: that is a map of assets to list of Lots.
        Also compute how many of each stock we have.
        """

        for l in self.lots:
            if l.stock not in self.asset_lots:
                self.asset_lots[l.stock] = list()
                self.asset_counts[l.stock] = 0

            self.asset_lots[l.stock].append(l)
            self.asset_counts[l.stock] += l.nr

    def __to_string(self, color_func=no_color):
        """
        Return a unicode string representation of this portfolio.
        """

        fmt = '%-7s %12.2f   %s %-7s   %-8d | $%12.2f  %12.2f\n'
        up  = '%-7s %-12s  %-10s  %-8s | %-12s  %12s\n' % ('Asset',
                                                           'Current price',
                                                           'Change (%)',
                                                           'Shares',
                                                           'Current Value',
                                                           'Change')
        up += '%-7s %-13s  %-10s  %-8s | %-12s  %12s\n' % ('-----',
                                                           '-------------',
                                                           '----------',
                                                           '------',
                                                           '-------------',
                                                           '------')

        total = 0
        total_change = 0

        for s in sorted(self.assets):
            p, c, o, _ = s.get_price()
            pa, _ = s.get_change()

            if c > 0:
                arrow = color_func(u'\u25b2', 'green')
                c_colored = color_func('%7.2f' % (c * 100), 'green')
            elif c < 0:
                arrow = color_func(u'\u25bc', 'red')
                c_colored = color_func('%7.2f' % (c * 100), 'red')
            else:
                arrow = ' '
                c_colored = '%7.2f' % (c * 100)


            change = self.asset_counts[s] * pa

            up += fmt % (s, p,
                         arrow, c_colored,
                         self.asset_counts[s],
                         self.asset_counts[s] * p,
                         change)

            total += self.asset_counts[s] * p
            total_change += change

        # Totals
        up += '\n'
        up += 'Daily change    $%12.2f\n' % total_change
        up += 'Total equity    $%12.2f\n' % total
        up += 'Cash:           $%12.2f\n' % self.cash
        up += 'Portfolio value $%12.2f\n' % (total + self.cash)
        up += 'Cost basis:     $%12.2f\n' % self.cost_basis()
        up += 'Total gain      $%12.2f'   % ((total + self.cash) - self.cost_basis())

        return up

    def __unicode__(self):
        return self.__to_string()

    def __str__(self):
        return self.to_string()

    def to_string_color(self):
        return self.to_string(color_func=colored)

    def refresh(self):
        """
        Refresh this portfolio.
        """

        for s in self.assets:
            s.refresh()

    def cost_basis(self):
        """
        Accumulate the cost basis for this portfolio. This uses a numerically
        tax efficient strategy for handling sells which affect cost basis.
        """

        cb = 0.0

        for l in self.lots:
            cb += l.cost_basis()

        return cb

    def sum_stock(self, stock):
        """
        Sum up all lots that match the passed stock. Returns a big tuple of:

          (Shares, CostBasis, Price,
           Change, ChangePercent,
           Gain, GainPercent)
        """

        la = LotAggregate(stock)

        la.price = stock.price()

        for l in self.asset_lots[stock]:
            la.shares += l.nr
            la.cb     += l.cost_basis()

        ca, cp = stock.get_change()

        la.gain     = (la.shares * stock.price()) - la.cb
        la.change   = la.shares * ca
        la.change_p = la.shares * cp

        if la.cb > 0.0:
            la.gain_p   = (la.gain / la.cb) * 100

        return la

    ##
    ## Portfolio parsing stuff.
    ##

    def parse_line(self, line):
        """
        Parse a line. Take care of comments and blank lines here.
        """

        line = line.strip();

        if line == '' or line[0] == '#':
            return

        # Ok, do the real parsing now: the first bit of the string is the
        # date. Split on the '|' to get the date bit.
        (date_str, tr_data) = line.split('|')
        date = datetime.strptime(date_str.strip(), '%b %d, %Y')

        # Now split off a comment, in case one is there
        if '#' in tr_data:
            tr_data, comment = tr_data.split('#')
        else:
            comment = ''

        # And now split the tr_data into items and parse them.
        tr_items = tr_data.split()

        l = None

        # This is a deposit/withdrawl.
        if len(tr_items) == 2:
            if tr_items[0] == 'DEPOSIT':
                self.cash += float(tr_items[1])
            elif tr_items[0] == 'WITHDRAWL':
                self.cash -= float(tr_items[1])
            else:
                print 'Unrecognized transaction type: %s' % tr_items[0]

        # Looks like we might have a stock trade.
        elif len(tr_items) == 4:
            if tr_items[0] == 'BUY':

                # If we have a buy then we just need to add a new lot to our
                # list of lots. Sells will go and modify the lots.
                l = Lot(Stock(tr_items[2]),
                        date,
                        float(tr_items[3]),
                        float(tr_items[1]),
                        cmt=comment)
            elif tr_items[0] == 'SELL':
                self.__handle_sell(tr_items)
            else:
                print 'Unrecognized transaction type: %s' % tr_items[0]
        else:
            print 'Bad data line: "%s"' % line

        # If we have a lot then add it to our list!
        if l:
            self.lots.append(l)

    def __handle_sell(self, tr_items):
        """
        Handle a sell. This requires thinking about which stocks to actually
        sell. For our purposes we will use a tax avoidance method. The idea is
        to sell stocks that minimize tax burden now. Another way of thinking
        about this is to minimize capital gains for the sell.

        This isn't the only method for choosing which stocks to sell, but it
        should give a reasonable guess of what the average investor might do.
        """

        s = Stock(tr_items[2])
        nr = float(tr_items[1])
        matching_lots = list()

        # Find lots that have the stock we are selling.
        for l in self.lots:
            if l.stock == s:
                matching_lots.append(l)

        # Now sort the lots by gain low to high.
        matching_lots.sort(key=methodcaller('compute_gain'))

        for l in matching_lots:
            nr = l.remove(nr)

            if nr == 0:
                break
