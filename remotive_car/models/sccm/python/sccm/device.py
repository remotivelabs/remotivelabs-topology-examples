from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any, AsyncGenerator, Awaitable

from sccm.config import Config


class Device(ABC):
    """
    A device represents a real device comprised of one or more underlying virtual devices. Its purpose is to provide a combined stream of
    events to be consumed by a Target.
    """

    name: str
    """A name for the device, used for logging and debugging. May be the same as for its underlying virtual device(s)."""

    config: Config
    """The configuration for this device."""

    async def __aenter__(self) -> Device:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        await self.close()

    @abstractmethod
    def events_stream(self) -> AsyncGenerator[Any, None]: ...

    @abstractmethod
    def close(self) -> Awaitable[None]: ...
