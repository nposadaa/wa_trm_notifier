from broadcaster import is_recoverable_browser_error


def test_recovers_from_closed_page_errors():
    assert is_recoverable_browser_error("Target page, context or browser has been closed")
    assert is_recoverable_browser_error("Page.evaluate: Execution context was destroyed")
    assert not is_recoverable_browser_error("Some unrelated runtime error")
