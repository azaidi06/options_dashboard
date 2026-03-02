/**
 * Main layout component with header and navigation
 */
import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';

export function Layout({ children }) {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();

  const isActive = (path) => location.pathname === path;

  return (
    <div className="flex h-screen bg-gray-50">
      {/* Sidebar */}
      <aside
        className={`${
          sidebarOpen ? 'w-64' : 'w-20'
        } bg-gray-900 text-white transition-all duration-300 overflow-hidden`}
      >
        <div className="p-4 border-b border-gray-700">
          <h1 className={`${sidebarOpen ? 'text-xl' : 'text-xs'} font-bold`}>
            {sidebarOpen ? 'Options Dashboard' : 'OD'}
          </h1>
        </div>

        <nav className="mt-8 space-y-2 px-3">
          <NavLink
            to="/"
            icon="📊"
            label="Home"
            active={isActive('/')}
            sidebarOpen={sidebarOpen}
          />
          <NavLink
            to="/stock"
            icon="📈"
            label="Stock Analysis"
            active={isActive('/stock')}
            sidebarOpen={sidebarOpen}
          />
          <NavLink
            to="/options"
            icon="💰"
            label="Put Options"
            active={isActive('/options')}
            sidebarOpen={sidebarOpen}
          />
        </nav>

        <button
          onClick={() => setSidebarOpen(!sidebarOpen)}
          className="absolute bottom-4 left-4 p-2 hover:bg-gray-800 rounded"
        >
          {sidebarOpen ? '◀' : '▶'}
        </button>
      </aside>

      {/* Main content */}
      <div className="flex-1 flex flex-col overflow-hidden">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 shadow-sm">
          <div className="px-8 py-4">
            <h2 className="text-2xl font-bold text-gray-900">
              Options Dashboard
            </h2>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 overflow-auto p-8">
          {children}
        </main>
      </div>
    </div>
  );
}

function NavLink({ to, icon, label, active, sidebarOpen }) {
  return (
    <Link
      to={to}
      className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
        active
          ? 'bg-blue-600 text-white'
          : 'text-gray-300 hover:bg-gray-800'
      }`}
    >
      <span className="text-lg">{icon}</span>
      {sidebarOpen && <span>{label}</span>}
    </Link>
  );
}
