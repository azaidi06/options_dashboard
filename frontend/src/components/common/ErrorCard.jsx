/**
 * Error display card - dark theme
 */
import { Button } from './Button';

export function ErrorCard({ error, onRetry }) {
  const isNetwork =
    error?.includes('Backend not running') ||
    error?.includes('fetch') ||
    error?.includes('network') ||
    error?.includes('Load failed');

  return (
    <div className="error-box mb-6">
      {isNetwork ? (
        <>
          <h4 className="text-red-700 dark:text-red-400 font-semibold text-lg mb-2">Backend Unavailable</h4>
          <p className="text-stone-700 dark:text-slate-300 mb-3">
            Could not connect to the API server. Start the backend with:
          </p>
          <pre className="bg-stone-100/80 dark:bg-slate-800/80 text-stone-800 dark:text-slate-200 rounded-lg px-4 py-3 text-sm font-mono mb-4 overflow-x-auto border border-stone-300/50 dark:border-slate-700/50">
            cd options_dashboard && python -m uvicorn api.main:app --port 8000 --reload
          </pre>
        </>
      ) : (
        <>
          <h4 className="text-red-700 dark:text-red-400 font-semibold text-lg mb-2">Error</h4>
          <p className="text-stone-700 dark:text-slate-300 mb-4">{error}</p>
        </>
      )}
      {onRetry && (
        <Button onClick={onRetry} className="bg-red-600 hover:bg-red-500 shadow-red-500/20">
          Retry
        </Button>
      )}
    </div>
  );
}
