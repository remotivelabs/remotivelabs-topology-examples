from __future__ import annotations

import asyncio
from dataclasses import dataclass

import structlog
from remotivelabs.broker import BrokerClient, Frame
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig

from .log import configure_logging

logger = structlog.get_logger(__name__)


@dataclass
class ECUB:
    ecu_name: str = "ECUB"
    net_1_ns: str = "ECUB-ecu_b_net_1_socket-ecu_a_net_1_socket-NET1"
    net_2_ns: str = "ECUB-ecu_b_net_2_socket-ecu_c_net_2_socket-NET2"

    def __init__(self, avp: BehavioralModelArgs) -> None:
        self._broker_client = BrokerClient(avp.url, auth=avp.auth)

        self.net_2 = CanNamespace(
            ECUB.net_2_ns,
            broker_client=self._broker_client,
            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name=ECUB.ecu_name)], delay_multiplier=avp.delay_multiplier)],
        )
        self.net_1 = CanNamespace(ECUB.net_1_ns, broker_client=self._broker_client)

        self.bm = BehavioralModel(
            ECUB.ecu_name,
            namespaces=[self.net_1, self.net_2],
            broker_client=self._broker_client,
            input_handlers=[
                self.net_1.create_input_handler([filters.FrameFilter("DummyFrame")], self.on_frame),
            ],
        )

    async def __aenter__(self):
        await self._broker_client.connect()
        await self.bm.start()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.bm.stop()
        await self._broker_client.disconnect()

    def __await__(self):
        return self.bm.run_forever().__await__()

    async def on_frame(self, frame: Frame) -> None:
        await self.net_2.restbus.update_signals(
            ("DummyFrame.A", frame.signals.get("DummyFrame.A") or 0),
            ("DummyFrame.B", frame.signals.get("DummyFrame.B") or 0),
            ("DummyFrame.C", frame.signals.get("DummyFrame.C") or 0),
            ("DummyFrame.D", frame.signals.get("DummyFrame.D") or 0),
        )


async def main(avp: BehavioralModelArgs):
    logger.info("Starting GWM ECU", args=avp)
    async with ECUB(avp) as gwm:
        await gwm


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args))
