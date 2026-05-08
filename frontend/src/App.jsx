/**
 * Main App component with routing
 */
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { SWRConfig } from 'swr';
import { HomePage } from './components/pages/HomePage';
import { LearnPage } from './components/pages/LearnPage';
import { StockAnalysisPage } from './components/pages/StockAnalysisPage';
import { OptionsPage } from './components/pages/OptionsPage';
import { TickersPage } from './components/pages/TickersPage';
import './index.css';

function App() {
  return (
    <SWRConfig
      value={{
        onErrorRetry: (error, _key, _config, revalidate, { retryCount }) => {
          // Don't retry on network errors (backend down)
          if (error.isNetworkError) return;
          // Don't retry on 404s
          if (error.status === 404) return;
          // Only retry up to 3 times
          if (retryCount >= 3) return;
          setTimeout(() => revalidate({ retryCount }), 5000);
        },
      }}
    >
      <Router>
        <Routes>
          <Route path="/" element={<HomePage />} />
          <Route path="/learn" element={<LearnPage />} />
          <Route path="/stock" element={<StockAnalysisPage />} />
          <Route path="/options" element={<OptionsPage />} />
          <Route path="/tickers" element={<TickersPage />} />
        </Routes>
      </Router>
    </SWRConfig>
  );
}

export default App;
