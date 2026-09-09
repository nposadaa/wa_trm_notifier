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

