"""Common utilities and enums for soliddriver-checks API."""

from enum import Enum, unique


@unique
class Evaluation(Enum):
    """Evaluation levels for KMP and KM analysis.

    PASS (1): Check passed, meets SUSE requirements
    WARNING (2): Non-critical issue, potential problem but not blocking
    ERROR (3): Critical issue, fails SUSE requirements
    """
    PASS = 1
    WARNING = 2
    ERROR = 3

    def __str__(self):
        return self.name

    def __int__(self):
        return self.value

    def to_json(self):
        return {"level": self.name, "value": self.value}
