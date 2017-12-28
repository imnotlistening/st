
from asset    import Asset
from st_query import *

class Stock(Asset):
    """
    A stock class derived from an asset.
    """

    # Constants for accessing the daily tracker data.
    OPEN        = '1. open'
    HIGH        = '2. high'
    LOW         = '3. low'
    CLOSE       = '4. close'
    ADJ_CLOSE   = '5. adjusted close'
    VOLUME      = '6. volume'
    DIV_AMOUNT  = '7. dividend amount'
    SPLIT_COEFF = '8. split coefficient'

    # Querying the server is really expensive. So cache the raw data. This lets
    # us look for cached data before we go to the actual server.
    raw_data_cache = dict()

    def __init__(self, ticker):
        super(Stock, self).__init__(ticker, Asset.STOCK)

        self.raw_compact_daily = None
        self.compact_daily = None
        self.sorted_daily_keys = None

    def force_refresh(self):
        """
        Query price data from Alphavantage. This gets the last 100 open and
        closes of the asset, etc. The most recent data point is an up-to-date
        price for the asset, in case the markets are currently open.

        This function only updates the Stock cache for raw data. refreesh() is
        what actually uses that data.
        """

        # Update the cache.
        Stock.raw_data_cache[self.ticker] = st_query_daily(self.ticker, False)

        self.__do_refresh()

    def refresh(self):
        """
        Refresh the stock - but check the cache first. If the cache has raw
        data for thi ticker we will use it. If there's no data then go and do
        a __refresh()
        """

        # Check the cache - if the data isn't there fill it.
        if not self.ticker in Stock.raw_data_cache:
            self.force_refresh()

        self.__do_refresh()

    def __do_refresh(self):
        """
        Actually do the refresh stuff - basically just get the useful data.
        """

        self.raw_compact_daily = Stock.raw_data_cache[self.ticker]

        # The raw data isn't super conducive to data processing. So let's
        # just pull out the time series data and put that into a dictionary.
        #
        # We store the sorted keys so that we can easily get the recent data
        # for generating useful info about the asset.
        self.compact_daily = self.raw_compact_daily['Time Series (Daily)']
        self.sorted_daily_keys = sorted(self.compact_daily.keys())

    def get_price(self):
        """
        Get latest price data. If it's not present, then call refresh() first.
        This aims to return the latest price as the following tuple:

          ( price, %change, open, volume )

        This interface aims for simplicty. It should not be made more complex
        than this. Other interfaces can do that.
        """

        # Make sure we have data.
        if not self.compact_daily:
            self.refresh()

        today     = self.sorted_daily_keys[-1]
        yesterday = self.sorted_daily_keys[-2]

        o = float(self.compact_daily[today][Stock.OPEN])
        p = float(self.compact_daily[today][Stock.ADJ_CLOSE])
        v = float(self.compact_daily[today][Stock.VOLUME])

        # work out percent change based on yesterdays adjusted close.
        c = p - float(self.compact_daily[yesterday][Stock.ADJ_CLOSE])
        c /= p

        return (p, c, o, v)

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
