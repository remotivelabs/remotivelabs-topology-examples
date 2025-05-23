import asyncio
import logging
import os

from remotivelabs.broker import BrokerClient
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.some_ip import ReturnCode, SomeIPError, SomeIPEvent, SomeIPNamespace, SomeIPRequest, SomeIPResponse


async def publisher(some_ip_eth: SomeIPNamespace, publish_interval: float = 0.1):
    """
    Publishes messages at regular intervals until canceled.
    """
    while True:
        await some_ip_eth.notify(SomeIPEvent(name="ByteEncodedMessages", service_instance_name="MyTestService", raw=os.urandom(12)))
        logging.debug("sent event 'ByteEncodedMessages'")
        await asyncio.sleep(publish_interval)


async def __echo_primitives(req: SomeIPRequest) -> SomeIPResponse:
    logging.debug("Got request %s", req)
    return SomeIPResponse(
        parameters=req.parameters,
    )


async def __request_with_no_parameters(req: SomeIPRequest) -> SomeIPResponse:
    logging.debug("Got request %s", req)
    return SomeIPResponse()


async def __echo_raw(req: SomeIPRequest) -> SomeIPResponse:
    logging.info("Got request %s", req)
    return SomeIPResponse(raw=req.raw)


async def __request_that_returns_error(req: SomeIPRequest) -> SomeIPError:
    logging.info("Got request %s", req)
    return SomeIPError(
        return_code=ReturnCode.E_NOT_OK.name,
    )


async def main(avp: BehavioralModelArgs):
    async with BrokerClient(url=avp.url, auth=avp.auth) as broker_client:
        some_ip_eth = SomeIPNamespace("ecu_a-ETH", client_id=99, broker_client=broker_client)
        async with BehavioralModel(
            "ecua",
            namespaces=[some_ip_eth],
            broker_client=broker_client,
            input_handlers=[
                some_ip_eth.create_input_handler(
                    [
                        filters.SomeIPRequestFilter(
                            service_instance_name="MyTestService",
                            method_name="echoPrimitives",
                        )
                    ],
                    __echo_primitives,
                ),
                some_ip_eth.create_input_handler(
                    [
                        filters.SomeIPRequestFilter(
                            service_instance_name="MyTestService",
                            method_name="requestWithNoParams",
                        )
                    ],
                    __request_with_no_parameters,
                ),
                some_ip_eth.create_input_handler(
                    [
                        filters.SomeIPRequestFilter(
                            service_instance_name="MyTestService",
                            method_name="echoRaw",
                        )
                    ],
                    __echo_raw,
                ),
                some_ip_eth.create_input_handler(
                    [
                        filters.SomeIPRequestFilter(
                            service_instance_name="MyTestService",
                            method_name="requestThatReturnsError",
                        )
                    ],
                    __request_that_returns_error,
                ),
            ],
        ) as bm:
            publish_task = asyncio.create_task(publisher(some_ip_eth))
            await asyncio.gather(bm.run_forever(), publish_task)


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    logging.basicConfig(level="DEBUG", format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    asyncio.run(main(args))
