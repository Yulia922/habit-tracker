from datetime import date, timedelta


class FakeTimeProvider:
    """Controllable time provider for unit tests."""

    def __init__(self, today: date) -> None:
        self._today = today

    def today(self) -> date:
        return self._today

    def advance(self, days: int = 1) -> None:
        self._today += timedelta(days=days)
