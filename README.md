<center><img src="https://github.com/user-attachments/assets/4dffdeb2-2a74-4418-a6af-2057e2df82b5" width="500" ></center>

# Solvis Control Integration for Home Assistant

[![Version](https://img.shields.io/github/v/release/LarsK1/hass_solvis_control?label=version)](https://github.com/LarsK1/hass_solvis_control/releases/latest)
[![HACS](https://img.shields.io/badge/HACS-Default-orange.svg)](https://hacs.xyz/)
[![Validate for HACS](https://github.com/LarsK1/hass_solvis_control/workflows/Validate%20for%20HACS/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/hacs.yml)
[![Validate with hassfest](https://github.com/LarsK1/hass_solvis_control/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/hassfest.yml)
[![Safe Code](https://github.com/LarsK1/hass_solvis_control/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/codeql.yml)
[![Issues](https://img.shields.io/github/issues/LarsK1/hass_solvis_control.svg)](https://github.com/LarsK1/hass_solvis_control/issues)
[![codecov](https://codecov.io/gh/LarsK1/hass_solvis_control/branch/main/graph/badge.svg?token=H7UWU8UGVI)](https://codecov.io/gh/LarsK1/hass_solvis_control)


Custom Home Assistant integration for [Solvis Heating Devices](https://www.solvis.de/).

Solvis GmbH is a German manufacturer of innovative and energy-efficient heating systems. The company develops hybrid heating solutions, solar panels, and heat pumps that can be flexibly combined. The Solvis Modbus interface allows seamless integration with Home Assistant for monitoring and control.

## Supported Devices

This integration provides full support for [SolvisControl 3 (SC3)](https://www.solvis.de/solviscontrol/) devices with an enabled Modbus interface, offering seamless integration with Home Assistant.  

[SolvisControl 2 (SC2)](https://www.solvis.de/solvisremote-ben-max/) devices are supported with limitations. SC2 requires a [SolvisRemote](https://www.solvis.de/solvisremote-ben-max/) module for Modbus communication, and functionality is available only from firmware version MA205.  

Older Solvis control units (e.g., SC1) and devices without Modbus support are not compatible.

## Supported Firmware SC3

Some features may depend on the firmware version installed on SC3. Keeping the device firmware up to date is recommended for best compatibility.

The following firmware versions are confirmed to be **fully supported**: 3.19.47, 3.20.05 and 3.20.16.<br>
The following versions are likely to work but are **not fully verified**: 3.15.09, 3.17.12.<br>
Other versions (3.5.1 and earlier) may also be compatible, but have **not been tested**.

**Warning:** Version 3.20.16 is not compatible with SolvisTom 9 kW. For systems with SolvisTom 9 kW and SolvisPia, continue using 3.20.05. See [Bedienungsanleitung SolvisMax für Installateure, BAL-SBSX-3-I, 32432-2h](https://solvis-files.s3.eu-central-1.amazonaws.com/downloads-fk/solvismax7/32432_BAL-SBSX-3-I.pdf)

The version of the network board should not be critical for the functionality of the integration. No issues have been observed so far with any of the currently used versions 3.0.1, 3.1.0, or 3.2.1.

## Supported Firmware SC2

Some features may depend on the firmware version installed on SC2. As there are some known deviations from documentation and actual firmware implementation, staying on the latest version is recommended, as the integartion is set to deal with these deviations.

The following firmware versions are confirmed to be **fully supported**: 205.08 (latest)<br>
Other versions may also be compatible, but have **not been tested**.

If you have information about the compatibility of an unlisted version, or encounter issues with a listed version, feedback is welcome.

## Known Limitations

Due to the wide range of configuration options, system versions, and occasionally unclear documentation, some entity names—especially for less common setups—may be incorrect or misleading.
Less common configurations include, for example, SolvisMax district heating, separate solid fuel boilers, external boilers, swimming pool heating circuits, or solar thermal systems with east/west-oriented roof surfaces.

If you encounter such cases, we appreciate feedback including a description of the issue and details about your system configuration, so we can take it into account in future versions.

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
## Configuring the Solvis SC3 Device
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
> - Screenshots are from Solvis SC3 (Ver. MA3.19.47).
> - Selecting "read" mode only allows data monitoring, but not active control.
> - It is strongly recommended to use the latest firmware version. For the SC3, the current version as of April 2025 is MA3.20.16.

</details>

## Configuring the Solvis SC2 Device
SC2 devices require a Solvis Remote device for Modbus communication.
To use this integration, the Solvis device must have Modbus enabled along the following steps:

<details>
   <summary>Follow these steps</summary>
   
   <br>
   
- Navigate to **Sonstig.** → **Nutzerwechsel** → **Installateur** and enter the default code **0064**.

<div align="center">
<img src="https://github.com/user-attachments/assets/887a0425-aacd-4810-9079-ea6b0589b1be" width="400"> <br>
</div>

(Sonstiges)<br>

<div align="center">
<img src="https://github.com/user-attachments/assets/b332ce3c-cb95-49bd-a10d-3304a2ba4dd4" width="400"> <br>
</div>

(Remote) <br>
<div align="center">
<img src="https://github.com/user-attachments/assets/de81be36-1b5d-43c8-a18d-c26db6e72f23" width="400"> <br>
</div>
(Datenprotokoll "Remote")<br>
(next screen)<br>
<div align="center">
<img src="https://github.com/user-attachments/assets/7c6c4563-c85d-4d52-b979-9eede3bdf0cd" width="400"> <br>
</div>
("schreiben") -> to enable remote control via integration <br><br>

> **Notes:**
> - Screenshots are from Solvis SC2 (Ver. MA205.08 N300), and Solvis Remote V2.20.06
> - Selecting "read" mode only allows data monitoring, but not active control.

</details>

# Device Configuration
Once the integration is installed and Modbus access is enabled, add the device in Home Assistant:

1. Go to **Settings → Devices & Services → Integrations**.
2. Click **Add Integration** and search for **Solvis Control**. Click on it.
3. Configure the integration:
   - Assign a **device name** (optional).
   - Enter the **IP address** of the Solvis Remote Device (found in your router's DHCP list).
   - Keep the **port** unchanged.
4. Select your **Solvis Control version** and set the **low, standard and high polling intervals**.
5. Use the checkboxes to select which **assemblies and system components** (second and/or third heating circuit, heat pump, solar collector, heat meter, PV2Heat) are connected to the heating system.
6. Next, for each available heating circuit (as defined in the previous step), you can configure the presence and behavior of the **room temperature sensor**. Select 'disabled' if no sensor is installed, 'read' to only read the value (default), or 'write' if the value should be writable.
7. In the final step of the configuration choose your model of the **stratified storage**.

After setup, the integration polls an initial set of parameters and completes the installation with a **success message**.

> **Notes:**
> - The integration attempts to determine the number of existing heating circuits via Modbus query. If the automatically determined number is incorrect or a different configuration is desired, the second and third heating circuits can be manually enabled or disabled. The corresponding entities will then be (not) added accordingly.
> - The integration uses three polling intervals: high, standard, and low.
>    - The **high polling interval** defaults to 10 seconds, with a minimum of 2 seconds. It is used for frequently changing values (e.g., flow temperatures).
>    - The **standard polling interval** defaults to 30 seconds, with a minimum of 2 seconds. It must be a multiple of the high interval and is used for regularly changing values (e.g., room temperature).
>    - The **low polling interval** defaults to 300 seconds, must be greater than 10 seconds, and must be a multiple of the standard interval. It is used for rarely changing values (e.g., firmware version).
> - For an overview of which values are retrieved at which interval, please refer to [the polling groups list](https://github.com/LarsK1/hass_solvis_control/blob/main/polling-groups.md)
> - The SC2 Processor and Modbus implementation seems to be rather slow in processing requests. As a result, the web interface responds rather sluggish with the integration running. If that poses a problem, increasing the polling intervals might reduce the issue.
> - The selected stratified storage model and configuration determine the amount of energy stored and reported by the integration. Two types of stratified storage tanks are available: SolvisBen (single size) and SolvisMax (available in 457, 757, and 957 sizes). Both models can be deployed in solo mode (without a heat generator), with a heat pump, or in hybrid mode (gas/oil burner and heat pump). The SolvisMax 957 offers three sensor-position configurations — 82/34/796, 212/34/663, and 301/34/574 — where the first number indicates the domestic hot water volume (OK-S4), the second the heating buffer volume (S4-S9), and the third the solar buffer volume (S4-UK).


# Features
This integration enables data polling and control of up to three heating circuits, solar panels, and heat pumps connected to [Solvis Heating Devices](https://www.solvis.de/) via the Solvis Modbus interface.

For a detailed list of supported entities, check [the supported entities list](https://github.com/LarsK1/hass_solvis_control/blob/main/supported-entities.md).

> **Notes:**
> - For more information on the Solvis Modbus interface, refer to:
>    - [SolvisRemote Modbus Spezifikationen Version 1.0 (01/2019) for SC2](https://solvis-files.s3.eu-central-1.amazonaws.com/seiten/produkte/solvisremote/Download/SolvisRemote+Modbus+Spezifikationen+201906.pdf)
>    - [SolvisControl 3 Modbus Spezifikationen Version 1.0 (09/2021) for SC3](https://solvis-files.s3.eu-central-1.amazonaws.com/downloads-fk/regelung/sc-3/SC-3_ModBus_Schnittstellenbeschreibung.pdf) 
> - Official Modbus specifications are partially outdated and contain incorrect information (example for SC2 - flow meters do not provide the flow in l/sec as described, but the impulse duration of the flow meter)
> - A revised SC3 Modbus specification is expected in 2025 (unofficial information from Solvis, December 2024).
> - Sometimes useful for debugging: [Anlagenschema SolvisMax - ALS-MAX7 Ver. 27350-2n](https://solvis-files.s3.eu-central-1.amazonaws.com/downloads-fk/solvismax7/27350_ALS-MAX-7.pdf)

## Provided platforms
The following platforms are currently used. Please see [the supported entities list](https://github.com/LarsK1/hass_solvis_control/blob/main/supported-entities.md) regarding, which entity is based on which platform:
- sensor
- number
- select
- switch
- binary_sensor

# Library of automations and applications
The following library is provided as is, and only based on community work. 
<details>
   <summary>Automation to automatically heat up the hot water at 6 am</summary>

```yaml
alias: Warmwasser früh
description: ""
triggers:
  - trigger: time
    at: "06:00:00"
conditions: []
actions:
  - type: turn_on
    device_id: 1f8c80d3e52454f35413e92ef9262d07
    entity_id: 0413a5bfcb98bfce58d8c93bd7362fa0
    domain: switch
mode: single
```
</details>

<details>
   <summary>Dashboard with heating scheme</summary>
   
<br>

**Thanks @gnomwechsel for sharing!**

Example:

<img width="400" alt="Solvis Heating Example" src="https://github.com/user-attachments/assets/1a9182d8-7d3f-46af-93df-26eb3ffc0dcf" />


Image for the picture-elements card (HQ 4000 x 2661 png):

<img width="400" alt="Solvis Heating" src="https://github.com/user-attachments/assets/ebed6a83-c790-4d22-ab85-306b1716ac96" />


YAML-Code:
```
cards:
  - type: picture-elements
    elements:
      - type: state-label
        entity: sensor.solvis_heizung_leistung_warmepumpe
        prefix: "out "
        style:
          left: 84%
          top: 85.5%
          font-size: 60%
          color: white
          margin: left
      - type: state-label
        entity: sensor.solvis_heizung_warmwasserpuffer
        style:
          left: 34%
          top: 44.7%
          font-size: 60%
          color: white
      - type: state-label
        entity: sensor.solvis_heizung_heizungspuffertemperatur_oben
        style:
          left: 34%
          top: 68%
          font-size: 60%
          color: white
      - type: state-label
        entity: sensor.solvis_heizung_heizungspuffertemperatur_unten
        style:
          left: 35%
          top: 78%
          font-size: 60%
          color: white
      - type: state-label
        style:
          left: 35%
          top: 95%
          font-size: 60%
          color: white
        entity: sensor.solvis_heizung_speicherreferenztemperatur
      - type: state-label
        entity: sensor.solvis_heizung_warmwassertemperatur
        style:
          left: 19.5%
          top: 76%
          font-size: 60%
          color: white
      - type: state-label
        style:
          left: 14.5%
          top: 91%
          font-size: 60%
          color: white
        entity: sensor.solvis_heizung_kaltwassertemperatur
      - type: state-label
        style:
          left: 20.5%
          top: 85%
          font-size: 60%
          color: white
        entity: sensor.solvis_heizung_durchfluss_warmwasser_3
      - type: state-label
        style:
          left: 18%
          top: 48.5%
          font-size: 60%
          color: white
        entity: sensor.solvis_heizung_hkr1_vorlauftemperatur
      - type: state-label
        entity: sensor.solvis_heizung_s8_temperatur_solarkollektor
        style:
          left: 77%
          top: 29%
          font-size: 60%
          color: white
      - type: state-label
        style:
          left: 76.2%
          top: 52.8%
          font-size: 60%
          color: white
        entity: sensor.solvis_heizung_solarkreislauftemperatur_2
      - type: state-label
        style:
          left: 66%
          top: 52%
          font-size: 60%
          color: white
        entity: sensor.solvis_heizung_solarwarmetauschertemperatur_out
      - type: state-label
        style:
          left: 66%
          top: 65%
          font-size: 60%
          color: white
        entity: sensor.solvis_heizung_solarwarmetauschertemperatur_in
      - type: state-label
        style:
          left: 58%
          top: 59%
          font-size: 60%
          color: white
        entity: sensor.solvis_heizung_durchflussmenge_solar
      - type: state-label
        style:
          left: 88%
          top: 9%
          font-size: 60%
          color: white
        entity: sensor.solvis_heizung_aussentemperatur
      - type: state-label
        entity: sensor.energy_tibber_pulse_jj_home_energie
        style:
          left: 58%
          top: 21%
          font-size: 60%
          color: white
      - type: state-label
        style:
          left: 90%
          top: 36%
          font-size: 60%
          color: white
        entity: sensor.solvis_heizung_leistung_solarthermie
      - type: state-label
        title: Gasbrenner Leistung
        entity: sensor.p_gasbrenner
        style:
          left: 46%
          top: 90%
          font-size: 60%
          color: white
        prefix: "Gas "
      - type: state-label
        title: PV2Heat Leistung
        entity: sensor.pv2heat_0
        style:
          left: 45.5%
          top: 39.5%
          font-size: 60%
          color: white
        prefix: "PV2Heat "
      - type: state-label
        title: WP Ladepumpe Leistung
        entity: sensor.solvis_heizung_wp_ladepumpe
        style:
          left: 70%
          top: 78%
          font-size: 60%
          color: white
      - type: state-label
        entity: sensor.solvis_heizung_elektrische_warmepumpenleistung
        prefix: "in "
        style:
          left: 83%
          top: 89%
          font-size: 60%
          color: white
    image: /api/image/serve/26a9d95b5ce92e19cf5bd2a289fc9a0b/512x512
    card_mod:
      style: |
        :host {
          display: block;
          width: 100%;
          height: calc(100vh - 115px);
          overflow: hidden;
        }
        ha-card {
          background: none !important;
          box-shadow: none !important;
          display: flex;
          justify-content: center;
          align-items: center;
        }
        img {
          width: auto !important;
          height: 100% !important;
        }
```

</details>


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

<details>
   <summary><b>Error: convert_from_registers() got an unexpected keyword argument 'word_order'</b></summary>
   <br>

   **Symptoms:**   
   
   The integration fails to initialize or throws errors during setup. Log message includes:
   <code>TypeError: ModbusClientMixin.convert_from_registers() got an unexpected keyword argument 'word_order'</code>

   **Cause:**
   
   An incompatible version of the pymodbus library is active.
   This often happens when another integration (e.g., SolarEdge Modbus, Huawei, Goe, ha-pysmaplus) installs its own older version of pymodbus, overriding the version required by this integration. See [this issue](https://github.com/LarsK1/hass_solvis_control/issues/101) for some more detailed info.
   
   **Solutions:** 
   - Ensure all Modbus-based integrations are updated to versions compatible with pymodbus >= 3.8.0.
   - If using the SolarEdge Modbus integration, update to V2.0.3, which includes a compatible pymodbus.
   - Reboot the entire Home Assistant system, not just Home Assistant Core, to ensure the correct library version is used.
   - Manually update pymodbus (only if you know what You're doing!): see [this post](https://github.com/LarsK1/hass_solvis_control/issues/101#issuecomment-2869655794) for instructions.

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
