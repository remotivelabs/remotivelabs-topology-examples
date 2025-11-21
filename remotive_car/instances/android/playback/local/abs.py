import asyncio
from dataclasses import dataclass

import structlog
from remotivelabs.broker import BrokerClient, Frame, RestbusSignalConfig
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig
from remotivelabs.topology.namespaces.generic import GenericNamespace

from .log import configure_logging

logger = structlog.get_logger(__name__)


@dataclass
class ABS:
    ecu_name: str = "ABS"
    vss_namespace_name: str = "ABS-VSS"
    chassis_can_namespace_name: str = "ABS-ChassisCan0"

    speed_signal_vss: str = "Vehicle.Speed"
    speed_signal: str = "UISpeedFrame.uispeed"

    def __init__(self, avp: BehavioralModelArgs) -> None:
        self._broker_client = BrokerClient(avp.url, auth=avp.auth)
        self.chassis_can = CanNamespace(
            ABS.chassis_can_namespace_name,
            broker_client=self._broker_client,
            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name=ABS.ecu_name)], delay_multiplier=avp.delay_multiplier)],
        )
        self.vss = GenericNamespace(
            ABS.vss_namespace_name,
            broker_client=self._broker_client,
        )
        self.bm = BehavioralModel(
            ABS.ecu_name,
            namespaces=[self.vss, self.chassis_can],
            broker_client=self._broker_client,
            input_handlers=[
                self.vss.create_input_handler([filters.FrameFilter(frame_name=ABS.speed_signal_vss)], self.on_speed_frame),
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

    async def on_speed_frame(self, frame: Frame) -> None:
        await self.chassis_can.restbus.update_signals(
            RestbusSignalConfig.set(name=ABS.speed_signal, value=frame.value),
        )


async def main(avp: BehavioralModelArgs):
    logger.info("Starting ABS ECU", args=avp)
    async with ABS(avp) as abs:
        await abs


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args))
