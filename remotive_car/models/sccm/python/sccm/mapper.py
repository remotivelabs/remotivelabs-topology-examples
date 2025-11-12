from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Mapper(ABC):
    """
    The purpose of the Mapper interface is to map an input event to an output event. It is purposefully simple, allowing flexibility in the
    implementation, but still contributing to a readable and usable design.

    It is unavoidable that the Mapper knows about both the input and output domains. This makes the Mapper a central component in the
    system, and care should be taken to make it as readable as possible.
    """

    @abstractmethod
    def map_event(self, input_event: Any) -> Any:
        """Convert an input event to an output event."""
