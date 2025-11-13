from __future__ import annotations

import asyncio
import re
from functools import partial
from typing import AsyncIterator

import pytest_asyncio
from adb_shell.adb_device import AdbDevice, AdbDeviceTcp
from hamcrest import equal_to
from remotivelabs.broker import BrokerClient, RestbusSignalConfig
from remotivelabs.topology.behavioral_model import PingRequest
from remotivelabs.topology.control.client import ControlClient
from remotivelabs.topology.testing.retry import await_at_most

import pytest


@pytest_asyncio.fixture()
async def broker_client(request: pytest.FixtureRequest) -> AsyncIterator[BrokerClient]:
    url = request.config.getoption("broker_url")
    async with BrokerClient(url=url) as broker_client, ControlClient(broker_client) as control_client:
        await control_client.send(target_ecu="IHU", request=PingRequest(), timeout=1, retries=10)
        yield broker_client

        await broker_client.restbus.update_signals(
            (
                "TCU-BodyCan0",
                [
                    RestbusSignalConfig.set(name="LocationFrame.Latitude", value=-48.526),
                    RestbusSignalConfig.set(name="LocationFrame.Longitude", value=-123.236),
                ],
            )
        )


@pytest_asyncio.fixture()
async def adb_device(request: pytest.FixtureRequest) -> AsyncIterator[AdbDevice]:
    host = request.config.getoption("android_device_host")
    device = AdbDeviceTcp(host, 6520, default_transport_timeout_s=5.0)
    device.connect()

    """
    To be able to read the location data from within Android we rely on 'adb shell dumpsys location'. This will however
    not fetch the latest location that exists within the GNSS provider. The latest location doesn't make its way into
    the rest of the Android system until an application requests the location. To do this we use the Cuttlefish built-in
    location test app.

    We open this app and push a button which will trigger a request for the latest location.
    """

    # Dismiss initial popup if there
    device.shell("input tap 1028 333")

    # Grant permissions to the location test app
    device.shell("pm grant --user 10 com.google.android.car.adaslocation android.permission.ACCESS_COARSE_LOCATION")
    device.shell("pm grant --user 10 com.google.android.car.adaslocation android.permission.ACCESS_FINE_LOCATION")

    # Start location test app
    device.shell("am start -n com.google.android.car.adaslocation/com.google.android.car.adaslocation.AdasLocationActivity")
    await asyncio.sleep(1)
    yield device

    # Send home command to close test app
    device.shell("input keyevent 3")


async def get_location(adb_device: AdbDevice):
    # Push button to trigger new location fetch from providers
    adb_device.shell("input tap 387 478")
    await asyncio.sleep(2)
    location_dump = str(adb_device.shell("dumpsys location"))

    match = re.search(r"location=Location\[gps ([\d\.\-]+),([\d\.\-]+)", location_dump)
    if match:
        latitude = float(match.group(1))
        longitude = float(match.group(2))
        return (latitude, longitude)

    return (0.0, 0.0)


@pytest.mark.asyncio
@pytest.mark.android
async def test_feed_location_to_android(broker_client: BrokerClient, adb_device: AdbDevice):
    await broker_client.restbus.update_signals(
        (
            "TCU-BodyCan0",
            [
                RestbusSignalConfig.set(name="LocationFrame.Latitude", value=69.059967),
                RestbusSignalConfig.set(name="LocationFrame.Longitude", value=20.548735),
            ],
        )
    )

    await await_at_most(seconds=10).until(
        partial(get_location, adb_device),
        equal_to((69.059967, 20.548735)),
    )
