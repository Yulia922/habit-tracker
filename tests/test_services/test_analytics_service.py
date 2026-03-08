from datetime import date, datetime

import pytest

from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.services.streak_calculator import (
    calculate_current_streak,
    calculate_longest_streak,
    get_pending_habits,
    is_done_for_period,
)


def _completions(habit_id: int, dates: list[date]) -> list[Completion]:
    return [Completion(habit_id=habit_id, completed_at=datetime.combine(d, datetime.min.time())) for d in dates]


class TestCurrentStreakDaily:
    @pytest.mark.parametrize(
        "dates,today,expected",
        [
            # Consecutive days ending today
            ([date(2026, 3, 6), date(2026, 3, 7), date(2026, 3, 8)], date(2026, 3, 8), 3),
            # Consecutive days ending yesterday (today not yet done — still alive)
            ([date(2026, 3, 6), date(2026, 3, 7)], date(2026, 3, 8), 2),
            # Gap breaks streak
            ([date(2026, 3, 5), date(2026, 3, 7)], date(2026, 3, 8), 1),
            # No completions
            ([], date(2026, 3, 8), 0),
            # Single completion today
            ([date(2026, 3, 8)], date(2026, 3, 8), 1),
            # Old completion, nothing recent
            ([date(2026, 2, 1)], date(2026, 3, 8), 0),
        ],
    )
    def test_streak(self, dates, today, expected):
        habit = Habit(name="X", periodicity=Periodicity.DAILY)
        assert calculate_current_streak(habit, _completions(1, dates), today) == expected


class TestCurrentStreakWeekly:
    @pytest.mark.parametrize(
        "dates,today,expected",
        [
            # 3 consecutive ISO weeks
            ([date(2026, 2, 16), date(2026, 2, 23), date(2026, 3, 2)], date(2026, 3, 8), 3),
            # Gap of one week
            ([date(2026, 2, 9), date(2026, 3, 2)], date(2026, 3, 8), 1),
            # Empty
            ([], date(2026, 3, 8), 0),
            # Current week not done, previous week done — still alive
            ([date(2026, 3, 2)], date(2026, 3, 8), 1),
        ],
    )
    def test_streak(self, dates, today, expected):
        habit = Habit(name="X", periodicity=Periodicity.WEEKLY)
        assert calculate_current_streak(habit, _completions(1, dates), today) == expected


class TestStreakStartedAt:
    def test_current_streak_ignores_completions_before_reset(self):
        habit = Habit(name="X", periodicity=Periodicity.DAILY, streak_started_at=date(2026, 3, 5))
        completions = _completions(1, [date(2026, 3, 3), date(2026, 3, 6), date(2026, 3, 7), date(2026, 3, 8)])
        assert calculate_current_streak(habit, completions, date(2026, 3, 8)) == 3

    def test_longest_streak_includes_all_history(self):
        habit = Habit(name="X", periodicity=Periodicity.DAILY, streak_started_at=date(2026, 3, 5))
        completions = _completions(1, [date(2026, 3, d) for d in range(1, 9)])
        assert calculate_longest_streak(habit, completions) == 8


class TestLongestStreak:
    def test_finds_best_run_not_current(self):
        habit = Habit(name="X", periodicity=Periodicity.DAILY)
        dates = [
            date(2026, 2, 1), date(2026, 2, 2), date(2026, 2, 3), date(2026, 2, 4), date(2026, 2, 5),  # 5
            # gap
            date(2026, 3, 7), date(2026, 3, 8),  # 2
        ]
        assert calculate_longest_streak(habit, _completions(1, dates)) == 5


class TestIsDoneForPeriod:
    def test_daily_done_today(self):
        habit = Habit(name="X", periodicity=Periodicity.DAILY)
        completions = _completions(1, [date(2026, 3, 8)])
        assert is_done_for_period(habit, completions, date(2026, 3, 8))

    def test_daily_not_done_different_day(self):
        habit = Habit(name="X", periodicity=Periodicity.DAILY)
        completions = _completions(1, [date(2026, 3, 8)])
        assert not is_done_for_period(habit, completions, date(2026, 3, 7))

    def test_weekly_done_same_iso_week(self):
        habit = Habit(name="X", periodicity=Periodicity.WEEKLY)
        # Wed Mar 4 and Sun Mar 8 are same ISO week (Mon Mar 2 – Sun Mar 8)
        completions = _completions(1, [date(2026, 3, 4)])
        assert is_done_for_period(habit, completions, date(2026, 3, 8))

    def test_weekly_not_done_different_week(self):
        habit = Habit(name="X", periodicity=Periodicity.WEEKLY)
        completions = _completions(1, [date(2026, 3, 4)])
        assert not is_done_for_period(habit, completions, date(2026, 3, 9))  # next Monday


class TestGetPendingHabits:
    def test_excludes_completed_habits(self):
        gym = Habit(id=1, name="Gym", periodicity=Periodicity.DAILY)
        run = Habit(id=2, name="Run", periodicity=Periodicity.DAILY)
        completions_map = {1: _completions(1, [date(2026, 3, 1)])}
        result = get_pending_habits([gym, run], completions_map, date(2026, 3, 1))
        assert result == [run]

    def test_all_done_returns_empty(self):
        gym = Habit(id=1, name="Gym", periodicity=Periodicity.DAILY)
        completions_map = {1: _completions(1, [date(2026, 3, 1)])}
        assert get_pending_habits([gym], completions_map, date(2026, 3, 1)) == []

    def test_none_done_returns_all(self):
        gym = Habit(id=1, name="Gym", periodicity=Periodicity.DAILY)
        run = Habit(id=2, name="Run", periodicity=Periodicity.DAILY)
        assert get_pending_habits([gym, run], {}, date(2026, 3, 1)) == [gym, run]
