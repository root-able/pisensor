# Source: https://sensirion.github.io/python-i2c-sen5x/quickstart.html

import time

from commons import (
    get_byid_split,
)

from sensirion_i2c_driver import (
    I2cConnection,
    LinuxI2cTransceiver,
)
from sensirion_i2c_sen5x import Sen5xI2cDevice


# CLASSES
def process_measures(
    values,
) -> dict:
    """Process collected sen55 measures"""

    measured_data = dict()

    for measure in values.to_str(",").split(","):
        measure_name, measure_value = get_byid_split(
            input_string=measure,
            string_separator=":",
            default_value="",
            items_count=2,
        )
        measure_rawvalue, measure_unit = get_byid_split(
            input_string=measure_value,
            string_separator=" ",
            default_value="Index",
            items_count=2,
        )
        measured_data[measure_name] = {
            "value": measure_rawvalue,
            "unit": measure_unit,
        }

    return measured_data


class sensor_sen55:

    def __init__(
        self,
        sensor_dev: str = "/dev/i2c-1",
    ):
        """Instanciate object"""

        self.device = Sen5xI2cDevice(I2cConnection(LinuxI2cTransceiver(sensor_dev)))

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

    def get_measures(
        self,
        interval: int = 0.1,
        iterations: int = 10,
    ):
        """Initiate measurement"""

        # Initiate data object
        measured_data = dict()

        # Begin measure
        self.device.start_measurement()

        # Iterate specified number of times
        for i in range(iterations):

            # Wait until next result is available
            while self.device.read_data_ready() is False:
                time.sleep(interval)

            # Collect measures and process them
            values = self.device.read_measured_values()
            measured_data = process_measures(values)

        # Stop measurement
        self.device.stop_measurement()

        return measured_data
