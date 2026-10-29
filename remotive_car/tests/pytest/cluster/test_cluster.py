"""
Instrument cluster tests that only rely on the CAN buses the DIM is connected to: the frames the cluster
consumes are set on the mocks that send them, and what it reports back in `DIMStatus` on BodyCan0 is checked.

They pass for every DIM that follows the platform DBCs, the cluster container in this example as well as a
real cluster behind a broker on physical CAN, so the same tests serve both.
"""

from __future__ import annotations

from typing import AsyncIterator

import pytest_asyncio
from remotivelabs.broker import BrokerClient, RestbusSignalConfig
from remotivelabs.topology.testing.frames import capture_frames

import pytest

pytestmark = pytest.mark.cluster

ABS = "ABS-ChassisCan0"
BCM = "BCM-BodyCan0"
# Any broker on BodyCan0 sees what the DIM sends
BODY_CAN = BCM

DIM_STATUS = "DIMStatus"
SPEED = "DIMStatus.DisplayedSpeed"
GEAR = "DIMStatus.DisplayedGear"
LEFT_LAMP = "DIMStatus.LeftIndicatorLamp"
RIGHT_LAMP = "DIMStatus.RightIndicatorLamp"

LEFT_REQUEST = "TurnLightControl.LeftTurnLightRequest"
RIGHT_REQUEST = "TurnLightControl.RightTurnLightRequest"

# GearInfo.GearLeverPosition
LEVER_REVERSE = 0
LEVER_DRIVE = 1
# DIMStatus.DisplayedGear
GEAR_REVERSE = 1
GEAR_DRIVE = 2

# A BCM blinks the indicators at about 1 Hz; TurnLightControl is sent every 50 ms
BLINK = [1] * 10 + [0] * 10

# Covers the 3 s input timeout of the cluster plus a few status cycles
STATUS_TIMEOUT = 6.0


async def set_speed(broker_client: BrokerClient, meters_per_second: float) -> None:
    await broker_client.restbus.update_signals((ABS, [RestbusSignalConfig.set(name="UISpeedFrame.uispeed", value=meters_per_second)]))


async def set_gear_lever(broker_client: BrokerClient, position: int) -> None:
    await broker_client.restbus.update_signals((BCM, [RestbusSignalConfig.set(name="GearInfo.GearLeverPosition", value=position)]))


async def set_turn_lights(broker_client: BrokerClient, left: list[int], right: list[int]) -> None:
    """Send the turn light requests as repeating patterns, one value per TurnLightControl frame."""
    await broker_client.restbus.update_signals(
        (BCM, [RestbusSignalConfig(name=LEFT_REQUEST, loop=left), RestbusSignalConfig(name=RIGHT_REQUEST, loop=right)])
    )


@pytest_asyncio.fixture()
async def broker_client(request: pytest.FixtureRequest) -> AsyncIterator[BrokerClient]:
    url = request.config.getoption("broker_url")
    async with BrokerClient(url=url) as broker_client:
        # Start from a known state: standstill, in drive, turn lights off
        await set_speed(broker_client, 0)
        await set_gear_lever(broker_client, LEVER_DRIVE)
        await set_turn_lights(broker_client, left=[0], right=[0])
        yield broker_client
        await set_speed(broker_client, 0)
        await set_gear_lever(broker_client, LEVER_DRIVE)
        await set_turn_lights(broker_client, left=[0], right=[0])


# @req COMP_REQ_DIM_SPEED: Displayed speed follows UISpeedFrame
@pytest.mark.asyncio
async def test_displayed_speed_follows_ui_speed(broker_client: BrokerClient):
    async with capture_frames((broker_client, BODY_CAN), [DIM_STATUS]) as cap:
        await cap.wait_for_frame(DIM_STATUS, {SPEED: 0}, STATUS_TIMEOUT)

        await set_speed(broker_client, 20)  # m/s
        await cap.wait_for_frame(DIM_STATUS, {SPEED: 72}, STATUS_TIMEOUT)  # km/h

        await set_speed(broker_client, 0)
        await cap.wait_for_frame(DIM_STATUS, {SPEED: 0}, STATUS_TIMEOUT)


# @req COMP_REQ_DIM_GEAR: Displayed gear follows GearInfo
@pytest.mark.asyncio
async def test_displayed_gear_follows_gear_info(broker_client: BrokerClient):
    async with capture_frames((broker_client, BODY_CAN), [DIM_STATUS]) as cap:
        await cap.wait_for_frame(DIM_STATUS, {GEAR: GEAR_DRIVE}, STATUS_TIMEOUT)

        await set_gear_lever(broker_client, LEVER_REVERSE)
        await cap.wait_for_frame(DIM_STATUS, {GEAR: GEAR_REVERSE}, STATUS_TIMEOUT)

        await set_gear_lever(broker_client, LEVER_DRIVE)
        await cap.wait_for_frame(DIM_STATUS, {GEAR: GEAR_DRIVE}, STATUS_TIMEOUT)


# @req COMP_REQ_DIM_TURN_INDICATOR: Indicator lamps follow TurnLightControl
@pytest.mark.asyncio
async def test_left_indicator_lamp_follows_left_turn_light_request(broker_client: BrokerClient):
    await set_turn_lights(broker_client, left=BLINK, right=[0])
    async with capture_frames((broker_client, BODY_CAN), [DIM_STATUS]) as cap:
        # A full blink cycle on the left, while the right lamp stays off
        await cap.wait_for_frames(
            [
                (DIM_STATUS, {LEFT_LAMP: 1, RIGHT_LAMP: 0}),
                (DIM_STATUS, {LEFT_LAMP: 0, RIGHT_LAMP: 0}),
                (DIM_STATUS, {LEFT_LAMP: 1, RIGHT_LAMP: 0}),
            ],
            STATUS_TIMEOUT,
        )


@pytest.mark.asyncio
async def test_right_indicator_lamp_follows_right_turn_light_request(broker_client: BrokerClient):
    await set_turn_lights(broker_client, left=[0], right=BLINK)
    async with capture_frames((broker_client, BODY_CAN), [DIM_STATUS]) as cap:
        await cap.wait_for_frames(
            [
                (DIM_STATUS, {LEFT_LAMP: 0, RIGHT_LAMP: 1}),
                (DIM_STATUS, {LEFT_LAMP: 0, RIGHT_LAMP: 0}),
                (DIM_STATUS, {LEFT_LAMP: 0, RIGHT_LAMP: 1}),
            ],
            STATUS_TIMEOUT,
        )


# @req COMP_REQ_DIM_SPEED_TIMEOUT: Speed is blanked when UISpeedFrame stops
@pytest.mark.asyncio
async def test_speed_not_displayed_without_ui_speed_frames(broker_client: BrokerClient):
    """
    Stopping the ABS restbus is the closest a test gets to a lost sender. The cluster blanks the speed,
    reported as DisplayedSpeed NotDisplayed (255), until frames return.
    """
    async with capture_frames((broker_client, BODY_CAN), [DIM_STATUS]) as cap:
        await cap.wait_for_frame(DIM_STATUS, {SPEED: 0}, STATUS_TIMEOUT)

        await broker_client.restbus.stop(ABS)
        try:
            await cap.wait_for_frame(DIM_STATUS, {SPEED: 255}, STATUS_TIMEOUT)
        finally:
            await broker_client.restbus.start(ABS)
        await cap.wait_for_frame(DIM_STATUS, {SPEED: 0}, STATUS_TIMEOUT)
