from habit_tracker.domain.periodicity import Periodicity
from habit_tracker.fixtures.test_data import TEST_HABITS, TEST_MODE_START


class TestFixtureData:
    def test_five_habits_defined(self):
        assert len(TEST_HABITS) == 5

    def test_has_both_periodicities(self):
        periods = {h["periodicity"] for h in TEST_HABITS}
        assert periods == {Periodicity.DAILY, Periodicity.WEEKLY}

    def test_all_habits_have_completions(self):
        for h in TEST_HABITS:
            assert len(h["completion_offsets"]) > 0, f"{h['name']} has no completions"

    def test_all_completion_offsets_are_before_start_date(self):
        for h in TEST_HABITS:
            for offset in h["completion_offsets"]:
                assert offset < 0, f"{h['name']} has offset {offset} >= 0 (must be before start date)"

    def test_names_are_unique(self):
        names = [h["name"] for h in TEST_HABITS]
        assert len(names) == len(set(names))

    def test_start_date_is_march_first(self):
        from datetime import date

        assert TEST_MODE_START == date(2026, 3, 1)
