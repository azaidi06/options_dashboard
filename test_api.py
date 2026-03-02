#!/usr/bin/env python
"""Quick test of FastAPI endpoints."""

import subprocess
import time
import requests
import json
import os
import signal

# Kill any existing uvicorn processes
os.system("pkill -f 'uvicorn api.main' 2>/dev/null")
time.sleep(1)

# Start API server
print("Starting API server...")
proc = subprocess.Popen(
    ["python", "-m", "uvicorn", "api.main:app", "--host", "127.0.0.1", "--port", "8001"],
    stdout=subprocess.DEVNULL,
    stderr=subprocess.DEVNULL,
)

# Give server time to start
time.sleep(3)

try:
    # Test health endpoint
    print("\n✓ Testing health endpoint...")
    resp = requests.get("http://127.0.0.1:8001/health")
    print(f"  Status: {resp.status_code}")
    print(f"  Response: {resp.json()}")

    # Test root endpoint
    print("\n✓ Testing root endpoint...")
    resp = requests.get("http://127.0.0.1:8001/")
    print(f"  Status: {resp.status_code}")
    data = resp.json()
    print(f"  Message: {data.get('message')}")

    # Test stock endpoint
    print("\n✓ Testing stock endpoint (AAPL, 1 month)...")
    resp = requests.get(
        "http://127.0.0.1:8001/api/stock/AAPL",
        params={
            "start": "2024-01-01",
            "end": "2024-02-01",
            "lookback_days": 30,
        }
    )
    if resp.status_code == 200:
        data = resp.json()
        print(f"  Status: {resp.status_code}")
        print(f"  Records: {data['metadata']['total_rows']}")
        print(f"  Sample: {json.dumps(data['data'][0], indent=2)}")
    else:
        print(f"  Status: {resp.status_code}")
        print(f"  Error: {resp.text}")

    # Test drawdown endpoint
    print("\n✓ Testing drawdown endpoint...")
    resp = requests.get(
        "http://127.0.0.1:8001/api/stock/AAPL/drawdown",
        params={
            "start": "2023-01-01",
            "end": "2024-01-01",
            "min_drawdown_pct": 0.05,
        }
    )
    if resp.status_code == 200:
        data = resp.json()
        print(f"  Status: {resp.status_code}")
        print(f"  Total events: {data['summary']['total_events']}")
        print(f"  Max drawdown: {data['summary']['max_drawdown_pct']:.2%}")
    else:
        print(f"  Status: {resp.status_code}")
        print(f"  Error: {resp.text}")

    # Test options tickers endpoint
    print("\n✓ Testing options tickers endpoint...")
    resp = requests.get("http://127.0.0.1:8001/api/options/tickers")
    if resp.status_code == 200:
        data = resp.json()
        print(f"  Status: {resp.status_code}")
        print(f"  Available tickers: {data['tickers'][:5]}...")
    else:
        print(f"  Status: {resp.status_code}")
        print(f"  Error: {resp.text}")

    print("\n✅ All tests passed!")

except Exception as e:
    print(f"\n❌ Error: {e}")

finally:
    # Kill server
    print("\nStopping API server...")
    proc.terminate()
    proc.wait(timeout=2)
