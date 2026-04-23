from __future__ import annotations

import asyncio
from enum import Enum

from behave.api.async_step import async_run_until_complete
from remotivelabs.broker import BrokerClient, RestbusSignalConfig
from remotivelabs.topology.testing.frames import capture_frames

from behave import given, then, when  # type: ignore[attr-defined]


class TurnSignalDirection(Enum):
    LEFT = 1
    RIGHT = 2
    NONE = 0


class TurnStalk:
    """
    Class to manage the interaction with the virtual interface and simulation for the turn signals.
    """

    target_signal_name = "TurnStalk.TurnSignal"
    target_namespace = "SCCM-DriverCan0"

    def __init__(self, broker_client: BrokerClient):
        self._client = broker_client

    async def set_turn_signal(self, direction: TurnSignalDirection):
        """Sets the turn signal direction on the simulation using the TurnSignalDirection enum"""
        await self._client.restbus.update_signals(
            (
                TurnStalk.target_namespace,
                [
                    RestbusSignalConfig.set(name=TurnStalk.target_signal_name, value=direction.value),
                ],
            )
        )


class HazardLightButton(Enum):
    OFF = 0
    ON = 1


class HazardLight:
    """
    Class to manage the interaction with the virtual interface and simulation for the hazard light.
    """

    def __init__(self, broker_client: BrokerClient):
        self._client = broker_client

    async def set_hazard_light(self, _button: HazardLightButton):
        """
        Sets the hazard light state on the simulation using the HazardLightButton enum.
        """

        await self._client.restbus.update_signals(
            (
                "SCCM-DriverCan0",
                [
                    RestbusSignalConfig(name="HazardLightButton.HazardLightButton", loop=[0], initial=[1]),
                ],
            )
        )


@given("the system is running")
@async_run_until_complete
async def step_given_system_in_simulation_mode(context):
    """
    Sets up the simulation environment by creating a gRPC channel and initializing the TurnStalk and Validator objects.
    """
    broker_client = BrokerClient(url=context.broker_url)

    context.broker_client = broker_client
    context.turn_stalk = TurnStalk(broker_client=broker_client)
    context.hazard_light = HazardLight(broker_client=broker_client)
    loop = asyncio.get_running_loop()
    context.add_cleanup(lambda: loop.create_task(context.broker_client.disconnect()))


async def do_step_when_indicate_turn(context, direction: str):
    try:
        turn_signal_direction = TurnSignalDirection[direction.upper()]
        await context.turn_stalk.set_turn_signal(turn_signal_direction)
        await context.turn_stalk.set_turn_signal(TurnSignalDirection[direction.upper()])
    except KeyError as e:
        raise ValueError(f"Invalid direction: {direction}. Must be 'left', 'right', or 'none'.") from e


@when("the SCCM indicates a {direction} turn")
@when("the turn stalk is turned {direction}")
@async_run_until_complete
async def step_when_indicate_turn(context, direction: str):
    await do_step_when_indicate_turn(context, direction)


@when("the turn stalk is reset")
@async_run_until_complete
async def step_when_turnstalk_reset(context):
    await do_step_when_indicate_turn(context, "none")


@when("the hazard light button is {status}")
@async_run_until_complete
async def when_hazard_light_button(context, status: str):
    try:
        hazard_light_status = HazardLightButton[status.upper()]
        await context.hazard_light.set_hazard_light(hazard_light_status)
    except KeyError as e:
        raise ValueError(f"Invalid direction: {status}. Must be 'ON' or 'OFF'.") from e


@then("the {turn} turn light blinks")
@async_run_until_complete
async def step_then_validate_turn_light_toggle(context, turn: str):
    frame_name = "TurnLightControl"
    signal_name = f"TurnLightControl.{turn.capitalize()}TurnLightRequest"
    ns_names = ["RLCM-BodyCan0", "FLCM-BodyCan0", "DIM-BodyCan0"]

    async def check_namespace(ns_name: str) -> None:
        async with capture_frames((context.broker_client, ns_name), [frame_name]) as cap:
            await cap.wait_for_signal_values(frame_name, signal_name, 2 * [1, 0], timeout=5)

    await asyncio.gather(*[check_namespace(ns) for ns in ns_names])


@then("the {turn} turn light remains off")
@async_run_until_complete
async def step_then_validate_turn_light_static(context, turn: str):
    frame_name = "TurnLightControl"
    signal_name = f"TurnLightControl.{turn.capitalize()}TurnLightRequest"
    ns_names = ["RLCM-BodyCan0", "FLCM-BodyCan0", "DIM-BodyCan0"]

    async def check_namespace(ns_name: str) -> None:
        async with capture_frames((context.broker_client, ns_name), [frame_name]) as cap:
            await cap.wait_for_signal_values(frame_name, signal_name, 8 * [0], timeout=4)

    await asyncio.gather(*[check_namespace(ns) for ns in ns_names])


@then("both left and right turn light blinks")
def step_then_validate_both_turn_lights_blink(context):
    context.execute_steps("""
            then the left turn light blinks
            and the right turn light blinks
        """)


@then("neither left nor right turn light blinks")
def step_then_validate_both_turn_lights_off(context):
    context.execute_steps("""
            then the left turn light remains off
            and the right turn light remains off
        """)
