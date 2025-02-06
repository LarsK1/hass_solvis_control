# Solvis Heating Integration for Home Assistant

[![Version](https://img.shields.io/github/v/release/LarsK1/hass_solvis_control?label=version)](https://github.com/LarsK1/hass_solvis_control/releases/latest)
[![Validate for HACS](https://github.com/LarsK1/hass_solvis_control/workflows/Validate%20for%20HACS/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/hacs.yml)
[![Validate% with hassfest](https://github.com/LarsK1/hass_solvis_control/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/hassfest.yml)
[![Safe Code](https://github.com/LarsK1/hass_solvis_control/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/codeql.yml)

Custom Home Assistant integration for [Solvis Heating Devices](https://www.solvis.de/) 

# Install
## HACS
The easiest way to install this component is by clicking the badge below, which adds this repo as a custom repo in your HASS instance.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?category=Integration&owner=LarsK1&repository=hass_solvis_control)

You can also add the integration manually by copying `custom_components/solvis_control` into `<HASS config directory>/custom_components`

Then click on the "Download" button in lower right corner and select the Repo-Version. Pls stay with the suggested version unless you know what you are doing. After installation pls restart HASS. 

## Preparation of Solvis SC device (at the heating system!)
To be able to use this integration the Solvis device needs an enabled modbus socket. To do so go to your device:
- Go to the installateur menu (default code : `0064`)
- "Sonstiges"
![image](https://github.com/user-attachments/assets/88367744-915a-444b-8203-c0c3b3bf1ef6)

- "„SmartHome/GLT (TCP)"
![image](https://github.com/user-attachments/assets/b4a20d03-589c-43bd-9683-df33d5124052)

- Toggle from "Modbus Aus" to "Modbus write"
![image](https://github.com/user-attachments/assets/cd5d7cd3-98c8-422a-afdd-bd66520a1c94)

## Configuration
Now you can add the device in the integration list:

Switch to your integrations view (settings -> Devices and services -> integrations and click on "add integration". Search for Solvis Control.

In the configuration, the device name can be assigned at your choice; the IP adress is that of your Solvis Remote Device (find out via Router DHCP list). The Port should stay unchanged.

On the next page select the version of your Solvis Control and the features of your Solvis installation. 

The integration then starts to poll an initial set of parameters and finishes with a "success message".

# Features
This integration interacts with Solvis SC2 / SC 3 devices to poll actual data and allows control of specific functions the the SC2 / SC3. It can be configured for heating circuits, solar panels and heatpump options. It leverages the Solvis Modbus interface. 
SC2 devices require the Solvis Remote device to connect to the Solvis.

For information on the Solvis Modbus interface refer to [SolvisRemote Modbus Spezifikationen](https://solvis-files.s3.eu-central-1.amazonaws.com/seiten/produkte/solvisremote/Download/SolvisRemote+Modbus+Spezifikationen+201906.pdf)

For a detailed view of the supported entites have a look at [the list of supported entities](/supported-entites.md)


## Contribution

Any PR is welcome. Please allow us a few days to check your contribution. If you do need any hints on where you could help, please open a discussion we'll always try to help.
### Translation
We translate this project using transifex. Please help us to do so [here](https://explore.transifex.com/homeassistant-solvis/homeassistant-solvis-plugin/).


