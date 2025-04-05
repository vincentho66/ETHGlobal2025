from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from typing import Literal, List, Optional
import pandas as pd
import os
import json
from pydantic import BaseModel
from io import StringIO
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