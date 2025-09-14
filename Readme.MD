# Presentation Notes — Technical & Business Explanation

## 📌 Project Summary
We built a backend service to track a **custom equal-weighted stock index** of the **top 100 US stocks by market cap**.  
The index is recalculated daily and can be exported for analysis.

---

## 💡 Why Equal-Weighted?
In a **market cap-weighted index** (e.g., S&P 500), big companies dominate returns.  
An equal-weighted index:
- Gives **every constituent the same weight** (1/100 here).
- Requires **daily rebalancing** because market caps shift.

---

## 🔹 Key Architecture Components

### 1. **FastAPI**
- Modern async Python framework (type hints → API docs automatically).
- High performance — comparable to Node/Go for JSON APIs.

**In our app:**  
Handles `/build-index`, `/index-performance`, etc.  
Returns JSON to frontend or Excel to analysts.

---

### 2. **SQLite/DuckDB**
- Stores prices, market caps, index compositions, and returns.
- Lightweight, portable, perfect for speed.

---

### 3. **Redis**
- In-memory database for caching.
- Reduces response time for repeated queries.
- Example: `/index-performance` cache avoids recalculating SQL for the same period.

---

### 4. **Docker**
- Encapsulates app + dependencies in a container.
- Ensures panelists, devs, and prod environments are identical.
- `docker-compose` runs:
  - API service
  - Redis instance
  - Mounted volume for database

---

## 📈 Data Flow

1. **Ingestion job** (`ingest.py`):
   - Fetches last ~6 months of market data via Yahoo Finance/Synthetic.
   - Populates `daily_prices` and `daily_market_caps`.

2. **Index Building**:
   - For each day in range:
     - Pick top 100 by market cap.
     - Assign equal weight = 1/100.
     - Calculate daily & cumulative returns.
     - Save to DB.

3. **API Access**:
   - GET endpoints → return JSON.
   - POST `/export-data` → generate Excel via Pandas + XlsxWriter.

---

## 📊 Finance Terminology (for non-finance judges)

- **Market Capitalization** = Price × Shares Outstanding.
- **Equal-Weighted Index** = Each stock has same proportional weight.
- **Daily Return** = % change from previous day.
- **Cumulative Return** = Compounded return over the period.
- **Rebalance** = Adjusting portfolio weights back to target.

---

## 🚀 Why This Matters
- Lets analysts compare **performance of equal-weighted strategy** to S&P 500.
- Highlights **mid-cap and smaller large-cap** contributions vs mega-cap dominance.
- Ready to integrate into a dashboard or trading backtest pipeline.

---

## ⚙️ Why These Technologies
**FastAPI** → modern, fast, self-documenting APIs.  
**Docker** → same code runs everywhere without config drift.  
**Redis** → faster repeated queries.  
**SQLite/DuckDB** → easy to set up, no external DB needed.  

---

