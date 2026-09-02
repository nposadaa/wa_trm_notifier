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
