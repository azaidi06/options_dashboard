"""Smoke tests for options routes.

These hit live data sources (parquet files) and assert the contract — not
the values. They are tagged 'integration' so they can be skipped in
environments without the data files.
"""
import pytest


@pytest.mark.integration
def test_options_tickers_lists_known_symbols(client):
    resp = client.get("/api/options/tickers")
    assert resp.status_code == 200
    tickers = resp.json()
    assert isinstance(tickers, list)
    assert any(t.upper() == "AAPL" for t in tickers)


@pytest.mark.integration
def test_options_dates_for_aapl(client):
    resp = client.get("/api/options/AAPL/dates")
    assert resp.status_code == 200
    dates = resp.json()
    assert isinstance(dates, list)
    assert len(dates) > 0
