import asyncio
import logging
import structlog
from remotivelabs.broker import BrokerClient, RestbusSignalConfig, Frame, FrameSubscription
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig, GenericNamespace
from remotivelabs.topology.namespaces import filters
from remotivelabs.broker.auth import ApiKeyAuth, TokenAuth

logger = structlog.get_logger(__name__)

LATITUDE = 123456789  # Example fixed value, use appropriate scaling for your DBC
LONGITUDE = 987654321

async def _on_hazard_button_pressed(frame: Frame) -> None:
    # print(f"Hazzard light frame {frame}")
    logger.info("hejsan")

async def main(avp: BehavioralModelArgs):
    logger.info("Starting LocationECU")
    # async with BrokerClient(url="https://personal-xktvetbdzw-aleks-base-on-open-sglnqbpwoa-ez.a.run.app:443", auth=ApiKeyAuth(api_key="F2385283-170A67D3-792CBBC9-DFF4FE14")) as broker_client:
    async with BrokerClient(url="https://personal-xktvetbdzw-aleks-base-on-open-sglnqbpwoa-ez.a.run.app:443", auth=TokenAuth("pa1.0/977EA719-AAFE48E1-6D2ADC17-19AADE3F-AD951324-C402B9D0-1A351C3D-F2A200D2")) as broker_client_cloud:
        logger.info("connected LocationECU")

        async with BrokerClient(url=avp.url, auth=avp.auth) as broker_client:
            can = CanNamespace(
                name="LocationECU-LocationCan0",
                broker_client=broker_client,
                restbus_configs=[
                    RestbusConfig([filters.SenderFilter(ecu_name="LocationECU")], cycle_time_millis=500)
                ],
            )
            async with BehavioralModel(
                "LocationECU",
                namespaces=[can],
                broker_client=broker_client,
            ):
                
                chassis_bus = CanNamespace("ChassisBus", broker_client_cloud)
                await chassis_bus.open()
                itr = await chassis_bus.subscribe_frames(FrameSubscription("ID04FGPSLatLong"), on_change=False, decode_named_values=True)
                async for frame in itr:
                    logger.info(f"Location: {frame.signals}")

                    await can.restbus.update_signals(
                        RestbusSignalConfig.set(name="LocationFrame.Latitude", value=frame.signals["ID04FGPSLatLong.GPSLatitude04F"]),
                        RestbusSignalConfig.set(name="LocationFrame.Longitude", value=frame.signals["ID04FGPSLatLong.GPSLongitude04F"]),
                    )
                    # await can.restbus.update_signals(
                    #     RestbusSignalConfig.set(name="LocationFrame.Latitude", value=23),
                    #     RestbusSignalConfig.set(name="LocationFrame.Longitude", value=43),
                    # )
                
                


        # vehicle_bus = CanNamespace("VehicleBus", broker_client_cloud)
        # chassis_bus = CanNamespace("ChassisBus", broker_client_cloud)


        # await chassis_bus.open()
        # itr = await chassis_bus.subscribe_frames(FrameSubscription("ID04FGPSLatLong"), on_change=False, decode_named_values=True)
        # async for frame in itr:
        #     logger.info(f"Location: {frame.signals}")



        # await vehicle_bus.open()
        # itr =  await vehicle_bus.subscribe("ID257DIspeed.DI_uiSpeed")
        # async for frame in itr:
        #     logger.info(f"VehicleBus speed: {frame}")

        # logger.info("open")

        # chassis_bus = CanNamespace("ChassisBus", broker_client)

        

        # a = await broker_client.list_namespaces()
        # logger.info(a)

        # async with BehavioralModel(
        #     "LocationECU",
        #     broker_client=broker_client,
        #     namespaces=[vehicle_bus, chassis_bus],
        #     # input_handlers=[
        #     #     vehicle_bus.create_input_handler(
        #     #         [filters.FrameFilter("ID257DIspeed")],
        #     #         _on_hazard_button_pressed,
        #     #     ),
        #     #     chassis_bus.create_input_handler(
        #     #         [filters.FrameFilter("ID04FGPSLatLong")],
        #     #         _on_hazard_button_pressed,
        #     #     ),
        #     # ],
        # ) as bm:
        #     logger.info("forever LocationECU")
        #     await bm.run_forever()


        # can = CanNamespace(
        #     name="LocationECU-LocationCan0",
        #     broker_client=broker_client,
        #     restbus_configs=[
        #         RestbusConfig([filters.SenderFilter(ecu_name="LocationECU")], cycle_time_millis=500)
        #     ],
        # )
        # async with BehavioralModel(
        #     "LocationECU",
        #     namespaces=[can],
        #     broker_client=broker_client,
        # ) as bm:
        #     while True:
        #         await can.restbus.update_signals(
        #             RestbusSignalConfig.set(name="LocationFrame.Latitude", value=LATITUDE),
        #             RestbusSignalConfig.set(name="LocationFrame.Longitude", value=LONGITUDE),
        #         )
        #         await asyncio.sleep(0.5)


# async def main_old(avp: BehavioralModelArgs):
#     logger.info("Starting LocationECU")
#     async with BrokerClient(url=avp.url, auth=avp.auth) as broker_client:
#         can = CanNamespace(
#             name="LocationECU-LocationCan0",
#             broker_client=broker_client,
#             restbus_configs=[
#                 RestbusConfig([filters.SenderFilter(ecu_name="LocationECU")], cycle_time_millis=500)
#             ],
#         )
#         async with BehavioralModel(
#             "LocationECU",
#             namespaces=[can],
#             broker_client=broker_client,
#         ) as bm:
#             while True:
#                 await can.restbus.update_signals(
#                     RestbusSignalConfig.set(name="LocationFrame.Latitude", value=LATITUDE),
#                     RestbusSignalConfig.set(name="LocationFrame.Longitude", value=LONGITUDE),
#                 )
#                 await asyncio.sleep(0.5)

if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    logging.basicConfig(level=args.loglevel)
    logging.getLogger("remotivelabs.topology").setLevel(logging.DEBUG)
    logging.getLogger("remotivelabs.broker").setLevel(logging.DEBUG)
    asyncio.run(main(args))