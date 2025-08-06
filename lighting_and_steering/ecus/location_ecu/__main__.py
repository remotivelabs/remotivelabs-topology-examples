import os
import asyncio
import logging
import structlog
from remotivelabs.broker import BrokerClient, RestbusSignalConfig, FrameSubscription
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig
from remotivelabs.topology.namespaces import filters
from remotivelabs.broker.auth import TokenAuth

logger = structlog.get_logger(__name__)

async def main(avp: BehavioralModelArgs):
    logger.info("Starting LocationECU")
    cloud_url = os.environ.get("CLOUD_URL")
    cloud_auth = os.environ.get("CLOUD_AUTH")
    if not cloud_url:
        raise RuntimeError("CLOUD_URL environment variable is not set or empty.")
    if not cloud_auth:
        raise RuntimeError("CLOUD_AUTH environment variable is not set or empty.")

    async with BrokerClient(url=cloud_url, auth=TokenAuth(cloud_auth)) as cloud_broker_client:
        logger.info("connected LocationECU")

        async with BrokerClient(url=avp.url, auth=avp.auth) as broker_client:
            can = CanNamespace(
                name="LocationECU-LocationCan0",
                broker_client=broker_client,
                restbus_configs=[
                    RestbusConfig([filters.SenderFilter(ecu_name="LocationECU")])
                ],
            )
            async with BehavioralModel(
                "LocationECU",
                namespaces=[can],
                broker_client=broker_client,
            ) as bm:
                
                chassis_bus = CanNamespace("ChassisBus", cloud_broker_client)
                await chassis_bus.open()
                itr = await chassis_bus.subscribe_frames(FrameSubscription("ID04FGPSLatLong"), on_change=False, decode_named_values=True)

                vehicle_bus = CanNamespace("VehicleBus", cloud_broker_client)
                await vehicle_bus.open()
                speed_itr = await vehicle_bus.subscribe_frames(FrameSubscription("ID257DIspeed"), on_change=False, decode_named_values=True)

                async def handle_location():
                    async for frame in itr:
                        # logger.info("Received location frame", frame=frame)
                        await can.restbus.update_signals(
                            RestbusSignalConfig.set(name="LocationFrame.Latitude", value=frame.signals["ID04FGPSLatLong.GPSLatitude04F"]),
                            RestbusSignalConfig.set(name="LocationFrame.Longitude", value=frame.signals["ID04FGPSLatLong.GPSLongitude04F"]),
                        )

                async def handle_speed():
                    async for frame in speed_itr:
                        # logger.info("Received speed frame", frame=frame)
                        await can.restbus.update_signals(
                            RestbusSignalConfig.set(name="UISpeedFrame.uispeed", value=frame.signals["ID257DIspeed.DI_uiSpeed"]),
                        )
                await asyncio.gather(handle_location(), handle_speed(), bm.run_forever())


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    logging.basicConfig(level=args.loglevel)
    logging.getLogger("remotivelabs.topology").setLevel(logging.DEBUG)
    # logging.getLogger("remotivelabs.broker").setLevel(logging.DEBUG)
    asyncio.run(main(args))