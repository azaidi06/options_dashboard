/**
 * Card components - dark glass-morphism theme
 */

export function Card({ children, className = '' }) {
  return <div className={`card ${className}`}>{children}</div>;
}

export function CardLg({ children, className = '' }) {
  return <div className={`card-lg ${className}`}>{children}</div>;
}

export function MetricCard({ label, value, delta, deltaType, className = '' }) {
  const deltaColor =
    deltaType === 'positive'
      ? 'text-emerald-400'
      : deltaType === 'negative'
        ? 'text-red-400'
        : 'text-slate-400';

  return (
    <div className={`metric-card ${className}`}>
      <div className="metric-label">{label}</div>
      <div className="flex items-baseline gap-2">
        <div className="metric-value">{value}</div>
        {delta && <span className={`text-sm font-medium ${deltaColor}`}>{delta}</span>}
      </div>
    </div>
  );
}
