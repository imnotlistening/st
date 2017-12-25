
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

    def __init__(self, ticker):
        super(Stock, self).__init__(ticker, Asset.STOCK)
        
        self.raw_compact_daily = None
        self.compact_daily = None
        self.sorted_daily_keys = None

    def refresh(self):
        """
        Query price data from Alphavantage. This gets the last 100 open and
        closes of the asset, etc. The most recent data point is an up-to-date
        price for the asset, in case the markets are currently open.
        """

        self.raw_compact_daily = st_query_daily(self.ticker, False)

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
        c *= 100

        return (p, c, o, v)
