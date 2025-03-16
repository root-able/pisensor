#!/usr/bin/env python

import time
import json
import requests

from commons import (
    read_yaml,
    get_snake_case,
)

from pisensor_sen55 import sensor_sen55
from pisensor_scd41 import scd41_get_measures


# Classes
class HassPoster:

    def __init__(self):
        self.config = dict()
        self.http_base_url = str()
        self.http_header = dict()
        self.location = str()
        self.sensors = list()
        self.measures = dict()

    def get_config(self, file_name: str) -> dict:
        self.config = read_yaml(
            file_name,
        ).get("home_assistant", dict())
        self.http_base_url = "http://{host}:{port}/api/states/sensor".format(
            host=self.config["host"],
            port=self.config["port"],
        )
        self.http_header = {
            "Authorization": "Bearer {token}".format(token=self.config["token"]),
            "content-type": "application/json",
        }
        self.location = self.config["location"]
        self.sensors = {
            sensor_config["sensor_name"]: sensor_config["sensor_device"]
            for sensor_config in self.config["sensors"]
        }

        return self.config

    def run_sensors(self):

        for sensor_name, sensor_dev in self.sensors:

            if sensor_name == "sen5":
                sensor_instance = sensor_sen55()
                self.measures[sensor_name] = sensor_instance.get_measures(iterations=10)

            elif sensor_name == "scd41":
                self.measures[sensor_name] = scd41_get_measures(self.config)

    def post_results(
        self,
        query_interval: int = 0.1,
    ):

        for sensor_name, sensor_measures in self.measures.items():
            for measure_name, measure_data in sensor_measures.items():

                measure_name_full = "{location} - {device} - {sensor}".format(
                    location=self.location,
                    device=sensor_name,
                    sensor=measure_name,
                )
                http_url = ".".join(
                    [
                        self.http_base_url.format(),
                        get_snake_case(measure_name_full),
                    ]
                )

                measure_value = measure_data["value"]
                measure_unit = measure_data["unit"]
                http_payload = {
                    "state": measure_value,
                    "attributes": {
                        "unit_of_measurement": measure_unit,
                        "friendly_name": measure_name_full,
                    },
                }

                http_response = requests.post(
                    http_url,
                    headers=self.http_header,
                    data=json.dumps(http_payload),
                )
                print(http_response.text)
                time.sleep(query_interval)


# MAIN
client = HassPoster()
client.get_config(file_name="settings.yaml")
client.run_sensors()
client.post_results()
