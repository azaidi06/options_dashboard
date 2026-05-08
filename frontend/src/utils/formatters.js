/**
 * Numeric formatters for the dashboard.
 * All exports are named.
 */

/**
 * Format a number with compact SI suffixes (K, M, B, T).
 * Examples: 1234 -> "1.2K", 44_600_000_000 -> "44.6B", 2.3e12 -> "2.3T"
 */
export function formatCompactNumber(n, dp = 1) {
  if (n === null || n === undefined || Number.isNaN(n)) return '—';
  const num = Number(n);
  if (!Number.isFinite(num)) return '—';
  const abs = Math.abs(num);
  const sign = num < 0 ? '-' : '';
  if (abs >= 1e12) return `${sign}${(abs / 1e12).toFixed(dp)}T`;
  if (abs >= 1e9) return `${sign}${(abs / 1e9).toFixed(dp)}B`;
  if (abs >= 1e6) return `${sign}${(abs / 1e6).toFixed(dp)}M`;
  if (abs >= 1e3) return `${sign}${(abs / 1e3).toFixed(dp)}K`;
  return `${sign}${abs.toFixed(0)}`;
}

/**
 * Format a volume number with the SI suffix appended.
 * Mostly an alias for formatCompactNumber for clarity at call sites.
 */
export function formatVolume(n, dp = 1) {
  return formatCompactNumber(n, dp);
}

/**
 * Format a currency value with `$` prefix.
 * Returns "—" for null/undefined/NaN.
 */
export function formatCurrency(n, dp = 2) {
  if (n === null || n === undefined || Number.isNaN(n)) return '—';
  const num = Number(n);
  if (!Number.isFinite(num)) return '—';
  const sign = num < 0 ? '-' : '';
  return `${sign}$${Math.abs(num).toFixed(dp)}`;
}

/**
 * Format a percentage. Input is in percent units already (e.g. 12.5 -> "12.50%").
 */
export function formatPercent(n, dp = 2) {
  if (n === null || n === undefined || Number.isNaN(n)) return '—';
  const num = Number(n);
  if (!Number.isFinite(num)) return '—';
  return `${num.toFixed(dp)}%`;
}

/**
 * Format a Greek (delta/gamma/theta/vega/rho) with a sensible number of decimals
 * given typical magnitudes. `name` is case-insensitive.
 */
export function formatGreek(n, name = 'delta') {
  if (n === null || n === undefined || Number.isNaN(n)) return '—';
  const num = Number(n);
  if (!Number.isFinite(num)) return '—';
  const k = String(name || '').toLowerCase();
  // Theta typical magnitude ~0.001-0.5, 3 dp reads cleaner than 4.
  // Gamma/Vega can be tiny; 4 dp keeps signal visible.
  // Delta is in [-1, 1], 3 dp is conventional.
  let dp = 3;
  if (k === 'gamma' || k === 'vega') dp = 4;
  else if (k === 'theta') dp = 3;
  else if (k === 'delta' || k === 'rho') dp = 3;
  return num.toFixed(dp);
}

/**
 * Format a date-like value to YYYY-MM-DD (the codebase convention).
 * Accepts Date objects or ISO/parseable strings.
 */
export function formatDate(d) {
  if (!d) return '—';
  if (d instanceof Date) {
    if (Number.isNaN(d.getTime())) return '—';
    return d.toISOString().slice(0, 10);
  }
  const s = String(d);
  // Already YYYY-MM-DD or ISO-ish — slice the date portion
  if (/^\d{4}-\d{2}-\d{2}/.test(s)) return s.slice(0, 10);
  const dt = new Date(s);
  if (Number.isNaN(dt.getTime())) return s;
  return dt.toISOString().slice(0, 10);
}
