from __future__ import annotations

import asyncio
from functools import partial
from typing import AsyncIterator

import pytest_asyncio
from adb_shell.adb_device import AdbDevice, AdbDeviceTcp
from hamcrest import equal_to
from remotivelabs.broker import BrokerClient, Signal
from remotivelabs.topology.behavioral_model import PingRequest
from remotivelabs.topology.control.client import ControlClient
from remotivelabs.topology.testing.retry import await_at_most

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
    device = AdbDeviceTcp(host, 6520, default_transport_timeout_s=5.0)
    device.connect()

    # Dismiss initial popup if there
    device.shell("input tap 1028 333")

    # Reset temperature on the left side (area_id: 1) to 20 degrees
    device.shell(f"dumpsys activity service com.android.car inject-vhal-event {HVAC_TEMPERATURE_SET} 1 17")
    await asyncio.sleep(1)
    yield device

    # Send home command to close hvac panel if opened during test. Wait a short duration in case it is still in the process of opening
    await asyncio.sleep(1)
    device.shell("input keyevent 3")


async def take_values(sub: AsyncIterator[list[Signal]], x: int = 1):
    result = {}
    for _ in range(x):
        signals = await sub.__anext__()
        result.update({s.name: s.value for s in signals})
    return result


@pytest.mark.asyncio
@pytest.mark.android
async def test_update_hvac_left_temperature(broker_client: BrokerClient, adb_device: AdbDevice):
    # Click the decrease temperature button on the left side of the UI. The position of the button changes between initial boot and after
    # reboot, click both locations to ensure test works.
    adb_device.shell("input tap 280 750")
    adb_device.shell("input tap 350 750")

    sub = await broker_client.subscribe(("HVAC-BodyCan0", ["HVACControl.LeftTemperature"]))
    await await_at_most(seconds=5).until(
        partial(take_values, sub),
        equal_to({"HVACControl.LeftTemperature": 16.5}),
    )
