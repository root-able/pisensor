# Source: https://sensirion.github.io/python-i2c-sen5x/quickstart.html

import time

from sensirion_i2c_driver import (
    I2cConnection,
    LinuxI2cTransceiver,
)
from sensirion_i2c_scd import Scd4xI2cDevice
from sensirion_i2c_sen5x import Sen5xI2cDevice

from commons import get_byid_split


# CLASSES
class sensirion_sensor:

    def __init__(
        self,
        sensor_dev: str = "/dev/i2c-1",
    ):
        """Instanciate object"""
        self.i2c_link = I2cConnection(LinuxI2cTransceiver(sensor_dev))
        self.rawdata = None
        self.measure_names = list()
        self.measure_values = list()
        self.measure_data = dict()

    def process_measures(
        self,
        precision: int = 1,
        default_value: str = "Index",
    ) -> dict:
        """Process collected sensirion measures"""

        measure_id = 0
        for measure_object in self.measure_values:

            measure_rawvalue, measure_unit = get_byid_split(
                input_string=str(measure_object),
                string_separator=" ",
                default_value="Index",
                items_count=2,
            )
            measure_name = self.measure_names[measure_id]
            self.measure_data[measure_name] = {
                "value": round(float(measure_rawvalue), precision),
                "unit": measure_unit,
            }
            measure_id += 1

        return self.measure_data


class sensor_scd41(sensirion_sensor):

    def __init__(
        self,
        sensor_dev: str = "/dev/i2c-1",
    ):
        """Instanciate object"""

        super().__init__(sensor_dev)
        self.device = Scd4xI2cDevice(self.i2c_link)

    def get_measures(self) -> dict:
        """Used to pull measure data from i2c scd41 device"""

        # Stop all existing periodic measures
        self.device.stop_periodic_measurement()

        # Put device in idle mode by waking it up
        self.device.wake_up()

        # Initiate a single shot measure
        self.device.measure_single_shot()

        # Retrieve measured values
        self.measure_names = ["CO2", "Temperature", "Humidity"]
        self.rawdata = self.device.read_measurement()

        # Process data
        self.process_measures()

        return self.measure_data


class sensor_sen55(sensirion_sensor):

    def __init__(
        self,
        sensor_dev: str = "/dev/i2c-1",
    ):
        """Instanciate object"""

        super().__init__(sensor_dev)
        self.device = Sen5xI2cDevice(self.i2c_link)

    def process_measures(
        self,
    ) -> dict:
        """Process collected sen55 measures"""

        for measure in self.rawdata.to_str(",").split(","):
            measure_name, measure_value = get_byid_split(
                input_string=measure,
                string_separator=":",
                default_value="",
                items_count=2,
            )
            self.measure_names.append(measure_name)
            self.measure_values.append(measure_value)

        super().process_measures()

        return self.measure_data

    def get_measures(
        self,
        interval: int = 0.1,
        iterations: int = 10,
    ) -> dict:
        """Initiate measurement"""

        # Begin measure
        self.device.start_measurement()

        # Iterate specified number of times
        for i in range(iterations):

            # Wait until next result is available
            while self.device.read_data_ready() is False:
                time.sleep(interval)

            # Collect measures and process them
            self.rawdata = self.device.read_measured_values()
            self.process_measures()

        # Stop measurement
        self.device.stop_measurement()

        return self.measure_data

    def print_details(
        self,
    ):
        """Print some device information"""

        # Getting device details
        print(f"Version: {self.device.get_version()}")
        print(f"Product Name: {self.device.get_product_name()}")
        print(f"Serial Number: {self.device.get_serial_number()}")
        print(f"Device Status: {self.device.read_device_status()}")

    def reset(
        self,
    ):
        """Reset device"""

        self.device.device_reset()
