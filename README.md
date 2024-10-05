# Solvis Heating Integration for Home Assistant

[![Version](https://img.shields.io/github/v/release/LarsK1/hass_solvis_control?label=version)](https://github.com/LarsK1/hass_solvis_control/releases/latest)
[![Validate for HACS](https://github.com/LarsK1/hass_solvis_control/workflows/Validate%20for%20HACS/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/hacs.yml)
[![Validate% with hassfest](https://github.com/LarsK1/hass_solvis_control/workflows/Validate%20with%20hassfest/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/hassfest.yml)
[![Safe Code](https://github.com/LarsK1/hass_solvis_control/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/LarsK1/hass_solvis_control/actions/workflows/codeql.yml)

Custom Home Assistant integration for [Solvis Heating Devices](https://www.solvis.de/) 

## Install
### HACS
The easiest way to install this component is by clicking the badge below, which adds this repo as a custom repo in your HASS instance.

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?category=Integration&owner=LarsK1&repository=hass_solvis_control)

You can also add the integration manually by copying `custom_components/solvis_control` into `<HASS config directory>/custom_components`

# Preparation:
For using this integration you are required to enable the Modbus Protocol on your Solvis Device. Please follow this guide: https://solvis-files.s3.eu-central-1.amazonaws.com/downloads-fk/regelung/sc-3/SC-3_ModBus_Schnittstellenbeschreibung.pdf

## Contribution

Any PR is welcome. Please allow us a few days to check your contribution. If you do need any hints on where you could help, please open a discussion we'll always try to help.
### Translation
We tranlsate this project using transifex. Please help us to do so [here](https://explore.transifex.com/homeassistant-solvis/homeassistant-solvis-plugin/).

