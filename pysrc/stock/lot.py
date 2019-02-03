#
# A single lot of stocks. This is used for grouping bunchs of stocks together so
# that proper cost basis reporting can be done for a portfolio.
#


class Lot(object):
    """
    Each lot is defined by a stock and some number of those stocks. An acquire
    cost is also present for a lot which later can be used for computing cost
    basis for a portfolio.
    """

    def __init__(self, stock, date, acquire_price, nr, cmt=None):
        """
        Make a lot with the passed stock and the passed date.
        """

        self.stock         = stock
        self.date          = date
        self.nr            = nr
        self.acquire_price = acquire_price
        self.comment       = cmt

    def cost_basis(self):
        """
        Return the cost basis for this lot. This is simply the acquire price
        times the number shares.
        """

        return self.nr * self.acquire_price

    def remove(self, nr):
        """
        Removes some stocks from this lot. Analogous to selling the stocks. If
        you pass in more stocks to remove than are in the lot then the remaining
        (the unremoved stocks) are returned. I.e if you remove 120 stocks from a
        lot with 100 stocks, 20 is returned (120 - 100).
        """

        if nr > self.nr:
            remainder = nr - self.nr
            self.nr = 0
            return remainder

        self.nr -= nr
        return 0

    def remove_all(self):
        return remove(self, self.nr)

    def compute_gain(self, refresh=False):
        """
        Compute the gain for this lot and return it.
        """

        if refresh:
            self.stock.refresh()

        price  = self.stock.price()

        return (price - self.acquire_price) * self.nr
