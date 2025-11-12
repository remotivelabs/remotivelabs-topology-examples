from dataclasses import dataclass
from typing import Any, AsyncGenerator

import evdev
from aiostream import Stream, stream

from sccm.config import Config
from sccm.device import Device


@dataclass
class DeviceEvent:
    device_name: str
    event: Any


class EvdevDevice(Device):
    """
    EvdevDevice is a Device that combines the event streams one or more evdev.InputDevice objects into a single stream.
    """

    def __init__(self, input_devices: list[evdev.InputDevice], config: Config):
        self.name = ",".join([device.name for device in input_devices])
        self.input_devices = input_devices
        self.config = config

    async def _open_device_stream(self, device: evdev.InputDevice) -> AsyncGenerator[DeviceEvent, None]:
        async for event in device.async_read_loop():
            yield DeviceEvent(device_name=device.name, event=event)

    async def _open_merged_stream_for_all_devices(self) -> Stream[DeviceEvent]:
        device_streams = [self._open_device_stream(device) for device in self.input_devices]
        return stream.merge(*device_streams)

    async def events_stream(self) -> AsyncGenerator[DeviceEvent, None]:
        merged_stream = await self._open_merged_stream_for_all_devices()
        async with merged_stream.stream() as streamer:
            async for event in streamer:
                yield event

    async def close(self) -> None:
        for device in self.input_devices:
            device.close()
