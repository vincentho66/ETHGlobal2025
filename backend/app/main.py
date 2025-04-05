from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from typing import Literal, List, Optional
import pandas as pd
import os
import json
import base64

import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.ticker as mticker
from matplotlib.patches import Rectangle
import matplotlib
matplotlib.use('Agg')

from pydantic import BaseModel
from io import StringIO, BytesIO
from backend.oneinch.getters import get_token_historical_prices
from backend.backtest.pfopt import PfOptBacktest, _compute_performance_metrics

from langchain_openai import OpenAI, ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from langchain_core.documents import Document
from langchain_core.runnables import RunnableLambda

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

#####################################################################################
#####################################################################################
#####################       backtest framework          #############################
#####################################################################################
#####################################################################################


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

def base64_to_link(image_base64):
    return f"data:image/png;base64,{image_base64}"

def generate_candlestick_base64(json_data: str) -> str:
    # Step 1: Parse JSON string
    ohlc_list = json.loads(json_data)
    df = pd.DataFrame(ohlc_list)
    df['time'] = pd.to_datetime(df['time'], unit='ms')

    # Step 2: Plot using matplotlib
    fig, ax = plt.subplots(figsize=(10, 5))
    
    for idx, row in df.iterrows():
        color = 'green' if row['close'] >= row['open'] else 'red'
        ax.add_patch(Rectangle(
            (mdates.date2num(row['time']) - 0.2, min(row['open'], row['close'])),
            0.4,
            abs(row['close'] - row['open']),
            color=color
        ))
        ax.vlines(mdates.date2num(row['time']),
                  row['low'], row['high'],
                  color=color, linewidth=1)

    # Step 3: Format X-axis as dates
    ax.xaxis_date()
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax.xaxis.set_major_locator(mticker.MaxNLocator(10))
    fig.autofmt_xdate()

    ax.set_ylabel('Price')

    # Step 4: Convert to base64
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()

    return image_base64

def generate_multiline_chart_base64(json_data: str) -> str:
    data = json.loads(json_data)
    df = pd.DataFrame(data)
    df['time'] = pd.to_datetime(df['time'], unit='ms')
    df.set_index('time', inplace=True)

    fig, ax = plt.subplots(figsize=(10, 5))

    gray_palette = ['#666666', '#888888', '#AAAAAA', '#BBBBBB']
    for idx, column in enumerate(df.columns):
        color = gray_palette[idx % len(gray_palette)]
        ax.plot(df.index, df[column], label=column, color=color)

    ax.set_ylabel("Price")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    ax.legend()

    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return image_base64

def generate_price_and_equity_chart_base64(
    token_json_data: str,
    equity_curve: list[float],
    equity_timestamps: list[int]
) -> str:
    # Token prices
    token_data = json.loads(token_json_data)
    df_token = pd.DataFrame(token_data)
    df_token['time'] = pd.to_datetime(df_token['time'], unit='ms')
    df_token.set_index('time', inplace=True)

    # Equity curve (shorter)
    df_equity = pd.DataFrame({
        'time': pd.to_datetime(equity_timestamps, unit='ms'),
        'equity': equity_curve
    }).set_index('time')

    # Plot
    fig, ax = plt.subplots(figsize=(10, 5))
    gray_palette = ['#666666', '#888888', '#AAAAAA', '#BBBBBB']

    # Plot token lines
    for idx, column in enumerate(df_token.columns):
        color = gray_palette[idx % len(gray_palette)]
        ax.plot(df_token.index, df_token[column], label=column, color=color, linewidth=2)

    # Plot equity curve (may start later)
    ax.plot(df_equity.index, df_equity['equity'],
            label='Equity Curve',
            color='skyblue',
            linewidth=3)

    # Format chart
    ax.set_ylabel("Price")
    ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    fig.autofmt_xdate()
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.3)

    # Export to base64
    buf = BytesIO()
    plt.tight_layout()
    plt.savefig(buf, format='png')
    plt.close(fig)
    buf.seek(0)

    image_base64 = base64.b64encode(buf.read()).decode('utf-8')
    buf.close()
    return image_base64

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
        image_base64 = generate_candlestick_base64(json_data)
        return base64_to_link(image_base64)
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
        json_data = df.to_json(orient="records")
        image_base64 = generate_multiline_chart_base64(json_data)
        return base64_to_link(image_base64)
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
        df = get_price_df(symbols, period, limit)
        df.iloc[:,1:] = df.iloc[:,1:]/df.iloc[0,1:]
        json_data = df.to_json(orient="records")

        price_df = df.set_index('time')
        bt = PfOptBacktest(price_df,lookback, rebalance)
        equity_curve = bt.run(algorithm)
        time = price_df.index.to_list()[-len(equity_curve):]
        print(len(equity_curve), len(time))
        performance = _compute_performance_metrics(equity_curve, time)

        image_base64 = generate_price_and_equity_chart_base64(json_data, equity_curve.tolist(), time)

        return {"img_link": base64_to_link(image_base64), **performance}
    except Exception as e:
        return {"symbol":symbols, "period": period, "limit": limit, "lookback":lookback, "rebalance":rebalance, "error": str(e)}

######################################################################
######################################################################
####################          survey          ########################
######################################################################
######################################################################

def initialize_user_profile():
    fn = "backend/LLM_config/user.json"
    if os.path.exists(fn):
        os.remove(fn)

initialize_user_profile()


@app.get("/survey")
async def get_survey():
    with open("backend/LLM_config/survey.json") as f:
        return json.load(f)

class SurveySubmission(BaseModel):
    risk_level: Literal[
        "I'd panic and sell everything",
        "I'd be worried but wait it out",
        "I'd stay calm and maybe buy more"
    ]
    horizon: Literal[
        "A few weeks",
        "A few months",
        "A few years",
        "Long-term (even pass down to kids)"
    ]
    themes: List[
        Literal["eth", "defi", "stablecoin", "l2", "rwa", "meme", "any"]
    ]
    exclusions: Optional[List[
        Literal["volatile", "meme", "illiquid", "manual"]
    ]] = []
    experience: Literal[
        "I'm new",
        "I've dabbled",
        "I'm a pro"
    ]
    notes: Optional[str] = ""

@app.post("/submit_survey")
async def submit_survey(submission: SurveySubmission):

    path = "backend/LLM_config/user.json"
    with open(path, "w") as f:
        json.dump(submission.model_dump(), f, indent=2)
    return {"status": "ok"}

def read_user_info(file_path:str) -> str:
    if not os.path.exists(file_path):
        return ""
    with open(file_path, "r") as f:
        profile = json.load(f)

    formatted = []
    for key, value in profile.items():
        if isinstance(value, list):
            val_str = ", ".join(value)
        else:
            val_str = value
        formatted.append(f"- {key.replace('_', ' ').title()}: {val_str}")

    return "\n".join(formatted)

######################################################################
######################################################################
######################           LLM          ########################
######################################################################
######################################################################


llm = ChatOpenAI(model="gpt-4o", api_key=os.getenv("OPENAI_API_KEY"))

def build_qa_chain(llm):
    q_system_prompt = """You are a portfolio assistant integrated with 1inch Fusion+ and other crypto tools. Your job is to help users build and manage token portfolios. You can:
- Help select tokens for an asset pool
- Explain token properties, use cases, or fundamentals
- Recommend allocation algorithms like equal weight, HRP, mean-variance, etc.
- Run backtests (or suggest them)
- Guide the user to deploy a tradebot

Currently, you support the following portfolio allocation algorithms:
- Mean-Variance Optimization (MVO)
- Hierarchical Risk Parity (HRP)

Suggest helpful questions and guide the user if they’re unsure. Ask clarifying questions when needed. Be friendly, concise, and beginner-friendly.

here are the user info: 
{user_info}

{context}
"""
    qa_prompt = ChatPromptTemplate.from_messages(
        [
            ("system", q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human","{input}")
        ]
    )
    qa_chain = create_stuff_documents_chain(llm, qa_prompt)
    wrapped_chain = qa_chain | RunnableLambda(lambda x: {"answer": x})

    return wrapped_chain

available_symbols = [
    Document(page_content=str(pd.read_csv('backend/oneinch/available_symbol.csv')['symbol'].to_list()))
]

store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

qa_chain = build_qa_chain(llm)
conversation_chain = RunnableWithMessageHistory(
    qa_chain,
    get_session_history,
    input_messages_key="input",
    history_messages_key="chat_history",
    output_messages_key="answer"
)

@app.post("/chat")
async def post_chat(user_input: str):

    user_info = read_user_info('backend/LLM_config/user.json')

    response = conversation_chain.invoke(
        {"input": user_input, "user_info": user_info, "context": available_symbols},
        config={"configurable": {"session_id": "default"}}
    )
    print(store)
    return response