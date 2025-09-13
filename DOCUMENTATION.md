## Business and Financial Concepts Guide

This guide explains the key ideas behind the project in plain terms.

### 1) What is an Index?
An index is a basket of stocks that represents some part of the market. We track the value of the basket over time. Here we build a custom index of the top 100 US stocks by market capitalization (size), and we give each stock equal weight (1/100 of the index).

### 2) Equal Weighting vs Market Cap Weighting
- Market cap weighting gives bigger companies more weight. If a company is twice the size, it gets twice the weight.
- Equal weighting gives every stock the same weight. This increases exposure to mid-sized names and requires regular rebalancing to keep weights equal.

### 3) Daily Top-100 Selection by Market Cap
Each trading day, we pick the top 100 stocks by market capitalization from a large-cap universe (S&P 500-like). Market cap is price × shares outstanding. If shares outstanding are not available, we use a proxy (average dollar volume) to rank stocks.

### 4) Rebalancing and Weights
On each day, we assign equal notional weights to the selected 100 stocks. For example, each stock gets weight 1/100 = 1%. This is a simple reconstitution-and-rebalance model that ensures the basket remains equal-weighted day by day.

### 5) Returns and Index Level
- A stock’s daily return is: (Price_today − Price_prev) / Price_prev.
- The index’s daily return is the weighted average of the constituents’ daily returns. Since weights are equal, it’s the simple average across 100 stocks.
- We chain daily returns to get an index level. If the base level is 100.0, and the daily return is r, the new level is: previous_level × (1 + r).

### 6) Composition Changes
Because top 100 by market cap can change, we track which stocks enter or exit compared to the previous trading day. This helps understand turnover and drivers.

### 7) Data Sources
- yfinance (Yahoo Finance) provides historical prices; shares outstanding and metadata require per-ticker calls and may rate-limit.
- Wikipedia S&P 500 provides a practical large-cap universe. For reliability, we also allow a CSV universe input and Stooq/synthetic price fallbacks.

### 8) Practical Considerations
- Corporate actions (splits, dividends) matter. We use adjusted prices to mitigate splits and cash dividends.
- Survivorship bias: Using a current S&P 500 list for past periods can bias results. A production system would use point-in-time constituents.
- Transaction costs and constraints: Real portfolios incur costs; equal-weight rebalancing is idealized here.

### 9) API Summary (Plain English)
- Build Index: “Select top 100 by size, give equal weights, compute day’s return and update the index.”
- Performance: “Show the daily and cumulative growth of the index.”
- Composition: “Show which 100 stocks were in the index on a given day.”
- Changes: “Show which stocks swapped in or out compared to the prior trading day.”
- Export: “Give me an Excel with performance, compositions, and changes so I can share.”

### 10) How to Present This in a Hackathon
- Start with the story: “We built an index that rebalances daily to the top 100 by size, but we give each stock equal representation.”
- Emphasize data engineering: robust ingestion with fallbacks, SQL-first modeling, and clean APIs.
- Show the Excel export and the composition changes to demonstrate practical insights.


