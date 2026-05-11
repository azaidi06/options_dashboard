"""Capture dark + light theme screenshots of the options dashboard.

Run with the dev server already up at http://localhost:5173.
"""
import sys
import time
from pathlib import Path
from playwright.sync_api import sync_playwright

OUT_DIR = Path(sys.argv[1] if len(sys.argv) > 1 else '.')
URLS = [
    ('home', 'http://localhost:5173/'),
    ('learn', 'http://localhost:5173/learn'),
]


def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={'width': 1440, 'height': 900})
        page = ctx.new_page()
        for theme in ('dark', 'light'):
            # Pre-seed localStorage for the next page navigation
            page.goto('http://localhost:5173/', wait_until='domcontentloaded')
            page.evaluate(
                f"localStorage.setItem('options-dashboard-theme', '{theme}')"
            )
            for name, url in URLS:
                page.goto(url, wait_until='networkidle')
                # Recharts and font load can take a beat
                page.wait_for_timeout(800)
                out = OUT_DIR / f'options_dashboard_{name}_{theme}.png'
                page.screenshot(path=str(out), full_page=True)
                print(f'wrote {out}')
        browser.close()


if __name__ == '__main__':
    main()
