from __future__ import annotations

import asyncio
from typing import AsyncIterator

import pytest_asyncio
from adb_shell.adb_device import AdbDevice, AdbDeviceTcp
from remotivelabs.broker import BrokerClient
from remotivelabs.topology.behavioral_model import PingRequest
from remotivelabs.topology.control.client import ControlClient
from remotivelabs.topology.testing.frames import capture_frames

import pytest

HVAC_TEMPERATURE_SET = 0x15600503


@pytest_asyncio.fixture()
async def broker_client(request: pytest.FixtureRequest) -> AsyncIterator[BrokerClient]:
    url = request.config.getoption("broker_url")
    async with BrokerClient(url=url) as broker_client, ControlClient(broker_client) as control_client:
        await control_client.send(target_ecu="IHU", request=PingRequest(), timeout=1, retries=10)
        yield broker_client


@pytest_asyncio.fixture()
async def adb_device(request: pytest.FixtureRequest) -> AsyncIterator[AdbDevice]:
    host = request.config.getoption("android_device_host")
    performance_level = request.config.getoption("android_performance_level")

    device = AdbDeviceTcp(host, 6520, default_transport_timeout_s=10.0)
    device.connect()

    # Dismiss initial popup if there
    device.shell("input tap 1028 333")

    # Reset temperature on the left side (area_id: 1) to 20 degrees
    device.shell(f"dumpsys activity service com.android.car inject-vhal-event {HVAC_TEMPERATURE_SET} 1 17")
    await asyncio.sleep(1)
    yield device

    # Send home command to close hvac panel if opened during test. Wait a short duration in case it is still in the process of opening
    if performance_level == "low":
        await asyncio.sleep(10)
    else:
        await asyncio.sleep(1)
    device.shell("input keyevent 3")


@pytest.mark.asyncio
@pytest.mark.android
async def test_update_hvac_left_temperature(broker_client: BrokerClient, adb_device: AdbDevice):
    # Click the decrease temperature button on the left side of the UI. The position of the button changes between initial boot and after
    # reboot, click both locations to ensure test works.
    adb_device.shell("input tap 280 750")
    adb_device.shell("input tap 350 750")

    async with capture_frames((broker_client, "HVAC-BodyCan0"), ["HVACControl"]) as cap:
        await cap.wait_for_frame("HVACControl", {"HVACControl.LeftTemperature": 16.5}, timeout=10)
