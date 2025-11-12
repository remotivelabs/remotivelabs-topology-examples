from __future__ import annotations

import logging
import os
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path


@dataclass
class SteeringWheelArgs:
    """
    CLI arguments for configuring a steering wheel
    """

    broker_url: str
    config_file: Path
    timeout: float
    loglevel: str
    print_only: bool

    @staticmethod
    def parse() -> SteeringWheelArgs:
        parser = ArgumentParser()
        parser.add_argument(
            "-b",
            "--broker-url",
            type=str,
            default=os.environ.get("REMOTIVE_BROKER_URL", "http://localhost:50051"),
            help="Override the URL of the broker to connect to, ignoring the config file.",
        )
        parser.add_argument(
            "-c",
            "--config",
            type=Path,
            default=Path(os.environ.get("REMOTIVE_WHEELS_CONFIG_PATH", Path(__file__).parent.parent / "config" / "moza.json")),
            help="The path to the config file to use. Defaults to <project_root>/config/moza.json",
        )
        parser.add_argument(
            "-t",
            "--timeout",
            type=float,
            default=float(os.environ.get("REMOTIVE_WHEELS_TIMEOUT", "30.0")),
            help="Device connection timeout, in minutes. Timout will reset when the device connects/disconnects.",
        )
        parser.add_argument(
            "-l",
            "--loglevel",
            type=str,
            default=os.environ.get("REMOTIVE_WHEELS_LOG_LEVEL", logging.getLevelName(logging.INFO)),
            choices=[
                logging.getLevelName(logging.CRITICAL),
                logging.getLevelName(logging.FATAL),
                logging.getLevelName(logging.ERROR),
                logging.getLevelName(logging.WARNING),
                logging.getLevelName(logging.INFO),
                logging.getLevelName(logging.DEBUG),
            ],
            help="The log level to use. Defaults to INFO.",
        )
        parser.add_argument(
            "-p",
            "--print-only",
            action="store_true",
            help="Print events to the console instead of sending them to a target.",
        )
        p = parser.parse_args()
        return SteeringWheelArgs(
            broker_url=p.broker_url, config_file=p.config, timeout=p.timeout, loglevel=p.loglevel, print_only=p.print_only
        )
