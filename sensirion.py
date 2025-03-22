# Source: https://sensirion.github.io/python-i2c-sen5x/quickstart.html

import time

from sensirion_i2c_driver import (
    I2cConnection,
    LinuxI2cTransceiver,
)
from sensirion_i2c_scd import Scd4xI2cDevice
from sensirion_i2c_sen5x import Sen5xI2cDevice

from commons import (
    get_byid_split,
    clean_float,
)


# TODO: Rename to pisensirion_sensors


# CLASSES
class SensirionSensor:

    def __init__(
        self,
        sensor_dev: str,
    ):
        """Instanciate object"""
        self.i2c_link = I2cConnection(LinuxI2cTransceiver(sensor_dev))
        self.rawdata = None
        self.measure_names = list()
        self.measure_values = list()
        self.measure_data = dict()

    def reset(self) -> None:
        """Reset sensirion sensor"""
        return None

    def start(self) -> None:
        """Start sensirion measurment session"""
        return None

    def stop(self) -> None:
        """Stop sensirion measurment session"""
        return None

    def get_measures(self) -> None:
        """Collect sensirion measures"""
        return None

    def process_measures(
        self,
        default_unit: str,
        precision: int,
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
                "value": clean_float(measure_rawvalue, 0.0, precision),
                "unit": measure_unit,
            }
            measure_id += 1

        return self.measure_data


class SensorScd41(SensirionSensor):

    def __init__(
        self,
        sensor_dev: str = "/dev/i2c-1",
    ):
        """Instanciate object"""

        super().__init__(sensor_dev)
        self.device = Scd4xI2cDevice(self.i2c_link)
        self.measure_names = ["CO2", "Temperature", "Humidity"]

    def reset(self) -> None:
        """Used to reset the status of the sensor"""
        self.device.stop_periodic_measurement()

    def start(self) -> None:
        """Used to begin a measurement session"""
        self.device.wake_up()

    def get_measures(self) -> None:
        """Used to collect raw measure data from i2c scd41 device"""
        self.device.measure_single_shot()
        self.rawdata = self.device.read_measurement()

    def process_measures(
        self,
        default_unit: str = "Unknown",
        precision: int = 1,
    ) -> dict:
        """Used to process raw measure data to  analyzed data"""
        self.measure_values = self.rawdata
        return super().process_measures(default_unit, precision)


class SensorSen55(SensirionSensor):

    def __init__(
        self,
        sensor_dev: str = "/dev/i2c-1",
    ):
        """Instanciate object"""
        super().__init__(sensor_dev)
        self.device = Sen5xI2cDevice(self.i2c_link)

    def reset(
        self,
    ):
        """Used to reset the status of the sensor"""
        self.device.device_reset()

    def start(
        self,
    ):
        """Used to begin a measurement session"""
        self.device.start_measurement()

    def stop(
        self,
    ):
        """Used to end a measurement session"""
        self.device.stop_measurement()

    def get_measures(
        self,
        interval: int = 1,
    ) -> None:
        """Used to collect raw measure data from i2c sen55 device"""
        while self.device.read_data_ready() is False:
            time.sleep(interval)
        self.rawdata = self.device.read_measured_values()

    def process_measures(
        self,
        default_unit: str = "Index",
        precision: int = 1,
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

        return super().process_measures(default_unit, precision)

    def print_details(
        self,
    ):
        """Print some device information"""
        print(f"Version: {self.device.get_version()}")
        print(f"Product Name: {self.device.get_product_name()}")
        print(f"Serial Number: {self.device.get_serial_number()}")
        print(f"Device Status: {self.device.read_device_status()}")
