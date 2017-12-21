#
# A portfolio of stocks. Manage and track a list of equities, and how much they
# have made/lost, etc.
#

class Transaction:
    """
    Simple class to track a 'transaction' - either equities or cash. Exists
    mostly to just glue some data together.
    """

    # The different types of supported transactions for our portfolio
    BUY       = 'buy'
    SELL      = 'sell'
    DEPOSIT   = 'dep'
    WITHDRAWL = 'wdrl'
    
    def __init__(self, tr_date, tr_type, quantity=0, stock=None, desc=None):
        """
        A list of these defines a portfolio.
        """
        self.tr_date = tr_date
        self.tr_type = tr_type
        self.quantity = quantity

        # Only keep track of this if we are trading an equity of some sort.
        if tr_type == Transaction.BUY or tr_type == Transaction.SELL:
            self.stock = stock

        self.description = desc
        
class Portfolio:
    """
    This wraps a list of transactions. Transactions can be for equities or for
    cash.
    """

    def __init__(self, filp):
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

    def add_transaction(self, trans):
        """
        Add a transaction to the list of transactions.
        """
        
