"""
Turn light tests that only rely on the BCM interface, i.e. the CAN signals it consumes and produces.

They pass for every BCM implementation in this example, both the python behavioral model and the FMU.
"""

from __future__ import annotations

import asyncio
from typing import AsyncIterator

import pytest_asyncio
from remotivelabs.broker import BrokerClient, RestbusSignalConfig
from remotivelabs.topology.behavioral_model import RebootRequest
from remotivelabs.topology.control import ControlClient
from remotivelabs.topology.testing.frames import capture_frames

import pytest

SCCM = "SCCM-DriverCan0"
FLCM = "FLCM-BodyCan0"
TURN_LIGHT_FRAME = "TurnLightControl"

LEFT = {"TurnLightControl.LeftTurnLightRequest": 1, "TurnLightControl.RightTurnLightRequest": 0}
RIGHT = {"TurnLightControl.LeftTurnLightRequest": 0, "TurnLightControl.RightTurnLightRequest": 1}
BOTH = {"TurnLightControl.LeftTurnLightRequest": 1, "TurnLightControl.RightTurnLightRequest": 1}
OFF = {"TurnLightControl.LeftTurnLightRequest": 0, "TurnLightControl.RightTurnLightRequest": 0}

# A full blink cycle: on -> off -> on
BLINK_LEFT = [(TURN_LIGHT_FRAME, LEFT), (TURN_LIGHT_FRAME, OFF), (TURN_LIGHT_FRAME, LEFT)]
BLINK_RIGHT = [(TURN_LIGHT_FRAME, RIGHT), (TURN_LIGHT_FRAME, OFF), (TURN_LIGHT_FRAME, RIGHT)]
BLINK_BOTH = [(TURN_LIGHT_FRAME, BOTH), (TURN_LIGHT_FRAME, OFF), (TURN_LIGHT_FRAME, BOTH)]

BLINK_TIMEOUT = 6.0


async def release_inputs(broker_client: BrokerClient) -> None:
    """Release the turn stalk and the hazard button."""
    await broker_client.restbus.update_signals(
        (
            SCCM,
            [
                RestbusSignalConfig.set(name="TurnStalk.TurnSignal", value=0),
                RestbusSignalConfig.set(name="HazardLightButton.HazardLightButton", value=0),
            ],
        )
    )


async def press_hazard_button(broker_client: BrokerClient) -> None:
    """Press and release the hazard button. Every press toggles the hazard lights."""
    await broker_client.restbus.update_signals(
        (SCCM, [RestbusSignalConfig(name="HazardLightButton.HazardLightButton", loop=[0], initial=[1])])
    )


async def turn_stalk(broker_client: BrokerClient, position: int) -> None:
    """Move the turn stalk: 0 = neutral, 1 = left, 2 = right."""
    await broker_client.restbus.update_signals((SCCM, [RestbusSignalConfig.set(name="TurnStalk.TurnSignal", value=position)]))


@pytest_asyncio.fixture()
async def broker_client(request: pytest.FixtureRequest) -> AsyncIterator[BrokerClient]:
    url = request.config.getoption("broker_url")
    async with BrokerClient(url=url) as broker_client, ControlClient(broker_client) as cc:
        # Both the turn stalk and the hazard button are stateful in the BCM, so start every test from a
        # known state: release the inputs, let the BCM see that, then reboot it.
        await release_inputs(broker_client)
        await asyncio.sleep(0.2)
        await cc.send(target_ecu="BCM", request=RebootRequest(), timeout=1, retries=10)
        yield broker_client
        await release_inputs(broker_client)


# @req COMP_REQ_BCM_TURN_LEFT: Turn Signal Left Activation
@pytest.mark.asyncio
async def test_turn_stalk_left_blinks_left_light(broker_client: BrokerClient):
    await turn_stalk(broker_client, 1)
    async with capture_frames((broker_client, FLCM), [TURN_LIGHT_FRAME]) as cap:
        await cap.wait_for_frames(BLINK_LEFT, BLINK_TIMEOUT)


# @req COMP_REQ_BCM_TURN_RIGHT: Turn Signal Right Activation
@pytest.mark.asyncio
async def test_turn_stalk_right_blinks_right_light(broker_client: BrokerClient):
    await turn_stalk(broker_client, 2)
    async with capture_frames((broker_client, FLCM), [TURN_LIGHT_FRAME]) as cap:
        await cap.wait_for_frames(BLINK_RIGHT, BLINK_TIMEOUT)


@pytest.mark.asyncio
async def test_turn_stalk_released_turns_light_off(broker_client: BrokerClient):
    await turn_stalk(broker_client, 1)
    async with capture_frames((broker_client, FLCM), [TURN_LIGHT_FRAME]) as cap:
        await cap.wait_for_frames(BLINK_LEFT, BLINK_TIMEOUT)

    await turn_stalk(broker_client, 0)
    async with capture_frames((broker_client, FLCM), [TURN_LIGHT_FRAME]) as cap:
        await cap.wait_for_frame(TURN_LIGHT_FRAME, OFF, timeout=BLINK_TIMEOUT)


# @req COMP_REQ_BCM_HAZARD: Hazard Light Signal Processing
@pytest.mark.asyncio
async def test_hazard_button_blinks_both_lights(broker_client: BrokerClient):
    await press_hazard_button(broker_client)
    async with capture_frames((broker_client, FLCM), [TURN_LIGHT_FRAME]) as cap:
        await cap.wait_for_frames(BLINK_BOTH, BLINK_TIMEOUT)


@pytest.mark.asyncio
async def test_second_hazard_button_press_turns_lights_off(broker_client: BrokerClient):
    await press_hazard_button(broker_client)
    async with capture_frames((broker_client, FLCM), [TURN_LIGHT_FRAME]) as cap:
        await cap.wait_for_frames(BLINK_BOTH, BLINK_TIMEOUT)

    await press_hazard_button(broker_client)
    async with capture_frames((broker_client, FLCM), [TURN_LIGHT_FRAME]) as cap:
        await cap.wait_for_frame(TURN_LIGHT_FRAME, OFF, timeout=BLINK_TIMEOUT)
