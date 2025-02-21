#!/usr/bin/env python

from sensirion_i2c_driver import LinuxI2cTransceiver, I2cConnection
from sensirion_i2c_scd import Scd4xI2cDevice

import os
import re
import json
import yaml
import pathlib
import requests


def snake_case(
    input_string: str,
) -> str:
    """Convert input string to a snake case formatted string"""
    return "_".join(
        re.sub(
            "([A-Z][a-z]+)",
            r" \1",
            re.sub("([A-Z]+)", r" \1", input_string.replace("-", " ")),
        ).split()
    ).lower()


def read_yaml(
    file_name: str,
    folder_path: str = str(),
) -> dict:
    """Used to get data from inside a YAML file"""
    if not folder_path:
        folder_path = pathlib.Path(__file__).parent.resolve()

    yaml_data = {}
    yaml_path = os.path.join(
        folder_path,
        file_name,
    )
    with open(yaml_path) as config_file:
        try:
            yaml_data = yaml.safe_load(config_file)
        except yaml.YAMLError as exc:
            print(exc)

    return yaml_data


def update_hass_sensor(
    config: dict,
    sensor_name: str,
    sensor_data: dict,
) -> None:
    """Used to update a sensor data in Home Assistant"""

    sensor_name = "{location} - {sensor}".format(
        location=config["location"],
        sensor=sensor_name,
    )
    sensor_name_short = snake_case(sensor_name)
    sensor_value = sensor_data["value"]
    sensor_unit = sensor_data["unit"]

    http_url = "http://{host}:{port}/api/states/sensor.{sensor}".format(
        host=config["host"],
        port=config["port"],
        sensor=sensor_name_short,
    )
    http_header = {
        "Authorization": "Bearer {token}".format(token=config["token"]),
        "content-type": "application/json",
    }
    http_payload = {
        "state": sensor_value,
        "attributes": {
            "unit_of_measurement": sensor_unit,
            "friendly_name": sensor_name,
        },
    }
    http_response = requests.post(
        http_url,
        headers=http_header,
        data=json.dumps(http_payload),
    )
    print(http_response.text)


def scd41_get_measures(
    config: dict,
    precision: int = 1,
) -> dict:
    """Used to pull measure data from i2c scd41 device"""
    measure_device = config["device"]
    measure_data = {}

    with LinuxI2cTransceiver(measure_device) as i2c_transceiver:
        # Initiate device communication
        scd4x = Scd4xI2cDevice(I2cConnection(i2c_transceiver))

        # Stop all existing periodic
        scd4x.stop_periodic_measurement()

        # Put device in idle mode by waking it up
        scd4x.wake_up()

        # Initiate a single shot measure
        scd4x.measure_single_shot()

        # Retrieve measured values
        co2, temperature, humidity = scd4x.read_measurement()

        # Format output data
        measure_data = {
            "CO2": {"value": co2.co2, "unit": "ppm"},
            "Temperature": {
                "value": round(temperature.degrees_celsius, precision),
                "unit": "°C",
            },
            "Humidity": {
                "value": round(humidity.percent_rh, precision),
                "unit": "%RS",
            },
        }

    return measure_data


def scd41_use(config_file_name: str) -> None:
    """Used to pull measure data from i2c scd41 device"""
    scd41_settings = read_yaml(
        config_file_name,
    ).get("home_assistant", dict())
    scd41_measures = scd41_get_measures(
        scd41_settings,
    )
    for measure_name, measure_data in scd41_measures.items():
        update_hass_sensor(
            scd41_settings,
            measure_name,
            measure_data,
        )


# MAIN
scd41_use("settings.yaml")
