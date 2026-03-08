.PHONY: fmt lint typecheck test check

fmt:
	uv run ruff format .
	uv run ruff check --fix .

lint:
	uv run ruff check .

typecheck:
	uv run mypy habit_tracker

test:
	uv run pytest

check: fmt lint typecheck test
