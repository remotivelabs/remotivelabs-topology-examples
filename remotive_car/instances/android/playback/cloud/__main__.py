import asyncio
import logging
import os

import structlog
from remotivelabs.broker import BrokerClient, FrameSubscription, RestbusSignalConfig
from remotivelabs.broker.auth import TokenAuth
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces.can import CanNamespace

logger = structlog.get_logger(__name__)


async def main(avp: BehavioralModelArgs):
    logger.info("Starting cloud playback")
    logger.info("Connecting broker", url=avp.url)
    cloud_url = os.environ.get("CLOUD_URL")
    cloud_auth = os.environ.get("CLOUD_AUTH")
    if not cloud_url:
        raise RuntimeError("CLOUD_URL environment variable is not set or empty.")
    if not cloud_auth:
        raise RuntimeError("CLOUD_AUTH environment variable is not set or empty.")

    async with BrokerClient(url=cloud_url, auth=TokenAuth(cloud_auth)) as cloud_broker_client:
        async with BrokerClient(url=avp.url, auth=avp.auth) as broker_client:
            chassis_bus = CanNamespace("ChassisBus", cloud_broker_client)
            await chassis_bus.open()
            latlong_itr = await chassis_bus.subscribe_frames(
                FrameSubscription("ID04FGPSLatLong"), on_change=False, decode_named_values=True
            )
            solar_itr = await chassis_bus.subscribe_frames(
                FrameSubscription("ID2D3UI_solarData"), on_change=False, decode_named_values=True
            )

            vehicle_bus = CanNamespace("VehicleBus", cloud_broker_client)
            await vehicle_bus.open()

            speed_itr = await vehicle_bus.subscribe_frames(FrameSubscription("ID257DIspeed"), on_change=False, decode_named_values=True)
            steering_angle_itr = await vehicle_bus.subscribe_frames(
                FrameSubscription("ID129SteeringAngle"), on_change=False, decode_named_values=True
            )
            brake_pedal_itr = await vehicle_bus.subscribe_frames(
                FrameSubscription("ID3C2VCLEFT_switchStatus"), on_change=False, decode_named_values=True
            )
            accelerator_pedal_itr = await vehicle_bus.subscribe_frames(
                FrameSubscription("ID118DriveSystemStatus"), on_change=False, decode_named_values=True
            )
            lighting_itr = await vehicle_bus.subscribe_frames(
                FrameSubscription("ID3F5VCFRONT_lighting"), on_change=False, decode_named_values=True
            )

            await asyncio.gather(
                handle_location(latlong_itr, broker_client),
                handle_heading(solar_itr, broker_client),
                handle_speed(speed_itr, broker_client),
                handle_steering_angle(steering_angle_itr, broker_client),
                handle_brake_pedal(brake_pedal_itr, broker_client),
                handle_accelerator_pedal(accelerator_pedal_itr, broker_client),
                handle_lighting(lighting_itr, broker_client),
            )


async def handle_location(itr, broker_client):
    async for frame in itr:
        logger.info("received location", frame=frame)
        await broker_client.restbus.update_signals(
            (
                "TCU-BodyCan0",
                [
                    RestbusSignalConfig.set(name="LocationFrame.Latitude", value=frame.signals["ID04FGPSLatLong.GPSLatitude04F"]),
                    RestbusSignalConfig.set(name="LocationFrame.Longitude", value=frame.signals["ID04FGPSLatLong.GPSLongitude04F"]),
                ],
            )
        )


async def handle_heading(itr, broker_client):
    async for frame in itr:
        heading = (
            float(frame.signals["ID2D3UI_solarData.UI_solarAzimuthAngle"])
            - float(frame.signals["ID2D3UI_solarData.UI_solarAzimuthAngleCarRef"])
        ) % 360
        await broker_client.restbus.update_signals(
            (
                "TCU-BodyCan0",
                [RestbusSignalConfig.set(name="LocationFrame.Heading", value=heading)],
            )
        )


async def handle_speed(itr, broker_client):
    async for frame in itr:
        await broker_client.restbus.update_signals(
            (
                "ABS-ChassisCan0",
                [
                    RestbusSignalConfig.set(name="UISpeedFrame.uispeed", value=(float(frame.signals["ID257DIspeed.DI_uiSpeed"]) / 3.6)),
                ],
            )
        )


async def handle_steering_angle(itr, broker_client):
    async for frame in itr:
        steering_angle = frame.signals["ID129SteeringAngle.SteeringAngle129"]
        if steering_angle is not None:
            await broker_client.restbus.update_signals(
                (
                    "SCCM-DriverCan0",
                    [RestbusSignalConfig.set(name="SteeringAngle.SteeringAngle", value=steering_angle)],
                )
            )


async def handle_brake_pedal(itr, broker_client):
    async for frame in itr:
        if frame.signals["ID3C2VCLEFT_switchStatus.VCLEFT_switchStatusIndex"] == "VCLEFT_SWITCH_STATUS_INDEX_0":
            brake_pedal = frame.signals["ID3C2VCLEFT_switchStatus.VCLEFT_brakePressed"]
            if brake_pedal is not None:
                await broker_client.restbus.update_signals(
                    (
                        "SCCM-DriverCan0",
                        [RestbusSignalConfig.set(name="BrakePedalPositionSensor.BrakePedalPosition", value=brake_pedal * 100)],
                    )
                )


async def handle_accelerator_pedal(itr, broker_client):
    async for frame in itr:
        accelerator_pedal = frame.signals["ID118DriveSystemStatus.DI_accelPedalPos"]
        if accelerator_pedal is not None and accelerator_pedal != 127:
            await broker_client.restbus.update_signals(
                (
                    "SCCM-DriverCan0",
                    [RestbusSignalConfig.set(name="AcceleratorPedalPositionSensor.AcceleratorPedalPosition", value=accelerator_pedal)],
                )
            )


async def handle_lighting(itr, broker_client):
    async for frame in itr:
        left_indicator = frame.signals["ID3F5VCFRONT_lighting.VCFRONT_indicatorLeftRequest"]
        right_indicator = frame.signals["ID3F5VCFRONT_lighting.VCFRONT_indicatorRightRequest"]
        if left_indicator is not None and right_indicator is not None:
            turn_signal = 0
            if left_indicator != "TURN_SIGNAL_OFF":
                turn_signal = 1
            elif right_indicator != "TURN_SIGNAL_OFF":
                turn_signal = 2

            await broker_client.restbus.update_signals(
                (
                    "SCCM-DriverCan0",
                    [RestbusSignalConfig.set(name="TurnStalk.TurnSignal", value=turn_signal)],
                )
            )


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    logging.basicConfig(level=args.loglevel)
    logging.getLogger("remotivelabs.topology").setLevel(logging.DEBUG)
    # logging.getLogger("remotivelabs.broker").setLevel(logging.DEBUG)
    asyncio.run(main(args))
