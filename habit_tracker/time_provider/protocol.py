from datetime import date
from typing import Protocol


class TimeProvider(Protocol):
    def today(self) -> date: ...
