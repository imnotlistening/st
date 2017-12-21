#
# Define an equity class the lets us describe an equity.
#

import json

import st_query

class Equity(object):
    """
    An equity!

    This class aims to present a nice convenient description of a equity.
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

    # Types of equity.
    STOCK	= 'stock'
    CRYPTOCUR	= 'crypto'
    
    def __init__(self, ticker, etype):
        """
        Init an equity with the passed ticker name.
        """

        self.ticker = ticker
        self.etype = etype
        
    def refresh(self):
        """
        Should be overridden by sub classes.
        """
        
    def get_price(self):
        """
        Should be overridden by sub classes.
        """

class Stock(Equity):
    """
    A stock class derived from an equity.
    """

    def __init__(self, ticker):
        super(Stock, self).__init__(ticker, Equity.STOCK)
        
        self.raw_compact_daily = None
        self.compact_daily = None
        self.sorted_daily_keys = None

    def refresh(self):
        """
        Query price data from Alphavantage. This gets the last 100 open and
        closes of the equity, etc. The most recent data point is an up-to-date
        price for the equity, in case the markets are currently open.
        """

        self.raw_compact_daily = st_query.st_query_daily(self.ticker, False)

        # The raw data isn't super conducive to data processing. So let's
        # just pull out the time series data and put that into a dictionary.
        #
        # We store the sorted keys so that we can easily get the recent data
        # for generating useful info about the equity.
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

        o = float(self.compact_daily[today][Equity.OPEN])
        p = float(self.compact_daily[today][Equity.ADJ_CLOSE])
        v = float(self.compact_daily[today][Equity.VOLUME])

        # work out percent change based on yesterdays adjusted close.
        c = p - float(self.compact_daily[yesterday][Equity.ADJ_CLOSE])
        c /= p
        c *= 100

        return (p, c, o, v)

class CryptoCurrency(Equity):
    """
    Crypto currency tracking.
    """

        def __init__(self, ticker):
            super(Stock, self).__init__(ticker, Equity.CRYPTOCUR)
        
            self.raw_compact_daily = None
            self.compact_daily = None
            self.sorted_daily_keys = None


        def refresh():
            """
            Refresh the crypto currency data.
            """

            
