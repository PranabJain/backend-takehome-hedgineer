import requests
import time

BASE = "http://localhost:8000"
start_date = "2025-05-12"
end_date = "2025-09-12"

def timed_request(endpoint, params=None):
    """Make a GET request and return (time_ms, status_code, length_of_json)"""
    start = time.perf_counter()
    resp = requests.get(f"{BASE}{endpoint}", params=params)
    elapsed = (time.perf_counter() - start) * 1000  # ms
    try:
        data = resp.json()
    except Exception:
        data = None
    return elapsed, resp.status_code, (len(data) if isinstance(data, list) else None)

# Warm up by building index (ensures data exists in DB)
print("[Warm-up] Building index so data exists in DB...")
requests.post(f"{BASE}/build-index", json={"start_date": start_date, "end_date": end_date})

params = {"start_date": start_date, "end_date": end_date}

print("\n[First request] Expect cache MISS (querying DB)...")
t1, status1, rows1 = timed_request("/index-performance", params)
print(f"Time: {t1:.2f} ms | Status: {status1} | Rows: {rows1}")

print("\n[Second request] Expect cache HIT (served from Redis)...")
t2, status2, rows2 = timed_request("/index-performance", params)
print(f"Time: {t2:.2f} ms | Status: {status2} | Rows: {rows2}")

if rows1 == rows2:
    improvement = ((t1 - t2) / t1) * 100 if t1 > 0 else 0
    print(f"\n✅ Redis caching improved response time by {improvement:.1f}%")
else:
    print("\n⚠️ Row counts differ between requests — caching check inconclusive.")
