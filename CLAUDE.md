# Stock Analysis Dashboard

Streamlit-based stock analysis and options education platform.

## Quick Start

```bash
pip install -r requirements.txt
export ALPHAVANTAGE_API_KEY="your_key"
streamlit run robust_app.py
```

## Architecture

- **Entry point**: `robust_app.py` (multi-page Streamlit app)
- **Pages**: `pages/1_Stock_Analysis.py`, `pages/2_Put_Options.py`
- **Utilities**: `utils.py` (stock data, indicators), `options_utils.py` (options math)
- **Data**: Parquet files in `options_data/` and `data/options/`

## Key APIs

- **yfinance**: Stock price data
- **Alpha Vantage**: Technical indicators (RSI, MACD, Bollinger Bands) - requires API key
- Rate limited to 5 calls/min (free tier)

## Data Format

Options data stored as gzip-compressed Parquet. Load with:
```python
from options_utils import load_amd_puts
df = load_amd_puts(min_date="2023-01-01")
```

## Deployment

AWS EC2 deployment automated via `aws_deploy_streamlit.py`. Uses Nginx reverse proxy with systemd service management.

## Code Patterns

- Technical indicators fetched via `get_rsi()`, `get_macd()`, `get_bollinger_bands()` in utils.py
- Drawdown analysis: `compute_underwater_periods()`, `identify_drawdown_events()`
- Options Greeks estimated with delta-gamma approximation in options_utils.py
- All charts use Plotly for interactivity
