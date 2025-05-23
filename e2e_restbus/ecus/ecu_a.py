import asyncio
import logging

from remotivelabs.broker import BrokerClient, Frame, SecocFreshnessValue, SecocKey
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces import filters
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig


class MyState:
    def __init__(self):
        self.my_counter = 0

    def request_update(self):
        print("increasing counter ", self.my_counter)
        self.my_counter += 1

    def get_counter(self):
        return self.my_counter


class MyConnection:
    def __init__(self, my_state: MyState):
        self.my_state = my_state

    # Print all raw frames received
    async def on_raw_frame(self, frame: Frame) -> None:
        self.my_state.request_update()
        print(f'Got raw frame "{frame.name}":', frame.value)


async def main(avp: BehavioralModelArgs):
    print("Starting EcuA simulator")
    async with BrokerClient(url=avp.url, auth=avp.auth) as broker_client:
        can0 = CanNamespace(
            name="ECUA-Can0",
            broker_client=broker_client,
            restbus_configs=[RestbusConfig([filters.SenderFilter(ecu_name="ECUA")], delay_multiplier=avp.delay_multiplier)],
        )

        my_state = MyState()
        my_connection = MyConnection(my_state)

        async with BehavioralModel(
            "ecua",
            namespaces=[can0],
            broker_client=broker_client,
            input_handlers=[can0.create_input_handler([filters.AllFramesFilter()], my_connection.on_raw_frame)],
        ) as bm:
            await can0.set_secoc_property(SecocKey(10, b"\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff"))
            await can0.set_secoc_property(SecocFreshnessValue(b"\x00\x00\x00\x00\x00\x00\x00\x00"))

            await bm.run_forever()


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    logging.basicConfig(level=args.loglevel, format="%(asctime)s.%(msecs)03d [%(levelname)s] %(message)s", datefmt="%H:%M:%S")
    asyncio.run(main(args))
