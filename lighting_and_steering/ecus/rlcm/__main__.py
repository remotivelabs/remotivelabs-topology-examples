from __future__ import annotations

import asyncio
from dataclasses import dataclass

import structlog
from remotivelabs.broker import BrokerClient, Frame, WriteSignal
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, GenericNamespace

from .log import configure_logging

logger = structlog.get_logger(__name__)


@dataclass
class RLCM:
    ecu_name: str = "RLCM"
    can_ns: str = "RLCM-BodyCan0"
    lin_ns: str = "RLCM-RearLightLIN"

    left_turn_light_request: str = "TurnLightControl.LeftTurnLightRequest"
    right_turn_light_request: str = "TurnLightControl.RightTurnLightRequest"

    def __init__(self, avp: BehavioralModelArgs) -> None:
        self._broker_client = BrokerClient(avp.url, auth=avp.auth)
        self.lin_bus = GenericNamespace(
            RLCM.lin_ns,
            broker_client=self._broker_client,
        )
        self.body_can_0 = CanNamespace(RLCM.can_ns, broker_client=self._broker_client)
        self.bm = BehavioralModel(
            RLCM.ecu_name,
            namespaces=[self.lin_bus, self.body_can_0],
            broker_client=self._broker_client,
            input_handlers=[self.body_can_0.create_input_handler([filters.FrameFilter("TurnLightControl")], self.on_turn_req_frame)],
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

    async def on_turn_req_frame(self, frame: Frame) -> None:
        logger.debug("Received frame", frame=frame)
        await self.lin_bus.publish(
            WriteSignal(
                name="DEVMLIN01Fr01.ReqLeft",
                value=frame.signals[self.left_turn_light_request],
            ),
            WriteSignal(
                name="DEVMLIN01Fr01.ReqRight",
                value=frame.signals[self.right_turn_light_request],
            ),
        )


async def main(avp: BehavioralModelArgs):
    logger.info("Starting RLCM ECU", args=avp)
    async with RLCM(avp) as rlcm:
        await rlcm


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args))
