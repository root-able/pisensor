#!/usr/bin/env python

import time
import json
import requests

from commons import (
    read_yaml,
    get_snake_case,
)

from pisensor_sen55 import sensor_sen55


def update_hass_sensor(
    config: dict,
    sensor_name: str,
    sensor_data: dict,
) -> None:
    """Used to update a sensor data in Home Assistant"""

    sensor_name = "{location} - {device} - {sensor}".format(
        location=config["location"],
        device="sen55",
        sensor=sensor_name,
    )
    sensor_name_short = get_snake_case(sensor_name)
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
    time.sleep(0.1)


def sen_use(
    config_file_name: str,
) -> None:
    """Used to pull measure data from i2c sensirion device"""

    sen_settings = read_yaml(
        config_file_name,
    ).get("home_assistant", dict())

    sen_sensor = sensor_sen55()

    sen_measures = sen_sensor.get_measures(iterations=10)
    for measure_name, measure_data in sen_measures.items():
        update_hass_sensor(
            sen_settings,
            measure_name,
            measure_data,
        )


# MAIN
sen_use("settings.yaml")
