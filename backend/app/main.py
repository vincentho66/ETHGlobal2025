from fastapi import FastAPI, Query
from typing import Literal
import pandas as pd
from io import StringIO
from backend.oneinch.getters import get_token_historical_prices
from backend.backtest.pfopt import PfOptBacktest, _compute_performance_metrics

app = FastAPI()

symbol_map_df = pd.read_csv("backend/oneinch/available_symbol.csv")
symbol_to_addr = dict(zip(symbol_map_df["symbol"], symbol_map_df["address"]))


# Optional: still use caching, but include all inputs in the key
def build_cache_key(symbol: str, period: str, limit: int):
    return f"{symbol}_{period}_{limit}"


_cached_ohlc_data = {}  # (symbol, period, limit) ➝ JSON string


def get_cached_ohlc(symbol: str, period: str, limit: int) -> str:
    key = build_cache_key(symbol, period, limit)
    if key in _cached_ohlc_data:
        return _cached_ohlc_data[key]

    address = symbol_to_addr.get(symbol)
    if not address:
        raise ValueError(f"Symbol {symbol} not found in available_symbol.csv")

    df = get_token_historical_prices(address, period=period, limit=limit)
    json_data = df.to_json(orient="records")
    _cached_ohlc_data[key] = json_data
    return json_data

def get_price_df(symbols: str, period: str, limit: int) -> pd.DataFrame:
    symbol_list = symbols.split(",")

    dfs = []
    for s in symbol_list:
        json_data = get_cached_ohlc(s, period, limit)
        df = pd.read_json(StringIO(json_data))
        df = df[["time", "close"]].rename(columns={"close": s})
        dfs.append(df)

    df_merged = dfs[0]
    for df in dfs[1:]:
        df_merged = df_merged.merge(df, on="time", how="inner")
    return df_merged


#####################################################################################
#####################################################################################
##########################        API Methods:     ##################################
#####################################################################################
#####################################################################################

@app.get("/token_price")
def get_token_price(
    symbol: str = Query(...),
    period: Literal["month", "week", "day", "4hour", "hour", "15min", "5min"] = Query("day"),
    limit: int = Query(1000)
):
    # return get_token_historical_prices()
    try:
        json_data = get_cached_ohlc(symbol,period,limit)
        return json_data
    except Exception as e:
        return {"symbol":symbol, "period": period, "limit": limit, "error": str(e)}

@app.get("/overview")
def get_overview(
    symbols: str = Query(...),
    period: Literal["month", "week", "day", "4hour", "hour", "15min", "5min"] = Query("day"),
    limit: int = Query(1000)
):
    try:
        df = get_price_df(symbols, period, limit)
        df.iloc[:,1:] = df.iloc[:,1:]/df.iloc[0,1:]
        return df.to_json(orient="records")
    except Exception as e:
        return {"symbol":symbols, "period": period, "limit": limit, "error": str(e)}

@app.get("/bt")
def run_backtest(
        symbols: str = Query(...),
        period: Literal["month", "week", "day", "4hour", "hour", "15min", "5min"] = Query("day"),
        limit: int = Query(1000), 
        lookback: int = Query(90),
        rebalance: int = Query(30),
        algorithm: Literal["mvo","hrp"] = Query("mvo")
):
    try:
        price_df = get_price_df(symbols, period, limit).set_index('time')
        time = price_df.index.to_list()
        bt = PfOptBacktest(price_df,lookback, rebalance)
        equity_curve = bt.run(algorithm)
        performance = _compute_performance_metrics(equity_curve, time)
        return {"equity_curve": equity_curve.tolist(), "time": time, **performance}
    except Exception as e:
        return {"symbol":symbols, "period": period, "limit": limit, "lookback":lookback, "rebalance":rebalance, "error": str(e)}

