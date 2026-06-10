from __future__ import annotations

import asyncio

import structlog
from remotivelabs.broker import BrokerClient, Frame, Header, WriteSignal
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.lin import LinNamespace

from .log import configure_logging

logger = structlog.get_logger(__name__)


class RL(BehavioralModel):
    ecu_name: str = "RL"
    lin_ns: str = "RL-RearLightLIN"

    DEVMLIN01Fr01: str = "DEVMLIN01Fr01"
    RLCM_counter: str = "DEVMLIN01Fr01.counter"

    DEVS1LIN01Fr1: str = "DEVS1LIN01Fr1"
    RL_counter_times_2: str = "DEVS1LIN01Fr1.counter_times_2"

    def __init__(self, broker_client: BrokerClient) -> None:
        self.lin_bus = LinNamespace(RL.lin_ns, broker_client=broker_client)
        super().__init__(
            RL.ecu_name,
            namespaces=[self.lin_bus],
            broker_client=broker_client,
            input_handlers=[self.lin_bus.create_input_handler([filters.FrameFilter(RL.DEVMLIN01Fr01)], self.on_devmlin01fr01_frame)],
        )

    async def start_lin(self):
        stream = await self.lin_bus.subscribe_headers(RL.DEVS1LIN01Fr1)

        async def on_frame():
            async for header in stream:
                await self.on_devs1lin01fr1_header(header)

        self.lin_task = asyncio.create_task(on_frame())

    async def on_devmlin01fr01_frame(self, frame: Frame) -> None:
        counter_value = frame.signals[RL.RLCM_counter]
        counter = int(counter_value) if counter_value is not None else 0

        # Publish on a lin namespace means "set the current state of this signal",
        # The value will be sent to the master when it is requested.
        # This means that we can do publish a lot of times, but only the last value will
        # be sent when the next request arrives
        await self.lin_bus.publish(WriteSignal(RL.RL_counter_times_2, counter * 2))

    async def on_devs1lin01fr1_header(self, header: Header) -> None:  # noqa: ARG002
        # Listening to the header sent by the master can be a way for slaves to perform updates
        # that should happen "per frame". E.g. sending out a sequence of values, one per frame.
        pass


async def main(avp: BehavioralModelArgs):
    logger.info("Starting RL ECU", args=avp)
    async with BrokerClient(avp.url, auth=avp.auth) as broker, RL(broker) as rl:
        await rl.start_lin()
        await rl.run_forever()


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args))
