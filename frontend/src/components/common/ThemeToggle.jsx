import { Sun, Moon } from 'lucide-react';
import { useTheme } from '../../theme/ThemeContext';

export default function ThemeToggle({ className = '' }) {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';
  const Icon = isDark ? Sun : Moon;
  return (
    <button
      type="button"
      onClick={toggleTheme}
      aria-label={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      title={isDark ? 'Switch to light mode' : 'Switch to dark mode'}
      className={`inline-flex items-center justify-center w-9 h-9 rounded-lg border transition-colors duration-200
        bg-white border-stone-200 text-stone-600 hover:bg-stone-100 hover:text-stone-900
        dark:bg-slate-800/80 dark:border-slate-700 dark:text-slate-400 dark:hover:bg-slate-700 dark:hover:text-slate-100
        ${className}`}
    >
      <Icon className="w-4 h-4" strokeWidth={2} />
    </button>
  );
}
