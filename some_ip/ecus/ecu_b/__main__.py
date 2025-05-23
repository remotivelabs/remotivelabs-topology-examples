from __future__ import annotations

import asyncio
import logging
import random

from remotivelabs.broker import BrokerClient
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.some_ip import SomeIPError, SomeIPEvent, SomeIPNamespace, SomeIPRequestReturn, SomeIPResponse


async def __on_event(event: SomeIPEvent) -> None:
    logging.debug("Got event with id %s, params=%s payload=%s", event.name, str(len(event.parameters)), event.raw)


async def requester(some_ip_eth: SomeIPNamespace, publish_interval: float = 0.1):
    """
    Sends SOME/IP requests on regular interval
    """
    await asyncio.sleep(2)

    while True:
        resp = await some_ip_eth.request(
            SomeIPRequestReturn(
                name="echoPrimitives",
                service_instance_name="MyTestService",
                parameters={
                    "ABool": random.getrandbits(1),
                    "AUint8": random.randint(0, 0xFF),
                    "AUint16": random.randint(0, 0xFFFF),
                    "AUint32": random.randint(0, 0xFFFFFFFF),
                    "AInt8": random.randint(0, 0xFF),
                    "AInt16": random.randint(0, 0xFFFF),
                    "AInt32": random.randint(0, 0xFFFFFFFF),
                    "AFloat32": random.uniform(0, 0xFFFFFFFF),
                },
            ),
        )
        response: SomeIPResponse | SomeIPError = await resp
        logging.debug("Got response %s", response)
        await asyncio.sleep(publish_interval)


async def main(avp: BehavioralModelArgs):
    async with BrokerClient(url=avp.url, auth=avp.auth) as broker_client:
        some_ip_eth = SomeIPNamespace("ecu_b-ETH", client_id=8293, broker_client=broker_client)
        async with BehavioralModel(
            "ecub",
            namespaces=[some_ip_eth],
            broker_client=broker_client,
            input_handlers=[
                some_ip_eth.create_input_handler(
                    [
                        filters.SomeIPEventFilter(
                            service_instance_name="MyTestService",
                            event_name="ByteEncodedMessages",
                        )
                    ],
                    __on_event,
                )
            ],
        ) as bm:
            publish_task = asyncio.create_task(requester(some_ip_eth))
            await asyncio.gather(bm.run_forever(), publish_task)


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    logging.basicConfig(level=args.loglevel, format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    asyncio.run(main(args))
