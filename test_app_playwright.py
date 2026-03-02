"""
Playwright E2E tests for Stock Analysis Dashboard.

Run with:
    pip install playwright pytest-playwright
    playwright install chromium
    pytest test_app_playwright.py -v --headed

Or run directly:
    python test_app_playwright.py
"""

import re
import time
from playwright.sync_api import Page, expect, sync_playwright


BASE_URL = "http://options-dashboard.duckdns.org/"
TIMEOUT = 30000  # 30 seconds for Streamlit to load


def wait_for_streamlit(page: Page):
    """Wait for Streamlit app to fully load."""
    # Wait for the main Streamlit container
    page.wait_for_selector('[data-testid="stAppViewContainer"]', timeout=TIMEOUT)
    # Wait for any spinners to disappear
    time.sleep(2)  # Give charts time to render


def test_home_page_loads(page: Page):
    """Test that the home page loads correctly."""
    page.goto(BASE_URL)
    wait_for_streamlit(page)

    # Check title is present
    expect(page.locator("h1")).to_contain_text("Stock Analysis Dashboard")

    # Check main sections are present (use more specific selectors)
    expect(page.get_by_text("1. Getting Started")).to_be_visible()
    expect(page.get_by_text("2. Stock Analysis Page")).to_be_visible()
    expect(page.get_by_text("3. Drawdown Analysis Tab")).to_be_visible()
    expect(page.get_by_text("4. Put Options Education")).to_be_visible()
    expect(page.get_by_text("5. Technical Indicators")).to_be_visible()
    expect(page.get_by_text("6. Tips & FAQ")).to_be_visible()

    print("✓ Home page loads correctly")


def test_home_page_expanders(page: Page):
    """Test that expanders on home page work."""
    page.goto(BASE_URL)
    wait_for_streamlit(page)

    # Click on "New to Stock Analysis? Start Here" expander
    expander = page.get_by_text("New to Stock Analysis? Start Here")
    expander.click()
    time.sleep(0.5)

    # Check content is visible
    expect(page.get_by_text("Recommended Learning Path")).to_be_visible()

    print("✓ Home page expanders work")


def test_home_page_tabs(page: Page):
    """Test technical indicator tabs on home page."""
    page.goto(BASE_URL)
    wait_for_streamlit(page)

    # Find and click on tabs using role selector
    tabs = ["RSI", "MACD", "Bollinger Bands", "Moving Averages"]

    for tab_name in tabs:
        tab = page.get_by_role("tab", name=tab_name)
        tab.click()
        time.sleep(0.5)

    print("✓ Home page tabs work")


def test_navigate_to_stock_analysis(page: Page):
    """Test navigation to Stock Analysis page."""
    page.goto(BASE_URL)
    wait_for_streamlit(page)

    # Click on Stock Analysis in sidebar
    page.get_by_role("link", name="Stock Analysis").click()
    wait_for_streamlit(page)

    # Verify we're on the right page
    expect(page.locator("h1")).to_contain_text("Stock Analysis Dashboard")

    # Check sidebar elements are present
    expect(page.get_by_text("Configuration")).to_be_visible()

    print("✓ Navigation to Stock Analysis works")


def test_stock_analysis_single_stock(page: Page):
    """Test single stock analysis functionality."""
    page.goto(f"{BASE_URL}Stock_Analysis")
    wait_for_streamlit(page)

    # Check category selector is present (in sidebar)
    sidebar = page.get_by_test_id("stSidebar")
    expect(sidebar.get_by_text("Category")).to_be_visible()

    # Check stock selector is present
    expect(sidebar.get_by_text("Select Stock")).to_be_visible()

    # Click Load Data button (first primary button)
    load_button = page.get_by_test_id("stBaseButton-primary").first
    load_button.click()

    # Wait for data to load
    time.sleep(5)

    # Check that metrics are displayed
    expect(page.get_by_text("Last Close")).to_be_visible()
    expect(page.get_by_text("Trading Days")).to_be_visible()

    print("✓ Single stock analysis loads data")


def test_stock_analysis_tabs(page: Page):
    """Test the three analysis tabs."""
    page.goto(f"{BASE_URL}Stock_Analysis")
    wait_for_streamlit(page)

    # Load data first (use first primary button)
    load_button = page.get_by_test_id("stBaseButton-primary").first
    load_button.click()
    time.sleep(5)

    # Test each tab using role selector
    tabs = ["Price Analysis", "Drawdown Analysis", "Put Options Learning"]

    for tab_name in tabs:
        tab = page.get_by_role("tab", name=tab_name)
        tab.click()
        time.sleep(2)  # Wait for charts to render
        print(f"  - {tab_name} tab loaded")

    print("✓ All Stock Analysis tabs work")


def test_stock_analysis_compare_mode(page: Page):
    """Test compare stocks mode."""
    page.goto(f"{BASE_URL}Stock_Analysis")
    wait_for_streamlit(page)

    # Switch to Compare Stocks mode (use radio group)
    compare_radio = page.get_by_role("radio", name="Compare Stocks")
    compare_radio.click()
    time.sleep(1)

    # Check that tickers input is visible
    expect(page.get_by_text("Tickers (comma-separated)")).to_be_visible()

    # Load data (first primary button)
    load_button = page.get_by_test_id("stBaseButton-primary").first
    load_button.click()
    time.sleep(5)

    # Check that comparison chart title is shown
    expect(page.locator("h2").filter(has_text="Stock Comparison")).to_be_visible()

    print("✓ Compare stocks mode works")


def test_navigate_to_put_options(page: Page):
    """Test navigation to Put Options page."""
    page.goto(BASE_URL)
    wait_for_streamlit(page)

    # Click on Put Options in sidebar
    page.get_by_role("link", name="Put Options").click()
    wait_for_streamlit(page)

    # Verify we're on the right page
    expect(page.locator("h1")).to_contain_text("Put Options Education")

    print("✓ Navigation to Put Options works")


def test_put_options_page_loads(page: Page):
    """Test that Put Options page loads with data."""
    page.goto(f"{BASE_URL}Put_Options")
    wait_for_streamlit(page)

    # Check that AMD quote banner is visible
    expect(page.get_by_text("AMD:")).to_be_visible()

    # Check that data loaded message appears
    expect(page.get_by_text("Data loaded:")).to_be_visible()

    # Check tabs are present
    tabs = ["Put Options 101", "AMD Option Chain", "Risk Calculators", "Greeks Deep Dive"]
    for tab_name in tabs:
        expect(page.get_by_role("tab", name=tab_name)).to_be_visible()

    print("✓ Put Options page loads correctly")


def test_put_options_101_tab(page: Page):
    """Test Put Options 101 tab content."""
    page.goto(f"{BASE_URL}Put_Options")
    wait_for_streamlit(page)

    # Click on Put Options 101 tab
    page.get_by_role("tab", name="Put Options 101").click()
    time.sleep(1)

    # Check expanders are present
    expect(page.get_by_text("What is a Put Option?")).to_be_visible()
    expect(page.get_by_text("Key Terms Glossary")).to_be_visible()

    # Check payoff diagram section
    expect(page.get_by_text("Interactive Payoff Diagram")).to_be_visible()

    print("✓ Put Options 101 tab works")


def test_put_options_chain_tab(page: Page):
    """Test AMD Option Chain tab."""
    page.goto(f"{BASE_URL}Put_Options")
    wait_for_streamlit(page)

    # Click on AMD Option Chain tab
    page.get_by_role("tab", name="AMD Option Chain").click()
    time.sleep(2)

    # Check option chain elements
    expect(page.get_by_text("Put Option Chain")).to_be_visible()
    expect(page.get_by_text("Filter by Moneyness")).to_be_visible()

    # Use subheader selector for Premium vs Strike
    expect(page.locator("h3").filter(has_text="Premium vs Strike")).to_be_visible()

    print("✓ AMD Option Chain tab works")


def test_put_options_risk_calculators(page: Page):
    """Test Risk Calculators tab."""
    page.goto(f"{BASE_URL}Put_Options")
    wait_for_streamlit(page)

    # Click on Risk Calculators tab
    page.get_by_role("tab", name="Risk Calculators").click()
    time.sleep(2)

    # Check calculator sections (use numbered headings)
    expect(page.get_by_text("1. Break-Even Calculator")).to_be_visible()
    expect(page.get_by_text("2. Position Sizing Tool")).to_be_visible()
    expect(page.get_by_text("3. What-If Simulator")).to_be_visible()
    expect(page.get_by_text("4. P/L Scenario Table")).to_be_visible()
    expect(page.get_by_text("5. Time Decay Visualizer")).to_be_visible()

    print("✓ Risk Calculators tab works")


def test_put_options_greeks_tab(page: Page):
    """Test Greeks Deep Dive tab."""
    page.goto(f"{BASE_URL}Put_Options")
    wait_for_streamlit(page)

    # Click on Greeks Deep Dive tab
    page.get_by_role("tab", name="Greeks Deep Dive").click()
    time.sleep(2)

    # Check Greek sections (use exact match or more specific text)
    expect(page.get_by_text("Delta (Δ) - Direction Exposure")).to_be_visible()
    expect(page.get_by_text("Theta (Θ) - Time Decay")).to_be_visible()
    expect(page.get_by_text("Gamma (Γ) - Delta Acceleration")).to_be_visible()
    expect(page.get_by_text("Vega (ν) - Volatility Sensitivity")).to_be_visible()

    print("✓ Greeks Deep Dive tab works")


def test_download_csv_button(page: Page):
    """Test CSV download button on Stock Analysis."""
    page.goto(f"{BASE_URL}Stock_Analysis")
    wait_for_streamlit(page)

    # Load data (first primary button)
    load_button = page.get_by_test_id("stBaseButton-primary").first
    load_button.click()
    time.sleep(5)

    # Check download button is present
    download_button = page.get_by_role("button", name="Download Data as CSV")
    expect(download_button).to_be_visible()

    print("✓ Download CSV button is present")


def test_sidebar_quick_help(page: Page):
    """Test sidebar help expanders."""
    page.goto(f"{BASE_URL}Stock_Analysis")
    wait_for_streamlit(page)

    sidebar = page.get_by_test_id("stSidebar")

    # Check expanders in sidebar
    expect(sidebar.get_by_text("How to Use")).to_be_visible()
    expect(sidebar.get_by_text("Color Guide")).to_be_visible()

    # Click an expander
    sidebar.get_by_text("How to Use").click()
    time.sleep(0.5)

    print("✓ Sidebar quick help works")


def test_clear_cache_button(page: Page):
    """Test clear cache button."""
    page.goto(f"{BASE_URL}Stock_Analysis")
    wait_for_streamlit(page)

    # Check clear cache button is present
    clear_button = page.get_by_role("button", name="🔄 Clear Cache & Refresh")
    expect(clear_button).to_be_visible()

    print("✓ Clear cache button is present")


def test_stock_data_charts_render(page: Page):
    """Test that charts actually render after loading data."""
    page.goto(f"{BASE_URL}Stock_Analysis")
    wait_for_streamlit(page)

    # Load data
    load_button = page.get_by_test_id("stBaseButton-primary").first
    load_button.click()
    time.sleep(6)

    # Check that Plotly charts are present (they use specific class/container)
    charts = page.locator('[data-testid="stPlotlyChart"]')
    expect(charts.first).to_be_visible()

    print("✓ Stock data charts render correctly")


def test_live_amd_quote(page: Page):
    """Test that live AMD quote displays on Put Options page."""
    page.goto(f"{BASE_URL}Put_Options")
    wait_for_streamlit(page)

    # Check AMD price is displayed (should have $ symbol)
    expect(page.get_by_text(re.compile(r"AMD: \$\d+\.\d+"))).to_be_visible()

    # Check day change is shown
    expect(page.get_by_text("Day Change")).to_be_visible()

    print("✓ Live AMD quote displays correctly")


def run_all_tests():
    """Run all tests and report results."""
    print("\n" + "="*60)
    print("Stock Analysis Dashboard - Playwright E2E Tests")
    print(f"Testing: {BASE_URL}")
    print("="*60 + "\n")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        tests = [
            ("Home Page Loads", test_home_page_loads),
            ("Home Page Expanders", test_home_page_expanders),
            ("Home Page Tabs", test_home_page_tabs),
            ("Navigate to Stock Analysis", test_navigate_to_stock_analysis),
            ("Stock Analysis - Single Stock", test_stock_analysis_single_stock),
            ("Stock Analysis - Tabs", test_stock_analysis_tabs),
            ("Stock Analysis - Compare Mode", test_stock_analysis_compare_mode),
            ("Stock Data Charts Render", test_stock_data_charts_render),
            ("Navigate to Put Options", test_navigate_to_put_options),
            ("Put Options Page Loads", test_put_options_page_loads),
            ("Live AMD Quote", test_live_amd_quote),
            ("Put Options 101 Tab", test_put_options_101_tab),
            ("Put Options Chain Tab", test_put_options_chain_tab),
            ("Risk Calculators Tab", test_put_options_risk_calculators),
            ("Greeks Deep Dive Tab", test_put_options_greeks_tab),
            ("Download CSV Button", test_download_csv_button),
            ("Sidebar Quick Help", test_sidebar_quick_help),
            ("Clear Cache Button", test_clear_cache_button),
        ]

        passed = 0
        failed = 0
        errors = []

        for name, test_func in tests:
            try:
                print(f"\nRunning: {name}...")
                test_func(page)
                passed += 1
            except Exception as e:
                failed += 1
                error_msg = str(e).split('\n')[0][:100]
                errors.append((name, error_msg))
                print(f"✗ {name} FAILED: {error_msg}")

        browser.close()

        # Summary
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)
        print(f"Passed: {passed}/{len(tests)}")
        print(f"Failed: {failed}/{len(tests)}")

        if errors:
            print("\nFailed Tests:")
            for name, error in errors:
                print(f"  - {name}: {error}...")

        print("\n")
        return failed == 0


if __name__ == "__main__":
    import sys
    success = run_all_tests()
    sys.exit(0 if success else 1)
