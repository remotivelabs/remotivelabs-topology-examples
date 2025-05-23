from __future__ import annotations

import asyncio
from collections import defaultdict
from enum import Enum
from typing import AsyncIterator

from behave import given, then, when
from behave.api.async_step import async_run_until_complete
from remotivelabs.broker import BrokerClient, NamespaceName, RestbusSignalConfig, Signal, SignalName, SignalValue
from remotivelabs.topology.testing.matcher import contains_signal_value_sequences
from remotivelabs.topology.testing.retry import await_at_most


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
        self._c = broker_client

    async def set_turn_signal(self, direction: TurnSignalDirection):
        """Sets the turn signal direction on the simulation using the TurnSignalDirection enum"""
        await self._c.restbus.update_signals(
            (
                TurnStalk.target_namespace,
                [
                    RestbusSignalConfig.set(name=TurnStalk.target_signal_name, value=direction.value),
                ],
            )
        )


class SignalValueAccumulator:
    def __init__(self, broker_client: BrokerClient, *signals: tuple[NamespaceName, list[SignalName]]) -> None:
        self._client = broker_client
        self.signals = signals
        self._values: dict[NamespaceName, dict[SignalName, list[SignalValue]]] = defaultdict(lambda: defaultdict(list))
        self._stream: AsyncIterator[list[Signal]] | None = None

    async def __aenter__(self) -> SignalValueAccumulator:
        self._stream = await self._client.subscribe(*self.signals)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        None

    async def __call__(self) -> dict[NamespaceName, dict[SignalName, list[SignalValue]]]:
        async def read():
            assert self._stream is not None
            for signal in await self._stream.__anext__():
                self._values[signal.namespace][signal.name].append(signal.value)

        await asyncio.shield(read())
        return self._values


@given("the system is running")
@async_run_until_complete
async def step_given_system_in_simulation_mode(context):
    """
    Sets up the simulation environment by creating a gRPC channel and initializing the TurnStalk and Validator objects.
    """
    broker_client = BrokerClient(url=context.broker_url)

    context.broker_client = broker_client
    context.turn_stalk = TurnStalk(broker_client=broker_client)
    loop = asyncio.get_running_loop()
    context.add_cleanup(lambda: loop.create_task(context.broker_client.disconnect()))


@when("the SCCM indicates a {direction} turn")
@async_run_until_complete
async def step_when_indicate_turn(context, direction: str):
    try:
        turn_signal_direction = TurnSignalDirection[direction.upper()]
        await context.turn_stalk.set_turn_signal(turn_signal_direction)
        await context.turn_stalk.set_turn_signal(TurnSignalDirection[direction.upper()])
    except KeyError as e:
        raise ValueError(f"Invalid direction: {direction}. Must be 'left', 'right', or 'none'.") from e


@then("the {turn} turn light blinks")
@async_run_until_complete
async def step_then_validate_turn_light_toggle(context, turn: str):
    signal_name = f"TurnLightControl.{turn.capitalize()}TurnLightRequest"
    async with SignalValueAccumulator(
        context.broker_client, ("RLCM-BodyCan0", [signal_name]), ("FLCM-BodyCan0", [signal_name]), ("DIM-BodyCan0", [signal_name])
    ) as consumer:
        await await_at_most(seconds=4).until(
            consumer,
            contains_signal_value_sequences(
                {
                    "RLCM-BodyCan0": {signal_name: 2 * [1, 0]},
                    "FLCM-BodyCan0": {signal_name: 2 * [1, 0]},
                    "DIM-BodyCan0": {signal_name: 2 * [1, 0]},
                }
            ),
        )


@then("the {turn} turn light remains off")
@async_run_until_complete
async def step_then_validate_turn_light_static(context, turn: str):
    signal_name = f"TurnLightControl.{turn.capitalize()}TurnLightRequest"
    async with SignalValueAccumulator(
        context.broker_client, ("RLCM-BodyCan0", [signal_name]), ("FLCM-BodyCan0", [signal_name]), ("DIM-BodyCan0", [signal_name])
    ) as consumer:
        await await_at_most(seconds=4).until(
            consumer,
            contains_signal_value_sequences(
                {
                    "RLCM-BodyCan0": {signal_name: 8 * [0]},
                    "FLCM-BodyCan0": {signal_name: 8 * [0]},
                    "DIM-BodyCan0": {signal_name: 8 * [0]},
                }
            ),
        )
