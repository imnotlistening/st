
from asset    import Asset
from st_query import *

class Stock(Asset):
    """
    A stock class derived from an asset.
    """

    def __init__(self, ticker):
        super(Stock, self).__init__(ticker, Asset.STOCK)

        self.__stock_data = None

    def refresh(self):
        """
        Refresh the stock data.
        """

        self.__stock_data = st_query_quote(self.ticker)

    def get_price(self):
        """
        Get latest price data. If it's not present, then call refresh() first.
        This aims to return the latest price as the following tuple:

          ( price, %change, open, volume )

        This interface aims for simplicty. It should not be made more complex
        than this. Other interfaces can do that.
        """

        if not self.__stock_data:
            self.refresh()

        p = float(self.__stock_data['latestPrice'])
        c = float(self.__stock_data['changePercent'])
        o = float(self.__stock_data['open'])
        v = float(self.__stock_data['avgTotalVolume'])

        return (p, c, o, v)

    def get_change(self):
        """
        Get the daily change in absolute dollars and %change. Returns the
        following tuple:

          (absChange, percentChange)
        """

        if not self.__stock_data:
            self.refresh()

        ca = float(self.__stock_data['change'])
        cp = float(self.__stock_data['changePercent'])

        return (ca, cp)

    def __unicode__(self):
        """
        A srtring describing this stock.
        """

        # Do a refresh first; without this there's not a lot to display.
        self.refresh()

        (p, c, o, v) = self.get_price()

        if c > 0:
            arrow = u'\u25b2'
        elif c < 0:
            arrow = u'\u25bc'
        else:
            arrow = ' '

        return '%6s: $%-8.2f  %s%6.2f%%   | $%-8.2f  vol %d' % (self.ticker,
                                                                p,
                                                                arrow, c * 100,
                                                                o,
                                                                v)
    def __repr__(self):
        return self.ticker

    def name(self):
        return self.__stock_data['companyName']

    def symb(self):
        return self.__stock_data['symbol']

    def price(self):
        return self.__stock_data['latestPrice']

    def change_percent(self):
        return self.__stock_data['changePercent']

    def change(self):
        return self.__stock_data['change']


#
# These functions provide sorting key functions for sorting lists of stocks.
#

def stock_key_name(s):
    return s.name()

def stock_key_symb(s):
    return s.symb()

def stock_key_price(s):
    return s.price()

def stock_key_change_percent(s):
    return s.change_percent()

def stock_key_change(s):
    return s.change()
