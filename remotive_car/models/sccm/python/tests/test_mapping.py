from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import AsyncIterator

from remotivelabs.broker import SignalValue
from remotivelabs.topology.mapping.models import CustomSignalAddress

from sccm.evdev_source import EvdevSource


@dataclass
class _Event:
    type: int
    code: int
    value: int


class _FakeDevice:
    """Stand-in for evdev.InputDevice — only async_read_loop/close are used by EvdevSource."""

    def __init__(self, events: list[_Event]) -> None:
        self._events = events

    async def async_read_loop(self) -> AsyncIterator[_Event]:
        for event in self._events:
            yield event

    def close(self) -> None:
        pass


async def _collect(agen: AsyncIterator[SignalValue]) -> list[SignalValue]:
    return [value async for value in agen]


# --- EvdevSource ---


def _address(device: str = "wheel", source_type: int = 3, source_code: int = 0) -> CustomSignalAddress:
    return CustomSignalAddress.model_validate(
        {"type": "custom.evdev", "signal": "ABS_X", "device": device, "source_type": source_type, "source_code": source_code}
    )


def test_evdev_source_yields_only_matching_events() -> None:
    source = EvdevSource(_address(source_type=3, source_code=0))
    device = _FakeDevice([_Event(3, 0, 100), _Event(3, 1, 5), _Event(1, 0, 7), _Event(3, 0, 200)])
    assert asyncio.run(_collect(source._read(device))) == [100, 200]


def test_evdev_source_reads_ref_extras() -> None:
    source = EvdevSource(_address())
    assert (source._device_name, source._source_type, source._source_code) == ("wheel", 3, 0)
