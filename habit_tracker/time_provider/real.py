from datetime import date


class RealTimeProvider:
    def today(self) -> date:
        return date.today()
