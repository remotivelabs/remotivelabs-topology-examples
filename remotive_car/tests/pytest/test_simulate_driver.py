from __future__ import annotations

from typing import AsyncIterator

import pytest_asyncio
from remotivelabs.broker import BrokerClient, RestbusSignalConfig
from remotivelabs.topology.control import ControlClient, ControlRequest
from remotivelabs.topology.testing.frames import capture_frames

import pytest


@pytest_asyncio.fixture()
async def broker_client(request: pytest.FixtureRequest) -> AsyncIterator[BrokerClient]:
    url = request.config.getoption("broker_url")
    async with BrokerClient(url=url) as c:
        yield c
        # reset the state of SCCM after the test is done
        await c.restbus.update_signals(
            (
                "SCCM-DriverCan0",
                [
                    RestbusSignalConfig.set(name="TurnStalk.TurnSignal", value=0),
                    RestbusSignalConfig.set(name="HazardLightButton.HazardLightButton", value=0),
                    RestbusSignalConfig.set(name="LightStalk.LightMode", value=0),
                    RestbusSignalConfig.set(name="LightStalk.HighBeam", value=0),
                ],
            )
        )


# @req COMP_REQ_BCM_TURN_LEFT: Turn Signal Left Activation
# @req COMP_REQ_FLCM_CONTROL: Front Light Control
# @req COMP_REQ_RLCM_CONTROL: Rear Light Control
@pytest.mark.asyncio
async def test_turn_left(broker_client: BrokerClient):
    # 1. turn left
    await broker_client.restbus.update_signals(
        (
            "SCCM-DriverCan0",
            [
                RestbusSignalConfig.set(name="TurnStalk.TurnSignal", value=1),
            ],
        )
    )
    # 2. validate that FLCM and RLCM are blinking
    async with capture_frames((broker_client, "FLCM-BodyCan0"), ["TurnLightControl"]) as cap:
        await cap.wait_for_frame(
            "TurnLightControl",
            {
                "TurnLightControl.LeftTurnLightRequest": 1,
                "TurnLightControl.RightTurnLightRequest": 0,
            },
            timeout=2,
        )

    async with capture_frames((broker_client, "RLCM-BodyCan0"), ["TurnLightControl"]) as cap:
        await cap.wait_for_frame(
            "TurnLightControl",
            {
                "TurnLightControl.LeftTurnLightRequest": 1,
                "TurnLightControl.RightTurnLightRequest": 0,
            },
            timeout=2,
        )

    async with capture_frames((broker_client, "RL-RearLightLIN"), ["DEVMLIN01Fr01"]) as cap:
        await cap.wait_for_frame(
            "DEVMLIN01Fr01",
            {
                "DEVMLIN01Fr01.ReqRight": 0,
                "DEVMLIN01Fr01.ReqLeft": 1,
            },
            timeout=2,
        )


# @req COMP_REQ_BCM_TURN_RIGHT: Turn Signal Right Activation
# @req COMP_REQ_FLCM_CONTROL: Front Light Control
# @req COMP_REQ_RLCM_CONTROL: Rear Light Control
@pytest.mark.asyncio
async def test_turn_right(broker_client: BrokerClient):
    # 1. turn right
    await broker_client.restbus.update_signals(
        (
            "SCCM-DriverCan0",
            [
                RestbusSignalConfig.set(name="TurnStalk.TurnSignal", value=2),
            ],
        )
    )

    # 2. validate that FLCM and RLCM are blinking
    async with capture_frames((broker_client, "FLCM-BodyCan0"), ["TurnLightControl"]) as cap:
        await cap.wait_for_frame(
            "TurnLightControl",
            {
                "TurnLightControl.LeftTurnLightRequest": 0,
                "TurnLightControl.RightTurnLightRequest": 1,
            },
            timeout=2,
        )

    async with capture_frames((broker_client, "RLCM-BodyCan0"), ["TurnLightControl"]) as cap:
        await cap.wait_for_frame(
            "TurnLightControl",
            {
                "TurnLightControl.LeftTurnLightRequest": 0,
                "TurnLightControl.RightTurnLightRequest": 1,
            },
            timeout=2,
        )

    async with capture_frames((broker_client, "RL-RearLightLIN"), ["DEVMLIN01Fr01"]) as cap:
        await cap.wait_for_frame(
            "DEVMLIN01Fr01",
            {
                "DEVMLIN01Fr01.ReqRight": 1,
                "DEVMLIN01Fr01.ReqLeft": 0,
            },
            timeout=2,
        )


# @req COMP_REQ_BCM_HAZARD: Hazard Light Signal Processing
# @req COMP_REQ_BCM_TURN_SM: Turn Signal State Machine
# @req COMP_REQ_FLCM_CONTROL: Front Light Control
@pytest.mark.asyncio
async def test_hazard(broker_client: BrokerClient):
    await broker_client.restbus.update_signals(
        (
            "SCCM-DriverCan0",
            [
                RestbusSignalConfig.set(name="HazardLightButton.HazardLightButton", value=1),
            ],
        )
    )

    async with (
        capture_frames((broker_client, "FLCM-BodyCan0"), ["TurnLightControl"]) as cap_flcm,
        capture_frames((broker_client, "RL-RearLightLIN"), ["DEVMLIN01Fr01"]) as cap_lin,
    ):
        await cap_flcm.wait_for_frame(
            "TurnLightControl",
            {
                "TurnLightControl.LeftTurnLightRequest": 1,
                "TurnLightControl.RightTurnLightRequest": 1,
            },
            timeout=2,
        )
        await cap_lin.wait_for_frame(
            "DEVMLIN01Fr01",
            {
                "DEVMLIN01Fr01.ReqRight": 1,
                "DEVMLIN01Fr01.ReqLeft": 1,
            },
            timeout=2,
        )

        await broker_client.restbus.update_signals(
            (
                "SCCM-DriverCan0",
                [
                    RestbusSignalConfig.set(name="HazardLightButton.HazardLightButton", value=1),
                ],
            )
        )
        await cap_flcm.wait_for_frame(
            "TurnLightControl",
            {
                "TurnLightControl.LeftTurnLightRequest": 1,
                "TurnLightControl.RightTurnLightRequest": 1,
            },
            timeout=2,
        )
        await cap_lin.wait_for_frame(
            "DEVMLIN01Fr01",
            {
                "DEVMLIN01Fr01.ReqRight": 1,
                "DEVMLIN01Fr01.ReqLeft": 1,
            },
            timeout=2,
        )


# @req COMP_REQ_FLCM_CONTROL: Front Light Control
# @req COMP_REQ_RLCM_CONTROL: Rear Light Control
@pytest.mark.asyncio
async def test_lights_on(broker_client: BrokerClient):
    # 1. turn light on
    await broker_client.restbus.update_signals(
        (
            "SCCM-DriverCan0",
            [
                RestbusSignalConfig.set(name="LightStalk.LightMode", value=1),
            ],
        )
    )

    # 2. validate that FLCM and RLCM turn on their daylight running lights
    async with capture_frames((broker_client, "FLCM-BodyCan0"), ["DaylightRunningLightControl"]) as cap:
        await cap.wait_for_frame(
            "DaylightRunningLightControl",
            {
                "DaylightRunningLightControl.LeftDaylightRunningLightRequest": 1,
                "DaylightRunningLightControl.RightDaylightRunningLightRequest": 1,
            },
            timeout=2,
        )

    async with capture_frames((broker_client, "RLCM-BodyCan0"), ["DaylightRunningLightControl"]) as cap:
        await cap.wait_for_frame(
            "DaylightRunningLightControl",
            {
                "DaylightRunningLightControl.LeftDaylightRunningLightRequest": 1,
                "DaylightRunningLightControl.RightDaylightRunningLightRequest": 1,
            },
            timeout=2,
        )


# @req COMP_REQ_FLCM_CONTROL: Front Light Control
# @req COMP_REQ_RLCM_CONTROL: Rear Light Control
@pytest.mark.asyncio
async def test_low_beams_on(broker_client: BrokerClient):
    # 1. turn daylight running lights on
    await broker_client.restbus.update_signals(
        (
            "SCCM-DriverCan0",
            [
                RestbusSignalConfig(name="LightStalk.LightMode", loop=[2], initial=[1]),
            ],
        )
    )

    # 2. validate that FLCM and RLCM turn on their low beams
    async with capture_frames((broker_client, "FLCM-BodyCan0"), ["DaylightRunningLightControl", "LowBeamLightControl"]) as cap:
        await cap.wait_for_frame(
            "DaylightRunningLightControl",
            {
                "DaylightRunningLightControl.LeftDaylightRunningLightRequest": 1,
                "DaylightRunningLightControl.RightDaylightRunningLightRequest": 1,
            },
            timeout=2,
        )
        await cap.wait_for_frame(
            "LowBeamLightControl",
            {
                "LowBeamLightControl.LeftLowBeamLightRequest": 1,
                "LowBeamLightControl.RightLowBeamLightRequest": 1,
            },
            timeout=2,
        )

    async with capture_frames((broker_client, "RLCM-BodyCan0"), ["DaylightRunningLightControl", "LowBeamLightControl"]) as cap:
        await cap.wait_for_frame(
            "DaylightRunningLightControl",
            {
                "DaylightRunningLightControl.LeftDaylightRunningLightRequest": 1,
                "DaylightRunningLightControl.RightDaylightRunningLightRequest": 1,
            },
            timeout=2,
        )
        await cap.wait_for_frame(
            "LowBeamLightControl",
            {
                "LowBeamLightControl.LeftLowBeamLightRequest": 1,
                "LowBeamLightControl.RightLowBeamLightRequest": 1,
            },
            timeout=2,
        )


@pytest.mark.asyncio
async def test_high_beams_on(broker_client: BrokerClient):
    # 1. turn high beams on
    await broker_client.restbus.update_signals(
        (
            "SCCM-DriverCan0",
            [
                RestbusSignalConfig.set(name="LightStalk.HighBeam", value=1),
            ],
        )
    )

    # 2. validate that FLCM turns on high beams
    async with capture_frames((broker_client, "FLCM-BodyCan0"), ["HighBeamLightControl"]) as cap:
        await cap.wait_for_frame(
            "HighBeamLightControl",
            {
                "HighBeamLightControl.LeftHighBeamLightRequest": 1,
                "HighBeamLightControl.RightHighBeamLightRequest": 1,
            },
            timeout=2,
        )


@pytest_asyncio.fixture()
async def set_operating_mode_emergency(broker_client: BrokerClient) -> AsyncIterator[BrokerClient]:
    async with ControlClient(broker_client) as cc:
        await cc.send("BCM", ControlRequest(type="emergency_mode", argument="emergency"))
        yield broker_client
        # once we're test is done, restore mode
        await cc.send("BCM", ControlRequest(type="emergency_mode", argument="normal"))


# @req COMP_REQ_BCM_TURN_SM: Turn Signal State Machine
# @req COMP_REQ_FLCM_CONTROL: Front Light Control
# @req COMP_REQ_RLCM_CONTROL: Rear Light Control
@pytest.mark.asyncio
async def test_emergency(set_operating_mode_emergency: BrokerClient):
    # We toggle using fixture, so we just need to validate that FLCM and RLCM are blinking
    async with capture_frames((set_operating_mode_emergency, "FLCM-BodyCan0"), ["TurnLightControl"]) as cap:
        await cap.wait_for_frame(
            "TurnLightControl",
            {
                "TurnLightControl.LeftTurnLightRequest": 1,
                "TurnLightControl.RightTurnLightRequest": 1,
            },
            timeout=2,
        )

    async with capture_frames((set_operating_mode_emergency, "RLCM-BodyCan0"), ["TurnLightControl"]) as cap:
        await cap.wait_for_frame(
            "TurnLightControl",
            {
                "TurnLightControl.LeftTurnLightRequest": 1,
                "TurnLightControl.RightTurnLightRequest": 1,
            },
            timeout=2,
        )
