/**
 * Home Page - one viewport: hero + nav cards + recent tickers + disclaimer.
 * Educational content lives at /learn.
 */
import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { LineChart, BarChart3, BookOpen, ArrowRight } from 'lucide-react';
import { Layout } from '../layout/Layout';

const RECENT_KEY = 'od.recent_tickers';
const MAX_RECENT = 6;

export function HomePage() {
  const [recent, setRecent] = useState([]);

  useEffect(() => {
    try {
      const stored = JSON.parse(localStorage.getItem(RECENT_KEY) || '[]');
      if (Array.isArray(stored)) setRecent(stored.slice(0, MAX_RECENT));
    } catch {
      // Ignore parse errors; recent tickers is purely cosmetic.
    }
  }, []);

  return (
    <Layout>
      <div className="max-w-6xl mx-auto">
        {/* ─── Hero ─── */}
        <div className="mb-8">
          <h1 className="text-4xl font-extrabold mb-3 gradient-text">Options Dashboard</h1>
          <p className="text-lg text-stone-600 dark:text-slate-400 max-w-3xl">
            Analyze stocks, study drawdowns, and explore historical option chains with real market data.
          </p>
        </div>

        {/* ─── Navigation Cards ─── */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
          <Link to="/stock" className="group">
            <div className="card-lg h-full border-stone-200 dark:border-slate-800 hover:border-indigo-500/30 transition-all duration-300 group-hover:shadow-lg group-hover:shadow-indigo-500/5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-indigo-600/15 flex items-center justify-center">
                  <LineChart className="w-5 h-5 text-indigo-700 dark:text-indigo-400" />
                </div>
                <h2 className="text-xl font-bold text-stone-900 dark:text-slate-100 group-hover:text-indigo-700 group-hover:dark:text-indigo-400 transition-colors">
                  Stock Analysis
                </h2>
                <ArrowRight className="w-4 h-4 ml-auto text-stone-400 dark:text-slate-600 group-hover:text-indigo-700 group-hover:dark:text-indigo-400 transition-colors" />
              </div>
              <p className="text-stone-600 dark:text-slate-400 mb-3 text-sm leading-relaxed">
                Price charts with rolling-high gradients, drawdown analysis, technical indicators, and entry-window opportunities.
              </p>
            </div>
          </Link>

          <Link to="/options" className="group">
            <div className="card-lg h-full border-stone-200 dark:border-slate-800 hover:border-purple-500/30 transition-all duration-300 group-hover:shadow-lg group-hover:shadow-purple-500/5">
              <div className="flex items-center gap-3 mb-4">
                <div className="w-10 h-10 rounded-lg bg-purple-600/15 flex items-center justify-center">
                  <BarChart3 className="w-5 h-5 text-purple-700 dark:text-purple-400" />
                </div>
                <h2 className="text-xl font-bold text-stone-900 dark:text-slate-100 group-hover:text-purple-700 group-hover:dark:text-purple-400 transition-colors">
                  Options
                </h2>
                <ArrowRight className="w-4 h-4 ml-auto text-stone-400 dark:text-slate-600 group-hover:text-purple-700 group-hover:dark:text-purple-400 transition-colors" />
              </div>
              <p className="text-stone-600 dark:text-slate-400 mb-3 text-sm leading-relaxed">
                Historical option chains (calls &amp; puts), IV smiles, payoff diagrams, calculators, and a Greeks reference.
              </p>
            </div>
          </Link>
        </div>

        {/* ─── Recently Viewed ─── */}
        <div className="mb-8">
          <p className="text-xs font-semibold text-stone-600 dark:text-slate-400 uppercase tracking-wider mb-3">
            Recently Viewed
          </p>
          {recent.length > 0 ? (
            <div className="flex flex-wrap gap-2">
              {recent.map((t) => (
                <Link
                  key={t}
                  to={`/stock?ticker=${encodeURIComponent(t)}`}
                  className="px-3 py-1.5 text-sm bg-white/60 dark:bg-slate-900/60 border border-stone-200 dark:border-slate-800 rounded-lg
                             text-stone-700 dark:text-slate-300 hover:border-indigo-500/30 hover:text-indigo-700 hover:dark:text-indigo-400
                             font-mono tabular-nums transition-colors"
                >
                  {t}
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-sm text-stone-500 dark:text-slate-500">
              Your recently-viewed tickers will appear here. Use the search in the header (press <kbd className="px-1 bg-stone-100 dark:bg-slate-800 rounded">/</kbd>) or pick a ticker from the data pages.
            </p>
          )}
        </div>

        {/* ─── Learn link ─── */}
        <Link
          to="/learn"
          className="flex items-center gap-3 card-lg border-stone-200 dark:border-slate-800 hover:border-stone-300 hover:dark:border-slate-700 transition-colors mb-8"
        >
          <BookOpen className="w-5 h-5 text-indigo-700 dark:text-indigo-400" />
          <div className="flex-1">
            <p className="font-semibold text-stone-900 dark:text-slate-100">New to this dashboard?</p>
            <p className="text-sm text-stone-600 dark:text-slate-400">
              Read the Learn page for indicator deep-dives, drawdown methodology, and put-option fundamentals.
            </p>
          </div>
          <ArrowRight className="w-4 h-4 text-stone-500 dark:text-slate-500" />
        </Link>

        {/* ─── Disclaimer ─── */}
        <div className="warning-box">
          <p className="text-sm">
            <strong className="text-amber-700 dark:text-amber-400">Disclaimer:</strong> This dashboard is for educational
            purposes only. Options trading involves significant risk. Past performance does not guarantee
            future results. Always do your own research and consider consulting a financial professional.
          </p>
        </div>
      </div>
    </Layout>
  );
}

/**
 * Helper exported for data pages to record visits in localStorage.
 * Keeps the most recent ticker first, dedupes, caps at MAX_RECENT.
 */
export function recordRecentTicker(ticker) {
  if (!ticker) return;
  const t = String(ticker).toUpperCase();
  try {
    const stored = JSON.parse(localStorage.getItem(RECENT_KEY) || '[]');
    const list = Array.isArray(stored) ? stored : [];
    const next = [t, ...list.filter((x) => x !== t)].slice(0, MAX_RECENT);
    localStorage.setItem(RECENT_KEY, JSON.stringify(next));
  } catch {
    // Ignore localStorage failures
  }
}
