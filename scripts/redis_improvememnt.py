import requests
import time
import redis

BASE = "http://localhost:8000"
start_date = "2025-05-12"
end_date = "2025-09-12"
key = f"perf:{start_date}:{end_date}"

# Connect to Redis (same host as in docker-compose)
r = redis.Redis(host='localhost', port=6379, db=0)
print(f"[Clearing Redis key: {key}]")
r.delete(key)

params = {"start_date": start_date, "end_date": end_date}

def timed_request():
    start = time.perf_counter()
    resp = requests.get(f"{BASE}/index-performance", params=params)
    elapsed = (time.perf_counter() - start) * 1000  # ms
    try:
        data_len = len(resp.json())
    except Exception:
        data_len = None
    return elapsed, data_len

print("\n[First request] Cache MISS (query DB + store in Redis)")
t1, rows1 = timed_request()
print(f"Time: {t1:.2f} ms | Rows: {rows1}")

print("\n[Second request] Cache HIT (fast from Redis)")
t2, rows2 = timed_request()
print(f"Time: {t2:.2f} ms | Rows: {rows2}")

if rows1 == rows2:
    print(f"\n✅ Improvement: {t1 - t2:.2f} ms faster ({(t1 - t2)/t1*100:.1f}%)")
else:
    print("\n⚠️ Row counts differ — caching test invalid")
