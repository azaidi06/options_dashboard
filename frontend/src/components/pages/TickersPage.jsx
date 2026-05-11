/**
 * Tickers Page - manage cached ticker data.
 *
 * Top half: probe a new ticker (or top up an existing one) and start fetch jobs.
 * Bottom half: searchable grid of currently-cached tickers; clicking a card
 * jumps to the Options page with that ticker preselected.
 */
import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Database, Search, ArrowRight, Plus, AlertTriangle, CheckCircle2, Info } from 'lucide-react';
import { Layout } from '../layout/Layout';
import { CardLg, MetricCard } from '../common/Card';
import { Input } from '../common/Input';
import { Button } from '../common/Button';
import { ErrorCard } from '../common/ErrorCard';
import { useTickerCoverage } from '../../hooks/useOptionsData';
import {
  probeTicker,
  startTickerFetch,
  fetchTickerJobStatus,
} from '../../utils/api';

const POLL_MS = 2000;

/**
 * YYYY-MM-DD for `n` days ago.
 */
function isoDaysAgo(n) {
  const d = new Date();
  d.setDate(d.getDate() - n);
  return d.toISOString().slice(0, 10);
}
const TODAY_ISO = () => new Date().toISOString().slice(0, 10);

function StatusPill({ tone, children }) {
  const tones = {
    green: 'bg-emerald-500/15 text-emerald-700 dark:text-emerald-300 ring-1 ring-emerald-500/30',
    blue: 'bg-blue-500/15 text-blue-700 dark:text-blue-300 ring-1 ring-blue-500/30',
    red: 'bg-red-500/15 text-red-700 dark:text-red-300 ring-1 ring-red-500/30',
    amber: 'bg-amber-500/15 text-amber-700 dark:text-amber-300 ring-1 ring-amber-500/30',
    slate: 'bg-stone-200/40 dark:bg-slate-700/40 text-stone-700 dark:text-slate-300 ring-1 ring-stone-400/40 dark:ring-slate-600/40',
  };
  return (
    <span className={`inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium ${tones[tone] || tones.slate}`}>
      {children}
    </span>
  );
}

function ProgressBar({ done, total }) {
  const pct = total > 0 ? Math.min(100, Math.round((done / total) * 100)) : 0;
  return (
    <div className="w-full">
      <div className="flex justify-between text-xs text-stone-600 dark:text-slate-400 mb-1.5 num">
        <span>{done.toLocaleString()} / {total.toLocaleString()}</span>
        <span>{pct}%</span>
      </div>
      <div className="h-2 w-full bg-stone-100 dark:bg-slate-800 rounded-full overflow-hidden ring-1 ring-stone-300/50 dark:ring-slate-700/50">
        <div
          className="h-full bg-indigo-500 rounded-full transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  );
}

/**
 * Render the result of a successful probe call.
 * Handles the three branches in the spec: not-upstream / cached / new.
 */
function ProbeResult({ probe, fromDate, toDate, setFromDate, setToDate, onFetch, fetching }) {
  if (!probe) return null;

  if (probe.existsUpstream === false) {
    return (
      <div className="error-box mt-4 flex items-start gap-3">
        <AlertTriangle className="w-5 h-5 text-red-700 dark:text-red-400 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-red-700 dark:text-red-300 font-semibold">Ticker not found upstream.</p>
          <p className="text-sm text-stone-700 dark:text-slate-300 mt-1">
            <span className="font-mono">{probe.ticker}</span> doesn't appear to exist on the upstream provider.
          </p>
        </div>
      </div>
    );
  }

  // Already cached
  if (probe.cached) {
    const c = probe.cached;
    const hasGaps = Array.isArray(probe.missingRanges) && probe.missingRanges.length > 0;
    return (
      <div className="info-box mt-4">
        <div className="flex items-start justify-between gap-3 flex-wrap">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="w-5 h-5 text-emerald-700 dark:text-emerald-400 flex-shrink-0 mt-0.5" />
            <div>
              <StatusPill tone="green">
                Already cached: {c.firstDate} → {c.lastDate} ({c.tradingDays?.toLocaleString()} trading days)
              </StatusPill>
              {hasGaps && (
                <p className="text-xs text-amber-700 dark:text-amber-300 mt-2">
                  {probe.missingRanges.length} missing range
                  {probe.missingRanges.length === 1 ? '' : 's'} detected — top up below.
                </p>
              )}
            </div>
          </div>
          {hasGaps && (
            <Button
              onClick={() => {
                // Top-up: fetch from earliest gap start to today.
                const first = probe.missingRanges[0]?.from || c.lastDate;
                onFetch(first, TODAY_ISO());
              }}
              disabled={fetching}
            >
              {fetching ? 'Starting…' : 'Top up to today'}
            </Button>
          )}
        </div>
      </div>
    );
  }

  // New ticker — let user pick a date range
  const avail = probe.available || {};
  return (
    <div className="info-box mt-4">
      <div className="flex items-start gap-3 mb-4">
        <Info className="w-5 h-5 text-blue-700 dark:text-blue-400 flex-shrink-0 mt-0.5" />
        <div>
          <p className="text-stone-900 dark:text-slate-100 font-semibold">New ticker — not yet cached.</p>
          <p className="text-sm text-stone-600 dark:text-slate-400 mt-1">
            Available upstream: <span className="font-mono text-stone-700 dark:text-slate-300">{avail.firstDate || '?'}</span> →{' '}
            <span className="font-mono text-stone-700 dark:text-slate-300">{avail.lastDate || '?'}</span>
          </p>
        </div>
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        <Input label="From" value={fromDate} onChange={setFromDate} type="date" />
        <Input label="To" value={toDate} onChange={setToDate} type="date" />
        <div className="flex items-end">
          <Button
            onClick={() => onFetch(fromDate, toDate)}
            disabled={fetching || !fromDate || !toDate}
            className="w-full"
          >
            {fetching ? 'Starting…' : 'Fetch'}
          </Button>
        </div>
      </div>
    </div>
  );
}

/**
 * Card representing a single cached ticker. Click navigates to Options page.
 */
function TickerCard({ row, onClick }) {
  return (
    <button
      type="button"
      onClick={onClick}
      className="card-lg group text-left transition-all duration-200 border-stone-200 dark:border-slate-800 hover:border-indigo-500/40 hover:shadow-lg hover:shadow-indigo-500/5"
    >
      <div className="flex items-start justify-between mb-3">
        <div className="text-xl font-extrabold text-stone-900 dark:text-slate-100 tracking-tight font-mono">
          {row.ticker}
        </div>
        <ArrowRight className="w-4 h-4 text-stone-400 dark:text-slate-600 group-hover:text-indigo-700 group-hover:dark:text-indigo-400 transition-colors" />
      </div>
      <div className="text-xs text-stone-500 dark:text-slate-500 uppercase tracking-wider mb-1">Coverage</div>
      <div className="text-sm text-stone-700 dark:text-slate-300 num">
        {row.firstDate} → {row.lastDate}
      </div>
      <div className="mt-2 text-xs text-stone-500 dark:text-slate-500">
        <span className="num text-stone-600 dark:text-slate-400">{Number(row.tradingDays || 0).toLocaleString()}</span> trading days
      </div>
    </button>
  );
}

export function TickersPage() {
  const navigate = useNavigate();
  const coverage = useTickerCoverage();

  // Add-ticker form state
  const [tickerInput, setTickerInput] = useState('');
  const [probing, setProbing] = useState(false);
  const [probeError, setProbeError] = useState(null);
  const [probe, setProbe] = useState(null);

  // Date range for new-ticker fetch (default: last 1 year → today)
  const [fromDate, setFromDate] = useState(isoDaysAgo(365));
  const [toDate, setToDate] = useState(TODAY_ISO());

  // Fetch job state
  const [job, setJob] = useState(null); // { jobId, ticker, status, progress: {done,total}, error }
  const [jobStarting, setJobStarting] = useState(false);
  const [jobError, setJobError] = useState(null);

  // Coverage filter
  const [filter, setFilter] = useState('');

  async function handleProbe(e) {
    if (e) e.preventDefault();
    const t = tickerInput.trim().toUpperCase();
    if (!t) return;
    setProbing(true);
    setProbeError(null);
    setProbe(null);
    setJob(null);
    setJobError(null);
    try {
      const result = await probeTicker(t);
      setProbe(result);
    } catch (err) {
      setProbeError(err.message || 'Probe failed');
    } finally {
      setProbing(false);
    }
  }

  async function handleFetch(from, to) {
    if (!probe?.ticker || !from || !to) return;
    setJobStarting(true);
    setJobError(null);
    try {
      const started = await startTickerFetch(probe.ticker, from, to);
      setJob({
        jobId: started.jobId,
        ticker: started.ticker || probe.ticker,
        status: started.status || 'queued',
        progress: { done: 0, total: 0 },
      });
    } catch (err) {
      setJobError(err.message || 'Failed to start fetch');
    } finally {
      setJobStarting(false);
    }
  }

  // Poll job status until terminal
  useEffect(() => {
    if (!job?.jobId) return;
    if (job.status === 'complete' || job.status === 'failed') return;
    let cancelled = false;
    const tick = async () => {
      try {
        const next = await fetchTickerJobStatus(job.jobId);
        if (cancelled) return;
        setJob((prev) => ({ ...prev, ...next }));
        if (next.status === 'complete') {
          // Refresh coverage list when a job finishes successfully.
          coverage.refetch?.();
        }
      } catch (err) {
        if (!cancelled) setJobError(err.message || 'Status poll failed');
      }
    };
    const id = setInterval(tick, POLL_MS);
    // Kick once immediately so the bar reflects something quickly
    tick();
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [job?.jobId, job?.status]);

  // Filtered + sorted coverage
  const filteredCoverage = useMemo(() => {
    const q = filter.trim().toUpperCase();
    const rows = Array.isArray(coverage.data) ? coverage.data : [];
    const out = q ? rows.filter((r) => String(r.ticker || '').toUpperCase().includes(q)) : rows;
    return [...out].sort((a, b) => String(a.ticker).localeCompare(String(b.ticker)));
  }, [coverage.data, filter]);

  const jobDone = job?.status === 'complete';
  const jobFailed = job?.status === 'failed';
  const jobActive = job && !jobDone && !jobFailed;

  return (
    <Layout>
      <div className="max-w-7xl mx-auto">
        {/* ─── Add Ticker ─── */}
        <CardLg className="mb-6">
          <div className="flex items-center gap-3 mb-4">
            <div className="w-9 h-9 rounded-lg bg-indigo-600/15 flex items-center justify-center">
              <Plus className="w-4 h-4 text-indigo-700 dark:text-indigo-400" />
            </div>
            <div>
              <h2 className="text-base font-semibold text-stone-800 dark:text-slate-200">Add Ticker</h2>
              <p className="text-xs text-stone-500 dark:text-slate-500">
                Probe a symbol to check upstream availability and existing cache, then fetch its history.
              </p>
            </div>
          </div>

          <form onSubmit={handleProbe} className="grid grid-cols-1 md:grid-cols-[1fr_auto] gap-3 items-end">
            <Input
              label="Add ticker (e.g., AMD)"
              value={tickerInput}
              onChange={(v) => setTickerInput(v.toUpperCase())}
              placeholder="AMD"
            />
            <Button onClick={handleProbe} disabled={probing || !tickerInput.trim()} className="md:w-32">
              {probing ? (
                <span className="flex items-center justify-center gap-2">
                  <span className="spinner" /> Probing…
                </span>
              ) : (
                'Probe'
              )}
            </Button>
          </form>

          {probeError && (
            <div className="mt-4">
              <ErrorCard error={probeError} />
            </div>
          )}

          <ProbeResult
            probe={probe}
            fromDate={fromDate}
            toDate={toDate}
            setFromDate={setFromDate}
            setToDate={setToDate}
            onFetch={handleFetch}
            fetching={jobStarting || jobActive}
          />

          {/* Job progress / outcome */}
          {jobError && (
            <div className="mt-4">
              <ErrorCard error={jobError} />
            </div>
          )}
          {job && (
            <div className="mt-4 card-lg bg-white/40 dark:bg-slate-900/40">
              <div className="flex items-center justify-between mb-3 flex-wrap gap-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm font-semibold text-stone-800 dark:text-slate-200 font-mono">{job.ticker}</span>
                  {jobActive && <StatusPill tone="blue">Running ({job.status || 'queued'})</StatusPill>}
                  {jobDone && <StatusPill tone="green">Complete</StatusPill>}
                  {jobFailed && <StatusPill tone="red">Failed</StatusPill>}
                </div>
                <span className="text-xs text-stone-500 dark:text-slate-500 font-mono">job: {job.jobId}</span>
              </div>
              <ProgressBar
                done={job.progress?.done || 0}
                total={job.progress?.total || 0}
              />
              {jobFailed && job.error && (
                <p className="mt-3 text-sm text-red-700 dark:text-red-300">{job.error}</p>
              )}
              {jobDone && (
                <p className="mt-3 text-sm text-emerald-700 dark:text-emerald-300">
                  Cached. The ticker will appear in the grid below.
                </p>
              )}
            </div>
          )}
        </CardLg>

        {/* ─── Coverage Grid ─── */}
        <CardLg>
          <div className="flex items-center justify-between mb-4 gap-3 flex-wrap">
            <div className="flex items-center gap-3">
              <div className="w-9 h-9 rounded-lg bg-indigo-600/15 flex items-center justify-center">
                <Database className="w-4 h-4 text-indigo-700 dark:text-indigo-400" />
              </div>
              <div>
                <h2 className="text-base font-semibold text-stone-800 dark:text-slate-200">Cached Tickers</h2>
                <p className="text-xs text-stone-500 dark:text-slate-500">
                  Click a card to load it on the Options page.
                </p>
              </div>
            </div>
            <div className="relative">
              <Search className="absolute left-2.5 top-1/2 -translate-y-1/2 w-4 h-4 text-stone-500 dark:text-slate-500 pointer-events-none" />
              <input
                type="text"
                value={filter}
                onChange={(e) => setFilter(e.target.value)}
                placeholder="Filter…"
                className="pl-8 pr-3 py-1.5 w-56 text-sm bg-stone-100/80 dark:bg-slate-800/80 border border-stone-300 dark:border-slate-700 rounded-lg
                           text-stone-900 dark:text-slate-100 placeholder-stone-400 dark:placeholder-slate-500 focus:outline-none
                           focus:ring-2 focus:ring-indigo-500/50 focus:border-indigo-500
                           transition-all duration-200"
              />
            </div>
          </div>

          {/* Loading skeletons */}
          {coverage.loading && (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {Array.from({ length: 6 }).map((_, i) => (
                <div key={i} className="card-lg">
                  <div className="skeleton h-6 w-1/3 mb-3" />
                  <div className="skeleton h-4 w-2/3 mb-2" />
                  <div className="skeleton h-3 w-1/2" />
                </div>
              ))}
            </div>
          )}

          {/* Error */}
          {!coverage.loading && coverage.error && (
            <ErrorCard error={coverage.error} onRetry={() => coverage.refetch?.()} />
          )}

          {/* Empty */}
          {!coverage.loading && !coverage.error && filteredCoverage.length === 0 && (
            <div className="flex items-center justify-center py-12">
              <div className="text-center max-w-md">
                <Database className="w-10 h-10 text-stone-400 dark:text-slate-600 mx-auto mb-3" strokeWidth={1.5} />
                <p className="text-stone-700 dark:text-slate-300 font-semibold mb-1">
                  {filter
                    ? `No tickers match “${filter}”.`
                    : 'No tickers cached yet — add one above'}
                </p>
                {!filter && (
                  <p className="text-stone-500 dark:text-slate-500 text-sm">
                    Probe a symbol with the form above to start caching its option history.
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Grid */}
          {!coverage.loading && !coverage.error && filteredCoverage.length > 0 && (
            <>
              <div className="mb-3 grid grid-cols-2 md:grid-cols-4 gap-3">
                <MetricCard
                  label="Tickers cached"
                  value={(coverage.data?.length || 0).toLocaleString()}
                />
                <MetricCard
                  label="Total trading days"
                  value={coverage.data
                    ?.reduce((sum, r) => sum + (Number(r.tradingDays) || 0), 0)
                    .toLocaleString() || '0'}
                />
                <MetricCard
                  label="Showing"
                  value={`${filteredCoverage.length} of ${coverage.data?.length || 0}`}
                />
                <MetricCard
                  label="Most recent"
                  value={
                    coverage.data?.length
                      ? coverage.data
                          .reduce((acc, r) =>
                            (acc?.lastDate || '') > (r.lastDate || '') ? acc : r,
                          coverage.data[0])
                          ?.lastDate || '—'
                      : '—'
                  }
                />
              </div>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                {filteredCoverage.map((row) => (
                  <TickerCard
                    key={row.ticker}
                    row={row}
                    onClick={() => navigate(`/options?ticker=${encodeURIComponent(row.ticker)}`)}
                  />
                ))}
              </div>
            </>
          )}
        </CardLg>
      </div>
    </Layout>
  );
}
