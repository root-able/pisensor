# pisensor

The objective of this project is to enable reporting for sensors of the SCD4X family to a Home Assistant instance, in the simplest and most straightforward way.

## Pre-Requisites

### Hardware

The code provided by this project is meant to be used in the following hardware configuration:

- Raspberry Pi or other ARM-based, GPIO-enabled compatible device.
- A sensor of the SCD4X family.
- Connection wires to bridge the two devices together.

#### Connection Pattern

The connection pattern between the two devices must respect the one described in [Sensirion's documentation](https://github.com/Sensirion/python-i2c-scd4x?tab=readme-ov-file#connect-the-sensor).
Here is a short summary of the connection pattern between each of the 4 connectors of the sensor, to the Raspberry Pi GPIO:

- <u>VCC:</u> *Pin 1*
- <u>SDA:</u> *Pin 3*
- <u>SCL:</u> *Pin 5*
- <u>GND:</u> *Pin 6*

With this connection pattern, the sensor should then be physically available through the I2C bus.

<u><i>Note:</i></u> SDA and SCL pins may be mutualized if already in use by other GPIO-connected devices. However, be aware that a pull-up resistance may sometime be required depending on the hardware configuration.

### Software

This project relies on [python drivers](https://github.com/Sensirion/python-i2c-scd4x) provided by Sensirion for the SCD4x sensor family.

## Initial Setup

### I2C Bus Setup

In order to make sure that the sensor is available at the software level, the following verification must be performed:

- The I2C interface is enabled on the Raspberry Pi.
- The I2C address of the device is set to the [default driver configuration of 0x62](https://github.com/Sensirion/python-i2c-scd4x?tab=readme-ov-file#supported-sensor-types).

To perform these verifications, follow the steps listed below.

#### Enable I2C Interface

```bash
# Install I2C required tools
sudo apt-get install i2c-tools

# Verify I2C status in firmware configuration
cat /boot/firmware/config.txt | grep -i i2c

# If required, set value to on
sudo vim /boot/firmware/config.txt

# If required, restart to apply changes
sudo init 6
```
#### Verify I2C Address

```bash
# Verify that I2C address 62 is populated
 i2cdetect -y 1 | grep 62
```

### Clone Repository

```bash
# Define folder to hold pisensor scripts
DEST_FOLDER="/opt/pisensor"

# Clone data from repo into dest folder
git clone https://github.com/root-able/pisensor.git ${DEST_FOLDER}

# Move into repo content
cd ${DEST_FOLDER}
```

### Fill In Configuration
```bash
# Create a configuration file from template
cp -v settings.template.yaml settings.yaml

# Fill in configuration file with private info (API token, host name, ...)
vi settings.yaml
```

### Install Dependencies
```bash
# Create Python virtualenv
python -m venv .venv

# Install requirements from repo file
.venv/bin/pip install -r requirements.txt
```

### Test the script
```bash
# Define the user that will run the script
USER_NAME="<USER_NAME>"

# Fix directory ownership
chown -R ${USER_NAME}:${USER_NAME} ${DEST_FOLDER}

# Make sure that the script is running fine
sudo -u ${USER_NAME} .venv/bin/python pisensor_scd41.py
```

### Configure Scheduling

```bash
# Create a cron job file
echo "* * * * * ${USER_NAME} ${DEST_FOLDER}/.venv/bin/python ${DEST_FOLDER}/pisensor_scd41.py >> ${DEST_FOLDER}/pisensor_scd41.log 2&>1" > /etc/cron.d/pisensor_scd41

# Monitor output log file for new execution runs
touch "${DEST_FOLDER}/pisensor_scd41.log" && tail -f "${DEST_FOLDER}/pisensor_scd41.log"
```