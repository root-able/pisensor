#!/usr/bin/env python

from sensirion_i2c_driver import (
    LinuxI2cTransceiver,
    I2cConnection,
)
from sensirion_i2c_scd import Scd4xI2cDevice


# FUNCTIONS
def process_measures(
    co2,
    temperature,
    humidity,
    precision: int = 1,
) -> dict:
    """Process collected scd41 measures"""

    processed_data = {
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

    return processed_data


# CLASS
class sensor_scd41:

    def __init__(
        self,
        sensor_dev: str = "/dev/i2c-1",
    ):
        """Instanciate object"""

        self.device = Scd4xI2cDevice(I2cConnection(LinuxI2cTransceiver(sensor_dev)))

    def get_measures(self):
        """Used to pull measure data from i2c scd41 device"""
        measure_data = {}

        # Stop all existing periodic measures
        self.device.stop_periodic_measurement()

        # Put device in idle mode by waking it up
        self.device.wake_up()

        # Initiate a single shot measure
        self.device.measure_single_shot()

        # Retrieve measured values
        co2, temperature, humidity = self.device.read_measurement()

        # Return processed data
        return process_measures(co2, temperature, humidity)
