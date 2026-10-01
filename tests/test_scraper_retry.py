import requests
from unittest.mock import MagicMock
import pytest
import scraper

def test_scrape_trm_success_first_try(monkeypatch):
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = [
        {"valor": "3184.0", "vigenciadesde": "2026-09-02T00:00:00.000"},
        {"valor": "3213.97", "vigenciadesde": "2026-09-01T00:00:00.000"}
    ]
    
    get_calls = []
    def mock_get(url, timeout):
        get_calls.append((url, timeout))
        return mock_resp

    monkeypatch.setattr(requests, "get", mock_get)

    result = scraper.scrape_trm(max_retries=3, retry_delay=0.01)
    assert len(get_calls) == 1
    assert result["trm"] == 3184.0
    assert result["previous_trm"] == 3213.97
    assert result["date"] == "2026-09-02"

def test_scrape_trm_recovers_after_503(monkeypatch):
    mock_fail_resp = MagicMock()
    mock_fail_resp.raise_for_status.side_effect = requests.HTTPError("503 Server Error: Service Unavailable")

    mock_ok_resp = MagicMock()
    mock_ok_resp.raise_for_status.return_value = None
    mock_ok_resp.json.return_value = [
        {"valor": "3184.0", "vigenciadesde": "2026-09-02T00:00:00.000"}
    ]

    call_count = [0]
    def mock_get(url, timeout):
        call_count[0] += 1
        if call_count[0] == 1:
            return mock_fail_resp
        return mock_ok_resp

    monkeypatch.setattr(requests, "get", mock_get)

    result = scraper.scrape_trm(max_retries=3, retry_delay=0.01)
    assert call_count[0] == 2
    assert result["trm"] == 3184.0
    assert result["previous_trm"] == 3184.0
    assert result["date"] == "2026-09-02"

def test_scrape_trm_exhausts_retries(monkeypatch):
    mock_fail_resp = MagicMock()
    mock_fail_resp.raise_for_status.side_effect = requests.HTTPError("503 Server Error: Service Unavailable")

    call_count = [0]
    def mock_get(url, timeout):
        call_count[0] += 1
        return mock_fail_resp

    monkeypatch.setattr(requests, "get", mock_get)

    result = scraper.scrape_trm(max_retries=3, retry_delay=0.01)
    assert call_count[0] == 3
    assert "error" in result
    assert "503 Server Error" in result["error"]

def test_scrape_trm_weekly_aggregation(monkeypatch):
    """Verify weekly metrics are computed correctly from 5 mock trading days."""
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = [
        {"valor": "3300.00", "vigenciadesde": "2026-10-01T00:00:00.000"},  # latest (trm)
        {"valor": "3250.50", "vigenciadesde": "2026-09-30T00:00:00.000"},
        {"valor": "3350.75", "vigenciadesde": "2026-09-29T00:00:00.000"},  # weekly max
        {"valor": "3180.00", "vigenciadesde": "2026-09-28T00:00:00.000"},  # weekly min
        {"valor": "3200.00", "vigenciadesde": "2026-09-27T00:00:00.000"},  # weekly start (oldest)
    ]

    monkeypatch.setattr(requests, "get", lambda url, timeout: mock_resp)

    result = scraper.scrape_trm(max_retries=1, retry_delay=0.01, limit=7)

    # Standard daily keys preserved
    assert result["trm"] == 3300.00
    assert result["previous_trm"] == 3250.50
    assert result["date"] == "2026-10-01"

    # Weekly aggregation keys
    assert result["weekly_max"] == 3350.75
    assert result["weekly_min"] == 3180.00
    assert result["weekly_start"] == 3200.00
    assert result["weekly_change"] == 100.00  # 3300 - 3200
    assert abs(result["weekly_change_pct"] - 3.125) < 0.01  # (100 / 3200) * 100

    # History list
    assert len(result["history"]) == 5
    assert result["history"][0]["date"] == "2026-10-01"
    assert result["history"][-1]["value"] == 3200.00

def test_scrape_trm_default_limit_no_weekly_keys(monkeypatch):
    """Verify default limit=2 does NOT include weekly aggregation keys."""
    mock_resp = MagicMock()
    mock_resp.raise_for_status.return_value = None
    mock_resp.json.return_value = [
        {"valor": "3300.00", "vigenciadesde": "2026-10-01T00:00:00.000"},
        {"valor": "3250.50", "vigenciadesde": "2026-09-30T00:00:00.000"},
    ]

    monkeypatch.setattr(requests, "get", lambda url, timeout: mock_resp)

    result = scraper.scrape_trm(max_retries=1, retry_delay=0.01)

    assert result["trm"] == 3300.00
    assert "weekly_max" not in result
    assert "weekly_min" not in result
    assert "history" not in result

