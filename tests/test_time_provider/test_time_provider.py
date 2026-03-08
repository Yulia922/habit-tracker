from datetime import date

from habit_tracker.time_provider.fake import FakeTimeProvider
from habit_tracker.time_provider.real import RealTimeProvider
from habit_tracker.time_provider.test_mode import TestModeTimeProvider


class TestRealTimeProvider:
    def test_returns_todays_date(self):
        assert RealTimeProvider().today() == date.today()


class TestTestModeTimeProvider:
    def test_starts_at_march_first_2026(self):
        assert TestModeTimeProvider().today() == date(2026, 3, 1)

    def test_advance_day_increments_by_one(self):
        p = TestModeTimeProvider()
        p.advance_day()
        assert p.today() == date(2026, 3, 2)

    def test_advance_multiple_days(self):
        p = TestModeTimeProvider()
        for _ in range(5):
            p.advance_day()
        assert p.today() == date(2026, 3, 6)

    def test_each_instance_starts_fresh(self):
        p1 = TestModeTimeProvider()
        p1.advance_day()
        p2 = TestModeTimeProvider()
        assert p2.today() == date(2026, 3, 1)


class TestFakeTimeProvider:
    def test_returns_configured_date(self):
        p = FakeTimeProvider(date(2026, 6, 15))
        assert p.today() == date(2026, 6, 15)

    def test_advance_moves_forward(self):
        p = FakeTimeProvider(date(2026, 3, 1))
        p.advance(days=3)
        assert p.today() == date(2026, 3, 4)
