#!/usr/bin/env python

import time
import json
import requests

from commons import (
    read_yaml,
    get_snake_case,
)

from sensirion import (
    SensirionSensor,
    SensorScd41,
    SensorSen55,
)


# Classes
class HassPoster:

    def __init__(self):
        self.config = dict()
        self.http_base_url = str()
        self.http_header = dict()
        self.location = str()
        self.sensors = dict()

    def get_config(self, file_name: str) -> None:
        """Load configuration from file"""
        self.config = read_yaml(
            file_name,
        ).get("home_assistant", dict())
        self.location = self.config["location"]

    def get_sensors(self) -> None:
        """Get sensors from configuration"""

        for sensor_config in self.config["sensors"]:

            sensor_name = sensor_config["name"]
            sensor_device = sensor_config["device"]

            sensor_instance = SensirionSensor(sensor_device)
            if sensor_name == "sen55":
                sensor_instance = SensorSen55(sensor_device)

            elif sensor_name == "scd41":
                sensor_instance = SensorScd41(sensor_device)

            else:
                exit()

            self.sensors[sensor_name] = sensor_instance

    def prepare_http(self) -> None:
        """Prepare HTTP required config"""
        self.http_base_url = "http://{host}:{port}/api/states/sensor".format(
            host=self.config["host"],
            port=self.config["port"],
        )
        self.http_header = {
            "Authorization": "Bearer {token}".format(token=self.config["token"]),
            "content-type": "application/json",
        }

    def post_results(
        self,
        sensor_name: str,
        measure_name: str,
        measure_data: dict,
    ):
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

    def start_sensors(self) -> None:
        """Start the configured sensors"""
        for sensor_instance in self.sensors.values():
            sensor_instance.reset()
            sensor_instance.start()

    def run_sensors(self) -> None:
        """Run the sensors configured"""
        for sensor_name, sensor_instance in self.sensors.items():
            sensor_instance.get_measures()
            sensor_instance.process_measures()

    def stop_sensors(self) -> None:
        """Stop the configured sensors"""
        for sensor_instance in self.sensors.values():
            sensor_instance.stop()

    def post_sensors(
        self,
        query_interval: int = 0.1,
    ) -> None:
        """Post the sensor results"""
        for sensor_name, sensor_instance in self.sensors.items():
            sensor_measures = sensor_instance.measure_data
            for measure_name, measure_data in sensor_measures.items():
                self.post_results(sensor_name, measure_name, measure_data)
                time.sleep(query_interval)


# MAIN
client = HassPoster()
client.get_config(file_name="settings.yaml")
client.get_sensors()
client.start_sensors()
client.run_sensors()
client.stop_sensors()
client.post_sensors()
