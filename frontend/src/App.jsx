/**
 * Main App component with routing
 */
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import { HomePage } from './components/pages/HomePage';
import { StockAnalysisPage } from './components/pages/StockAnalysisPage';
import { PutOptionsPage } from './components/pages/PutOptionsPage';
import './index.css';

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<HomePage />} />
        <Route path="/stock" element={<StockAnalysisPage />} />
        <Route path="/options" element={<PutOptionsPage />} />
      </Routes>
    </Router>
  );
}

export default App;
