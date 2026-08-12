from __future__ import annotations

import os
from argparse import ArgumentParser
from dataclasses import dataclass
from pathlib import Path

from remotivelabs.broker.auth import AuthMethod
from remotivelabs.topology.cli.args import add_broker_args, add_loglevel_arg, broker_auth

_DEFAULT_MAPPING = Path(__file__).parent.parent / "config" / "moza.mapping.yaml"


@dataclass(frozen=True)
class SteeringWheelArgs:
    """
    CLI arguments for configuring a steering wheel.

    Attributes:
        url: RemotiveBroker URL.
        auth: Auth method to use for RemotiveBroker.
        mapping: Path to the remotive-topology-mapping YAML file.
        loglevel: Logging level.
    """

    url: str
    auth: AuthMethod
    mapping: Path
    loglevel: str

    @staticmethod
    def parse() -> SteeringWheelArgs:
        parser = ArgumentParser(description="Publish physical steering-wheel inputs as CAN signals.")
        add_broker_args(parser)
        add_loglevel_arg(parser)
        parser.add_argument(
            "-m",
            "--mapping",
            type=Path,
            default=Path(os.environ.get("REMOTIVE_WHEELS_CONFIG_PATH", _DEFAULT_MAPPING)),
            metavar="PATH",
            help="Path to the mapping file to use. Defaults to <project_root>/config/moza.mapping.yaml",
        )
        p, _ = parser.parse_known_args()
        return SteeringWheelArgs(url=p.url, auth=broker_auth(p.x_api_key), mapping=p.mapping, loglevel=p.loglevel)
