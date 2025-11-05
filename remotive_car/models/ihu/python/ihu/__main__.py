from __future__ import annotations

import asyncio
from dataclasses import dataclass

import structlog
from remotivelabs.broker import BrokerClient
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.some_ip import SomeIPEvent, SomeIPNamespace

from .log import configure_logging

logger = structlog.get_logger(__name__)


@dataclass
class IHU:
    someip_ns: str = "IHU-SOMEIP"
    ecu_name: str = "IHU"

    def __init__(self, avp: BehavioralModelArgs) -> None:
        self._broker_client = BrokerClient(url=avp.url, auth=avp.auth)

        self._some_ip_eth = SomeIPNamespace(IHU.someip_ns, client_id=3, broker_client=self._broker_client)
        self.bm = BehavioralModel(
            IHU.ecu_name,
            namespaces=[self._some_ip_eth],
            broker_client=self._broker_client,
            input_handlers=[
                self._some_ip_eth.create_input_handler(
                    [filters.SomeIPEventFilter(service_instance_name="TurnlightIndicator", event_name="TurnlightControlEvent")],
                    self.on_event,
                ),
                self._some_ip_eth.create_input_handler(
                    [filters.SomeIPEventFilter(service_instance_name="LocationService", event_name="LocationEvent")],
                    self.on_event,
                ),
                self._some_ip_eth.create_input_handler(
                    [filters.SomeIPEventFilter(service_instance_name="SpeedService", event_name="SpeedEvent")],
                    self.on_event,
                ),
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

    async def on_event(self, event: SomeIPEvent) -> None:
        pass


async def main(avp: BehavioralModelArgs):
    logger.info("Starting IHU ECU", args=avp)

    async with IHU(avp) as ihu:
        await ihu


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    asyncio.run(main(args))
