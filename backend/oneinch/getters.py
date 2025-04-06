import requests
import pandas as pd
import os
from typing import Literal

def get_available_symbol_df(chain_id = 1):
    apiUrl = "https://api.1inch.dev/token/v1.2/multi-chain"

    headers = {"Authorization": f"Bearer {os.getenv('ONEINCH_API_KEY')}"}

    response = requests.get(apiUrl, headers=headers)
    df = pd.DataFrame([[info['symbol'], info['address']] for info in response.json() if info['chainId'] == chain_id],
             columns = ['symbol','address'])
    return df

def get_token_historical_prices(token_addr:str = "0xeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeeee", 
    period:Literal['month','week','day','4hour','hour','15min','5min'] = 'day', 
    limit:int = 1000):
    apiUrl = "https://api.1inch.dev/portfolio/integrations/prices/v1/time_range/cross_prices"

    headers = {"Authorization": f"Bearer {os.getenv('ONEINCH_API_KEY')}"}
    params = {
    "token0_address": token_addr,
    "token1_address": "0xdac17f958d2ee523a2206206994597c13d831ec7",
    "chain_id": 1,
    "granularity": period,
    "limit": limit
    }

    response = requests.get(apiUrl, headers=headers, params=params).json()

    cols = ['time','open','high','low','close']
    if not isinstance(response, list):
        if 'error' in response.keys():
            return pd.DataFrame(columns=cols)
    else:
        df = pd.DataFrame(response)
        df['time'] = pd.to_datetime(df['timestamp'], unit='s')
    return df[cols].iloc[::-1]
