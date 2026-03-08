"""Pure functions for streak calculation — no I/O, no repos.

For daily habits, 'done yesterday' keeps a streak alive even if today
is not yet completed.

For weekly habits, ISO weeks (Monday–Sunday) are the unit.
"""

from datetime import date, timedelta

from habit_tracker.domain.completion import Completion
from habit_tracker.domain.habit import Habit
from habit_tracker.domain.periodicity import Periodicity


def _iso_week(d: date) -> tuple[int, int]:
    iso = d.isocalendar()
    return (iso[0], iso[1])


def calculate_current_streak(habit: Habit, completions: list[Completion], today: date) -> int:
    completed_dates = {c.completed_at.date() for c in completions}
    if habit.streak_started_at:
        completed_dates = {d for d in completed_dates if d >= habit.streak_started_at}

    if not completed_dates:
        return 0

    if habit.periodicity == Periodicity.DAILY:
        return _daily_streak(completed_dates, today)
    return _weekly_streak(completed_dates, today)


def _daily_streak(completed_dates: set[date], today: date) -> int:
    # Start counting from today if done, otherwise from yesterday
    cursor = today if today in completed_dates else today - timedelta(days=1)
    if cursor not in completed_dates:
        return 0

    streak = 0
    while cursor in completed_dates:
        streak += 1
        cursor -= timedelta(days=1)
    return streak


def _weekly_streak(completed_dates: set[date], today: date) -> int:
    completed_weeks = {_iso_week(d) for d in completed_dates}
    current_week = _iso_week(today)
    prev_week = _iso_week(today - timedelta(weeks=1))

    # Start from current week if done, otherwise previous week
    if current_week in completed_weeks:
        cursor_date = today
    elif prev_week in completed_weeks:
        cursor_date = today - timedelta(weeks=1)
    else:
        return 0

    streak = 0
    while _iso_week(cursor_date) in completed_weeks:
        streak += 1
        cursor_date -= timedelta(weeks=1)
    return streak


def calculate_longest_streak(habit: Habit, completions: list[Completion]) -> int:
    """Scan all completions regardless of streak_started_at."""
    if not completions:
        return 0

    if habit.periodicity == Periodicity.DAILY:
        return _longest_daily(completions)
    return _longest_weekly(completions)


def _longest_daily(completions: list[Completion]) -> int:
    days = sorted({c.completed_at.date() for c in completions})
    best = 1
    current = 1
    for i in range(1, len(days)):
        if days[i] - days[i - 1] == timedelta(days=1):
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def _longest_weekly(completions: list[Completion]) -> int:
    weeks = sorted({_iso_week(c.completed_at.date()) for c in completions})
    best = 1
    current = 1
    for i in range(1, len(weeks)):
        prev_year, prev_week = weeks[i - 1]
        cur_year, cur_week = weeks[i]
        # Check if consecutive ISO weeks
        prev_date = date.fromisocalendar(prev_year, prev_week, 1)
        cur_date = date.fromisocalendar(cur_year, cur_week, 1)
        if (cur_date - prev_date).days == 7:
            current += 1
            best = max(best, current)
        else:
            current = 1
    return best


def is_done_for_period(habit: Habit, completions: list[Completion], ref_date: date) -> bool:
    if habit.periodicity == Periodicity.DAILY:
        return any(c.completed_at.date() == ref_date for c in completions)
    ref_week = _iso_week(ref_date)
    return any(_iso_week(c.completed_at.date()) == ref_week for c in completions)


def get_pending_habits(
    habits: list[Habit],
    completions_by_habit: dict[int, list[Completion]],
    today: date,
) -> list[Habit]:
    return [h for h in habits if not is_done_for_period(h, completions_by_habit.get(h.id or 0, []), today)]
