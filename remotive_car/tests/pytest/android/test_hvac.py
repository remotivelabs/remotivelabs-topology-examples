from __future__ import annotations

import re
from functools import partial
from typing import AsyncIterator

import pytest_asyncio
from adb_shell.adb_device import AdbDevice, AdbDeviceTcp
from hamcrest import equal_to
from remotivelabs.broker import BrokerClient
from remotivelabs.topology.testing.frames import capture_frames
from remotivelabs.topology.testing.hamcrest import await_at_most
from remotivelabs.topology.testing.retry import retry

import pytest

HVAC_TEMPERATURE_SET = 0x15600503
LEFT_AREA_ID = 1
INITIAL_TEMPERATURE = 25.0
TEMPERATURE_STEP = 0.5

CAR_SERVICE = "dumpsys activity service com.android.car"
SYSTEM_BAR_WINDOW = "BottomCarSystemBar"


def read_left_temperature(device: AdbDevice) -> float:
    """
    Read HVAC_TEMPERATURE_SET for the left side from the VHAL, through the car service shell.

    The value is the only float in the dump, so it is picked out without depending on the exact layout.
    """
    dump = str(device.shell(f"{CAR_SERVICE} get-property-value {HVAC_TEMPERATURE_SET} {LEFT_AREA_ID}"))
    match = re.search(r"-?\d+\.\d+", dump)
    if match is None:
        raise AssertionError(f"no temperature found in car service dump: {dump}")
    return float(match.group())


def system_bar_is_visible(device: AdbDevice) -> bool:
    """The temperature buttons live in SystemUI's BottomCarSystemBar window, which taps only reach once it is visible."""
    dump = str(device.shell("dumpsys window windows"))
    window = next((w for w in dump.split("Window #") if SYSTEM_BAR_WINDOW in w), "")
    return "isVisible=true" in window


@pytest_asyncio.fixture()
async def broker_client(request: pytest.FixtureRequest) -> AsyncIterator[BrokerClient]:
    url = request.config.getoption("broker_url")
    async with BrokerClient(url=url) as broker_client:
        yield broker_client


@pytest_asyncio.fixture()
async def adb_device(request: pytest.FixtureRequest) -> AsyncIterator[AdbDevice]:
    host = request.config.getoption("android_device_host")

    device = AdbDeviceTcp(host, 6520, default_transport_timeout_s=10.0)
    device.connect()

    # A slow device may still be booting, so wait for the UI the test interacts with
    await await_at_most(seconds=120).until(partial(system_bar_is_visible, device), equal_to(True))

    # Dismiss initial popup if there
    device.shell("input tap 1200 650")

    # Put the temperature on the left side (area_id: 1) back to a mid-range value, so that repeated runs
    # against the same device do not walk it down to the minimum. Android may override this while it is
    # still booting, which the test tolerates rather than relies on.
    device.shell(f"{CAR_SERVICE} set-property-value {HVAC_TEMPERATURE_SET} {LEFT_AREA_ID} {INITIAL_TEMPERATURE}")

    yield device

    # Send home command to close hvac panel if opened during test
    device.shell("input keyevent 3")


@pytest.mark.asyncio
@pytest.mark.android
async def test_update_hvac_left_temperature(broker_client: BrokerClient, adb_device: AdbDevice):
    async with capture_frames((broker_client, "HVAC-BodyCan0"), ["HVACControl"]) as cap:

        async def decrease_left_temperature() -> None:
            # Android resets the temperature to its own initial value at some point during boot, so read
            # the current value as late as possible and expect one step down from that
            temperature = read_left_temperature(adb_device)

            # Click the decrease temperature button on the left side of the UI
            adb_device.shell("input tap 250 1200")

            expected = temperature - TEMPERATURE_STEP
            await cap.wait_for_frame("HVACControl", {"HVACControl.LeftTemperature": expected}, timeout=15)

        # A tap that races a reset lowers a temperature we no longer expect, so press again from the new value.
        # Every attempt presses the button, so keep the number of attempts low to stay above the minimum
        # temperature, and give each attempt time to reach the bus instead.
        await retry(decrease_left_temperature, timeout=60)
