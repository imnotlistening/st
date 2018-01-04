#
# A portfolio of stocks. Manage and track a list of equities, and how much they
# have made/lost, etc.
#

from datetime  import datetime
from stock     import Stock

from termcolor import colored

class Transaction:
    """
    Simple class to track a 'transaction' - either equities or cash. Exists
    mostly to just glue some data together.
    """

    # The different types of supported transactions for our portfolio
    BUY       = 'BUY'
    SELL      = 'SELL'
    DEPOSIT   = 'DEPOSIT'
    WITHDRAWL = 'WITHDRAWL'

    def __init__(self, tr_date, tr_type,
                 quantity=0, ticker=None, price=0, desc=None):
        """
        A list of these defines a portfolio.
        """
        self.tr_date = tr_date
        self.tr_type = tr_type
        self.quantity = quantity

        # Only keep track of this if we are trading an equity of some sort.
        if tr_type == Transaction.BUY or tr_type == Transaction.SELL:
            self.stock = Stock(ticker)
            self.price = price

        self.description = desc

class Portfolio:
    """
    This wraps a list of transactions. Transactions can be for equities or for
    cash.
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

        self.transactions = list()
        self.asset_counts = dict()

        f = open(file_path)

        for line in f:
            self.parse_line(line)

    def __unicode__(self):
        """
        Return a string representation of this portfolio.
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

        self.accumulate_assets()

        total = 0
        total_change = 0

        for asset in sorted(self.asset_counts.keys()):
            stock = Stock(asset)
            p, c, o, _ = stock.get_price()
            pa, _ = stock.get_change()

            if c > 0:
                arrow = colored(u'\u25b2', 'green')
                c_colored = colored('%7.2f' % (c * 100), 'green')
            elif c < 0:
                arrow = colored(u'\u25bc', 'red')
                c_colored = colored('%7.2f' % (c * 100), 'red')
            else:
                arrow = ' '
                c_colored = '%7.2f' % (c * 100)


            change = self.asset_counts[asset] * pa

            up += fmt % (asset,
                         p,
                         arrow, c_colored,
                         self.asset_counts[asset],
                         self.asset_counts[asset] * p,
                         change)

            total += self.asset_counts[asset] * p
            total_change += change

        # Totals
        up += '\n'
        up += 'Total Change    $%12.2f\n' % total_change
        up += 'Total Equity    $%12.2f\n' % total
        up += 'Cash:           $%12.2f\n' % self.cash
        up += 'Portfolio value $%12.2f'   % (total + self.cash)

        return up

    def accumulate_assets(self):
        """
        Run through the transactions and accumate the quantities of each
        asset.
        """

        self.cash = 0
        self.asset_counts = dict()

        for t in self.transactions:
            if t.tr_type == Transaction.BUY:
                if not repr(t.stock) in self.asset_counts:
                    self.asset_counts[repr(t.stock)] = 0
                self.asset_counts[repr(t.stock)] += t.quantity
            elif t.tr_type == Transaction.SELL:
                if not repr(t.stock) in self.asset_counts:
                    self.asset_counts[repr(t.stock)] = 0
                self.asset_counts[repr(t.stock)] -= t.quantity
            elif t.tr_type == Transaction.DEPOSIT:
                self.cash += t.quantity
            else:
                self.cash -= t.quantity

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

        t = None

        # This is a deposit/withdrawl.
        if len(tr_items) == 2:
            if tr_items[0] == 'DEPOSIT':
                t = Transaction(date, Transaction.DEPOSIT, float(tr_items[1]),
                                desc=comment)
            elif tr_items[0] == 'WITHDRAWL':
                t = Transaction(date, Transaction.WITHDRAWL, float(tr_items[1]),
                                desc=comment)
            else:
                print 'Unrecognized transaction type: %s' % tr_items[0]

        # Looks like we might have a stock trade.
        elif len(tr_items) == 4:
            if tr_items[0] == 'BUY':
                t = Transaction(date, Transaction.BUY,
                                quantity=float(tr_items[1]),
                                ticker=tr_items[2],
                                price=float(tr_items[3]),
                                desc=comment)
            elif tr_items[0] == 'SELL':
                t = Transaction(date, Transaction.SELL,
                                quantity=float(tr_items[1]),
                                ticker=tr_items[2],
                                price=float(tr_items[3]),
                                desc=comment)
            else:
                print 'Unrecognized transaction type: %s' % tr_items[0]
        else:
            print 'Bad data line: "%s"' % line

        if not t:
            return

        # Ok, we have our transaction, let's add it to our list.
        self.transactions.append(t)
        self.transactions.sort(key=lambda d: t.tr_date)
