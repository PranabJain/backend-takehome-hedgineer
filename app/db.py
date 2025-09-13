import sqlite3
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple
import datetime as dt

DB_DIR = Path("/codemill/jainpran/dig_2025_test/data")
DB_DIR.mkdir(parents=True, exist_ok=True)


def get_connection(db_path: Optional[str] = None) -> sqlite3.Connection:
    from .config import settings

    path = db_path or settings.database_path
    conn = sqlite3.connect(path, detect_types=sqlite3.PARSE_DECLTYPES)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL;")
    conn.execute("PRAGMA foreign_keys=ON;")
    return conn

def _row_to_dict(row: sqlite3.Row) -> Dict[str, Any]:
    """Convert sqlite3.Row to dict, with date/datetime objects converted to ISO strings."""
    d = dict(row)
    for k, v in d.items():
        if isinstance(v, (dt.date, dt.datetime)):
            d[k] = v.isoformat()
    return d

def init_db(conn: Optional[sqlite3.Connection] = None) -> None:
    close_conn = False
    if conn is None:
        conn = get_connection()
        close_conn = True
    schema_path = Path(__file__).with_name("schema.sql")
    with open(schema_path, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
    if close_conn:
        conn.close()

def execute_many(
    conn: sqlite3.Connection, sql: str, params_seq: Iterable[Tuple[Any, ...]]
) -> None:
    with conn:
        conn.executemany(sql, params_seq)

def execute(conn: sqlite3.Connection, sql: str, params: Tuple[Any, ...] = ()) -> None:
    with conn:
        conn.execute(sql, params)

def query(
    conn: sqlite3.Connection, sql: str, params: Tuple[Any, ...] = ()
) -> List[Dict[str, Any]]:
    cur = conn.execute(sql, params)
    rows = cur.fetchall()
    return [_row_to_dict(r) for r in rows]
