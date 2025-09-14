# 📈 Equal-Weighted Top-100 US Stocks Index Backend

## 📌 Project Summary
A backend service that tracks a **custom equal-weighted stock index** of the top 100 US stocks by daily market capitalisation.

- Selects the **top 100 stocks by market cap** each trading day  
- Assigns **equal weights (1/100 each)**  
- Calculates **daily and cumulative returns**  
- Updates daily and stores results in a database  
- Exports data in **JSON** or well-formatted **Excel**  

---

## 💡 Why Equal-Weighted?
- Market cap-weighted indexes (e.g., S&P 500) are dominated by mega-caps  
- Equal-weighting gives **each stock the same influence**  
- Increases exposure to **mid-cap companies**  
- Requires **daily rebalancing** as market caps change  

---

## 🔹 Tech Stack
- **FastAPI** — API framework  
- **SQLite / DuckDB** — persistent storage  
- **Redis** — in-memory cache to speed up repeated queries  
- **Docker + docker-compose** — containerisation for consistent setup  
- **Pandas / Polars** — data manipulation  
- **Yahoo Finance API / Synthetic data generator** — price & market cap source  
- **XlsxWriter / OpenPyXL** — Excel export  

---

## 🛠 Setup Instructions

### Docker Setup
```bash
# Clone the repo
git clone <repo_url>
cd <repo_name>

# Create virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Copy environment variables
cp .env.example .env

Docker Setup
# Build API image fresh
docker compose build --no-cache api

# Start API + Redis
docker compose up -d

# Run ingestion inside container
docker compose run --rm api python ingest.py
```bash

📥 Data Acquisition Job

Before using the index endpoints, load market data:
docker compose run --rm api python ingest.py

📡 API Usage
```bash

1. Build Index
curl -X POST "http://localhost:8000/build-index" \
-H "Content-Type: application/json" \
-d '{"start_date":"2025-05-12","end_date":"2025-09-12"}'

2. Get Index Performance
curl "http://localhost:8000/index-performance?start_date=2025-05-12&end_date=2025-09-12"

3. Get Composition for a Date
curl "http://localhost:8000/index-composition?date=2025-09-12"

4. Get Composition Changes
curl "http://localhost:8000/composition-changes?start_date=2025-05-12&end_date=2025-09-12"

5. Export Data (Excel)
curl -X POST "http://localhost:8000/export-data" \
-H "Content-Type: application/json" \
-d '{"start_date":"2025-05-12","end_date":"2025-09-12"}' \
--output index_export.xlsx

🗄 Database Schema
stocks

symbol (TEXT) — Stock ticker

name (TEXT) — Company name

sector (TEXT) — Sector classification

industry (TEXT) — Industry classification

exchange (TEXT) — Exchange

daily_prices

(symbol, date) — Primary key

close (REAL)

adj_close (REAL)

volume (INTEGER)

daily_market_caps

(symbol, date) — Primary key

market_cap (REAL)

index_compositions

(date, symbol) — Primary key

weight (REAL)

index_performance

(date) — Primary key

daily_return (REAL)

cumulative_return (REAL)

index_level (REAL)

📊 Finance Terms

Market Capitalisation = Price × Shares Outstanding

Equal-Weighted Index = All constituents get equal weight

Daily Return = % change from previous day

Cumulative Return = Compounded performance

Rebalance = Adjusting holdings to target weights


