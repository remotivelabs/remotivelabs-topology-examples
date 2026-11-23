import argparse
import asyncio
import os

from remotivelabs.broker import BrokerClient, RestbusSignalConfig


async def main(broker_url: str, namespace: str, signal_name: str, value: float):
    async with BrokerClient(url=broker_url) as broker_client:
        await broker_client.restbus.update_signals((namespace, [RestbusSignalConfig.set(name=signal_name, value=value)]))
        print(f"Updated {namespace}:{signal_name} to {value}")


def parse_args():
    parser = argparse.ArgumentParser()

    def parse_signal_name(s: str):
        arr = s.split(":")
        if len(arr) != 2:
            raise argparse.ArgumentTypeError("must have format namespace:signal")
        return arr

    parser.add_argument(
        "--broker_url",
        action="store",
        default=os.environ.get("BROKER_URL", "http://127.0.0.1:50051"),
        type=str,
        help="Broker to run tests towards, e.g. http://127.0.0.1:50051.",
    )
    parser.add_argument(
        "--signal",
        action="store",
        required=True,
        type=parse_signal_name,
        metavar="NAMESPACE:SIGNAL",
        help="Signal to update, e.g. 'SCCM-DriverCan0:SteeringAngle.SteeringAngle'.",
    )
    parser.add_argument(
        "--value",
        action="store",
        required=True,
        type=float,
        help="Value to update signal with.",
    )
    args, _ = parser.parse_known_args()
    return args


if __name__ == "__main__":
    args = parse_args()
    asyncio.run(main(args.broker_url, args.signal[0], args.signal[1], args.value))
