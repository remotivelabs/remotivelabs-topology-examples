from __future__ import annotations

import structlog
from remotivelabs.broker import BrokerClient
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig
from typing_extensions import Self

from sccm.adapters.evdev_to_topology_mapper import Signal
from sccm.target import Target

logger = structlog.get_logger(__name__)


class SCCM(Target):
    def __init__(self, broker_url: str) -> None:
        self._name = "SCCM"
        self._namespace = "SCCM-DriverCan0"
        self._broker_url = broker_url
        self._bus: CanNamespace | None = None

    async def __aenter__(self) -> Self:
        logger.debug("starting simulation", broker_url=self._broker_url, client_name=self._name)
        self._broker_client = BrokerClient(url=self._broker_url)
        await self._broker_client.connect()
        self._bus = CanNamespace(
            name=self._namespace,
            broker_client=self._broker_client,
            restbus_configs=[RestbusConfig(restbus_filters=[filters.SenderFilter(ecu_name=self._name)])],
        )
        await self._bus.open()
        await self._bus.restbus.start()

        return self

    async def __aexit__(self, exc_type, exc_value, traceback) -> None:
        if self._bus:
            logger.debug("stopping simulation", client_name=self._name)
            await self._bus.close()
            await self._broker_client.disconnect()

    async def send(self, output_event: Signal) -> None:
        assert self._bus is not None
        await self._bus.restbus.update_signals((output_event.signal_id, output_event.value))
