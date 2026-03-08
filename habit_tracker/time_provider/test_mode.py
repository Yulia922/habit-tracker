from datetime import date, timedelta

TEST_MODE_START = date(2026, 3, 1)


class TestModeTimeProvider:
    """In-memory simulated clock starting at 2026-03-01.

    Each instance starts fresh — no shared state between runs.
    Used by --test-mode and useful for integration tests.
    """

    def __init__(self) -> None:
        self._current = TEST_MODE_START

    def today(self) -> date:
        return self._current

    def advance_day(self) -> None:
        self._current += timedelta(days=1)
