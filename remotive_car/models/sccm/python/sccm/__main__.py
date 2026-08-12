from __future__ import annotations

import asyncio

import structlog
from remotivelabs.broker import BrokerClient
from remotivelabs.topology.mapping import MappingModel

from sccm.args import SteeringWheelArgs
from sccm.evdev_source import EvdevSource
from sccm.log import configure_logging

logger = structlog.get_logger(__name__)

ECU_NAME = "SCCM"


async def main(args: SteeringWheelArgs) -> None:
    """
    SCCM (Steering Column Control Module) — reads physical steering-wheel inputs from evdev devices
    and publishes them as CAN signals on the DriverCan restbus.

    The evdev `Source` is the only bespoke part; the mapping file, transforms, and CAN restbus
    output are all driven by `MappingModel`.
    """
    logger.info("starting steering wheel", args=args)
    async with BrokerClient(url=args.url, auth=args.auth) as broker:
        model = MappingModel.from_mapping_file(args.mapping, broker, ecu=ECU_NAME)
        model.register_source("custom.evdev", EvdevSource)
        await model.run_forever()


if __name__ == "__main__":
    args = SteeringWheelArgs.parse()
    configure_logging(level=args.loglevel)
    asyncio.run(main(args))
