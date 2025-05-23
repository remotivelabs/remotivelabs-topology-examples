from __future__ import annotations

import asyncio
from collections import defaultdict
from typing import AsyncIterator, Generator

import pytest
import pytest_asyncio
from remotivelabs.broker import BrokerClient, NamespaceName, RestbusSignalConfig, Signal, SignalName, SignalValue
from remotivelabs.topology.behavioral_model import PingRequest
from remotivelabs.topology.control import ControlClient, ControlRequest
from remotivelabs.topology.testing.matcher import contains_signal_value_sequences
from remotivelabs.topology.testing.retry import await_at_most


@pytest.fixture()
def url(request: pytest.FixtureRequest) -> Generator[str, None, None]:
    yield request.config.getoption("--broker_url")


@pytest_asyncio.fixture()
async def broker_client(url: str) -> AsyncIterator[BrokerClient]:
    """
    Sample fixture for setting system into a specific mode
    """

    async with BrokerClient(url=url) as c, ControlClient(client=c) as cc:
        await cc.send(target_ecu="ecub", request=PingRequest(), timeout=1, retries=10)
        await c.restbus.update_signals(
            (
                "ECUA-Can0",
                [
                    RestbusSignalConfig.set(name="SomeFrame_10ms.SomeSts", value=1),
                    RestbusSignalConfig(name="SomeFrame_10ms.SomeSignal417", loop=[0, 1]),
                ],
            )
        )
        yield c


@pytest.mark.asyncio
async def test_to_send_custom_control_message(broker_client: BrokerClient):
    """
    Sends a custom control message to ECU and verifies the response.
    """
    async with ControlClient(client=broker_client) as cc:
        request = ControlRequest(type="ecub_control_message", argument="test")
        resp = await cc.send(target_ecu="ecub", request=request)
        assert resp.data == "test"


@pytest.mark.asyncio
async def test_reset_rest_bus(broker_client: BrokerClient):
    """
    Verifies signal values before and after resetting the namespace.
    """
    async with SignalValueAccumulator(broker_client, ("ECUB-Can0", ["SomeFrame_10ms.SomeSignal417", "SomeFrame_10ms.SomeSts"])) as consumer:
        await await_at_most(seconds=4).until(
            consumer,
            contains_signal_value_sequences(
                {
                    "ECUB-Can0": {"SomeFrame_10ms.SomeSignal417": [0, 1], "SomeFrame_10ms.SomeSts": [1, 1]},
                }
            ),
        )

    await broker_client.restbus.reset_namespaces("ECUA-Can0")

    async with SignalValueAccumulator(broker_client, ("ECUB-Can0", ["SomeFrame_10ms.SomeSignal417", "SomeFrame_10ms.SomeSts"])) as consumer:
        await await_at_most(seconds=4).until(
            consumer,
            contains_signal_value_sequences(
                {
                    "ECUB-Can0": {"SomeFrame_10ms.SomeSignal417": [0, 0], "SomeFrame_10ms.SomeSts": [0, 0]},
                }
            ),
        )


@pytest.mark.asyncio
async def test_write_update_bit(broker_client: BrokerClient):
    """
    Sets a signal with an initial value, then verifies its update pattern.
    """
    async with SignalValueAccumulator(broker_client, ("ECUA-Can0", ["SomeOtherFrame_10ms.FeatureA_UB"])) as consumer:
        await broker_client.restbus.reset_namespaces("ECUA-Can0")
        await broker_client.restbus.update_signals(
            (
                "ECUA-Can0",
                [
                    RestbusSignalConfig.set_update_bit("SomeOtherFrame_10ms.FeatureA_UB"),
                ],
            )
        )

        await await_at_most(seconds=4).until(
            consumer,
            contains_signal_value_sequences(
                {
                    "ECUA-Can0": {"SomeOtherFrame_10ms.FeatureA_UB": [1, 0, 0, 0, 0, 0, 0]},
                }
            ),
        )


@pytest.mark.asyncio
async def test_e2e_counter(broker_client: BrokerClient):
    """
    Validates that the counter signal increments correctly over time.
    """
    async with (
        SignalValueAccumulator(broker_client, ("ECUB-Can0", ["E2eAutosar01A_Frame_4bit.Counter_4bit"])) as consumer,
    ):
        await await_at_most(seconds=4).until(
            consumer,
            contains_signal_value_sequences(
                {
                    "ECUB-Can0": {"E2eAutosar01A_Frame_4bit.Counter_4bit": 2 * list(range(15))},
                }
            ),
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
