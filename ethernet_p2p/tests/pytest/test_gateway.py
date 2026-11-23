from __future__ import annotations

from typing import AsyncIterator

import pytest_asyncio
from remotivelabs.broker import BrokerClient, RestbusSignalConfig, Signal
from remotivelabs.topology.testing import capture_frames

import pytest


@pytest_asyncio.fixture()
async def broker_client(request: pytest.FixtureRequest) -> AsyncIterator[BrokerClient]:
    url = request.config.getoption("broker_url")
    async with BrokerClient(url=url) as broker_client:
        yield broker_client
        # reset the state of SCCM after the test is done
        await broker_client.restbus.update_signals(
            (
                "ECUA-ecu_a_net_1_socket-ecu_b_net_1_socket-NET1",
                [
                    RestbusSignalConfig.set(name="DummyFrame.A", value=0),
                    RestbusSignalConfig.set(name="DummyFrame.B", value=0),
                    RestbusSignalConfig.set(name="DummyFrame.C", value=0),
                    RestbusSignalConfig.set(name="DummyFrame.D", value=0),
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
async def test_gateway(broker_client: BrokerClient):
    await broker_client.restbus.update_signals(
        (
            "ECUA-ecu_a_net_1_socket-ecu_b_net_1_socket-NET1",
            [
                RestbusSignalConfig.set(name="DummyFrame.A", value=1),
                RestbusSignalConfig.set(name="DummyFrame.B", value=2),
                RestbusSignalConfig.set(name="DummyFrame.C", value=3),
                RestbusSignalConfig.set(name="DummyFrame.D", value=4),
            ],
        )
    )

    async with capture_frames(
        (broker_client, "tap_ECUB-ecu_b_net_2_socket-ecu_c_net_2_socket-NET2"),
        frames=["DummyFrame"],
    ) as cap:
        await cap.wait_for_frame("DummyFrame", {"DummyFrame.A": 1, "DummyFrame.B": 2, "DummyFrame.C": 3, "DummyFrame.D": 4}, timeout=2.0)
