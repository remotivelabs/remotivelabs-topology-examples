import asyncio

import structlog

from sccm.adapters.ecu import SCCM
from sccm.adapters.evdev_to_topology_mapper import EvdevToTopologyMapper
from sccm.adapters.log import configure_logging
from sccm.adapters.printer import Printer
from sccm.args import SteeringWheelArgs
from sccm.config import Config, read_config
from sccm.device import Device
from sccm.device_control import DeviceControl
from sccm.event_loop import EventLoop
from sccm.mapper import Mapper
from sccm.target import Target

logger = structlog.get_logger(__name__)


async def main(args: SteeringWheelArgs):
    logger.info("starting steering wheel", args=args)
    timeout_in_sec = args.timeout * 60

    logger.debug("loading configuration", config_file=args.config_file)
    config: Config = read_config(args.config_file)

    device_control = DeviceControl(config=config, timeout_in_sec=timeout_in_sec)

    # loop to allow devices and targets to reconnect if connection is lost
    while True:
        try:
            wait_for_device_task = device_control.create_task()
            device: Device = await wait_for_device_task

            logger.info("creating mapper", config=device.config)
            mapper: Mapper = EvdevToTopologyMapper(config=device.config)

            if args.print_only:
                logger.info("using printer target")
                target: Target = Printer()
            else:
                broker_url = args.broker_url or device.config.broker.url
                target = SCCM(broker_url=broker_url)

            logger.debug("running event loop")
            loop = EventLoop(device=device, mapper=mapper, target=target)
            loop_task = loop.create_task()
            await loop_task

        except TimeoutError:
            logger.error("no device found within timeout, exiting...", timeout_in_min=args.timeout)
            return
        except Exception:
            logger.exception("loop exited due to error, restarting...")
        except KeyboardInterrupt:
            logger.info("keyboard interrupt, exiting...")
            return


def entrypoint():
    args = SteeringWheelArgs.parse()
    configure_logging(level=args.loglevel)
    asyncio.run(main(args))


if __name__ == "__main__":
    entrypoint()
