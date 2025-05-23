from __future__ import annotations

import asyncio
import os
import random
from math import isclose

import pytest
import pytest_asyncio
from remotivelabs.broker import BrokerClient
from remotivelabs.topology.behavioral_model import PingRequest
from remotivelabs.topology.control import ControlClient
from remotivelabs.topology.namespaces.some_ip import ReturnCode, SomeIPError, SomeIPNamespace, SomeIPRequestReturn, SomeIPResponse


@pytest_asyncio.fixture()
async def some_ip_eth(request: pytest.FixtureRequest):
    async with (
        BrokerClient(request.config.getoption("broker_url")) as broker_client,
        ControlClient(broker_client) as cc,
    ):
        await cc.send(target_ecu="ecub", request=PingRequest(), timeout=1, retries=10)

        async with SomeIPNamespace("topology-ETH", broker_client, 9393, decode_named_values=True) as some_ip_eth:
            yield some_ip_eth


@pytest.mark.asyncio
async def test_retrieve_latest_bytes(some_ip_eth: SomeIPNamespace):
    stream = await some_ip_eth.subscribe(
        ("ByteEncodedMessages", "MyTestService"),
    )
    async for event in stream:
        assert isinstance(event.raw, bytes)
        break


def compare_param_dict(dict1: dict[str, int | float | bytes | str], dict2: dict[str, int | float | bytes | str]) -> None:
    assert dict1.keys() == dict2.keys(), f"Key sets do not match: {dict1.keys()} != {dict2.keys()}"

    for key, val1 in dict1.items():
        val2 = dict2[key]
        if isinstance(val1, float) and isinstance(val2, float):
            assert isclose(val1, val2, rel_tol=1e-6)
        else:
            assert val1 == val2


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "params, runs",
    [
        (
            {
                "ABool": random.getrandbits(1),
                "AUint8": random.randint(0, 0xFF),
                "AUint16": random.randint(0, 0xFFFF),
                "AUint32": random.randint(0, 0xFFFFFFFF),
                "AInt8": random.randint(-128, 127),
                "AInt16": random.randint(-32768, 32767),
                "AInt32": random.randint(-2147483648, 2147483647),
                "AFloat32": random.uniform(-3.4028235e38, 3.4028235e38),
            },
            i,
        )
        for i in range(0, 15)
    ],
)
async def test_some_ip_request(some_ip_eth: SomeIPNamespace, params: dict[str, int | float | bytes | str], runs: int):
    del runs
    resp = await some_ip_eth.request(SomeIPRequestReturn(name="echoPrimitives", service_instance_name="MyTestService", parameters=params))
    response: SomeIPResponse | SomeIPError = await asyncio.wait_for(resp, 5)
    assert isinstance(response, SomeIPResponse)
    compare_param_dict(response.parameters, params)


@pytest.mark.asyncio
async def test_some_ip_session_id_is_incremented(some_ip_eth: SomeIPNamespace):
    sent_parameters_list: list[dict[str, int | float | bytes | str]] = [
        {
            "ABool": random.getrandbits(1),
            "AUint8": random.randint(0, 0xFF),
            "AUint16": random.randint(0, 0xFFFF),
            "AUint32": random.randint(0, 0xFFFFFFFF),
            "AInt8": random.randint(-128, 127),
            "AInt16": random.randint(-32768, 32767),
            "AInt32": random.randint(-2147483648, 2147483647),
            "AFloat32": random.uniform(-3.4028235e38, 3.4028235e38),
        }
        for _ in range(1, 32)
    ]

    responses: list[SomeIPResponse | SomeIPError] = await asyncio.gather(
        *[
            asyncio.wait_for(resp, 5)
            for resp in [
                await some_ip_eth.request(
                    SomeIPRequestReturn(name="echoPrimitives", service_instance_name="MyTestService", parameters=params),
                )
                for params in sent_parameters_list
            ]
        ]
    )

    for sent_parameters, response in zip(sent_parameters_list, responses):
        assert isinstance(response, SomeIPResponse)
        compare_param_dict(response.parameters, sent_parameters)


@pytest.mark.asyncio
async def test_some_ip_request_with_no_parameters(some_ip_eth: SomeIPNamespace):
    resp = await some_ip_eth.request(SomeIPRequestReturn(name="requestWithNoParams", service_instance_name="MyTestService"))
    response: SomeIPResponse | SomeIPError = await asyncio.wait_for(resp, 5)
    assert isinstance(response, SomeIPResponse)
    compare_param_dict(response.parameters, {})


@pytest.mark.asyncio
async def test_some_ip_request_echo_raw(some_ip_eth: SomeIPNamespace):
    raw = os.urandom(12)
    resp = await some_ip_eth.request(SomeIPRequestReturn(name="echoRaw", service_instance_name="MyTestService", raw=raw))
    response: SomeIPResponse | SomeIPError = await asyncio.wait_for(resp, 5)
    assert isinstance(response, SomeIPResponse)
    assert response.raw == raw


@pytest.mark.asyncio
async def test_some_ip_request_returns_error(some_ip_eth: SomeIPNamespace):
    raw = os.urandom(12)
    resp = await some_ip_eth.request(SomeIPRequestReturn(name="requestThatReturnsError", service_instance_name="MyTestService", raw=raw))
    response: SomeIPResponse | SomeIPError = await asyncio.wait_for(resp, 5)
    assert isinstance(response, SomeIPError)
    assert response.return_code == ReturnCode.E_NOT_OK.name
