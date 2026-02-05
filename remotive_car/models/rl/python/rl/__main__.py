from __future__ import annotations

import asyncio
from dataclasses import dataclass

import structlog
from remotivelabs.broker import BrokerClient, Frame, Header, WriteSignal
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import GenericNamespace

from .log import configure_logging

logger = structlog.get_logger(__name__)


@dataclass
class RL:
    ecu_name: str = "RL"
    lin_ns: str = "RL-RearLightLIN"

    RLCM_counter: str = "DEVMLIN01Fr01.counter"
    RL_counter_times_2: str = "DEVS1LIN01Fr1.counter_times_2"

    def __init__(self, avp: BehavioralModelArgs) -> None:
        self._broker_client = BrokerClient(avp.url, auth=avp.auth)
        self.lin_bus = GenericNamespace(
            RL.lin_ns,
            broker_client=self._broker_client,
        )
        self.bm = BehavioralModel(
            RL.ecu_name,
            namespaces=[self.lin_bus],
            broker_client=self._broker_client,
            input_handlers=[self.lin_bus.create_input_handler([filters.FrameFilter("DEVMLIN01Fr01")], self.on_devmlin01fr01_frame)],
        )

    async def start_lin(self):
        stream = await self._broker_client.subscribe_header((self.lin_ns, ["DEVS1LIN01Fr1"]))

        async def on_frame():
            async for frame in stream:
                await self.on_devs1lin01fr1_header(frame)

        self.lin_task = asyncio.create_task(on_frame())

    async def __aenter__(self):
        await self._broker_client.connect()
        await self.bm.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.bm.stop()
        await self._broker_client.disconnect()

    def __await__(self):
        return self.bm.run_forever().__await__()

    async def on_devmlin01fr01_frame(self, frame: Frame) -> None:
        counter_value = frame.signals[RL.RLCM_counter]
        counter = int(counter_value) if counter_value is not None else 0

        # Publish on a lin namespace means "set the current state of this signal",
        # The value will be sent to the master when it is requested.
        # This means that we can do publish a lot of times, but only the last value will
        # be sent when the next request arrives
        await self.lin_bus.publish(WriteSignal(RL.RL_counter_times_2, counter * 2))

    async def on_devs1lin01fr1_header(self, header: Header) -> None:
        # Listening to the header sent by the master can be a way for slaves to perform updates
        # that should happen "per frame". E.g. sending out a sequence of values, one per frame.
        pass


async def main(avp: BehavioralModelArgs):
    logger.info("Starting RL ECU", args=avp)
    async with RL(avp) as rl:
        await rl.start_lin()
        await rl


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args))
