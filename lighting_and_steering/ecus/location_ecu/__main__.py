import asyncio
import structlog
from remotivelabs.broker import BrokerClient, RestbusSignalConfig
from remotivelabs.topology.behavioral_model import BehavioralModel
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs
from remotivelabs.topology.namespaces.can import CanNamespace, RestbusConfig
from remotivelabs.topology.namespaces import filters

logger = structlog.get_logger(__name__)

LATITUDE = 123456789  # Example fixed value, use appropriate scaling for your DBC
LONGITUDE = 987654321

async def main(avp: BehavioralModelArgs):
    logger.info("Starting LocationECU")
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
        ) as bm:
            while True:
                await can.restbus.update_signals(
                    RestbusSignalConfig.set(name="LocationFrame.Latitude", value=LATITUDE),
                    RestbusSignalConfig.set(name="LocationFrame.Longitude", value=LONGITUDE),
                )
                await asyncio.sleep(0.5)

if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    asyncio.run(main(args))