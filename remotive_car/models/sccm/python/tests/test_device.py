from __future__ import annotations

from typing import AsyncGenerator, Mapping

import pytest

from sccm.device import Device
from sccm.mapper import Mapper


class InvertingMapper(Mapper):
    def map_event(self, input_event: int) -> int:
        # simply invert the event
        return -1 * input_event


class SimpleIntegerDevice(Device):
    name: str = "test"
    mappers: Mapping[str, Mapper]

    def __init__(self, devices: dict[str, list[int]], mappers: Mapping[str, Mapper]) -> None:
        self.devices = devices
        self.mappers = mappers

    async def events_stream(self) -> AsyncGenerator[int, None]:
        for device_name, inputs in self.devices.items():
            for input in inputs:
                yield self.mappers[device_name].map_event(input)

    async def close(self) -> None:
        pass


@pytest.mark.asyncio
async def test_feed_events_through_one_virtual_device_and_verify_output() -> None:
    # given
    virtual_device_name = "test"
    mappers = {virtual_device_name: InvertingMapper()}
    device = SimpleIntegerDevice(devices={virtual_device_name: [1, 2, 3, 4, 5]}, mappers=mappers)
    expected_outputs = [-1, -2, -3, -4, -5]
    actual_outputs = []

    # when
    async for event in device.events_stream():
        actual_outputs.append(event)

    # then
    assert actual_outputs == expected_outputs


@pytest.mark.asyncio
async def test_feed_events_through_multiple_virtual_devices_and_verify_output() -> None:
    # given
    device = SimpleIntegerDevice(
        devices={"device1": [1, 2, 3, 4, 5], "device2": [6, 7, 8, 9, 10]},
        mappers={"device1": InvertingMapper(), "device2": InvertingMapper()},
    )
    expected_outputs = [-1, -2, -3, -4, -5, -6, -7, -8, -9, -10]
    actual_outputs = []

    # when
    async for event in device.events_stream():
        actual_outputs.append(event)

    # then
    assert actual_outputs == expected_outputs
