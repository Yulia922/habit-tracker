# Habit Tracker

A CLI tool for tracking daily and weekly habits. Create habits, check them off, and watch your streaks grow. The app greets you with a context-aware summary each session and provides analytics on your progress. Built with Python, SQLite, and Rich for a friendly terminal experience reminiscent of old-school phone interfaces.

## Features

- Create, edit, activate, and deactivate habits
- Support for daily and weekly habits
- Track habit completion history
- Calculate current and longest streaks
- Identify struggling habits
- CLI-based navigation interface
- SQLite database persistence
- Test mode with predefined habits
- Analytics dashboard

## Project Structure

habit_tracker/
│
├── cli/            # Command-line interface screens
├── domain/         # Core domain models and business logic
├── services/       # Application services and analytics
├── repositories/   # Data access layer
├── db/             # Database schema and engine
├── fixtures/       # Test data
├── time_provider/  # Time abstraction for testing
└── __main__.py     # Application entry point

## Setup

```bash
# Install dependencies
uv sync

# Run the app
uv run python -m habit_tracker

# Run in test mode (in-memory DB, preloaded habits, simulated date)
uv run python -m habit_tracker --test-mode
```

## Development

```bash
make fmt        # Format and auto-fix lint issues
make lint       # Check for lint errors
make typecheck  # Run mypy strict type checking
make test       # Run tests with coverage
make check      # All of the above in sequence
```
