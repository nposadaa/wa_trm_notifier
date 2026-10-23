from broadcaster import chat_name_matches_target, is_recoverable_browser_error


def test_recovers_from_closed_page_errors():
    assert is_recoverable_browser_error("Target page, context or browser has been closed")
    assert is_recoverable_browser_error("Page.evaluate: Execution context was destroyed")
    assert not is_recoverable_browser_error("Some unrelated runtime error")


def test_matches_chat_names_with_common_normalization():
    assert chat_name_matches_target("COP/USD Notifier", "COP/USD Notifier")
    assert chat_name_matches_target("COP / USD Notifier", "COP/USD Notifier")
    assert chat_name_matches_target("COP USD Notifier", "COP/USD Notifier")
    assert not chat_name_matches_target("Some Other Group", "COP/USD Notifier")


def test_deep_clean_preserves_service_worker(tmp_path, monkeypatch):
    import os
    import browser_config
    
    # Mock USER_DATA_DIR to point to tmp_path
    sw_dir = tmp_path / "Default" / "Service Worker"
    sw_dir.mkdir(parents=True)
    dummy_file = sw_dir / "dummy.txt"
    dummy_file.write_text("sw data")
    
    monkeypatch.setattr(browser_config, "USER_DATA_DIR", str(tmp_path))
    
    browser_config.deep_clean_profile()
    
    assert sw_dir.exists(), "Service Worker directory must be preserved during deep clean (DEC-034)"
    assert dummy_file.exists(), "Service Worker content must remain intact"


def test_normalize_message_text_preserves_spanish_accents_and_strips_emojis():
    from broadcaster import normalize_message_text

    raw = "📉 *Cierre Mercado USD/COP - 2026-10-23*\n\n💵 Cierre: $3,145.00 COP (-0.85% vs apertura)\n🔼 Máximo: $3,189.00 COP\n🔽 Mínimo: $3,136.00 COP\n📊 Apertura: $3,172.00 COP"
    normalized = normalize_message_text(raw)

    # Must preserve accented characters
    assert "Máximo" in normalized
    assert "Mínimo" in normalized
    # Must preserve currency, percentages, numbers
    assert "$3,145.00 COP" in normalized
    assert "(-0.85% vs apertura)" in normalized
    # Must remove markdown asterisks
    assert "*" not in normalized
    # Must strip emojis
    assert "📉" not in normalized
    assert "💵" not in normalized
    assert "🔼" not in normalized
    assert "🔽" not in normalized
    assert "📊" not in normalized


def test_extract_message_snippet_matches_whatsapp_dom_row():
    from broadcaster import extract_message_snippet, normalize_message_text

    closing_message = (
        "📉 *Cierre Mercado USD/COP - 2026-10-23*\n\n"
        "💵 Cierre: $3,145.00 COP (-0.85% vs apertura)\n"
        "🔼 Máximo: $3,189.00 COP\n"
        "🔽 Mínimo: $3,136.00 COP\n"
        "📊 Apertura: $3,172.00 COP\n\n"
        "Fuente: SET-ICAP (proxy.icap.com.co)"
    )

    snippet = extract_message_snippet(closing_message, max_chars=80)
    assert snippet == "Cierre Mercado USD/COP - 2026-10-23 Cierre: $3,145.00 COP (-0.85% vs apertura)"

    # WhatsApp DOM text from actual log
    dom_row_text = (
        "Cierre Mercado USD/COP - 2026-10-23\n"
        "Cierre: $3,145.00 COP (-0.85% vs apertura)\n"
        "Máximo: $3,189.00 COP\n"
        "Mínimo: $3,136.00 COP\n"
        "Apertura: $3,172.00 COP\n"
        "Fuente: SET-ICAP (proxy.icap.com.co)"
    )
    dom_normalized = normalize_message_text(dom_row_text)

    # Snippet must be a clean substring of normalized DOM row
    assert snippet in dom_normalized


def test_extract_message_snippet_morning_trm():
    from broadcaster import extract_message_snippet, normalize_message_text

    morning_message = (
        "📉 *TRM Oficial - 2026-10-23*\n\n"
        "💵 Valor: $3,191.47 COP (+ $27.71). Fuente: www.superfinanciera.gov.co"
    )
    snippet = extract_message_snippet(morning_message, max_chars=80)

    dom_row_text = "TRM Oficial - 2026-10-23 Valor: $3,191.47 COP (+ $27.71). Fuente: www.superfinanciera.gov.co"
    dom_normalized = normalize_message_text(dom_row_text)

    assert snippet in dom_normalized

