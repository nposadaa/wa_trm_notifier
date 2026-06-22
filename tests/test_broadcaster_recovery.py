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
