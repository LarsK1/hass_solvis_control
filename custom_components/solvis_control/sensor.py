"""Solvis sensors."""

import logging
from decimal import Decimal
import re

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.const import (
    CONF_IP_ADDRESS,
    CONF_NAME,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
)

from .const import (
    DATA_COORDINATOR,
    DOMAIN,
    MANUFACTURER,
    REGISTERS,
    CONF_HOST,
    CONF_NAME,
)
from .coordinator import SolvisModbusCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Setup sensor entities."""

    conf_host = entry.data.get(CONF_HOST)
    if conf_host is None:
        _LOGGER.error("Device has no address")

    # Generate device info
    device_info = DeviceInfo(
        identifiers={(DOMAIN, entry.data.get(CONF_HOST))},
        name=entry.data.get(CONF_NAME),
        manufacturer=MANUFACTURER,
        model="Solvis Control 3",
    )

    # Add sensors
    sensors_to_add = []

    for register in REGISTERS:
        sensors_to_add.append(
            SolvisSensor(
                hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR],
                device_info,
                conf_host,
                register.name,
                register.unit,
                register.device_class,
                register.state_class,
            )
        )

    async_add_entities(sensors_to_add)


class SolvisSensor(CoordinatorEntity, SensorEntity):
    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        address,
        name: str,
        unit_of_measurement: str | None = None,
        device_class: str | None = None,
        state_class: str | None = None,
    ):
        """Init entity."""
        super().__init__(coordinator)

        self._address = address
        self._response_key = name
        self._attr_name = name

        self._attr_has_entity_name = True
        self._attr_unique_id = f"{re.sub('^[A-Za-z0-9_-]*$', '', name)}_{name}"
        self._attr_translation_key = name

        self._attr_device_info = device_info
        self._attr_available = False
        self._attr_native_unit_of_measurement = unit_of_measurement
        self._attr_device_class = device_class
        self._attr_state_class = state_class

    @callback
    def _handle_coordinator_update(self) -> None:
        """Handle updated data from the coordinator."""

        if self.coordinator.data is None:
            _LOGGER.warning("Data from coordinator is None. Skipping update")
            return

        if not isinstance(self.coordinator.data, dict):
            _LOGGER.warning("Invalid data from coordinator")
            self._attr_available = False
            return

        response_data = self.coordinator.data.get(self._response_key)
        if response_data is None:
            _LOGGER.warning("No data for available for (%s)", self._response_key)
            self._attr_available = False
            return

        if (
            not isinstance(response_data, int)
            and not isinstance(response_data, float)
            and not isinstance(response_data, complex)
            and not isinstance(response_data, Decimal)
        ):
            _LOGGER.warning(
                "Invalid response data type from coordinator. %s has type %s",
                response_data,
                type(response_data),
            )
            self._attr_available = False
            return

        self._attr_available = True
        self._attr_native_value = response_data
        self.async_write_ha_state()


# """Platform for sensor integration."""

# from __future__ import annotations

# from datetime import timedelta
# import logging

# from homeassistant.components.sensor import (
#     SensorDeviceClass,
#     SensorEntity,
#     SensorStateClass,
# )
# from homeassistant.config_entries import ConfigEntry
# from homeassistant.const import UnitOfTemperature
# from homeassistant.core import HomeAssistant
# from homeassistant.helpers.entity_platform import AddEntitiesCallback

# from .const import DOMAIN
# from .coordinator import SolvisModbusCoordinator

# _LOGGER = logging.getLogger(__name__)

# PARALLEL_UPDATES = 1
# SCAN_INTERVAL = timedelta(seconds=60)


# async def async_setup_entry(
#     hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
# ) -> None:
#     """Set up the sensors."""

#     coordinator = hass.data[DOMAIN][entry.entry_id]
#     my_api = hass.data[DOMAIN][entry.entry_id]
#     coordinator = SolvisModbusCoordinator(hass, my_api)
#     entities: list[SensorEntity] = [
#         Warmwasserpuffer(coordinator),
#         Warmwassertemperatur(coordinator),
#     ]

#     await coordinator.async_config_entry_first_refresh()
#     async_add_entities(entities)


# class Warmwasserpuffer(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Warmwasserpuffer"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class Warmwassertemperatur(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Warmwassertemperatur"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class Speicherreferenztemperatur(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Speicherreferenztemperatur"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class Heizungspuffertemperatur_oben(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Heizungspuffertemperatur oben"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class Aussentemperatur(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Außentemperatur"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class Heizungspuffertemperatur_unten(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Heizungspuffertemperatur unten"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class Zirkulationsdurchfluss(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Zirkulationsdurchfluss"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class Vorlauftemperatur(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Vorlauftemperatur"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class Kaltwassertemperatur(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Kaltwassertemperatur"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class Durchfluss_Warmwasserzirkualation(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Durchfluss Warmwasserzirkualation"
#     _attr_native_unit_of_measurement = "L/h"
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class Laufzeit_Brenner(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Laufzeit Brenner"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class Brennerstarts(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Brennerstarts"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class Ionisationsstrom(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Ionisationsstrom"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class A01_Pumpe_Zirkulation(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "A01.Pumpe Zirkulation"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class A02_Pumpe_Warmwasser(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "A02.Pumpe Warmwasser"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class A03_Pumpe_HK1(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "A03.Pumpe HK1"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class A05_Pumpe_Zirkulation(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "A05.Pumpe Zirkulation"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class A12_Brennerstatus(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "A12.Brennerstatus"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class WW_Nachheizung_2322(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "WW Nachheizung 2322"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class HKR1_Betriebsart(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "HKR1 Betriebsart"


# # Niedrigeres Abfrageintervall


# class HKR1_Absenktemperatur_Nacht(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "HKR1 Absenktemperatur Nacht"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class HKR1_Solltemperatur_Tag(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "HKR1 Solltemperatur Tag"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class DigIn_Stoerungen(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "DigIn Störungen"


# class WW_Solltemperatur(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "WW Solltemperatur"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT


# class VersionSC2(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "VersionSC2"


# class VersionNBG(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "VersionNBG"


# class ZirkulationBetriebsart(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "ZirkulationBetriebsart"


# class Raumtemperatur_HKR1(SensorEntity):
#     """Representation of a Sensor."""

#     _attr_name = "Raumtemperatur HKR1"
#     _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS
#     _attr_device_class = SensorDeviceClass.TEMPERATURE
#     _attr_state_class = SensorStateClass.MEASUREMENT

#   - platform: template
#     sensors:
#       ww_zirkulationsart:
#         friendly_name: "WW Zirkulation Betriebsart"
#         entity_id: sensor.zirkulationbetriebsart
#         value_template: >-
#           {% if states('sensor.zirkulationbetriebsart') == '1' %}
#             Aus
#           {% elif states('sensor.zirkulationbetriebsart') == '2' %}
#             Puls
#           {% elif states('sensor.zirkulationbetriebsart') == '3' %}
#             Temp
#           {% elif states('sensor.zirkulationbetriebsart') == '4' %}
#             Warten
#           {% else %}
#             unbekannt
#           {% endif %}

#       hkr1betriebsart:
#         friendly_name: "Heizkreislauf Betriebsart"
#         entity_id: sensor.hkr1_betriebsart
#         value_template: "{%if states.sensor.hkr1_betriebsart.state == '1' %}Aus{% elif states.sensor.hkr1_betriebsart.state == '2' %}Automatik{% elif states.sensor.hkr1_betriebsart.state == '3' %}Tagbetrieb{% elif states.sensor.hkr1_betriebsart.state == '4' %}Absenkbetrieb{% elif states.sensor.hkr1_betriebsart.state == '5' %}Standby{% elif states.sensor.hkr1_betriebsart.state == '6' %}Eco{% elif states.sensor.hkr1_betriebsart.state == '7' %}Urlaub{% elif states.sensor.hkr1_betriebsart.state == '8' %}WW Vorang{% elif states.sensor.zirkulationbetriebsart.state == '9' %}Frostschutz{% elif states.sensor.zirkulationbetriebsart.state == '10' %}Pumpenschutz{% elif states.sensor.hkr1_betriebsart.state == '11' %}Estrich{% endif %}"
