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
          <h4 className="text-red-400 font-semibold text-lg mb-2">Backend Unavailable</h4>
          <p className="text-slate-300 mb-3">
            Could not connect to the API server. Start the backend with:
          </p>
          <pre className="bg-slate-800/80 text-slate-200 rounded-lg px-4 py-3 text-sm font-mono mb-4 overflow-x-auto border border-slate-700/50">
            cd options_dashboard && python -m uvicorn api.main:app --port 8000 --reload
          </pre>
        </>
      ) : (
        <>
          <h4 className="text-red-400 font-semibold text-lg mb-2">Error</h4>
          <p className="text-slate-300 mb-4">{error}</p>
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
