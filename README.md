# Solvis Heating Integration for Home Assistant

[![Version](https://img.shields.io/github/v/release/LarsK1/hass_solvis_control?label=version)](https://github.com/LarsK1/hass_solvis_control/releases/latest)
[![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz/)
[![Validate for HACS](https://github.com/LarsK1/hass_solvis_control/workflows/Validate%20for%20HACS/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/hacs.yml)
[![Validate with hassfest](https://github.com/LarsK1/hass_solvis_control/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/hassfest.yml)
[![Safe Code](https://github.com/LarsK1/hass_solvis_control/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/codeql.yml)
[![Issues](https://img.shields.io/github/issues/LarsK1/hass_solvis_control.svg)](https://github.com/LarsK1/hass_solvis_control/issues)
[![codecov](https://codecov.io/gh/LarsK1/hass_solvis_control/branch/main/graph/badge.svg?token=H7UWU8UGVI)](https://codecov.io/gh/LarsK1/hass_solvis_control)


Custom Home Assistant integration for [Solvis Heating Devices](https://www.solvis.de/).

Solvis GmbH is a German manufacturer of innovative and energy-efficient heating systems. The company develops hybrid heating solutions, solar panels, and heat pumps that can be flexibly combined. The Solvis Modbus interface allows seamless integration with Home Assistant for monitoring and control.

## Supported and Unsupported Devices

This integration provides full support for [SolvisControl 3 (SC3)](https://www.solvis.de/solviscontrol/) devices with an enabled Modbus interface, offering seamless integration with Home Assistant.  

[SolvisControl 2 (SC2)](https://www.solvis.de/solvisremote-ben-max/) devices are supported with limitations. SC2 requires a [SolvisRemote](https://www.solvis.de/solvisremote-ben-max/) module for Modbus communication, and functionality is available only from firmware version MA205.  

Older Solvis control units (e.g., SC1) and devices without Modbus support are not compatible.  
Some features may depend on the installed firmware version. Keeping the device firmware up to date is recommended for best compatibility.

# Installation
## Using HACS (recommended)
The easiest way to install this component is using the [Home Assistant Community Store](http://hacs.xyz) by **clicking the badge below**, which adds this repository as a custom repository to your Home Assistant instance:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?category=Integration&owner=LarsK1&repository=hass_solvis_control)

   2. Click the **Download** button in the lower right corner.
   3. Select the recommended **version**.
   4. **Restart** Home Assistant.


> **Note on available versions:** Please stay with the recommended version unless you know what you are doing!

## Manual Installation

<details>
   <summary>Details</summary>
   
   <br>
   
   1. Copy the [repository](https://github.com/LarsK1/hass_solvis_control) contents of `custom_components/solvis_control` into `<HASS config directory>/custom_components`.
   2. **Restart** Home Assistant.
      
</details>

# Prerequisites
## Configuring the Solvis SC Device
To use this integration, the Solvis device must have Modbus enabled. 

<details>
   <summary>Follow these steps</summary>
   
   <br>
   
- Navigate to **Sonstiges** → **Nutzerwechsel** → **Installateur** and enter the default code **0064**.

<div align="center">
<img src="https://github.com/user-attachments/assets/02d4213d-c038-49f9-877e-2e1a5323dc33" width="400"> <br>
<img src="https://github.com/user-attachments/assets/5bff79fe-45c7-43f3-8636-cceed53ee901" width="400"> <br>
<img src="https://github.com/user-attachments/assets/97122d49-10c9-4ae5-808c-b98b2854a12f" width="400">
</div>

- Navigate to **Sonstiges** → **Modbus** → **SmartHome/GLT** and change **Modus** from **Aus** to **write**.

<div align="center">
<img src="https://github.com/user-attachments/assets/199ab24f-3875-47fa-9a8e-cb6b396784f3" width="400"> <br>
<img src="https://github.com/user-attachments/assets/6f5059c3-dd65-4b91-a7ae-51ccfe627828" width="400"> <br>
<img src="https://github.com/user-attachments/assets/ef0e0b1a-02e1-4504-94e7-15cffef53443" width="400"> <br>
<img src="https://github.com/user-attachments/assets/61087560-cb17-4f19-81c4-774b0ac66cba" width="400">
</div>

> **Notes:**
> - Screenshots are from Solvis SC3 (Ver. MA3.19.47) and may differ slightly for SC2 or other versions of SC3.
> - Selecting "read" mode only allows data monitoring, but not active control.
> - SC2 devices require a Solvis Remote device for Modbus communication.
> - It is strongly recommended to use the latest firmware version. For the SC3, the current version as of February 2025 is MA3.19.47.

</details>

# Device Configuration
Once the integration is installed and Modbus access is enabled, add the device in Home Assistant:

1. Go to **Settings → Devices & Services → Integrations**.
2. Click **Add Integration** and search for **Solvis Control**. Click on it.
3. Configure the integration:
   - Assign a **device name** (optional).
   - Enter the **IP address** of the Solvis Remote Device (found in your router's DHCP list).
   - Keep the **port** unchanged.
4. Select your **Solvis Control version** and set the **standard and slow polling intervals**.
5. Use the checkboxes to select which additional components (heating circuits, solar collectors, heat pump) are connected to the heating system. 

After setup, the integration polls an initial set of parameters and completes the installation with a **success message**.

> **Note:**
> - The standard polling interval defaults to 30 seconds, with a minimum of 5 seconds. The slow polling interval defaults to 300 seconds, must be greater than 10 seconds, and must be a multiple of the standard polling interval. Data is polled based on these intervals, depending on its rate of change: for example, temperature values use the standard interval, while the version number, which changes less frequently, is polled using the slow interval.
> For an overview of which values are retrieved at which interval, please refer to [the polling groups list](https://github.com/LarsK1/hass_solvis_control/blob/main/polling-groups.md)

# Features
This integration enables data polling and control of up to three heating circuits, solar panels, and heat pumps connected to [Solvis Heating Devices](https://www.solvis.de/) via the Solvis Modbus interface.

For a detailed list of supported entities, check [the supported entities list](https://github.com/LarsK1/hass_solvis_control/blob/main/supported-entities.md).

> **Notes:**
> - For more information on the Solvis Modbus interface, refer to:
>    - [SolvisRemote Modbus Spezifikationen Version 1.0 (01/2019) for SC2](https://solvis-files.s3.eu-central-1.amazonaws.com/seiten/produkte/solvisremote/Download/SolvisRemote+Modbus+Spezifikationen+201906.pdf)
>    - [SolvisControl 3 Modbus Spezifikationen Version 1.0 (09/2021) for SC3](https://solvis-files.s3.eu-central-1.amazonaws.com/downloads-fk/regelung/sc-3/SC-3_ModBus_Schnittstellenbeschreibung.pdf) 
> - Official Modbus specifications are partially outdated and contain incorrect information.
> - A revised SC3 Modbus specification is expected in 2025 (unofficial information from Solvis, December 2024).
> - Sometimes useful for debugging: [Anlagenschema SolvisMax - ALS-MAX7 Ver. 27350-2n](https://solvis-files.s3.eu-central-1.amazonaws.com/downloads-fk/solvismax7/27350_ALS-MAX-7.pdf)

# Troubleshooting

If you experience issues with the integration, check the following common problems and solutions.

<details>
   <summary><b>Verify connection from Home Assistant to SC3 devices</b></summary>
   <br>

   To check if the Modbus connection is active on an SC3 device:  
   1. Switch to **Installateur** mode.  
   2. Navigate to **Sonstiges** → **Status Modbus**.  
   3. The connection should appear under **TCP server**.

   <div align="center">
      <img src="https://github.com/user-attachments/assets/ef0e0b1a-02e1-4504-94e7-15cffef53443" width="400">  
      <img src="https://github.com/user-attachments/assets/c4ba1115-0b57-4bae-8ec8-5f87a4d68353" width="400">
   </div>

> **Note:** The integration only establishes a Modbus connection briefly to poll data. Therefore, the Home Assistant IP is not permanently visible in the connection overview but appears only for short periods.

</details>

<details>
   <summary><b>Modbus connection fails</b></summary>
   <br>

   **Symptoms:**  
   &nbsp;&nbsp;&nbsp;&nbsp;No communication between Home Assistant and the Solvis device.  

   **Solutions:**  
   - Ensure that Modbus is enabled in the Solvis device (`Sonstiges → Modbus → SmartHome/GLT`).  
   - Verify that the correct IP address and port number are set in the integration.  
   - Test the network connection (e.g., using `ping`).  
   - Check firewall or router settings for potential blocks.

</details>

<details>
   <summary><b>Incomplete or incorrect sensor data</b></summary>
   <br>

   **Symptoms:**  
   &nbsp;&nbsp;&nbsp;&nbsp;Some sensor values are missing or show unrealistic readings.  

   **Solutions:**  
   - Ensure that the Solvis device runs the latest firmware version.  
   - Restart Home Assistant.

</details>

<details>
   <summary><b>Integration not recognized in Home Assistant</b></summary>
   <br>

   **Symptoms:**  
   &nbsp;&nbsp;&nbsp;&nbsp;The integration does not appear in the list of available integrations.  

   **Solutions:**  
   - Ensure that all integration files are correctly placed under `custom_components/solvis_control`.  
   - Clear Home Assistant’s cache and restart the system.  

</details>

<details>
   <summary><b>Issues with write operations (Modbus Write)</b></summary>
   <br>

   **Symptoms:**  
   &nbsp;&nbsp;&nbsp;&nbsp;Changes (e.g., target temperatures) are not applied.  

   **Solutions:**  
   - Ensure that Modbus is set to `write` mode instead of `read` (see prerequisites).  
   - Update the Solvis controller firmware.  

</details>

If the issue persists, please provide debug logs and open an issue on [GitHub](https://github.com/LarsK1/hass_solvis_control/issues).

## Reporting Issues

If the issue persists, enable debug logging in Home Assistant by adding the following to your `configuration.yaml`:  

```yaml
logger:
  logs:
    custom_components.solvis_control: debug
```

After restarting Home Assistant, check the logs under **Settings** → **System** → **Logs** for any error messages related to the integration.

When opening an issue on GitHub, please include:

- **A clear description of the issue:**  
  What is happening, and what did you expect?
- **Relevant error messages from the logs:**  
  Copy and paste any related log entries.
- **Details about your setup:**  
  - Home Assistant version  
  - Solvis device model  
  - Firmware version
- **Steps to reproduce the issue:**  
  If possible, describe how to trigger the problem.

Providing detailed information will help diagnose and resolve the issue more efficiently.

# Contribution
We welcome pull requests! Please allow time for review. If you need guidance on where to contribute, open a discussion — we're happy to help!

## Translation
We translate this project using Transifex. Contribute translations [here](https://explore.transifex.com/homeassistant-solvis/homeassistant-solvis-plugin/).
