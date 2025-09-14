PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS stocks (
    symbol TEXT PRIMARY KEY,
    name TEXT,
    sector TEXT,
    industry TEXT,
    exchange TEXT
);

CREATE TABLE IF NOT EXISTS daily_prices (
    symbol TEXT NOT NULL,
    date DATE NOT NULL,
    close REAL,
    adj_close REAL,
    volume INTEGER,
    PRIMARY KEY (symbol, date),
    FOREIGN KEY (symbol) REFERENCES stocks(symbol) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS daily_market_caps (
    symbol TEXT NOT NULL,
    date DATE NOT NULL,
    market_cap REAL NOT NULL,
    PRIMARY KEY (symbol, date),
    FOREIGN KEY (symbol) REFERENCES stocks(symbol) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS index_compositions (
    date DATE NOT NULL,
    symbol TEXT NOT NULL,
    weight REAL NOT NULL,
    PRIMARY KEY (date, symbol),
    FOREIGN KEY (symbol) REFERENCES stocks(symbol) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS index_performance (
    date DATE PRIMARY KEY,
    daily_return REAL NOT NULL,
    cumulative_return REAL NOT NULL,
    index_level REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_prices_date ON daily_prices(date);
CREATE INDEX IF NOT EXISTS idx_mcaps_date ON daily_market_caps(date);
CREATE INDEX IF NOT EXISTS idx_compo_date ON index_compositions(date);

