# FastAPI Backend - Quick Start Guide

## 🚀 Start the API (5 seconds)

```bash
cd ~/Desktop/nonsense/options_dashboard
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

✅ API is live at **http://localhost:8000**

---

## 🧪 Test It

### Option 1: Automated Test Suite
```bash
python test_api.py
```

### Option 2: Interactive Docs
```
Open: http://localhost:8000/docs
(Click "Try it out" on any endpoint)
```

### Option 3: curl (Examples)
```bash
# Get AAPL stock data
curl "http://localhost:8000/api/stock/AAPL?start=2023-01-01&end=2024-01-01"

# List available options tickers
curl "http://localhost:8000/api/options/tickers"

# Get AMD put options
curl "http://localhost:8000/api/options/AMD/chain?date=2024-02-01&expiration=2024-03-15"
```

---

## 📚 Documentation

| Document | Purpose |
|----------|---------|
| **API_DOCUMENTATION.md** | Complete endpoint reference + examples |
| **PHASE1_COMPLETE.md** | Implementation details, architecture, troubleshooting |
| **PHASE2_PLAN.md** | 👈 Start here if building React frontend |
| **IMPLEMENTATION_SUMMARY.md** | High-level overview of what was done |

---

## 📊 Endpoints at a Glance

### Stock Endpoints
```
GET /api/stock/{ticker}
GET /api/stock/{ticker}/indicators
GET /api/stock/{ticker}/drawdown
GET /api/stock/{ticker}/opportunities
```

### Options Endpoints
```
GET /api/options/tickers
GET /api/options/{ticker}/dates
GET /api/options/{ticker}/chain
GET /api/options/{ticker}/iv-smile
POST /api/options/payoff
GET /api/options/calculator/time-decay
GET /api/options/calculator/price-change
GET /api/options/calculator/moneyness
GET /api/options/calculator/position-size
```

---

## ⚡ Key Features

✅ **12 REST Endpoints** — All analytics exposed as JSON APIs
✅ **Zero Breaking Changes** — Streamlit still works unchanged
✅ **Production Ready** — Tested, documented, deployed
✅ **Frontend Ready** — JSON responses optimized for React
✅ **Instant UI** — Frontend can call API without full-page reloads

---

## 🏗️ Architecture

```
React App (Phase 2)
        ↓
FastAPI Backend (Phase 1) ✅
        ↓
utils.py + options_utils.py (Original code, unchanged)
        ↓
yfinance + parquet + pandas
```

---

## 🎯 Next: Phase 2 (React Frontend)

When ready to build the React UI:

```bash
cd frontend
npm create vite@latest . -- --template react
npm install
npm install recharts swr tailwindcss
npm run dev
```

Then follow **PHASE2_PLAN.md** for component-by-component build instructions.

---

## ❓ Common Issues

| Issue | Fix |
|-------|-----|
| Port 8000 already in use | `lsof -ti:8000 \| xargs kill -9` |
| ModuleNotFoundError | Make sure you're in `options_dashboard/` directory |
| "No data returned" | Check ticker symbol (case matters), increase date range |
| CORS error in browser | Already enabled — should work with React |

---

## 📍 File Structure

```
options_dashboard/
├── api/                    ← NEW Backend (Phase 1)
├── utils.py                ← ORIGINAL (unchanged)
├── options_utils.py        ← ORIGINAL (unchanged)
├── robust_app.py           ← Streamlit (unchanged)
├── test_api.py             ← Test suite
├── requirements.txt        ← Updated
└── [documentation files]
```

---

## 💾 Installation (if needed)

```bash
pip install -r requirements.txt
# Already includes: fastapi, uvicorn, pandas, yfinance, etc.
```

---

## 🔗 Useful Links

- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health
- **GitHub**: Review implementation in `api/` directory

---

## ✅ Status

**Phase 1**: Complete ✅
- Backend API built and tested
- 12 endpoints working
- Documentation complete

**Phase 2**: Ready to start
- React UI to be built
- Estimated 4-5 days of development
- See PHASE2_PLAN.md for details

---

## 🚀 One Command to Rule Them All

```bash
# Terminal 1: Start the API
python -m uvicorn api.main:app --reload

# Terminal 2 (when ready for React): Start React dev server
cd frontend && npm run dev

# Terminal 3 (optional): Keep Streamlit running
streamlit run robust_app.py

# Now open in browser:
# API Docs:    http://localhost:8000/docs
# React App:   http://localhost:5173
# Streamlit:   http://localhost:8501
```

---

**That's it! You're ready to go. 🎉**

For detailed docs, see the markdown files in this directory.
