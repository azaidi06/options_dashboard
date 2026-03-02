/**
 * Main layout component with sidebar navigation - dark theme
 */
import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

const NAV_ITEMS = [
  { to: '/', label: 'Home', icon: '⌂' },
  { to: '/stock', label: 'Stock Analysis', icon: '◈' },
  { to: '/options', label: 'Put Options', icon: '◆' },
];

const PAGE_TITLES = {
  '/': 'Home',
  '/stock': 'Stock Analysis',
  '/options': 'Put Options',
};

export function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();
  const pageTitle = PAGE_TITLES[location.pathname] || 'Options Dashboard';

  return (
    <div className="flex h-screen bg-slate-950">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-60' : 'w-[68px]'
        } bg-slate-900 border-r border-slate-800 transition-all duration-300 flex flex-col`}
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
                <span className={`text-base ${isActive ? 'text-indigo-400' : 'text-slate-500'}`}>
                  {item.icon}
                </span>
                {sidebarOpen && <span>{item.label}</span>}
              </Link>
            );
          })}
        </nav>

        {/* Collapse toggle */}
        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="p-3 mx-3 mb-3 text-slate-500 hover:text-slate-300 hover:bg-slate-800/50 rounded-lg transition-all duration-200"
        >
          {sidebarOpen ? '‹' : '›'}
        </button>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-slate-900/50 backdrop-blur-sm border-b border-slate-800/50">
          <div className="px-8 py-4 flex items-center justify-between">
            <h2 className="text-base font-semibold text-slate-200">{pageTitle}</h2>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto px-8 py-6">
          {children}
        </main>
      </div>
    </div>
  );
}
