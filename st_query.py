#
# Implement routines for querying the alphavantage stock data base.
#

import requests
import json

API_URL = 'https://api.iextrading.com/1.0/'

def st_query_quote(stock):
    """
    Query information about a stock.
    """

    url = API_URL + 'stock/' + stock + '/quote'

    # print '> Query URL: ' + url

    req = requests.get(url)

    return json.loads(req.content)
