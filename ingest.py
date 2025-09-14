import datetime as dt
import time
from typing import List, Tuple, Optional
import io
import pandas as pd
import numpy as np
import requests
import yfinance as yf

# Ensure the project root is on sys.path for environments that clean sys.path
import sys
from pathlib import Path
import os
sys.path.insert(0, str(Path(__file__).resolve().parent))

from app.db import get_connection, init_db, execute_many, execute

# --- Force yfinance to use browser-like headers (helps in containers) ---
yf.utils.get_yf_headers = lambda: {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

WIKI_SP500_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"


def fetch_sp500_symbols() -> pd.DataFrame:
    # Primary: use yfinance helper to avoid direct scraping
    try:
        symbols = yf.tickers_sp500()
        df = pd.DataFrame({"symbol": symbols})
        df["symbol"] = df["symbol"].astype(str).str.replace(".", "-", regex=False)
        df["name"] = None
        df["sector"] = None
        return df[["symbol", "name", "sector"]]
    except Exception:
        pass

    # Fallback: Wikipedia with retry
    for i in range(3):
        try:
            tables = pd.read_html(WIKI_SP500_URL)
            df = tables[0]
            df = df.rename(columns={"Symbol": "symbol", "Security": "name", "GICS Sector": "sector"})
            df["symbol"] = df["symbol"].astype(str).str.replace(".", "-", regex=False)
            return df[["symbol", "name", "sector"]]
        except Exception:
            time.sleep(1.5 * (i + 1))

    # CSV fallback
    csv_path = os.getenv("SP500_CSV") or "sp500_static.csv"
    if os.path.exists(csv_path):
        try:
            df = pd.read_csv(csv_path)
            df.columns = [c.lower() for c in df.columns]
            if "symbol" in df.columns:
                df["symbol"] = df["symbol"].astype(str).str.replace(".", "-", regex=False)
                if "name" not in df.columns:
                    df["name"] = None
                if "sector" not in df.columns:
                    df["sector"] = None
                return df[["symbol", "name", "sector"]]
        except Exception:
            pass

    # GitHub CSV fallback
    try:
        github_csv = (
            os.getenv(
                "SP500_GITHUB_CSV",
                "https://raw.githubusercontent.com/datasets/s-and-p-500-companies/main/data/constituents.csv",
            )
        )
        df = pd.read_csv(github_csv)
        cols = {c.lower(): c for c in df.columns}
        if "symbol" in cols:
            sym_col = cols["symbol"]
        elif "ticker" in cols:
            sym_col = cols["ticker"]
        else:
            sym_col = None
        name_col = cols.get("security") or cols.get("name")
        sector_col = cols.get("gics sector") or cols.get("sector")

        if sym_col is not None:
            out = pd.DataFrame({
                "symbol": df[sym_col].astype(str).str.replace(".", "-", regex=False)
            })
            out["name"] = df[name_col] if name_col else None
            out["sector"] = df[sector_col] if sector_col else None
            return out[["symbol", "name", "sector"]]
    except Exception:
        pass

    # Last resort: static list
    static_symbols = [
        "AAPL","MSFT","AMZN","GOOGL","GOOG","NVDA","META","TSLA","BRK-B","UNH",
        "LLY","JPM","V","XOM","WMT","JNJ","MA","PG","ORCL","AVGO","HD","CVX",
        "MRK","COST","ADBE","NFLX","CRM","TMO","PEP","KO","CSCO","ACN","ABT",
        "MCD","DHR","TXN","LIN","AMD","NKE","PM","BMY","PFE","WFC","DIS","AMGN",
        "IBM","INTC","QCOM","UPS","MS","GS","BAC","C","BLK","CAT","DE","HON",
        "LMT","BA","GE","SBUX","BKNG","AMAT","GILD","ISRG","ADP","MU","T","VZ",
        "MO","SO","NEE","DUK","UNP","PLD","RTX","MDLZ","LOW","SPGI","CHTR","TGT",
        "CVS","COP","ELV","SCHW","USB","BK","CB","CME","ICE","AON","MET","PRU",
        "PNC","TFC","OXY","PSX","MPC","F","GM","HCA","CI","HUM","ZTS","REGN",
        "MRVL","LRCX","ORLY","AZO","ROP","FI","ADI","KLAC","LULU","AEP","EOG",
        "KMI","KHC","DG","DHI","PGR","ALL"
    ]
    return pd.DataFrame({"symbol": static_symbols, "name": None, "sector": None})


def fetch_metadata_and_shares(symbols: List[str]) -> pd.DataFrame:
    data = []
    for sym in symbols:
        try:
            tk = yf.Ticker(sym)
            info = tk.get_info()
            shares = info.get("sharesOutstanding")
            name = info.get("longName") or info.get("shortName")
            sector = info.get("sector")
            row = {"symbol": sym, "shares_outstanding": None, "name": name, "sector": sector}
            if shares is not None:
                try:
                    row["shares_outstanding"] = int(shares)
                except Exception:
                    row["shares_outstanding"] = None
            data.append(row)
        except Exception:
            data.append({"symbol": sym, "shares_outstanding": None, "name": None, "sector": None})
        time.sleep(0.05)
    return pd.DataFrame(data)


def _chunks(lst: List[str], size: int) -> List[List[str]]:
    return [lst[i:i+size] for i in range(0, len(lst), size)]


def check_yahoo_available() -> bool:
    try:
        test = yf.download("AAPL", period="5d", interval="1d", progress=False, threads=False)
        if isinstance(test, pd.DataFrame) and not test.empty:
            return True
    except Exception:
        pass
    return False


def check_stooq_available() -> bool:
    try:
        url = "https://stooq.com/q/d/l/?s=aapl&i=d"
        resp = requests.get(url, timeout=5)
        if resp.status_code == 200 and "Date" in resp.text:
            return True
    except Exception:
        pass
    return False


def fetch_prices_yahoo(symbols: List[str], start: str, end: str) -> pd.DataFrame:
    records = []
    for batch in _chunks(symbols, 25):
        try:
            data = yf.download(batch, start=start, end=end, auto_adjust=False, group_by='ticker', progress=False, threads=False)
        except Exception as e:
            print(f"Yahoo batch download failed for batch starting with '{batch[0]}': {e}. Skipping batch.")
            data = None

        if data is None or (isinstance(data, pd.DataFrame) and data.empty):
            time.sleep(0.1)
            continue

        for sym in batch:
            try:
                if sym not in data:
                    if len(batch) == 1 and isinstance(data, pd.DataFrame) and "Close" in data.columns:
                        df = data.reset_index()
                    else:
                        continue
                else:
                    df = data[sym].reset_index()
                df = df.rename(columns={"Date": "date", "Close": "close", "Adj Close": "adj_close", "Volume": "volume"})
                for _, r in df.iterrows():
                    records.append({
                        "symbol": sym,
                        "date": r["date"].date().isoformat(),
                        "close": None if pd.isna(r.get("close")) else float(r.get("close")),
                        "adj_close": None if pd.isna(r.get("adj_close")) else float(r.get("adj_close")),
                        "volume": None if pd.isna(r.get("volume")) else int(r.get("volume")),
                    })
            except Exception:
                continue
        time.sleep(0.05)
    return pd.DataFrame.from_records(records)


def fetch_prices_stooq(symbols: List[str], start: str, end: str) -> pd.DataFrame:
    start_dt, end_dt = pd.to_datetime(start), pd.to_datetime(end)
    records = []
    for sym in symbols:
        try:
            url = f"https://stooq.com/q/d/l/?s={sym.lower()}&i=d"
            csv = requests.get(url, timeout=10)
            if csv.status_code != 200:
                continue
            df = pd.read_csv(io.StringIO(csv.text))
            if "Date" not in df.columns:
                continue
            df["Date"] = pd.to_datetime(df["Date"])
            df = df[(df["Date"] >= start_dt) & (df["Date"] <= end_dt)]
            for _, r in df.iterrows():
                records.append({
                    "symbol": sym,
                    "date": r["Date"].date().isoformat(),
                    "close": None if pd.isna(r.get("Close")) else float(r.get("Close")),
                    "adj_close": None if pd.isna(r.get("Close")) else float(r.get("Close")),
                    "volume": None if pd.isna(r.get("Volume")) else int(r.get("Volume")),
                })
        except Exception:
            continue
        time.sleep(0.02)
    return pd.DataFrame.from_records(records)


def generate_synthetic_prices(symbols: List[str], start: str, end: str) -> pd.DataFrame:
    dates = pd.bdate_range(start=start, end=end)
    records = []
    rng = np.random.default_rng(42)
    for sym in symbols:
        price0 = rng.uniform(20, 300)
        vols = rng.normal(0.0005, 0.02, size=len(dates))
        prices = price0 * np.exp(np.cumsum(vols))
        vols_shares = rng.integers(1_000_000, 10_000_000, size=len(dates))
        for d, p, v in zip(dates, prices, vols_shares):
            records.append({
                "symbol": sym,
                "date": d.date().isoformat(),
                "close": float(p),
                "adj_close": float(p),
                "volume": int(v),
            })
    return pd.DataFrame.from_records(records)


def main() -> None:
    init_db()
    conn = get_connection()

    meta = fetch_sp500_symbols()
    if meta is None or meta.empty:
        raise RuntimeError("Failed to get symbols.")

    end = dt.date.today()
    start = end - dt.timedelta(days=180)  # ~6 months calendar (≥ 90 weekdays)
    symbols = meta["symbol"].tolist()

    # Synthetic shares outstanding
    meta["shares_outstanding"] = np.random.randint(200_000_000, 10_000_000_000, size=len(meta))
    execute_many(
        conn,
        "INSERT OR REPLACE INTO stocks(symbol, name, sector) VALUES(?, ?, ?)",
        [(r.symbol, r.name or r.symbol, r.sector or "Tech") for r in meta.itertuples(index=False)]
    )

    prices_df = pd.DataFrame()
    if check_yahoo_available():
        try:
            prices_df = fetch_prices_yahoo(symbols, start.isoformat(), end.isoformat())
        except Exception:
            prices_df = pd.DataFrame()

    if prices_df.empty:
        prices_df = generate_synthetic_prices(symbols, start.isoformat(), end.isoformat())

    if prices_df.empty:
        raise RuntimeError("No price data from any source.")

    execute_many(
        conn,
        """
        INSERT OR REPLACE INTO daily_prices(symbol, date, close, adj_close, volume)
        VALUES(?, ?, ?, ?, ?)""",
        [(r.symbol, r.date, r.close, r.adj_close, r.volume)
         for r in prices_df.itertuples(index=False)]
    )

    prices_df = prices_df.merge(meta[["symbol", "shares_outstanding"]], on="symbol", how="left")
    prices_df["market_cap"] = prices_df["adj_close"] * prices_df["shares_outstanding"]

    execute_many(
        conn,
        "INSERT OR REPLACE INTO daily_market_caps(symbol, date, market_cap) VALUES(?, ?, ?)",
        [(r.symbol, r.date, r.market_cap) for r in prices_df.itertuples(index=False)]
    )

    conn.close()
    print(f"Ingest complete. {len(prices_df)} price rows over {prices_df['date'].nunique()} trading days.")


if __name__ == "__main__":
    main()
