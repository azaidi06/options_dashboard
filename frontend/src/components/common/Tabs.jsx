/**
 * Tabs component
 */
import { useState } from 'react';

export function Tabs({ children, defaultTab = 0 }) {
  const [activeTab, setActiveTab] = useState(defaultTab);

  // Filter out null/undefined children
  const validChildren = children.filter((child) => child != null);

  return (
    <div>
      {/* Tab buttons */}
      <div className="flex border-b border-gray-200 gap-0">
        {validChildren.map((tab, index) => (
          <button
            key={index}
            onClick={() => setActiveTab(index)}
            className={`tab-button ${activeTab === index ? 'active' : ''}`}
          >
            {tab.props.label}
          </button>
        ))}
      </div>

      {/* Tab content */}
      <div className="mt-4">
        {validChildren[activeTab]}
      </div>
    </div>
  );
}

export function Tab({ children, label }) {
  return <div>{children}</div>;
}
