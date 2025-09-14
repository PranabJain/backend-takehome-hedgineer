import requests

BASE = "http://localhost:8000"
start_date = "2025-01-12"
end_date = "2025-09-12"

# Build Index
print("\n[1] Build Index:")
print(requests.post(f"{BASE}/build-index", json={"start_date": start_date, "end_date": end_date}).json())

# Performance
print("\n[2] Performance sample:")
perf = requests.get(f"{BASE}/index-performance", params={"start_date": start_date, "end_date": end_date}).json()
print(len(perf), "rows")
print(perf[:3])

# Composition
print("\n[3] Composition sample for last day:")
comp = requests.get(f"{BASE}/index-composition", params={"date": end_date}).json()
print(len(comp), "rows")
print(comp[:5])

# Changes
print("\n[4] Composition changes sample:")
changes = requests.get(f"{BASE}/composition-changes", params={"start_date": start_date, "end_date": end_date}).json()
print(len(changes), "change days")
print(changes[:3])

# Export
print("\n[5] Export Excel:")
export_resp = requests.post(f"{BASE}/export-data", json={"start_date": start_date, "end_date": end_date})
if export_resp.status_code == 200:
    with open("index_export.xlsx", "wb") as f:
        f.write(export_resp.content)
    print("Excel saved as index_export.xlsx")
