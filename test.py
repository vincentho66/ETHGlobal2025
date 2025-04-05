import os
from backend.oneinch.getters import get_available_symbol_df, get_token_historical_prices
print(os.getenv('PYTHONPATH'))
print(os.getenv('ONEINCH_API_KEY'))
print(get_token_historical_prices())