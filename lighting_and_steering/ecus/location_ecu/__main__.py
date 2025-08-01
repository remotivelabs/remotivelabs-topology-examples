import asyncio
import logging
import structlog
from remotivelabs.broker import BrokerClient, RestbusSignalConfig, FrameSubscription
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig
from remotivelabs.topology.namespaces import filters
from remotivelabs.broker.auth import ApiKeyAuth, TokenAuth

logger = structlog.get_logger(__name__)

async def main(avp: BehavioralModelArgs):
    logger.info("Starting LocationECU")
    async with BrokerClient(url="https://personal-xktvetbdzw-arm-demo-sglnqbpwoa-ez.a.run.app:443", auth=ApiKeyAuth(api_key="05C8A73B-18F85959-B8AA8717-1776F8B6")) as cloud_broker_client:
    # async with BrokerClient(url="https://personal-xktvetbdzw-arm-demo-sglnqbpwoa-ez.a.run.app:443", auth=ApiKeyAuth(api_key="05C8A73B-18F85959-B8AA8717-1776F8B60")) as cloud_broker_client:
    # async with BrokerClient(url="https://personal-xktvetbdzw-aleks-base-on-open-sglnqbpwoa-ez.a.run.app:443", auth=TokenAuth("pa1.0/977EA719-AAFE48E1-6D2ADC17-19AADE3F-AD951324-C402B9D0-1A351C3D-F2A200D2")) as cloud_broker_client:
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
            ):
                
                chassis_bus = CanNamespace("ChassisBus", cloud_broker_client)
                await chassis_bus.open()
                itr = await chassis_bus.subscribe_frames(FrameSubscription("ID04FGPSLatLong"), on_change=False, decode_named_values=True)
                async for frame in itr:
                    # logger.info(f"Location: {frame.signals}")

                    await can.restbus.update_signals(
                        RestbusSignalConfig.set(name="LocationFrame.Latitude", value=frame.signals["ID04FGPSLatLong.GPSLatitude04F"]),
                        RestbusSignalConfig.set(name="LocationFrame.Longitude", value=frame.signals["ID04FGPSLatLong.GPSLongitude04F"]),
                    )

if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    logging.basicConfig(level=args.loglevel)
    logging.getLogger("remotivelabs.topology").setLevel(logging.DEBUG)
    # logging.getLogger("remotivelabs.broker").setLevel(logging.DEBUG)
    asyncio.run(main(args))