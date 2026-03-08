import argparse
import sys


def main() -> None:
    parser = argparse.ArgumentParser(description="Habit Tracker — track daily and weekly habits")
    parser.add_argument(
        "--test-mode", action="store_true", help="Run with in-memory DB and simulated date (2026-03-01)"
    )
    args = parser.parse_args()

    if args.test_mode:
        print("Habit Tracker [test mode] — coming soon")
    else:
        print("Habit Tracker — coming soon")

    sys.exit(0)


if __name__ == "__main__":
    main()
