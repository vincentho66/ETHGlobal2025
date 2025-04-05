import pandas as pd
import numpy as np
from typing import Literal
from pypfopt import EfficientFrontier, risk_models, expected_returns, HRPOpt
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

def _clip_and_normalize(df:pd.DataFrame):
    clipped = df.clip(lower=0)
    normalized = clipped.div(clipped.sum(axis=1), axis=0)
    return normalized

def _compute_equity_curve(price_df:pd.DataFrame, weight_history_df:pd.DataFrame, transaction_cost=0.001):

    returns = price_df.pct_change().fillna(0)
    weights = weight_history_df.reindex(returns.index, method='ffill')
    port_returns = (weights.shift() * returns).sum(axis=1)
    turnover = weights.diff().abs().sum(axis=1)
    net_returns = port_returns - turnover * transaction_cost
    equity_curve = (1 + net_returns).cumprod()

    return equity_curve

def _compute_performance_metrics(equity_curve, time):
    equity_curve = np.asarray(equity_curve)
    time = np.asarray(time)/1000
    
    # Return
    total_return = equity_curve[-1] / equity_curve[0] - 1

    # Log returns
    log_returns = np.diff(np.log(equity_curve))
    
    # Time delta for frequency normalization
    time_deltas = np.diff(time)
    avg_seconds = np.mean(time_deltas)
    freq_per_year = 365 * 24 * 3600 / avg_seconds  # approximate annualization

    # Sharpe ratio (annualized)
    excess_returns = log_returns * avg_seconds / (365 * 24 * 3600)
    sharpe_ratio = np.mean(excess_returns) / np.std(excess_returns, ddof=1) * np.sqrt(freq_per_year)

    # Drawdown
    peak = np.maximum.accumulate(equity_curve)
    drawdown = equity_curve / peak - 1
    max_drawdown = np.min(drawdown)

    # Max drawdown duration
    peak_idx = 0
    max_duration = 0
    current_duration = 0
    for i in range(1, len(equity_curve)):
        if equity_curve[i] >= peak[peak_idx]:
            peak_idx = i
            current_duration = 0
        else:
            current_duration = time[i] - time[peak_idx]
            max_duration = max(max_duration, current_duration)

    # Profit factor
    pnl = np.diff(equity_curve)
    gross_profit = np.sum(pnl[pnl > 0])
    gross_loss = -np.sum(pnl[pnl < 0])
    profit_factor = gross_profit / gross_loss if gross_loss != 0 else np.inf

    return {
        'Total Return': total_return,
        'Sharpe Ratio': sharpe_ratio,
        'Max Drawdown': max_drawdown,
        'Max Drawdown Duration (day)': max_duration/86400,
        'Profit Factor': profit_factor
    }

class PfOptBacktest:

    def __init__(self, price_df: pd.DataFrame, lookback_days: int, rebalance_days:int):
        self.price_df = price_df
        self.lookback_days = lookback_days
        self.rebalance_days = rebalance_days
    
    @staticmethod
    def _get_weight(prices_window:pd.DataFrame, method: Literal['mvo','hrp'] = 'mvo'):
        if method == 'mvo':
            weight = PfOptBacktest.__get_mvo_weights(prices_window)
        elif method == 'hrp':
            weight = PfOptBacktest.__get_hrp_weights(prices_window)
        else:
            raise NotImplementedError(f'{method} not implemented, try: "mvo","hrp"')
        
        return weight
    
    def get_weight_history(self, method: Literal['mvo','hrp'] = 'mvo'):
        dates = []
        weights_list = []
        for i in range(self.lookback_days, len(self.price_df), self.rebalance_days):
            window = self.price_df.iloc[i - self.lookback_days:i]

            date = self.price_df.index[i]
            weights = PfOptBacktest._get_weight(window, method)
            weights_list.append(weights)
            dates.append(date)
        weight_history_df = pd.DataFrame(weights_list, index = dates, columns = self.price_df.columns)
        return _clip_and_normalize(weight_history_df)
    
    def run(self, method: Literal['mvo','hrp'] = 'mvo'):
        weight_history_df = self.get_weight_history(method)
        equity_curve = _compute_equity_curve(self.price_df, weight_history_df)
        price_df = self.price_df.copy()
        price_df['equity_curve'] = equity_curve
        price_df = price_df.loc[weight_history_df.index[0]:]
        price_df = price_df/price_df.iloc[0]
        equity_curve = price_df['equity_curve'].values
        return equity_curve
        


    @staticmethod
    def __get_mvo_weights(prices_window:pd.DataFrame):
        mu = expected_returns.mean_historical_return(prices_window)
        cov = risk_models.sample_cov(prices_window)
        ef = EfficientFrontier(mu, cov, weight_bounds=(0, 1))
        try:
            weights = ef.max_sharpe()
        except:
            weights = ef.min_volatility()
        return pd.Series(weights).astype(float)
    
    @staticmethod
    def __get_hrp_weights(prices_window:pd.DataFrame):
        hrp = HRPOpt(prices_window)
        weights = hrp.optimize()
        return pd.Series(weights).astype(float)
