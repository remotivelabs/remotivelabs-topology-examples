from typing import AsyncIterator

import pytest
import pytest_asyncio
from remotivelabs.broker import BrokerClient, RestbusSignalConfig
from remotivelabs.topology.behavioral_model import PingRequest
from remotivelabs.topology.control import ControlClient
from remotivelabs.topology.testing.frames import capture_frames


@pytest_asyncio.fixture()
async def broker_client(request: pytest.FixtureRequest) -> AsyncIterator[BrokerClient]:
    # Get broker URL from the command line
    url = request.config.getoption("broker_url")
    async with BrokerClient(url=url) as broker_client, ControlClient(broker_client) as cc:
        # Validate that models are started
        await cc.send(target_ecu="SCCM", request=PingRequest(), timeout=1, retries=10)
        yield broker_client


@pytest.mark.asyncio
@pytest.mark.timeout(10, func_only=True)
async def test_light_turns_on_when_hazard_button_is_pressed(broker_client: BrokerClient):
    # We start sending the new signal. Note how we can control the restbus from the test case directly.
    # This should cause the bcm to send TurnLightControl.RightTurnLightRequest and TurnLightControl.LeftTurnLightRequest
    # with value 1 to the FLCM
    await broker_client.restbus.update_signals(
        ("SCCM-DriverCan0", [RestbusSignalConfig.set(name="HazardLightButton.HazardLightButton", value=1)])
    )

    # We subscribe to TurnLightControl frame on FLCM-BodyCan0 and validate the signal value
    async with capture_frames((broker_client, "FLCM-BodyCan0"), ["TurnLightControl"]) as cap:
        await cap.wait_for_frame(
            "TurnLightControl",
            {"TurnLightControl.RightTurnLightRequest": 1.0, "TurnLightControl.LeftTurnLightRequest": 1.0},
            timeout=9,
        )
