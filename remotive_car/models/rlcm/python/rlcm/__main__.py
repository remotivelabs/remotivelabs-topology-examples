from __future__ import annotations

import asyncio
from typing import Final

import structlog
from remotivelabs.broker import BrokerClient, Frame, WriteSignal
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace
from remotivelabs.topology.namespaces.lin import LinNamespace

from .log import configure_logging

LOGGER = structlog.get_logger(__name__)


class RLCM(BehavioralModel):
    """
    Rear Light Control Module (RLCM) ECU acting as a gateway between the body CAN bus and the rear light LIN bus.

    RLCM is a LIN master.
    """

    ecu_name: Final[str] = "RLCM"
    can_ns: Final[str] = "RLCM-BodyCan0"
    lin_ns: Final[str] = "RLCM-RearLightLIN"

    can_turn_light_frame: Final[str] = "TurnLightControl"
    can_left_turn_light_request: Final[str] = "TurnLightControl.LeftTurnLightRequest"
    can_right_turn_light_request: Final[str] = "TurnLightControl.RightTurnLightRequest"

    lin_master_frame: Final[str] = "DEVMLIN01Fr01"
    lin_master_left_light_request: Final[str] = "DEVMLIN01Fr01.ReqLeft"
    lin_master_right_light_request: Final[str] = "DEVMLIN01Fr01.ReqRight"
    lin_master_counter: Final[str] = "DEVMLIN01Fr01.counter"

    # 2 bit unsigned int counter
    counter: int = 0

    def __init__(self, broker_client: BrokerClient) -> None:
        self.lin_bus = LinNamespace(RLCM.lin_ns, broker_client=broker_client)
        self.body_can_0 = CanNamespace(RLCM.can_ns, broker_client=broker_client)
        super().__init__(
            RLCM.ecu_name,
            namespaces=[self.lin_bus, self.body_can_0],
            broker_client=broker_client,
            input_handlers=[
                self.body_can_0.create_input_handler([filters.FrameFilter(RLCM.can_turn_light_frame)], self.on_turn_req_frame),
                self.lin_bus.create_input_handler([filters.FrameFilter(RLCM.lin_master_frame)], self.on_devmlin01fr01_frame),
            ],
        )

    async def on_turn_req_frame(self, frame: Frame) -> None:
        await self.lin_bus.publish(
            WriteSignal(
                name=RLCM.lin_master_left_light_request,
                value=frame.signals[RLCM.can_left_turn_light_request],
            ),
            WriteSignal(
                name=RLCM.lin_master_right_light_request,
                value=frame.signals[RLCM.can_right_turn_light_request],
            ),
        )

    # A master can send updates "per frame" by listening to the frame
    # sent by itself. For slaves, the same thing can be accomplished by
    # listening to the header messages.
    async def on_devmlin01fr01_frame(self, _frame: Frame) -> None:
        self.counter = (self.counter + 1) % 4
        await self.lin_bus.publish(
            WriteSignal(name=RLCM.lin_master_counter, value=self.counter),
        )


async def main(avp: BehavioralModelArgs):
    LOGGER.info("Starting RLCM ECU", args=avp)
    async with BrokerClient(avp.url, auth=avp.auth) as broker, RLCM(broker) as rlcm:
        await rlcm.run_forever()


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args))
