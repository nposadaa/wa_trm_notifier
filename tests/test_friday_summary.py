"""Tests for Friday Weekly Intelligence Summary feature in main.py."""
import os
import sys
import argparse
import logging
from unittest.mock import patch, MagicMock
import pytest

# Ensure project root is importable
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import main


def _make_args(**overrides):
    """Create a mock args namespace with sensible defaults."""
    defaults = {
        "headless": False,
        "discovery": False,
        "dry_run": True,
        "force": True,
        "friday": False,
    }
    defaults.update(overrides)
    return argparse.Namespace(**defaults)


# --- Mock TRM data for testing ---
MOCK_DAILY_DATA = {
    "trm": 3312.84,
    "previous_trm": 3341.23,
    "date": "2026-10-01",
    "scraped_at": "2026-10-01T14:00:00",
}

MOCK_WEEKLY_DATA = {
    "trm": 3312.84,
    "previous_trm": 3341.23,
    "date": "2026-10-01",
    "scraped_at": "2026-10-01T14:00:00",
    "weekly_max": 3349.63,
    "weekly_min": 3208.66,
    "weekly_start": 3208.66,
    "weekly_change": 104.18,
    "weekly_change_pct": 3.2468,
    "history": [],
}


class TestFridayDetection:
    """Tests for Friday auto-detection and --friday flag."""

    @patch("main.scrape_trm")
    @patch("main.get_cot_now")
    @patch("main.argparse.ArgumentParser.parse_args")
    def test_friday_flag_triggers_weekly_summary(self, mock_parse, mock_cot, mock_scrape, caplog):
        """--friday flag forces weekly summary even on non-Friday."""
        mock_parse.return_value = _make_args(friday=True)
        # Simulate a Wednesday (weekday=2)
        mock_dt = MagicMock()
        mock_dt.weekday.return_value = 2
        mock_dt.strftime.return_value = "2026-10-01"
        mock_cot.return_value = mock_dt

        # First call = daily scrape, second call = weekly scrape
        mock_scrape.side_effect = [MOCK_DAILY_DATA, MOCK_WEEKLY_DATA]

        with caplog.at_level(logging.INFO, logger="trm_notifier"):
            main.main()

        log_text = caplog.text
        assert "Resumen Semanal TRM" in log_text
        assert "Máximo semana" in log_text
        assert "Mínimo semana" in log_text
        assert "Variación semanal" in log_text

    @patch("main.scrape_trm")
    @patch("main.get_cot_now")
    @patch("main.argparse.ArgumentParser.parse_args")
    def test_non_friday_no_weekly_summary(self, mock_parse, mock_cot, mock_scrape, caplog):
        """Non-Friday without --friday flag should NOT include weekly summary."""
        mock_parse.return_value = _make_args(friday=False)
        # Simulate a Thursday (weekday=3)
        mock_dt = MagicMock()
        mock_dt.weekday.return_value = 3
        mock_dt.strftime.return_value = "2026-10-01"
        mock_cot.return_value = mock_dt

        mock_scrape.return_value = MOCK_DAILY_DATA

        with caplog.at_level(logging.INFO, logger="trm_notifier"):
            main.main()

        log_text = caplog.text
        assert "Resumen Semanal TRM" not in log_text

    @patch("main.scrape_trm")
    @patch("main.get_cot_now")
    @patch("main.argparse.ArgumentParser.parse_args")
    def test_real_friday_auto_triggers_weekly(self, mock_parse, mock_cot, mock_scrape, caplog):
        """Real Friday (weekday=4) auto-triggers weekly summary without --friday flag."""
        mock_parse.return_value = _make_args(friday=False)
        # Simulate a Friday (weekday=4)
        mock_dt = MagicMock()
        mock_dt.weekday.return_value = 4
        mock_dt.strftime.return_value = "2026-10-03"
        mock_cot.return_value = mock_dt

        mock_scrape.side_effect = [MOCK_DAILY_DATA, MOCK_WEEKLY_DATA]

        with caplog.at_level(logging.INFO, logger="trm_notifier"):
            main.main()

        log_text = caplog.text
        assert "Resumen Semanal TRM" in log_text


class TestFridayMessageFormatting:
    """Tests for the weekly summary message format."""

    @patch("main.scrape_trm")
    @patch("main.get_cot_now")
    @patch("main.argparse.ArgumentParser.parse_args")
    def test_weekly_max_min_in_message(self, mock_parse, mock_cot, mock_scrape, caplog):
        """Weekly max and min values are correctly formatted in the message."""
        mock_parse.return_value = _make_args(friday=True)
        mock_dt = MagicMock()
        mock_dt.weekday.return_value = 2
        mock_dt.strftime.return_value = "2026-10-01"
        mock_cot.return_value = mock_dt

        mock_scrape.side_effect = [MOCK_DAILY_DATA, MOCK_WEEKLY_DATA]

        with caplog.at_level(logging.INFO, logger="trm_notifier"):
            main.main()

        log_text = caplog.text
        assert "$3,349.63" in log_text  # weekly max
        assert "$3,208.66" in log_text  # weekly min

    @patch("main.scrape_trm")
    @patch("main.get_cot_now")
    @patch("main.argparse.ArgumentParser.parse_args")
    def test_weekly_trend_emoji_up(self, mock_parse, mock_cot, mock_scrape, caplog):
        """Positive weekly change shows 📈 trend emoji."""
        mock_parse.return_value = _make_args(friday=True)
        mock_dt = MagicMock()
        mock_dt.weekday.return_value = 2
        mock_dt.strftime.return_value = "2026-10-01"
        mock_cot.return_value = mock_dt

        mock_scrape.side_effect = [MOCK_DAILY_DATA, MOCK_WEEKLY_DATA]

        with caplog.at_level(logging.INFO, logger="trm_notifier"):
            main.main()

        log_text = caplog.text
        assert "+$104.18" in log_text

    @patch("main.scrape_trm")
    @patch("main.get_cot_now")
    @patch("main.argparse.ArgumentParser.parse_args")
    def test_weekly_trend_emoji_down(self, mock_parse, mock_cot, mock_scrape, caplog):
        """Negative weekly change shows 📉 trend emoji."""
        mock_parse.return_value = _make_args(friday=True)
        mock_dt = MagicMock()
        mock_dt.weekday.return_value = 2
        mock_dt.strftime.return_value = "2026-10-01"
        mock_cot.return_value = mock_dt

        down_weekly = dict(MOCK_WEEKLY_DATA)
        down_weekly["weekly_change"] = -50.0
        down_weekly["weekly_change_pct"] = -1.5

        mock_scrape.side_effect = [MOCK_DAILY_DATA, down_weekly]

        with caplog.at_level(logging.INFO, logger="trm_notifier"):
            main.main()

        log_text = caplog.text
        assert "-$50.00" in log_text

    @patch("main.scrape_trm")
    @patch("main.get_cot_now")
    @patch("main.argparse.ArgumentParser.parse_args")
    def test_weekly_data_unavailable_graceful(self, mock_parse, mock_cot, mock_scrape, caplog):
        """When weekly API call fails, message is sent without weekly block."""
        mock_parse.return_value = _make_args(friday=True)
        mock_dt = MagicMock()
        mock_dt.weekday.return_value = 2
        mock_dt.strftime.return_value = "2026-10-01"
        mock_cot.return_value = mock_dt

        # Weekly call returns error
        mock_scrape.side_effect = [MOCK_DAILY_DATA, {"error": "503 Server Error"}]

        with caplog.at_level(logging.INFO, logger="trm_notifier"):
            main.main()

        log_text = caplog.text
        assert "TRM Oficial" in log_text  # daily message present
        assert "Resumen Semanal TRM" not in log_text  # weekly block skipped
