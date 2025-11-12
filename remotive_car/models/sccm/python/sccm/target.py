from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class Target(ABC):
    """
    Target is a generic interface for sending events to a target system, e.g. a RemotiveBroker.

    As with the Mapper, the interface is simple but flexible, contributing to a readable and usable design.
    """

    async def __aenter__(self) -> Target:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass

    @abstractmethod
    async def send(self, output_event: Any) -> None:
        """Send an output event to the target"""
