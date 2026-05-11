/**
 * Tabs component - pill style, dark theme, ARIA-compliant
 */
import { useState, Children } from 'react';

export function Tabs({ children, defaultTab = 0 }) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  const tabs = Children.toArray(children).filter(Boolean);

  return (
    <div>
      {/* Tab bar - pill style */}
      <div
        role="tablist"
        className="flex gap-1 p-1 bg-white/60 dark:bg-slate-900/60 border border-stone-200 dark:border-slate-800 rounded-xl mb-6 overflow-x-auto"
      >
        {tabs.map((tab, i) => {
          const active = i === activeTab;
          return (
            <button
              key={i}
              role="tab"
              aria-selected={active}
              aria-controls={`tabpanel-${i}`}
              id={`tab-${i}`}
              tabIndex={active ? 0 : -1}
              onClick={() => setActiveTab(i)}
              className={`tab-button whitespace-nowrap ${active ? 'active' : ''}`}
            >
              {tab.props.label}
            </button>
          );
        })}
      </div>

      {/* Active panel */}
      <div
        role="tabpanel"
        id={`tabpanel-${activeTab}`}
        aria-labelledby={`tab-${activeTab}`}
      >
        {tabs[activeTab]?.props.children}
      </div>
    </div>
  );
}

export function Tab({ label, children }) {
  return <>{children}</>;
}
