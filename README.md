# pisensor

The objective of this project is to enable reporting for sensors of the Sensirion Brand to a Home Assistant instance, in the simplest and most straightforward way.

## Pre-Requisites

### Hardware

The code provided by this project is meant to be used in the following hardware configuration:

- Raspberry Pi or other ARM-based, GPIO-enabled compatible device.
- A sensor built by Sensirion company.
- Connection wires to bridge all devices together.

#### SCD41

The specific connection steps below apply to sensors of the SCD41 family.

The connection pattern between the sensor and GPIO-enabled device must match the one described in [Sensirion's documentation](https://github.com/Sensirion/python-i2c-scd4x?tab=readme-ov-file#connect-the-sensor).
Here is a short summary of the connection pattern between each of the 4 connectors of the sensor, to the Raspberry Pi's GPIO:

- <u>VCC:</u> *Pin 1*
- <u>SDA:</u> *Pin 3*
- <u>SCL:</u> *Pin 5*
- <u>GND:</u> *Pin 6*

#### SEN55

The specific connection steps below apply to sensors of the SEN55 family.

The connection pattern between the sensor and GPIO-enabled device must match the one described in [Sensirion's documentation](https://github.com/Sensirion/embedded-i2c-sen5x?tab=readme-ov-file#connecting-the-sensor).
Here is a short summary of the connection pattern between each of the 5 (out of 6) sensor connectors that should be connected to the Raspberry Pi's GPIO:

- <u>VCC:</u> *Pin 1*
- <u>GND:</u> *Pin 2*
- <u>SDA:</u> *Pin 3*
- <u>SCL:</u> *Pin 4*
- <u>GND:</u> *Pin 5* (This selects I2C interface mode)
- <u>Not Connected:</u> *Pin 6*


#### Additional Considerations

With this connection patterns in place, all sensor should then be physically available through the I2C bus to the GPIO-enabled device.
In most cases, SDA and SCL pins may be mutualized between multiple devices. However, with a high device count, additional pull-up resistors may sometime be required.


### Software

This project relies on the respective python drivers provided by Sensirion for all their sensors families.
These are dependencies, and associated code may be found in following repositories:

- [SCD41 Python Driver](https://github.com/Sensirion/python-i2c-scd4x)
- [SEN55 Python Driver](https://github.com/Sensirion/python-i2c-sen5x)

## Initial Setup

### I2C Bus Setup

In order to make sure that the sensor is available at the software level, the following verification must be performed:

- The I2C interface is enabled on the Raspberry Pi.
- The I2C address of the device is set to the following default configurations:
  - <u>SCD41 Defaults:</u> [`0x62`](https://github.com/Sensirion/python-i2c-scd4x?tab=readme-ov-file#supported-sensor-types)
  - <u>SEN55 Defaults:</u> `0x69`
  
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
# Verify that I2C address are populated
i2cdetect -y 1
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

# Fill in configuration file with private info (API token, host name, device address, ...)
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
sudo -u ${USER_NAME} .venv/bin/python sensirion_pisensor.py
```

### Configure Scheduling

#### Systemctl Service

To ensure continuous execution of the `pisensor` poller, the recommended way is to install a dedicated systemctl service. This ensures continuous polling of all Sensirion sensors.

```bash
# Create a service file using template
cp -v pisensor.service /etc/systemd/system

# Replace placeholder home folder with actual deployment value
sed -i "s/<DEST_FOLDER>/${DEST_FOLDER}/g" /etc/systemd/system

# Reload services
systemctl daemon-reload 

# Start service
systemctl start pisensor 

# Check service status
systemctl start pisensor 

# Enable service to start at boot
systemctl enable pisensor 
```

#### Scheduled Task

Another possibility to schedule the execution of the `pisensor` poller is to use a linux scheduled task. However, since some measures use historical data derivation (NOC, VOC), this may prevent getting accurate values for these measures. This option is therefore less recommended than using a systemctl service creation.

```bash
# Create a cron job file
echo "* * * * * ${USER_NAME} ${DEST_FOLDER}/.venv/bin/python ${DEST_FOLDER}/pisensor.py >> ${DEST_FOLDER}/pisensor.log 2&>1" > /etc/cron.d/pisensor

# Monitor output log file for new execution runs
touch "${DEST_FOLDER}/pisensor.log" && tail -f "${DEST_FOLDER}/pisensor.log"
```