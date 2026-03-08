import pytest

from habit_tracker.cli.navigation import NavigationError, NavigationStack


class FakeScreen:
    pass


class TestNavigationStack:
    def test_push_makes_screen_current(self):
        stack = NavigationStack()
        s = FakeScreen()
        stack.push(s)
        assert stack.current() is s

    def test_pop_returns_to_previous(self):
        stack = NavigationStack()
        s1, s2 = FakeScreen(), FakeScreen()
        stack.push(s1)
        stack.push(s2)
        stack.pop()
        assert stack.current() is s1

    def test_pop_empty_raises(self):
        stack = NavigationStack()
        stack.push(FakeScreen())
        stack.pop()
        with pytest.raises(NavigationError):
            stack.pop()

    def test_current_empty_raises(self):
        with pytest.raises(NavigationError):
            NavigationStack().current()

    def test_replace_swaps_top(self):
        stack = NavigationStack()
        s1, s2 = FakeScreen(), FakeScreen()
        stack.push(s1)
        stack.replace(s2)
        assert stack.current() is s2
        # Only one item on stack — pop should leave it empty
        stack.pop()
        with pytest.raises(NavigationError):
            stack.current()

    def test_depth(self):
        stack = NavigationStack()
        assert stack.depth == 0
        stack.push(FakeScreen())
        stack.push(FakeScreen())
        assert stack.depth == 2
