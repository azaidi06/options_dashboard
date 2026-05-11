#!/usr/bin/env python3
"""
Bulk-rewrite Tailwind utility classes for light/dark theme support.

Currently the codebase uses bare slate-* / indigo-* utilities assuming a
dark UI. After this script:
  bg-slate-900            -> bg-white dark:bg-slate-900
  hover:bg-slate-800      -> hover:bg-stone-100 hover:dark:bg-slate-800
  text-slate-300/80       -> text-stone-700/80 dark:text-slate-300/80
  text-indigo-400         -> text-indigo-700 dark:text-indigo-400

The `dark:` variant is wired in index.css to fire when [data-theme=dark].

Run from anywhere:
  python scripts/rewrite_theme_classes.py frontend/src
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# ---- mappings (dark utility number -> light utility) ------------------------

SLATE_BG = {
    '950': 'stone-100',
    '900': 'white',
    '800': 'stone-100',
    '700': 'stone-200',
    '600': 'stone-300',
    '500': 'stone-400',
}
SLATE_TEXT = {
    '50':  'stone-950',
    '100': 'stone-900',
    '200': 'stone-800',
    '300': 'stone-700',
    '400': 'stone-600',
    '500': 'stone-500',
    '600': 'stone-400',
    '700': 'stone-300',
}
SLATE_BORDER = {
    '950': 'stone-200',
    '900': 'stone-200',
    '800': 'stone-200',
    '700': 'stone-300',
    '600': 'stone-400',
    '500': 'stone-500',
}
SLATE_PLACEHOLDER = {
    '500': 'stone-400',
    '400': 'stone-500',
}
SLATE_RING = {
    '700': 'stone-300',
    '600': 'stone-400',
    '500': 'stone-500',
}
SLATE_DIVIDE = {
    '800': 'stone-200',
    '700': 'stone-300',
}
INDIGO_TEXT = {
    '500': 'indigo-600',
    '400': 'indigo-700',
    '300': 'indigo-700',
}

# Accent text colors (red/emerald/rose/amber/blue/purple) — the dark-mode
# shades 300 / 400 are too pale on a white background. Map them to the
# 700 (and 600) shades for light, keep the originals via dark: prefix.
ACCENT_FAMILIES = ('red', 'emerald', 'rose', 'amber', 'orange', 'green',
                   'blue', 'purple', 'pink', 'fuchsia', 'cyan', 'sky',
                   'teal', 'violet', 'yellow')
ACCENT_LIGHT_FOR = {
    '300': '700',
    '400': '700',
    '500': '600',
}

# ---- regex pieces -----------------------------------------------------------

# Match any chain of variant prefixes that does NOT already include `dark:`.
# Variants are like "hover:", "focus:", "group-hover:", "md:", etc.
# Negative lookahead ensures we don't transform classes already qualified.
PREFIX = r'((?:(?!dark:)[a-z][\w-]*:)*)'
NUM = r'(\d+)'
OPAC = r'(/[\d.]+)?'
# Left word boundary: also reject ':' so we don't re-match inside an
# already-prefixed class like `dark:text-slate-200` (the `text-slate-200`
# piece would otherwise re-match because ':' isn't a word char).
WB_L = r'(?<![\w:/-])'
WB_R = r'(?![\w-])'


def make_slate_rule(prop: str, mapping: dict[str, str]):
    pattern = re.compile(rf'{WB_L}{PREFIX}{prop}-slate-{NUM}{OPAC}{WB_R}')

    def repl(m: re.Match) -> str:
        prefix = m.group(1) or ''
        n = m.group(2)
        opacity = m.group(3) or ''
        if n not in mapping:
            return m.group(0)
        light = mapping[n]
        light_cls = f'{prefix}{prop}-{light}{opacity}'
        dark_cls = f'{prefix}dark:{prop}-slate-{n}{opacity}'
        return f'{light_cls} {dark_cls}'

    return pattern, repl


def make_indigo_text_rule():
    pattern = re.compile(rf'{WB_L}{PREFIX}text-indigo-{NUM}{OPAC}{WB_R}')

    def repl(m: re.Match) -> str:
        prefix = m.group(1) or ''
        n = m.group(2)
        opacity = m.group(3) or ''
        if n not in INDIGO_TEXT:
            return m.group(0)
        light_cls = f'{prefix}text-{INDIGO_TEXT[n]}{opacity}'
        dark_cls = f'{prefix}dark:text-indigo-{n}{opacity}'
        return f'{light_cls} {dark_cls}'

    return pattern, repl


def make_accent_text_rule():
    families = '|'.join(ACCENT_FAMILIES)
    pattern = re.compile(rf'{WB_L}{PREFIX}text-({families})-{NUM}{OPAC}{WB_R}')

    def repl(m: re.Match) -> str:
        prefix = m.group(1) or ''
        family = m.group(2)
        n = m.group(3)
        opacity = m.group(4) or ''
        if n not in ACCENT_LIGHT_FOR:
            return m.group(0)
        light_cls = f'{prefix}text-{family}-{ACCENT_LIGHT_FOR[n]}{opacity}'
        dark_cls = f'{prefix}dark:text-{family}-{n}{opacity}'
        return f'{light_cls} {dark_cls}'

    return pattern, repl


RULES = [
    make_slate_rule('bg', SLATE_BG),
    make_slate_rule('text', SLATE_TEXT),
    make_slate_rule('border', SLATE_BORDER),
    make_slate_rule('placeholder', SLATE_PLACEHOLDER),
    make_slate_rule('ring', SLATE_RING),
    make_slate_rule('divide', SLATE_DIVIDE),
    make_indigo_text_rule(),
    make_accent_text_rule(),
]


def transform(src: str) -> str:
    out = src
    for pat, repl in RULES:
        out = pat.sub(repl, out)
    return out


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('roots', nargs='+', help='Directories or files to rewrite')
    ap.add_argument('--ext', default='.jsx,.js,.tsx,.ts,.html', help='Comma-separated extensions')
    ap.add_argument('--dry-run', action='store_true')
    args = ap.parse_args()

    exts = tuple(e.strip() for e in args.ext.split(',') if e.strip())
    files: list[Path] = []
    for root in args.roots:
        p = Path(root)
        if p.is_file():
            files.append(p)
        else:
            for ext in exts:
                files.extend(p.rglob(f'*{ext}'))

    changed = 0
    for f in sorted(set(files)):
        try:
            src = f.read_text()
        except Exception as e:
            print(f'skip {f}: {e}', file=sys.stderr)
            continue
        new = transform(src)
        if new != src:
            changed += 1
            if args.dry_run:
                print(f'would rewrite {f}')
            else:
                f.write_text(new)
                print(f'rewrote {f}')
    print(f'\n{"would change" if args.dry_run else "changed"} {changed} files')
    return 0


if __name__ == '__main__':
    sys.exit(main())
