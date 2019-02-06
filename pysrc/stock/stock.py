
from asset    import Asset
from st_query import *

class Stock(Asset):
    """
    A stock class derived from an asset.
    """

    # Cache of data that's global to all stocks. Prevents needless look up of
    # data and constant refreshing.
    __data_cache = dict()

    def __init__(self, ticker):
        super(Stock, self).__init__(ticker, Asset.STOCK)

    def refresh(self):
        """
        Refresh the stock data.
        """

        stock_data = st_query_quote(self.ticker)

        Stock.__data_cache[self.ticker] = stock_data

    def __get_data(self):
        return Stock.__data_cache.get(self.ticker)

    def get_data(self):
        """
        Get the latest data refreshing the stock if it's not present.
        """

        data = self.__get_data()
        if not data:
            self.refresh()
            data = self.__get_data()

        return data

    def get_price(self):
        """
        Get latest price data. If it's not present, then call refresh() first.
        This aims to return the latest price as the following tuple:

          ( price, %change, open, volume )

        This interface aims for simplicty. It should not be made more complex
        than this. Other interfaces can do that.
        """

        data = self.get_data()

        p = float(data['latestPrice'])
        c = float(data['changePercent'])
        o = float(data['open'])
        v = float(data['avgTotalVolume'])

        return (p, c, o, v)

    def get_change(self):
        """
        Get the daily change in absolute dollars and %change. Returns the
        following tuple:

          (absChange, percentChange)
        """

        data = self.get_data()

        ca = float(data['change'])
        cp = float(data['changePercent'])

        return (ca, cp)

    def __unicode__(self):
        """
        A string describing this stock.
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
    def __eq__(self, s):
        if not isinstance(s, Stock):
            return NotImplemented

        return s.ticker == self.ticker

    def __ne__(self, s):
        eq = self.__eq__(s)

        if eq == NotImplemented:
            return NotImplemented

        return not eq

    def __lt__(self, s):
        if not isinstance(s, Stock):
            return NotImplemented

        # Alphabetical sort.
        return self.get_data()['symbol'] < s.get_data()['symbol']

    def __repr__(self):
        return self.ticker

    def __hash__(self):
        return hash(self.ticker)

    def name(self):
        return self.get_data()['companyName']

    def symb(self):
        return self.get_data()['symbol']

    def price(self):
        return self.get_data()['latestPrice']

    def change_percent(self):
        return self.get_data()['changePercent']

    def change(self):
        return self.get_data()['change']


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
