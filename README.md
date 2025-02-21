# Solvis Heating Integration for Home Assistant

[![Version](https://img.shields.io/github/v/release/LarsK1/hass_solvis_control?label=version)](https://github.com/LarsK1/hass_solvis_control/releases/latest)
[![Validate for HACS](https://github.com/LarsK1/hass_solvis_control/workflows/Validate%20for%20HACS/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/hacs.yml)
[![Validate% with hassfest](https://github.com/LarsK1/hass_solvis_control/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/hassfest.yml)
[![Safe Code](https://github.com/LarsK1/hass_solvis_control/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/codeql.yml)

Custom Home Assistant integration for [Solvis Heating Devices](https://www.solvis.de/) 

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
   
   1. Copy the contents of `custom_components/solvis_control` into `<HASS config directory>/custom_components`.
   2. Click the **Download** button in the lower right corner.
   3. Select the recommended **version**.
   4. **Restart** Home Assistant.
      
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
> - Screenshots are from Solvis SC3 (Ver. MA3.19.47) and may differ slightly for SC2 or other versions.
> - Selecting "read" mode only allows data monitoring, but not active control.
> - SC2 devices require a Solvis Remote device for Modbus communication.

</details>

# Device Configuration
Once the integration is installed and Modbus access is enabled, add the device in Home Assistant:

1. Go to **Settings → Devices & Services → Integrations**.
2. Click **Add Integration** and search for **Solvis Control**.
3. Configure the integration:
   - Assign a **device name** (optional).
   - Enter the **IP address** of the Solvis Remote Device (found in your router's DHCP list).
   - Keep the **port** unchanged.
4. Select your **Solvis Control version** and available features.

After setup, the integration will poll an initial set of parameters and complete the installation with a **success message**.

# Features
This integration allows data polling and control of up to three heating circuits, solar panels and heat pumps connected to [Solvis Heating Devices](https://www.solvis.de/). It utilizes the Solvis Modbus interface.

For a detailed list of supported entities, check [the supported entities list](https://github.com/LarsK1/hass_solvis_control/blob/main/supported-entites.md).

> **Notes:**
> - For more information on the Solvis Modbus interface, refer to:
>    - [SolvisRemote Modbus Spezifikationen Version 1.0 (01/2019) for SC2](https://solvis-files.s3.eu-central-1.amazonaws.com/seiten/produkte/solvisremote/Download/SolvisRemote+Modbus+Spezifikationen+201906.pdf)
>    - [SolvisControl 3 Modbus Spezifikationen Version 1.0 (09/2021) for SC3](https://solvis-files.s3.eu-central-1.amazonaws.com/downloads-fk/regelung/sc-3/SC-3_ModBus_Schnittstellenbeschreibung.pdf) 
> - Official Modbus specifications are partially outdated and contain errors.
> - A revised SC3 Modbus specification is expected in 2025 (unofficial information from Solvis, Dec 2024).
> - Sometimes useful for debugging: [Anlagenschema SolvisMax - ALS-MAX7 Ver. 27350-2n](https://solvis-files.s3.eu-central-1.amazonaws.com/downloads-fk/solvismax7/27350_ALS-MAX-7.pdf)

# Troubleshooting
On SC3 devices, the connection to Home Assistant can by verified.

<details>
   <summary>Follow these steps</summary>
   
   <br>
   
  - Switch to **Installateur** mode.
  - Navigate to **Sonstiges** → **Status Modbus**.
  - The connection should appear under **TCP server**.

<div align="center">
<img src="https://github.com/user-attachments/assets/ef0e0b1a-02e1-4504-94e7-15cffef53443" width="400"> <br>
<img src="https://github.com/user-attachments/assets/c4ba1115-0b57-4bae-8ec8-5f87a4d68353" width="400">
</div>

</details>

# Removing the integration

The integration and its entities can be removed by following these steps:

1. Go to **Settings** → **Devices & services** and select the integration card.
2. From the list of devices, select the integration instance you want to remove.
3. Next to the entry click on the three-dot (⋮) menu. Then, select **Delete**.

This does not remove the integrations files yet.

## Remove the integrations files if installed via HACS 

1. Open the HACS Addon.
2. Locate the "Solvis Control" entry in the group of downloaded repositories.
3. Next to the entry click on the three-dot (⋮) menu. Then, select **Delete**.
4. **Restart** Home Assistant.

## Remove the integrations files manually

<details>
   <summary>Follow these steps</summary>
   
   <br>
   
   1. Delete the directory `<HASS config directory>/custom_components/solvis_control` and its components.
   2. **Restart** Home Assistant.

</details>

# Contribution
We welcome pull requests! Please allow time for review. If you need guidance on where to contribute, open a discussion — we're happy to help!

## Translation
We translate this project using Transifex. Contribute translations [here](https://explore.transifex.com/homeassistant-solvis/homeassistant-solvis-plugin/).
