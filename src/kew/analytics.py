"""Queue metrics and wait-time estimation."""

from dataclasses import dataclass


@dataclass(slots=True)
class QueueEstimator:
    """Estimate a queue wait using a configurable service time."""

    seconds_per_person: float = 60.0

    def __post_init__(self) -> None:
        """Validate estimator configuration."""
        if self.seconds_per_person < 0:
            raise ValueError("seconds_per_person must be non-negative")

    def estimate_seconds(self, person_count: int) -> float:
        """Return the expected wait for a non-negative person count."""
        if person_count < 0:
            raise ValueError("person_count must be non-negative")
        return person_count * self.seconds_per_person
