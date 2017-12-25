#
# Define an asset class the lets us describe an asset.
#

class Asset(object):
    """
    An asset!

    This class aims to present a nice convenient description of a asset.
    """

    # Types of asset.
    STOCK	= 'stock'
    CRYPTOCUR	= 'crypto'
    
    def __init__(self, ticker, etype):
        """
        Init an asset with the passed ticker name.
        """

        self.ticker = ticker
        self.etype = etype
        
    def refresh(self):
        """
        Should be overridden by sub classes.
        """
        pass
        
    def get_price(self):
        """
        Should be overridden by sub classes.
        """
        pass

