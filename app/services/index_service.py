from __future__ import annotations

import datetime as dt
from typing import Any, Dict, List, Optional, Union

from ..db import get_connection, execute_many, query
from ..config import settings


def _normalize_date(d: Union[str, dt.date, None]) -> Optional[str]:
    if d is None:
        return None
    if isinstance(d, dt.date):
        return d.isoformat()
    if isinstance(d, str):
        return d
    raise ValueError(f"Unsupported date type: {type(d)}")


def safe_parse_date(val):
    """Return a datetime.date from either a string or datetime.date."""
    if isinstance(val, dt.date):
        return val
    if isinstance(val, str):
        return dt.date.fromisoformat(val)
    raise ValueError(f"Unsupported date format: {type(val)}")


def build_index(start_date: Union[str, dt.date],
                end_date: Optional[Union[str, dt.date]] = None) -> Dict[str, Any]:
    start_date_str = _normalize_date(start_date)
    end_date_str = _normalize_date(end_date) or start_date_str

    conn = get_connection()

    dates_rows = query(
        conn,
        """
        SELECT DISTINCT date
        FROM daily_market_caps
        WHERE date BETWEEN ? AND ?
        ORDER BY date
        """,
        (start_date_str, end_date_str),
    )

    # Fix: parse safely to handle both str and date from DB
    trading_dates = [safe_parse_date(r["date"]) for r in dates_rows]

    if not trading_dates:
        conn.close()
        return {"status": "error", "message": "No trading days in range"}

    compositions: List[tuple] = []
    perf_rows: List[tuple] = []

    index_level = settings.index_base_level
    cumulative_return = 0.0

    for current_date in trading_dates:
        top_rows = query(
            conn,
            """
            SELECT symbol, market_cap
            FROM daily_market_caps
            WHERE date = ?
            ORDER BY market_cap DESC
            LIMIT 100
            """,
            (current_date.isoformat(),),
        )

        if not top_rows:
            continue

        weight = 1.0 / len(top_rows)

        for r in top_rows:
            compositions.append((current_date.isoformat(), r["symbol"], weight))

        if perf_rows:
            prev_date = perf_rows[-1][0]
            prev_symbols = {sym for d, sym, _ in compositions if d == prev_date}
            curr_symbols = {sym for sym, _ in [(r["symbol"], r["market_cap"]) for r in top_rows]}

            common_syms = prev_symbols & curr_symbols
            if common_syms:
                returns = []
                for sym in common_syms:
                    prices = query(
                        conn,
                        """
                        SELECT adj_close
                        FROM daily_prices
                        WHERE symbol = ? AND date IN (?, ?)
                        ORDER BY date
                        """,
                        (sym, prev_date, current_date.isoformat()),
                    )
                    if len(prices) == 2 and prices[0]["adj_close"] and prices[1]["adj_close"]:
                        ret = (prices[1]["adj_close"] / prices[0]["adj_close"]) - 1.0
                        returns.append(ret)
                daily_return = sum(returns) / len(returns) if returns else 0.0
            else:
                daily_return = 0.0
        else:
            daily_return = 0.0

        index_level *= (1 + daily_return)
        cumulative_return = (index_level / settings.index_base_level) - 1.0

        perf_rows.append((current_date.isoformat(), daily_return, cumulative_return, index_level))

    execute_many(
        conn,
        "INSERT OR REPLACE INTO index_compositions(date, symbol, weight) VALUES(?, ?, ?)",
        compositions
    )
    execute_many(
        conn,
        "INSERT OR REPLACE INTO index_performance(date, daily_return, cumulative_return, index_level) VALUES(?, ?, ?, ?)",
        perf_rows
    )

    conn.close()

    return {
        "status": "success",
        "start": start_date_str,
        "end": end_date_str,
        "days_processed": len(trading_dates),
        "message": "Index built and stored"
    }


def get_index_performance(start_date: Union[str, dt.date],
                          end_date: Optional[Union[str, dt.date]] = None) -> List[Dict[str, Any]]:
    start_date_str = _normalize_date(start_date)
    end_date_str = _normalize_date(end_date) or start_date_str

    conn = get_connection()
    rows = query(
        conn,
        """
        SELECT *
        FROM index_performance
        WHERE date BETWEEN ? AND ?
        ORDER BY date
        """,
        (start_date_str, end_date_str),
    )
    conn.close()
    return rows


def get_index_composition(date: Union[str, dt.date]) -> List[Dict[str, Any]]:
    date_str = _normalize_date(date)
    conn = get_connection()
    rows = query(
        conn,
        """
        SELECT symbol, weight
        FROM index_compositions
        WHERE date = ?
        ORDER BY symbol
        """,
        (date_str,),
    )
    conn.close()
    return rows


def get_composition_changes(start_date: Union[str, dt.date],
                            end_date: Union[str, dt.date]) -> List[Dict[str, Any]]:
    start_date_str = _normalize_date(start_date)
    end_date_str = _normalize_date(end_date)

    conn = get_connection()
    dates_rows = query(
        conn,
        """
        SELECT DISTINCT date
        FROM index_compositions
        WHERE date BETWEEN ? AND ?
        ORDER BY date
        """,
        (start_date_str, end_date_str),
    )
    dates = [r["date"] for r in dates_rows]

    changes: List[Dict[str, Any]] = []
    prev_symbols: Optional[set] = None

    for d in dates:
        rows = query(
            conn,
            "SELECT symbol FROM index_compositions WHERE date = ? ORDER BY symbol",
            (d,),
        )
        symbols = {r["symbol"] for r in rows}

        if prev_symbols is not None:
            entered = sorted(list(symbols - prev_symbols))
            exited = sorted(list(prev_symbols - symbols))
            if entered or exited:
                changes.append({
                    "date": d,
                    "entered": entered,
                    "exited": exited
                })

        prev_symbols = symbols

    conn.close()
    return changes
