#!/usr/bin/env python3
"""
Replace inline hex color literals in chart components with theme-token
references. Run AFTER importing `useTheme` and adding `const t = useTheme().tokens;`
inside each component (done by hand).

Replacements (case-insensitive):
  '#0f172a' / "#0f172a" / ="#0f172a"  -> t.surface  / {t.surface}
  ...

Use --dry-run to preview.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

HEX_TO_TOKEN = {
    '#0f172a': 'surface',
    '#1e293b': 'surfaceElev',
    '#334155': 'border',
    '#475569': 'axis',
    '#64748b': 'textFaint',
    '#94a3b8': 'textMute',
    '#cbd5e1': 'textMid',
    '#e2e8f0': 'text',
    '#f1f5f9': 'text',
    '#10b981': 'positive',
    '#ef4444': 'negative',
    '#f43f5e': 'negative',
    '#f59e0b': 'warning',
    '#fbbf24': 'warningStrong',
    '#fb923c': 'warningStrong',
    '#818cf8': 'indigo',
    '#6366f1': 'indigoStrong',
    '#a5b4fc': 'indigoFaint',
    '#a78bfa': 'cat7',
    '#ec4899': 'cat6',
    '#06b6d4': 'info',
}

# Build patterns for each hex (longest first, case-insensitive)
KEYS = sorted(HEX_TO_TOKEN.keys(), key=len, reverse=True)


def transform(src: str) -> str:
    out = src
    for hex_lit in KEYS:
        token = HEX_TO_TOKEN[hex_lit]
        ci = re.compile(re.escape(hex_lit), re.IGNORECASE)

        # 1) JSX attribute form:  attr="#hex"  ->  attr={t.token}
        attr_pat = re.compile(
            rf'(\w+)\s*=\s*"' + re.escape(hex_lit) + r'"',
            re.IGNORECASE,
        )
        out = attr_pat.sub(lambda m: f'{m.group(1)}={{t.{token}}}', out)

        # 2) String-literal form (single or double quotes):
        #    '#hex'  ->  t.token
        #    "#hex"  ->  t.token
        str_pat = re.compile(
            r"(['\"])" + re.escape(hex_lit) + r"\1",
            re.IGNORECASE,
        )
        out = str_pat.sub(f't.{token}', out)

    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('files', nargs='+')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    changed = 0
    for path in args.files:
        p = Path(path)
        src = p.read_text()
        new = transform(src)
        if new != src:
            changed += 1
            if args.dry_run:
                print(f'would rewrite {p}')
            else:
                p.write_text(new)
                print(f'rewrote {p}')
    print(f'\n{"would change" if args.dry_run else "changed"} {changed} files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
