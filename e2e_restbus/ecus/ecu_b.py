from __future__ import annotations

import asyncio
import logging

from remotivelabs.broker import BrokerClient, Frame
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.control import ControlRequest, ControlResponse
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig


async def __on_raw_frame(frame: Frame) -> None:
    print(f"Got frame with id {frame.name} payload: {frame.value!r} signals: {frame.signals}")


async def __some_frame_10ms(frame: Frame) -> None:
    print(f"Got frame with id {frame.name} payload: {frame.value!r} signals: {frame.signals}")


async def on_contro_signal(request: ControlRequest) -> ControlResponse:
    return ControlResponse(status="ok", data=request.argument)


async def main(avp: BehavioralModelArgs):
    print("Starting EcuB simulator")
    async with BrokerClient(url=avp.url, auth=avp.auth) as broker_client:
        can0 = CanNamespace(
            name="ECUB-Can0",
            broker_client=broker_client,
            restbus_configs=[
                RestbusConfig(
                    [filters.SenderFilter(ecu_name="ECUB")],
                    delay_multiplier=avp.delay_multiplier,
                ),
                RestbusConfig(
                    [filters.FrameFilter(frame_name="FrameWithNoCycleTime")], cycle_time_millis=500, delay_multiplier=avp.delay_multiplier
                ),
            ],
        )
        async with BehavioralModel(
            "ecub",
            namespaces=[can0],
            broker_client=broker_client,
            input_handlers=[
                can0.create_input_handler(
                    [filters.AllFramesFilter(), filters.FrameFilter(frame_name="SomeFrame_10ms", include=False)], __on_raw_frame
                ),
                can0.create_input_handler([filters.FrameFilter("SomeFrame_10ms")], __some_frame_10ms),
            ],
            control_handlers=[("ecub_control_message", on_contro_signal)],
        ) as bm:
            await bm.run_forever()


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    logging.basicConfig(level=args.loglevel, format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    asyncio.run(main(args))
