# Options Dashboard

FastAPI + React stock analysis and options education platform.

## Quick Start

Backend (FastAPI):

```bash
pip install -r requirements.txt
export ALPHAVANTAGE_API_KEY="your_key"
python -m uvicorn api.main:app --port 8000 --reload
```

Frontend (Vite + React):

```bash
cd frontend
npm install
npm run dev          # serves on http://localhost:5173 (or next free port)
```

## Architecture

- **Backend**: `api/main.py` (FastAPI app), `api/routes/{stock,options}.py`,
  `api/services/{analytics,options}.py` (service layer wrapping `utils.py` + `options_utils.py`).
- **Frontend**: `frontend/` (React + Vite + Recharts + SWR + Tailwind v4).
  Routes: `/`, `/learn`, `/stock`, `/options`.
- **Utilities**: `utils.py` (stock data, indicators), `options_utils.py` (options math).
- **Data**: Parquet files in `options_data/` (per-ticker option chains) and `data/options/`.

## Key APIs

- **yfinance**: Stock price data
- **Alpha Vantage**: Technical indicators (RSI, MACD, Bollinger Bands) — requires API key (5 calls/min on the free tier)

## Data Format

Options data stored as gzip-compressed Parquet. Load with:

```python
from options_utils import load_amd_puts
df = load_amd_puts(min_date="2023-01-01")
```

## Deployment

AWS EC2: backend served by `options-dashboard-api.service`, fronted by Nginx
(`nginx.conf`, `options-dashboard-nginx.service`). Frontend builds via
`vite build` and is served as static assets via the same Nginx config.

## Code Patterns

- Technical indicators fetched via `get_rsi()`, `get_macd()`, `get_bollinger_bands()` in `utils.py`
- Drawdown analysis: `compute_underwater_periods()`, `identify_drawdown_events()`
- Options Greeks estimated with delta-gamma approximation in `options_utils.py`
- Frontend charts use Recharts; numeric formatters live at `frontend/src/utils/formatters.js`
