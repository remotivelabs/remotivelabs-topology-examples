from __future__ import annotations

from pathlib import Path

from sccm import config


def test_parse_logitech_config():
    """Test that the Logitech config file can be parsed properly"""
    # setup
    config_file = Path("config/logitech.json")

    # when
    data = config.read_config(config_file)

    # then
    assert data.name == "Logitech G29 Racing Wheel"
    assert data.broker.url == "http://sccm-broker:50051"
    assert len(data.devices) == 1

    assert "Logitech G29 Driving Force Racing Wheel" in data.devices.keys()
    assert len(data.devices["Logitech G29 Driving Force Racing Wheel"].button_mappings) == 7


def test_parse_moza_config():
    """Test that the Moza config file can be parsed properly"""
    # setup
    config_file = Path("config/moza.json")

    # when
    data = config.read_config(config_file)

    # then
    assert data.name == "Gudsen R3 Racing Wheel"
    assert data.broker.url == "http://sccm-broker:50051"
    assert len(data.devices) == 2

    assert "Gudsen R3 Racing Wheel and Pedals" in data.devices
    assert len(data.devices["Gudsen R3 Racing Wheel and Pedals"].button_mappings) == 6

    assert "Gudsen MOZA Multi-function Stalk" in data.devices
    assert len(data.devices["Gudsen MOZA Multi-function Stalk"].button_mappings) == 5
