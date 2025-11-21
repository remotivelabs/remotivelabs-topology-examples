from __future__ import annotations

import argparse
import asyncio

import structlog
from remotivelabs.broker.recording_session import RecordingSessionClient
from remotivelabs.topology.cli.behavioral_model import BehavioralModelArgs

from .log import configure_logging

logger = structlog.get_logger(__name__)


async def main(avp: BehavioralModelArgs, recording_session: str):
    logger.info("Starting csv playback", args=avp, recording_session=recording_session)
    async with (
        RecordingSessionClient(avp.url, auth=avp.auth) as client,
        client.get_session(recording_session, force_reopen=True) as session,
    ):
        await session.set_repeat(0)
        await session.play(0)
        await asyncio.Event().wait()


def parse_recording_args(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--recording-session", help="Path to recording session file", required=True)
    recording_args, _ = parser.parse_known_args(argv)
    return recording_args


if __name__ == "__main__":
    args = BehavioralModelArgs.parse()
    configure_logging(args.loglevel)
    recording_args = parse_recording_args()

    asyncio.run(main(args, recording_args.recording_session))
