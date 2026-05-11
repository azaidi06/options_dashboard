import { createContext, useContext, useEffect, useState, useCallback } from 'react';
import { TOKENS_BY_THEME, darkTokens } from './tokens';

const STORAGE_KEY = 'options-dashboard-theme';
const ThemeContext = createContext(null);

function readStoredTheme() {
  if (typeof window === 'undefined') return 'dark';
  try {
    const stored = window.localStorage.getItem(STORAGE_KEY);
    if (stored === 'light' || stored === 'dark') return stored;
  } catch {
    // ignore (private mode, disabled storage, etc.)
  }
  return 'dark';
}

export function ThemeProvider({ children }) {
  const [theme, setThemeState] = useState(readStoredTheme);

  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme);
    try {
      window.localStorage.setItem(STORAGE_KEY, theme);
    } catch {
      // ignore
    }
  }, [theme]);

  const setTheme = useCallback((next) => {
    if (next !== 'dark' && next !== 'light') return;
    setThemeState(next);
  }, []);

  const toggleTheme = useCallback(() => {
    setThemeState((prev) => (prev === 'dark' ? 'light' : 'dark'));
  }, []);

  const tokens = TOKENS_BY_THEME[theme] ?? darkTokens;

  return (
    <ThemeContext.Provider value={{ theme, setTheme, toggleTheme, tokens }}>
      {children}
    </ThemeContext.Provider>
  );
}

export function useTheme() {
  const ctx = useContext(ThemeContext);
  if (!ctx) {
    // Defensive fallback for components that might mount outside the provider
    // during dev hot-reloads. Returns dark tokens and no-op setters.
    return { theme: 'dark', setTheme: () => {}, toggleTheme: () => {}, tokens: darkTokens };
  }
  return ctx;
}
