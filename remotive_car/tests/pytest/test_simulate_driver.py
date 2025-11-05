from __future__ import annotations

from functools import partial
from typing import AsyncIterator

import pytest_asyncio
from hamcrest import equal_to
from remotivelabs.broker import BrokerClient, RestbusSignalConfig, Signal
from remotivelabs.topology.control import ControlClient, ControlRequest
from remotivelabs.topology.testing.retry import await_at_most

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


async def take_values(sub: AsyncIterator[list[Signal]], x: int = 1):
    result = {}
    for _ in range(x):
        signals = await sub.__anext__()
        result.update({s.name: s.value for s in signals})
    return result


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
    sub = await broker_client.subscribe(
        ("FLCM-BodyCan0", ["TurnLightControl.LeftTurnLightRequest", "TurnLightControl.RightTurnLightRequest"])
    )
    await await_at_most(seconds=2).until(
        partial(take_values, sub),
        equal_to({"TurnLightControl.LeftTurnLightRequest": 1, "TurnLightControl.RightTurnLightRequest": 0}),
    )

    sub = await broker_client.subscribe(
        ("RLCM-BodyCan0", ["TurnLightControl.LeftTurnLightRequest", "TurnLightControl.RightTurnLightRequest"])
    )
    await await_at_most(seconds=2).until(
        partial(take_values, sub),
        equal_to({"TurnLightControl.LeftTurnLightRequest": 1, "TurnLightControl.RightTurnLightRequest": 0}),
    )

    sub = await broker_client.subscribe(("RL-RearLightLIN", ["DEVMLIN01Fr01.ReqRight", "DEVMLIN01Fr01.ReqLeft"]))
    await await_at_most(seconds=2).until(
        partial(take_values, sub),
        equal_to({"DEVMLIN01Fr01.ReqRight": 0, "DEVMLIN01Fr01.ReqLeft": 1}),
    )


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
    sub = await broker_client.subscribe(
        ("FLCM-BodyCan0", ["TurnLightControl.LeftTurnLightRequest", "TurnLightControl.RightTurnLightRequest"])
    )
    await await_at_most(seconds=2).until(
        partial(take_values, sub),
        equal_to({"TurnLightControl.LeftTurnLightRequest": 0, "TurnLightControl.RightTurnLightRequest": 1}),
    )

    sub = await broker_client.subscribe(
        ("RLCM-BodyCan0", ["TurnLightControl.LeftTurnLightRequest", "TurnLightControl.RightTurnLightRequest"])
    )
    await await_at_most(seconds=2).until(
        partial(take_values, sub),
        equal_to({"TurnLightControl.LeftTurnLightRequest": 0, "TurnLightControl.RightTurnLightRequest": 1}),
    )

    sub = await broker_client.subscribe(("RL-RearLightLIN", ["DEVMLIN01Fr01.ReqRight", "DEVMLIN01Fr01.ReqLeft"]))
    await await_at_most(seconds=2).until(
        partial(take_values, sub),
        equal_to({"DEVMLIN01Fr01.ReqRight": 1, "DEVMLIN01Fr01.ReqLeft": 0}),
    )


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

    sub = await broker_client.subscribe(
        ("FLCM-BodyCan0", ["TurnLightControl.LeftTurnLightRequest", "TurnLightControl.RightTurnLightRequest"])
    )
    await await_at_most(seconds=2).until(
        partial(take_values, sub),
        equal_to({"TurnLightControl.LeftTurnLightRequest": 1, "TurnLightControl.RightTurnLightRequest": 1}),
    )

    sub_lin = await broker_client.subscribe(("RL-RearLightLIN", ["DEVMLIN01Fr01.ReqRight", "DEVMLIN01Fr01.ReqLeft"]))
    await await_at_most(seconds=2).until(
        partial(take_values, sub_lin),
        equal_to({"DEVMLIN01Fr01.ReqRight": 1, "DEVMLIN01Fr01.ReqLeft": 1}),
    )

    await broker_client.restbus.update_signals(
        (
            "SCCM-DriverCan0",
            [
                RestbusSignalConfig.set(name="HazardLightButton.HazardLightButton", value=1),
            ],
        )
    )
    await await_at_most(seconds=2).until(
        partial(take_values, sub),
        equal_to({"TurnLightControl.LeftTurnLightRequest": 1, "TurnLightControl.RightTurnLightRequest": 1}),
    )

    await await_at_most(seconds=2).until(
        partial(take_values, sub_lin),
        equal_to({"DEVMLIN01Fr01.ReqRight": 1, "DEVMLIN01Fr01.ReqLeft": 1}),
    )


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
    sub = await broker_client.subscribe(
        (
            "FLCM-BodyCan0",
            ["DaylightRunningLightControl.LeftDaylightRunningLightRequest", "DaylightRunningLightControl.RightDaylightRunningLightRequest"],
        )
    )
    await await_at_most(seconds=2).until(
        partial(take_values, sub),
        equal_to(
            {
                "DaylightRunningLightControl.LeftDaylightRunningLightRequest": 1,
                "DaylightRunningLightControl.RightDaylightRunningLightRequest": 1,
            }
        ),
    )

    sub = await broker_client.subscribe(
        (
            "RLCM-BodyCan0",
            ["DaylightRunningLightControl.LeftDaylightRunningLightRequest", "DaylightRunningLightControl.RightDaylightRunningLightRequest"],
        )
    )
    await await_at_most(seconds=2).until(
        partial(take_values, sub),
        equal_to(
            {
                "DaylightRunningLightControl.LeftDaylightRunningLightRequest": 1,
                "DaylightRunningLightControl.RightDaylightRunningLightRequest": 1,
            }
        ),
    )


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

    # 3. validate that FLCM and RLCM turn on their low beams
    sub = await broker_client.subscribe(
        (
            "FLCM-BodyCan0",
            [
                "DaylightRunningLightControl.LeftDaylightRunningLightRequest",
                "DaylightRunningLightControl.RightDaylightRunningLightRequest",
                "LowBeamLightControl.LeftLowBeamLightRequest",
                "LowBeamLightControl.RightLowBeamLightRequest",
            ],
        )
    )
    await await_at_most(seconds=2).until(
        partial(take_values, sub, 2),
        equal_to(
            {
                "DaylightRunningLightControl.LeftDaylightRunningLightRequest": 1,
                "DaylightRunningLightControl.RightDaylightRunningLightRequest": 1,
                "LowBeamLightControl.LeftLowBeamLightRequest": 1,
                "LowBeamLightControl.RightLowBeamLightRequest": 1,
            }
        ),
    )

    sub = await broker_client.subscribe(
        (
            "RLCM-BodyCan0",
            [
                "DaylightRunningLightControl.LeftDaylightRunningLightRequest",
                "DaylightRunningLightControl.RightDaylightRunningLightRequest",
                "LowBeamLightControl.LeftLowBeamLightRequest",
                "LowBeamLightControl.RightLowBeamLightRequest",
            ],
        )
    )
    await await_at_most(seconds=2).until(
        partial(take_values, sub, 2),
        equal_to(
            {
                "DaylightRunningLightControl.LeftDaylightRunningLightRequest": 1,
                "DaylightRunningLightControl.RightDaylightRunningLightRequest": 1,
                "LowBeamLightControl.LeftLowBeamLightRequest": 1,
                "LowBeamLightControl.RightLowBeamLightRequest": 1,
            }
        ),
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

    # 3. validate that FLCM turns on high beams
    sub = await broker_client.subscribe(
        (
            "FLCM-BodyCan0",
            ["HighBeamLightControl.LeftHighBeamLightRequest", "HighBeamLightControl.RightHighBeamLightRequest"],
        )
    )
    await await_at_most(seconds=2).until(
        partial(take_values, sub),
        equal_to(
            {
                "HighBeamLightControl.LeftHighBeamLightRequest": 1,
                "HighBeamLightControl.RightHighBeamLightRequest": 1,
            }
        ),
    )


@pytest_asyncio.fixture()
async def set_operating_mode_emergency(broker_client: BrokerClient) -> AsyncIterator[BrokerClient]:
    async with ControlClient(broker_client) as cc:
        await cc.send("BCM", ControlRequest(type="emergency_mode", argument="emergency"))
        yield broker_client
        # once we're test is done, restore mode
        await cc.send("BCM", ControlRequest(type="emergency_mode", argument="normal"))


@pytest.mark.asyncio
async def test_emergency(set_operating_mode_emergency: BrokerClient):
    # We toggle using fixture, so we just need to validate that FLCM and RLCM are blinking
    sub = await set_operating_mode_emergency.subscribe(
        (
            "FLCM-BodyCan0",
            ["TurnLightControl.LeftTurnLightRequest", "TurnLightControl.RightTurnLightRequest"],
        )
    )
    await await_at_most(seconds=2).until(
        partial(take_values, sub),
        equal_to({"TurnLightControl.LeftTurnLightRequest": 1, "TurnLightControl.RightTurnLightRequest": 1}),
    )

    sub = await set_operating_mode_emergency.subscribe(
        (
            "RLCM-BodyCan0",
            ["TurnLightControl.LeftTurnLightRequest", "TurnLightControl.RightTurnLightRequest"],
        )
    )
    await await_at_most(seconds=2).until(
        partial(take_values, sub),
        equal_to({"TurnLightControl.LeftTurnLightRequest": 1, "TurnLightControl.RightTurnLightRequest": 1}),
    )
