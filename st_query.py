#
# Implement routines for querying the alphavantage stock data base.
#

import requests
import json
import os

API_URL = 'https://www.alphavantage.co/query?'
API_KEY = None

def __st_timeseries_query(**kwargs):
    """
    Low level function to generate the query and turn the result into a JSON
    object. Accepted arguments are:
    
      function
      symbol
      interval
      outputsize
      apikey
    """

    url_args = list()
    
    for var, arg in kwargs.items():
        url_args.append(var + '='  + arg)
    
    query = '&'.join(arg for arg in url_args)
    query = API_URL + query
    
    # print '> [Q] %s' % query

    req = requests.get(query)
    
    return json.loads(req.content)

def st_query_intraday(ticker, interval, full_data):
    """
    Basic routine to query intraday data for a given ticker. It will return
    a JSON object with the data. The format looks like so:
    
    {
        "Meta Data": {
            "1. Information": "Intraday (1min) prices and volumes", 
            "2. Symbol": "NVDA", 
            "3. Last Refreshed": "2017-12-20 16:00:00", 
            "4. Interval": "1min", 
            "5. Output Size": "Compact", 
            "6. Time Zone": "US/Eastern"
        }, 
        "Time Series (1min)": {
            "2017-12-20 14:21:00": {
                "1. open": "196.4300", 
                "2. high": "196.4500", 
                "3. low": "196.4100", 
                "4. close": "196.4300", 
                "5. volume": "4134"
            },
            ...
        }
    }

    Accepted intervals are: '1min', '5min', '15min', '30min', '60min'
    """

    if full_data:
        data_size = 'full'
    else:
        data_size = 'compact'

    intraday_args = {
        'function'   : 'TIME_SERIES_INTRADAY',
        'symbol'     : ticker,
        'interval'   : interval,
        'outputsize' : data_size,
        'apikey'     : API_KEY
    }

    return __st_timeseries_query(**intraday_args)

def st_query_daily(ticker, full_data):
    """
    Basic routine to query daily prices. The first data point is the cumulative
    price/trading data for the current day.

    Output is in JSON like so:

    {
        "Meta Data": {
            "1. Information": "Daily Time Series with Splits and Dividend Events",
            "2. Symbol": "NVDA",
            "3. Last Refreshed": "2017-12-20",
            "4. Output Size": "Compact",
            "5. Time Zone": "US/Eastern"
        },
        "Time Series (Daily)": {
            "2017-12-20": {
                "1. open": "197.7000",
                "2. high": "198.0700",
                "3. low": "194.5500",
                "4. close": "196.8000",
                "5. adjusted close": "196.8000",
                "6. volume": "7212897",
                "7. dividend amount": "0.0000",
                "8. split coefficient": "1.0000"
            },
            ...
        }
    }
    """

    if full_data:
        data_size = 'full'
    else:
        data_size = 'compact'

    daily_adjusted_args = {
        'function'   : 'TIME_SERIES_DAILY_ADJUSTED',
        'symbol'     : ticker,
        'outputsize' : data_size,
        'apikey'     : API_KEY
    }

    return __st_timeseries_query(**daily_adjusted_args)

def st_query_crypto_intraday(curreny, market):
    """
    Query a crypto currency value from a given merket.
    """

    crypto_intraday_args = {
        'function' : 'DIGITAL_CURRENCY_INTRADAY',
        'symbol'   : currency,
        'market'   : market,
        'apikey'   : API_KEY
    }

    return __st_timeseries_query(**crypto_intraday_args)

def st_query_crypto_daily(currency, market):
    """
    Query a crypto currency value from a given merket.
    """

    crypto_daily_args = {
        'function' : 'DIGITAL_CURRENCY_DAILY',
        'symbol'   : currency,
        'market'   : market,
        'apikey'   : API_KEY
    }

    return __st_timeseries_query(**crypto_daily_args)

#
# When the module is loaded lets try and read an API key from the env.
if not API_KEY:
    if os.environ['API_KEY']:
        API_KEY = os.environ['API_KEY']
    else:
        # Looks like we are missing an API key... Fall back to demo. This may
        # or may not work! Instead just get an API key!
        API_KEY = 'demo'
        print 'Warning: missing API_KEY for Alpha Vantage APIs'
