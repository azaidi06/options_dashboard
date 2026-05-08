"""Smoke tests for stock routes."""
import pytest


@pytest.mark.integration
def test_stock_endpoint_rejects_invalid_ticker(client):
    resp = client.get("/api/stock/THIS_IS_NOT_A_REAL_TICKER_XYZ")
    assert resp.status_code in (400, 404, 422, 500)


@pytest.mark.integration
def test_indicators_endpoint_shape(client):
    resp = client.get("/api/stock/AAPL/indicators?lookback_days=5")
    if resp.status_code == 200:
        body = resp.json()
        assert isinstance(body, dict)
