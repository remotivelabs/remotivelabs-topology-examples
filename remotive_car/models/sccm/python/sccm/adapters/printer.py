from __future__ import annotations

from typing import Any

from typing_extensions import Self

from sccm.target import Target


class Printer(Target):
    """
    Used for debugging/development when you don't want to connect to a real target.

    See -p/--print-only argument.
    """

    def __init__(self) -> None:
        self._name = "Printer"

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        pass

    async def send(self, output_event: Any) -> None:
        print(output_event)
