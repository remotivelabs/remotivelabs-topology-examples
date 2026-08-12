from __future__ import annotations

import asyncio
from typing import AsyncIterator

import evdev
import structlog
from remotivelabs.broker import SignalValue
from remotivelabs.topology.mapping.models import SignalAddress

logger = structlog.get_logger(__name__)


def _find_device(name: str) -> evdev.InputDevice | None:
    """Return the connected evdev device with this name, or None if not present."""
    for path in evdev.list_devices():
        try:
            device = evdev.InputDevice(path)
        except OSError:
            # device vanished between listing and opening; ignore this path
            continue
        if device.name == name:
            return device
        device.close()
    return None


class EvdevSource:
    """
    A mapping `Source` that yields values for a single evdev input (device + event type/code).

    One source owns one event stream: it waits for its named device to connect, reads the
    device's events, yields the value of every event matching `source_type`/`source_code`, and
    reconnects on its own when the device drops. Connect/reconnect/disconnect is handled per
    device — there is no central wait-for-all-devices step.

    The source self-heals from all of its own failures (device enumeration, open, and read):
    any error is logged and the source backs off and reconnects, so a flaky USB device never
    propagates out to tear down the broker connection or the other sources.
    """

    def __init__(self, address: SignalAddress, *, poll_interval_sec: float = 1.0) -> None:
        """Build from a `custom.evdev` mapping address, reading its device/source_type/source_code fields."""
        self._device_name: str = address["device"]
        self._source_type = int(address["source_type"])
        self._source_code = int(address["source_code"])
        self._poll_interval_sec = poll_interval_sec

    async def signals(self) -> AsyncIterator[SignalValue]:
        while True:
            device = None
            try:
                device = await self._await_device()
                logger.debug("evdev device connected", device=self._device_name, type=self._source_type, code=self._source_code)
                async for value in self._read(device):
                    yield value
            except OSError:
                logger.info("evdev device disconnected; reconnecting", device=self._device_name)
            except Exception:
                logger.exception("evdev source error; reconnecting", device=self._device_name)
            finally:
                if device is not None:
                    device.close()
            await asyncio.sleep(self._poll_interval_sec)

    async def _read(self, device: evdev.InputDevice) -> AsyncIterator[SignalValue]:
        async for event in device.async_read_loop():
            if event.type == self._source_type and event.code == self._source_code:
                yield event.value

    async def _await_device(self) -> evdev.InputDevice:
        while True:
            device = _find_device(self._device_name)
            if device is not None:
                return device
            await asyncio.sleep(self._poll_interval_sec)
