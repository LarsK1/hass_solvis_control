"""Platform for sensor integration."""

from __future__ import annotations

from datetime import timedelta
import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN
from .coordinator import SolvisModbusCoordinator

_LOGGER = logging.getLogger(__name__)

PARALLEL_UPDATES = 1
SCAN_INTERVAL = timedelta(seconds=60)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the sensors."""

    coordinator = hass.data[DOMAIN][entry.entry_id]
    my_api = hass.data[DOMAIN][entry.entry_id]
    coordinator = SolvisModbusCoordinator(hass, my_api)
    entities: list[SensorEntity] = [
        Warmwasserpuffer(coordinator),
        Warmwassertemperatur(coordinator),
    ]

    await coordinator.async_config_entry_first_refresh()
    async_add_entities(entities)


class Warmwasserpuffer(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Warmwasserpuffer"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class Warmwassertemperatur(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Warmwassertemperatur"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class Speicherreferenztemperatur(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Speicherreferenztemperatur"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class Heizungspuffertemperatur_oben(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Heizungspuffertemperatur oben"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class Aussentemperatur(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Außentemperatur"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class Heizungspuffertemperatur_unten(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Heizungspuffertemperatur unten"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class Zirkulationsdurchfluss(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Zirkulationsdurchfluss"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class Vorlauftemperatur(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Vorlauftemperatur"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class Kaltwassertemperatur(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Kaltwassertemperatur"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class Durchfluss_Warmwasserzirkualation(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Durchfluss Warmwasserzirkualation"
    _attr_native_unit_of_measurement = "L/h"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class Laufzeit_Brenner(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Laufzeit Brenner"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class Brennerstarts(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Brennerstarts"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class Ionisationsstrom(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Ionisationsstrom"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class A01_Pumpe_Zirkulation(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "A01.Pumpe Zirkulation"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class A02_Pumpe_Warmwasser(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "A02.Pumpe Warmwasser"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class A03_Pumpe_HK1(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "A03.Pumpe HK1"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class A05_Pumpe_Zirkulation(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "A05.Pumpe Zirkulation"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class A12_Brennerstatus(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "A12.Brennerstatus"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class WW_Nachheizung_2322(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "WW Nachheizung 2322"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class HKR1_Betriebsart(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "HKR1 Betriebsart"


# Niedrigeres Abfrageintervall


class HKR1_Absenktemperatur_Nacht(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "HKR1 Absenktemperatur Nacht"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class HKR1_Solltemperatur_Tag(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "HKR1 Solltemperatur Tag"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class DigIn_Stoerungen(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "DigIn Störungen"


class WW_Solltemperatur(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "WW Solltemperatur"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT


class VersionSC2(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "VersionSC2"


class VersionNBG(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "VersionNBG"


class ZirkulationBetriebsart(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "ZirkulationBetriebsart"


class Raumtemperatur_HKR1(SensorEntity):
    """Representation of a Sensor."""

    _attr_name = "Raumtemperatur HKR1"
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
