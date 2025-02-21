# pisensor

## Pre-Requisites

### Hardware

### Software

## Initial Setup

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

# Fill in configuration file with private info
vi settings.yaml
```

### Install Dependencies
```bash
# Create Python virtualenv
python -m venv .venv

# Install requirements from repo file
.venv/bin/pip install -r requirements.txt
```

### Configure Scheduling

TBC