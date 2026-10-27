from datetime import datetime
import sys
from types import SimpleNamespace

import main
import pytest


def test_success_marker_uses_current_day_for_stale_trm_data(tmp_path, monkeypatch):
    marker_file_morning = tmp_path / "last_success_morning.date"
    marker_file_legacy  = tmp_path / "last_success.date"
    fail_notify_file    = tmp_path / "last_fail_notify.date"

    monkeypatch.setattr(main, "LAST_SUCCESS_FILE_MORNING", str(marker_file_morning))
    monkeypatch.setattr(main, "LAST_SUCCESS_FILE_LEGACY",  str(marker_file_legacy))
    monkeypatch.setattr(main, "LAST_FAIL_NOTIFICATION",    str(fail_notify_file))
    monkeypatch.setattr(
        main,
        "get_cot_now",
        lambda: datetime(2026, 6, 22, 12, 0, tzinfo=main.COT_TZ),
    )
    monkeypatch.setattr(
        main,
        "scrape_trm",
        lambda **kwargs: {
            "trm": 3459.53,
            "previous_trm": 3439.91,
            "date": "2026-06-19",
        },
    )
    monkeypatch.setattr(main, "run_broadcaster", lambda *args, **kwargs: (True, False))
    monkeypatch.setattr(sys, "argv", ["main.py"])

    main.main()

    # Both per-edition and legacy files must record today's COT date
    assert marker_file_morning.read_text(encoding="utf-8").strip() == "2026-06-22"
    assert marker_file_legacy.read_text(encoding="utf-8").strip()  == "2026-06-22"


def test_closing_edition_success_marker(tmp_path, monkeypatch):
    marker_file_morning = tmp_path / "last_success_morning.date"
    marker_file_closing = tmp_path / "last_success_closing.date"
    marker_file_legacy  = tmp_path / "last_success.date"

    # Pre-populate morning marker to verify it is NOT overwritten
    marker_file_morning.write_text("2026-06-21", encoding="utf-8")
    marker_file_legacy.write_text("2026-06-21", encoding="utf-8")

    monkeypatch.setattr(main, "LAST_SUCCESS_FILE_MORNING", str(marker_file_morning))
    monkeypatch.setattr(main, "LAST_SUCCESS_FILE_CLOSING", str(marker_file_closing))
    monkeypatch.setattr(main, "LAST_SUCCESS_FILE_LEGACY",  str(marker_file_legacy))
    monkeypatch.setattr(
        main,
        "get_cot_now",
        lambda: datetime(2026, 6, 22, 18, 15, tzinfo=main.COT_TZ),
    )
    monkeypatch.setattr(
        main,
        "scrape_spot_market",
        lambda **kwargs: {
            "cierre": 3188.0,
            "apertura": 3193.0,
            "minimo": 3171.0,
            "maximo": 3197.75,
            "promedio": 3184.5,
            "change": -5.0,
            "change_pct": -0.1565,
            "fecha": "2026-06-22",
        },
    )
    monkeypatch.setattr(main, "run_broadcaster", lambda *args, **kwargs: (True, False))
    monkeypatch.setattr(sys, "argv", ["main.py", "--edition", "closing"])

    main.main()

    # Closing file recorded today's date
    assert marker_file_closing.read_text(encoding="utf-8").strip() == "2026-06-22"
    # Morning and legacy files remain untouched
    assert marker_file_morning.read_text(encoding="utf-8").strip() == "2026-06-21"
    assert marker_file_legacy.read_text(encoding="utf-8").strip()  == "2026-06-21"


def test_build_closing_message_formatting():
    # Negative change (down vs open)
    msg_neg = main.build_closing_message({
        "cierre": 3188.0,
        "apertura": 3193.0,
        "minimo": 3171.0,
        "maximo": 3197.75,
        "change": -5.0,
        "change_pct": -0.16,
        "fecha": "2026-10-22",
    })
    assert "📉 *Cierre Mercado USD/COP - 2026-10-22*" in msg_neg
    assert "💵 Cierre: $3,188.00 COP (-0.16% vs apertura)" in msg_neg
    assert "--" not in msg_neg

    # Positive change (up vs open)
    msg_pos = main.build_closing_message({
        "cierre": 3200.0,
        "apertura": 3193.0,
        "minimo": 3171.0,
        "maximo": 3205.0,
        "change": 7.0,
        "change_pct": 0.22,
        "fecha": "2026-10-22",
    })
    assert "📈 *Cierre Mercado USD/COP - 2026-10-22*" in msg_pos
    assert "💵 Cierre: $3,200.00 COP (+0.22% vs apertura)" in msg_pos
    assert "++" not in msg_pos

    # Flat change (equal to open)
    msg_flat = main.build_closing_message({
        "cierre": 3193.0,
        "apertura": 3193.0,
        "minimo": 3180.0,
        "maximo": 3200.0,
        "change": 0.0,
        "change_pct": 0.0,
        "fecha": "2026-10-22",
    })
    assert "➖ *Cierre Mercado USD/COP - 2026-10-22*" in msg_flat
    assert "💵 Cierre: $3,193.00 COP (0.00% vs apertura)" in msg_flat


def test_failed_outbox_run_schedules_profile_maintenance(tmp_path, monkeypatch):
    gsd_dir = tmp_path / ".gsd"
    gsd_dir.mkdir()
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(
        main,
        "get_cot_now",
        lambda: datetime(2026, 6, 22, 7, 0, tzinfo=main.COT_TZ),
    )
    monkeypatch.setattr(
        main,
        "scrape_trm",
        lambda **kwargs: {
            "trm": 3459.53,
            "previous_trm": 3439.91,
            "date": "2026-06-22",
        },
    )
    monkeypatch.setattr(main, "run_broadcaster", lambda *args, **kwargs: (False, True))
    monkeypatch.setattr(
        main,
        "logger",
        SimpleNamespace(info=lambda *args: None, error=lambda *args: None),
    )
    monkeypatch.setattr(sys, "argv", ["main.py"])

    with pytest.raises(SystemExit) as exc_info:
        main.main()

    assert exc_info.value.code == 1
    assert (gsd_dir / "needs_maintenance").read_text(encoding="utf-8")
