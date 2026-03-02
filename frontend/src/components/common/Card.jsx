/**
 * Card component for grouping content
 */
export function Card({ children, className = '' }) {
  return (
    <div className={`card ${className}`}>
      {children}
    </div>
  );
}

export function CardLg({ children, className = '' }) {
  return (
    <div className={`card-lg ${className}`}>
      {children}
    </div>
  );
}

export function MetricCard({ label, value, className = '' }) {
  return (
    <div className={`metric-card ${className}`}>
      <div className="metric-label">{label}</div>
      <div className="metric-value">{value}</div>
    </div>
  );
}
