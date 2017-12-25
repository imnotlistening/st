
from asset    import Asset
from st_query import *

class CryptoCurrency(Asset):
    """
    Crypto currency tracking.
    """

    # Constants for accessing the daily tracker data. Annoyingly the crypto
    # data has this currency field put in it.
    data_elems = {
        'OPEN'       : '1a. open (%s)',
        'HIGH'       : '2a. high (%s)',
        'LOW'        : '3a. low (%s)',
        'CLOSE'      : '4a. close (%s)',
        'MARKET_CAP' : '6. market cap (%s)'
    }

    # This guy doesn't have the market field.
    __VOLUME = '5. volume'
    
    def __init__(self, ticker, market):
        super(CryptoCurrency, self).__init__(ticker, Asset.CRYPTOCUR)
        
        self.raw_compact_daily = None
        self.compact_daily = None
        self.sorted_daily_keys = None

        self.market = market

        for k, v in self.data_elems.items():
            setattr(self, k, v % market)

        self.VOLUME = CryptoCurrency.__VOLUME
            
        # self.OPEN       = '1a. open (%s)' % self.market
        # self.HIGH       = '2a. high (%s)' % self.market
        # self.LOW        = '3a. low (%s)' % self.market
        # self.CLOSE      = '4a. close (%s)' % self.market
        # self.
        # self.MARKET_CAP = '6. market cap (%s)' % self.market
        
    def refresh(self):
        """
        Refresh the crypto currency data.
        """

        self.raw_compact_daily = st_query_crypto_daily(self.ticker, self.market)

        self.compact_daily = self.raw_compact_daily['Time Series (Digital Currency Daily)']
        self.sorted_daily_keys = sorted(self.compact_daily.keys())

    def get_price(self):
        """
        Return the latest price.
        """

        # Make sure we have data.
        if not self.compact_daily:
            self.refresh()

        today     = self.sorted_daily_keys[-1]
        yesterday = self.sorted_daily_keys[-2]

        o = float(self.compact_daily[today][self.OPEN])
        p = float(self.compact_daily[today][self.CLOSE])
        v = float(self.compact_daily[today][self.VOLUME])

        # work out percent change based on yesterdays adjusted close.
        c = p - float(self.compact_daily[yesterday][self.CLOSE])
        c /= p
        c *= 100

        return (p, c, o, v)
