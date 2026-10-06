"""Unit tests for SET-ICAP USD/COP Spot Market Scraper."""
import os
import sys
from unittest.mock import patch, MagicMock
import pytest
import requests

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scraper import scrape_spot_market

MOCK_SPOT_PAYLOAD = {
    "market": "71",
    "message_count": 10,
    "messages": [
        {
            "id": 1000,
            "status": "success",
            "message": "Grafico de Monedas",
            "result": []
        },
        {
            "id": 1008,
            "status": "success",
            "message": "Estadísticas",
            "result": [
                {
                    "Merc.": "NEXT DAY",
                    "Moneda": "USD/COP",
                    "Plazo": "0 - 1 mes",
                    "Apertura": "3181.0000",
                    "Cierre": "3233.0000",
                },
                {
                    "Merc.": "SPOT",
                    "Moneda": "USD/COP",
                    "Plazo": "0",
                    "Monto Acumulado": "521853420.2600",
                    "Apertura": "3179.2000",
                    "Cierre": "3230.2500",
                    "No Trans.": "577",
                    "Promedio": "3210.8676",
                    "Precio mínimo": "3035.0000",
                    "Precio máximo": "3288.0000",
                    "Monto promedio": "904425.3384",
                    "Monto mínimo": "20.0000",
                    "Monto máximo": "75000000.0000",
                    "Monto último": "6000000.0000",
                    "Fecha": "2026-10-06"
                }
            ]
        }
    ]
}


class TestSpotScraperParsing:
    """Tests for parsing logic and metric calculations."""

    @patch("scraper.requests.get")
    def test_spot_scraper_happy_path(self, mock_get):
        """Verify successful extraction of all spot indicators."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = MOCK_SPOT_PAYLOAD
        mock_resp.raise_for_status.return_value = None
        mock_get.return_value = mock_resp

        res = scrape_spot_market(max_retries=1)

        assert "error" not in res
        assert res["cierre"] == 3230.25
        assert res["apertura"] == 3179.20
        assert res["promedio"] == 3210.8676
        assert res["minimo"] == 3035.0
        assert res["maximo"] == 3288.0
        assert res["transacciones"] == 577
        assert res["monto_acumulado"] == 521853420.26
        assert res["fecha"] == "2026-10-06"
        assert res["change"] == round(3230.25 - 3179.20, 2)
        assert res["change_pct"] == round(((3230.25 - 3179.20) / 3179.20) * 100, 4)
        assert "scraped_at" in res

    @patch("scraper.requests.get")
    def test_spot_scraper_key_variations_unaccented(self, mock_get):
        """Verify unaccented keys (Precio minimo/maximo) are handled cleanly."""
        payload = {
            "market": "71",
            "messages": [
                {
                    "id": 1008,
                    "result": [
                        {
                            "Merc.": "SPOT",
                            "Moneda": "USD/COP",
                            "Apertura": "3200.00",
                            "Cierre": "3210.00",
                            "Promedio": "3205.50",
                            "Precio minimo": "3195.00",
                            "Precio maximo": "3220.00",
                            "No Trans.": "120",
                            "Monto Acumulado": "1000000.00",
                            "Fecha": "2026-10-06"
                        }
                    ]
                }
            ]
        }
        mock_resp = MagicMock()
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        res = scrape_spot_market(max_retries=1)

        assert "error" not in res
        assert res["minimo"] == 3195.0
        assert res["maximo"] == 3220.0
        assert res["transacciones"] == 120

    @patch("scraper.requests.get")
    def test_spot_scraper_apertura_zero_division_guard(self, mock_get):
        """Ensure apertura = 0.0 does not trigger ZeroDivisionError."""
        payload = {
            "market": "71",
            "messages": [
                {
                    "id": 1008,
                    "result": [
                        {
                            "Merc.": "SPOT",
                            "Moneda": "USD/COP",
                            "Apertura": "0.00",
                            "Cierre": "3200.00",
                            "Promedio": "3200.00",
                            "Precio mínimo": "0.00",
                            "Precio máximo": "3200.00",
                            "No Trans.": "1",
                            "Monto Acumulado": "50000.00",
                            "Fecha": "2026-10-06"
                        }
                    ]
                }
            ]
        }
        mock_resp = MagicMock()
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        res = scrape_spot_market(max_retries=1)

        assert "error" not in res
        assert res["change_pct"] == 0.0


class TestSpotScraperErrorHandling:
    """Tests for edge cases and network retry mechanisms."""

    @patch("scraper.requests.get")
    def test_spot_scraper_missing_spot_row(self, mock_get):
        """Missing USD/COP SPOT row returns structured error dict."""
        payload = {
            "market": "71",
            "messages": [
                {
                    "id": 1008,
                    "result": [
                        {"Merc.": "NEXT DAY", "Moneda": "USD/EUR"}
                    ]
                }
            ]
        }
        mock_resp = MagicMock()
        mock_resp.json.return_value = payload
        mock_get.return_value = mock_resp

        res = scrape_spot_market(max_retries=1, retry_delay=0.01)
        assert "error" in res
        assert "not found" in res["error"].lower()

    @patch("scraper.requests.get")
    def test_spot_scraper_empty_messages(self, mock_get):
        """Empty messages payload returns structured error dict."""
        mock_resp = MagicMock()
        mock_resp.json.return_value = {"market": "71"}
        mock_get.return_value = mock_resp

        res = scrape_spot_market(max_retries=1, retry_delay=0.01)
        assert "error" in res

    @patch("scraper.time.sleep")
    @patch("scraper.requests.get")
    def test_spot_scraper_retry_on_transient_error(self, mock_get, mock_sleep):
        """Transient HTTP error triggers backoff and recovers on subsequent attempt."""
        err_resp = MagicMock()
        err_resp.raise_for_status.side_effect = requests.exceptions.HTTPError("500 Server Error")

        ok_resp = MagicMock()
        ok_resp.json.return_value = MOCK_SPOT_PAYLOAD
        ok_resp.raise_for_status.return_value = None

        mock_get.side_effect = [err_resp, ok_resp]

        res = scrape_spot_market(max_retries=2, retry_delay=0.01)

        assert "error" not in res
        assert res["cierre"] == 3230.25
        assert mock_get.call_count == 2
        assert mock_sleep.call_count == 1

    @patch("scraper.time.sleep")
    @patch("scraper.requests.get")
    def test_spot_scraper_fatal_connection_error(self, mock_get, mock_sleep):
        """Persistent connection failure returns clean error dict after exhausting retries."""
        mock_get.side_effect = requests.exceptions.ConnectionError("Connection refused")

        res = scrape_spot_market(max_retries=2, retry_delay=0.01)

        assert "error" in res
        assert "Connection refused" in res["error"]
        assert mock_get.call_count == 2
