# Options Dashboard - React Frontend

Modern React UI for stock analysis and options education.

## Quick Start

### Prerequisites
- Node.js 18+
- FastAPI backend running on http://localhost:8000
- Python backend must be running (see main README)

### Setup

```bash
# Install dependencies
npm install

# Copy environment config
cp .env.example .env.local
```

### Development

```bash
# Terminal 1: Start FastAPI backend
cd ..
python -m uvicorn api.main:app --reload --port 8000

# Terminal 2: Start React dev server
cd frontend
npm run dev
```

Then open http://localhost:5173 in your browser.

### Production

```bash
# Build the app
npm run build

# Output: frontend/dist/ (ready for Nginx)

# Preview production build
npm run preview
```

## Project Structure

```
src/
├── components/
│   ├── layout/      - Header, sidebar, layout
│   ├── pages/       - Home, Stock Analysis, Put Options
│   ├── stock/       - Stock analysis components
│   ├── options/     - Options analysis components (Phase 2b)
│   └── common/      - Reusable UI components
├── hooks/           - Custom React hooks for data fetching
├── utils/           - API client, helpers
├── App.jsx          - Main app with routing
└── index.css        - Tailwind CSS styles
```

## Features

### Stock Analysis Page ✓
- Real-time stock data with OHLCV
- Technical indicators (RSI, MACD, Bollinger, Moving Averages)
- Drawdown analysis with underwater periods
- Opportunity windows identification
- Interactive charts (Recharts)
- Responsive design

### Put Options Page 🔄 (Phase 2b)
- Option chain explorer (coming soon)
- IV smile visualization (coming soon)
- Payoff diagrams (coming soon)
- Greeks calculators (coming soon)

## Tech Stack

- **React 19** - UI framework
- **Vite 7** - Build tool (lightning fast)
- **React Router v6** - Navigation
- **Recharts** - Charts library
- **SWR** - Data fetching + caching
- **Tailwind CSS v4** - Styling

## API Integration

The app connects to FastAPI backend running on port 8000:

```javascript
// Proxied in dev (Vite config)
/api/* → http://localhost:8000/api

// API endpoints available:
GET    /api/stock/{ticker}                    - Stock data
GET    /api/stock/{ticker}/indicators         - Technical indicators
GET    /api/stock/{ticker}/drawdown           - Drawdown analysis
GET    /api/stock/{ticker}/opportunities      - Opportunity windows
GET    /api/options/tickers                   - Available tickers
GET    /api/options/{ticker}/chain            - Option chain
GET    /api/options/{ticker}/iv-smile         - IV smile
POST   /api/options/payoff                    - Payoff diagram
(... more options endpoints)
```

## Styling

- **Tailwind CSS v4** for all utility classes
- Custom color palette (blue, red, green)
- Responsive grid layout
- Component classes in `index.css`

## Performance

- **SWR caching** prevents unnecessary API calls
- **Debounced inputs** reduce request frequency
- **Code splitting** via Vite chunks
- **Lazy component loading** via React.lazy (future)

## Browser Support

- Chrome/Edge: Latest
- Firefox: Latest
- Safari: Latest (12.2+)
- Mobile browsers supported via responsive design

## Development Notes

### Adding a New Component

1. Create component file: `src/components/section/ComponentName.jsx`
2. Import and export
3. Use Tailwind utility classes
4. Handle loading/error states

### Adding a New API Hook

1. Create hook file: `src/hooks/useComponentData.js`
2. Use SWR for caching
3. Export loading, error, data states
4. Use in component via hook

### Styling Guidelines

- Use Tailwind utility classes (don't create new CSS)
- Component classes defined in `index.css`
- Colors: blue-600 (primary), red-600 (danger), green-600 (success)
- Responsive: mobile-first, md: breakpoint for larger screens

## Deployment

### Nginx Configuration

```nginx
location / {
    root /home/ubuntu/options_dashboard/frontend/dist;
    try_files $uri $uri/ /index.html;
}

location /api/ {
    proxy_pass http://127.0.0.1:8000;
}
```

### Build and Deploy

```bash
npm run build
# Copy dist/ to /home/ubuntu/options_dashboard/frontend/dist/
sudo systemctl reload nginx
```

## Troubleshooting

### "Cannot GET /"
- Make sure `npm run dev` is running or production build is deployed
- Check vite.config.js proxy settings

### "API request failed"
- Verify FastAPI backend is running on port 8000
- Check browser console for CORS errors
- Ensure proxy is configured in vite.config.js

### Chart not displaying
- Check browser console for errors
- Ensure data is returned from API
- Verify Recharts is installed: `npm list recharts`

## Contributing

When adding features:
1. Keep components focused and small
2. Use custom hooks for data logic
3. Follow existing naming conventions
4. Test in multiple browsers
5. Ensure responsive design

## License

Same as main project
