/**
 * Main layout component with sidebar navigation - dark theme
 */
import { useState, useRef, useEffect } from 'react';
import { Link, useLocation, useNavigate } from 'react-router-dom';
import { Home, LineChart, BarChart3, BookOpen, Search } from 'lucide-react';
import AppSwitcher from '../common/AppSwitcher';

const NAV_ITEMS = [
  { to: '/', label: 'Home', Icon: Home },
  { to: '/stock', label: 'Stock Analysis', Icon: LineChart },
  { to: '/options', label: 'Put Options', Icon: BarChart3 },
  { to: '/learn', label: 'Learn', Icon: BookOpen },
];

const PAGE_TITLES = {
  '/': 'Home',
  '/stock': 'Stock Analysis',
  '/options': 'Put Options',
  '/learn': 'Learn',
};

export function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [tickerQuery, setTickerQuery] = useState('');
  const location = useLocation();
  const navigate = useNavigate();
  const tickerInputRef = useRef(null);
  const pageTitle = PAGE_TITLES[location.pathname] || 'Options Dashboard';

  // "/" focuses the ticker quick-switch unless already typing in another field
  useEffect(() => {
    function handleKey(e) {
      if (e.key !== '/') return;
      const tag = (e.target?.tagName || '').toLowerCase();
      if (tag === 'input' || tag === 'textarea' || tag === 'select') return;
      if (e.target?.isContentEditable) return;
      e.preventDefault();
      tickerInputRef.current?.focus();
    }
    window.addEventListener('keydown', handleKey);
    return () => window.removeEventListener('keydown', handleKey);
  }, []);

  function handleTickerSubmit(e) {
    e.preventDefault();
    const t = tickerQuery.trim().toUpperCase();
    if (!t) return;
    navigate(`/stock?ticker=${encodeURIComponent(t)}`);
    setTickerQuery('');
    tickerInputRef.current?.blur();
  }

  return (
    <div className="min-h-screen flex bg-slate-950">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-60' : 'w-[68px]'
        } bg-slate-900 border-r border-slate-800 transition-all duration-300 flex flex-col sticky top-0 h-screen`}
      >
        {/* Logo area */}
        <div className="px-4 py-5 border-b border-slate-800">
          {sidebarOpen ? (
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-indigo-500/20">
                OD
              </div>
              <span className="text-sm font-bold text-slate-100 tracking-tight">
                Options Dashboard
              </span>
            </div>
          ) : (
            <div className="flex justify-center">
              <div className="w-8 h-8 rounded-lg bg-indigo-600 flex items-center justify-center text-white font-bold text-sm shadow-lg shadow-indigo-500/20">
                OD
              </div>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="mt-4 flex-1 px-3 space-y-1">
          {NAV_ITEMS.map((item) => {
            const isActive = location.pathname === item.to;
            const { Icon } = item;
            return (
              <Link
                key={item.to}
                to={item.to}
                className={`flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-indigo-600/15 text-indigo-400 ring-1 ring-indigo-500/20'
                    : 'text-slate-400 hover:bg-slate-800/60 hover:text-slate-200'
                }`}
                title={!sidebarOpen ? item.label : undefined}
              >
                <Icon
                  className={`w-4 h-4 ${isActive ? 'text-indigo-400' : 'text-slate-500'}`}
                  strokeWidth={2}
                />
                {sidebarOpen && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Collapse toggle */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-3 mx-3 mb-3 text-slate-500 hover:text-slate-300 hover:bg-slate-800/50 rounded-lg transition-all duration-200"
          aria-label={sidebarOpen ? 'Collapse sidebar' : 'Expand sidebar'}
        >
          {sidebarOpen ? '‹' : '›'}
        </button>
      </aside>

      {/* Main content (document scrolls) */}
      <div className="flex-1 flex flex-col">
        {/* Header */}
        <header className="bg-slate-900/50 backdrop-blur-sm border-b border-slate-800/50 sticky top-0 z-10">
          <div className="px-8 py-4 flex items-center justify-between gap-4">
            <h2 className="text-base font-semibold text-slate-200">{pageTitle}</h2>
            <div className="flex items-center gap-4">
              <AppSwitcher />
              <form onSubmit={handleTickerSubmit} className="flex-shrink-0">
              <div className="relative">
                <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-slate-500 pointer-events-none" />
                <input
                  ref={tickerInputRef}
                  type="text"
                  value={tickerQuery}
                  onChange={(e) => setTickerQuery(e.target.value)}
                  placeholder="Quick ticker switch (press / )"
                  className="pl-8 pr-3 py-1.5 w-72 text-sm bg-slate-800/80 border border-slate-700 rounded-lg
                             text-slate-100 placeholder-slate-500 focus:outline-none
                             focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500
                             transition-all duration-200"
                  aria-label="Quick ticker switch"
                />
              </div>
            </form>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 px-8 py-6">{children}</main>
      </div>
    </div>
  );
}
