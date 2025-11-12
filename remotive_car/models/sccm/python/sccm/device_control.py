from __future__ import annotations

import asyncio

import evdev
import structlog

from sccm.adapters.evdev_device import EvdevDevice
from sccm.config import Config
from sccm.device import Device

logger = structlog.get_logger(__name__)


class DeviceControl:
    """
    DeviceControl is responsible for configuring a Device using the given config.

    It may happen that the device is not connected when the app is started. If so, the DeviceControl will wait for the device to connect.
    """

    def __init__(self, config: Config, timeout_in_sec: float = 60.0):
        self.config = config
        self.timeout_in_sec = timeout_in_sec

    def _poll_for_connected_devices(self) -> EvdevDevice | None:
        """
        Polls for evdev.InputDevices and return a Device object if a matching device is found, else None.
        """
        # We need a map of evdev device names to evdev devices, because the evdev device name is the only persistent identifier.
        # evdev usually identifies the device by its path (e.g. /dev/input/event0).
        connected_evdev_devices = {evdev.InputDevice(path).name: evdev.InputDevice(path) for path in evdev.list_devices()}
        logger.debug("polling for connected devices", devices=connected_evdev_devices)
        if not connected_evdev_devices:
            return None

        # now try to find all (virtual) devices in each config so that we can create a complete EvdevDevice
        wanted_devices = self.config.devices.keys()
        matches: list[evdev.InputDevice] = [connected_evdev_devices[name] for name in wanted_devices if name in connected_evdev_devices]
        if len(matches) == len(self.config.devices):
            return EvdevDevice(input_devices=matches, config=self.config)
        return None

    async def _wait_for_device_ready(self, polling_interval_in_sec: float = 1.0, timeout_in_sec: float = 60.0) -> Device:
        """
        Waits for a device to connect, and then returns the device.

        Raises TimeoutError if no device is found within the timeout.
        """
        time_left = timeout_in_sec
        while time_left > 0:
            device = self._poll_for_connected_devices()
            if device:
                logger.info("device found", device=device)
                return device

            await asyncio.sleep(polling_interval_in_sec)
            time_left -= polling_interval_in_sec

        raise TimeoutError("No device found")

    def create_task(self) -> asyncio.Task[Device]:
        """
        Returns a task that will wait for a device to connect and then return it.

        Raises TimeoutError if no device is found within the timeout.
        """
        return asyncio.create_task(self._wait_for_device_ready(timeout_in_sec=self.timeout_in_sec))
