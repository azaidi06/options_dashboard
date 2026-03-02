/**
 * Tabs component - pill style, dark theme
 */
import { useState, Children } from 'react';

export function Tabs({ children, defaultTab = 0 }) {
  const [activeTab, setActiveTab] = useState(defaultTab);
  const tabs = Children.toArray(children).filter(Boolean);

  return (
    <div>
      {/* Tab bar - pill style */}
      <div className="flex gap-1 p-1 bg-slate-900/60 border border-slate-800 rounded-xl mb-6 overflow-x-auto">
        {tabs.map((tab, i) => (
          <button
            key={i}
            onClick={() => setActiveTab(i)}
            className={`tab-button whitespace-nowrap ${i === activeTab ? 'active' : ''}`}
          >
            {tab.props.label}
          </button>
        ))}
      </div>

      {/* Active panel */}
      <div>{tabs[activeTab]?.props.children}</div>
    </div>
  );
}

export function Tab({ label, children }) {
  return <>{children}</>;
}
