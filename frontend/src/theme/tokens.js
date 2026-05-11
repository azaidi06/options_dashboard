/**
 * Chart / inline-style color tokens for both themes.
 *
 * Tailwind utility classes (bg-slate-*, etc.) handle most of the UI
 * via the `dark:` variant in index.css. These tokens cover the inline
 * Recharts props (stroke, fill, tick.fill) where CSS variables aren't
 * easy to thread through SVG attribute strings.
 */

export const darkTokens = {
  // surfaces
  bg: '#020617',
  surface: '#0F172A',
  surfaceElev: '#1E293B',
  border: '#334155',
  borderMute: '#1E293B',

  // typography
  text: '#F1F5F9',
  textMid: '#CBD5E1',
  textMute: '#94A3B8',
  textFaint: '#64748B',

  // chart axes / grid
  axis: '#475569',
  axisTick: '#94A3B8',
  grid: '#334155',
  gridFaint: '#1E293B',

  // accents
  indigo: '#818CF8',
  indigoStrong: '#6366F1',
  indigoFaint: '#A5B4FC',

  // semantic
  positive: '#10B981',
  positiveStrong: '#059669',
  negative: '#EF4444',
  negativeStrong: '#DC2626',
  warning: '#F59E0B',
  warningStrong: '#FBBF24',
  info: '#06B6D4',

  // categorical (for series with many lines)
  cat1: '#818CF8',
  cat2: '#10B981',
  cat3: '#F59E0B',
  cat4: '#EF4444',
  cat5: '#06B6D4',
  cat6: '#EC4899',
  cat7: '#A78BFA',
  cat8: '#FB923C',

  // tooltip
  tooltipBg: '#1E293B',
  tooltipBorder: '#334155',
  tooltipText: '#F1F5F9',
};

export const lightTokens = {
  // surfaces (stone palette)
  bg: '#F5F5F4',
  surface: '#FFFFFF',
  surfaceElev: '#FAFAF9',
  border: '#D6D3D1',
  borderMute: '#E7E5E4',

  // typography
  text: '#1C1917',
  textMid: '#44403C',
  textMute: '#78716C',
  textFaint: '#A8A29E',

  // chart axes / grid
  axis: '#A8A29E',
  axisTick: '#57534E',
  grid: '#E7E5E4',
  gridFaint: '#F5F5F4',

  // accents — darkened for AA contrast on light bg
  indigo: '#4F46E5',
  indigoStrong: '#4338CA',
  indigoFaint: '#6366F1',

  // semantic
  positive: '#059669',
  positiveStrong: '#047857',
  negative: '#DC2626',
  negativeStrong: '#B91C1C',
  warning: '#D97706',
  warningStrong: '#B45309',
  info: '#0891B2',

  // categorical
  cat1: '#4F46E5',
  cat2: '#059669',
  cat3: '#B45309',
  cat4: '#DC2626',
  cat5: '#0891B2',
  cat6: '#BE185D',
  cat7: '#6D28D9',
  cat8: '#C2410C',

  // tooltip
  tooltipBg: '#FFFFFF',
  tooltipBorder: '#D6D3D1',
  tooltipText: '#1C1917',
};

export const TOKENS_BY_THEME = {
  dark: darkTokens,
  light: lightTokens,
};
