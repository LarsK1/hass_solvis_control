
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

from .const import DATA_COORDINATOR, DOMAIN, MANUFACTURER, REGISTERS, CONF_HOST, CONF_NAME
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
            _LOGGER.warning(
                "Invalid data from coordinator"
            )
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

# modbus:
#   - name: "Solvis Ben"
#     type: tcp
#     host: 10.10.4.211
#     port: 502

#     sensors:
#       - name: Warmwasserpuffer
#         unit_of_measurement: °C
#         scale: 0.1
#         slave: 1
#         precision: 2
#         input_type: input
#         address: 33024
#         scan_interval: 30
#         unique_id: 4ce76dec-0acf-4831-ae51-680c57d1b448

#       - name: Warmwassertemperatur
#         unit_of_measurement: °C
#         scale: 0.1
#         slave: 1
#         precision: 2
#         input_type: input
#         address: 33025
#         scan_interval: 30
#         unique_id: 90cb7b6a-1af1-4a50-bd2d-2c9e9e54dbf6

#       - name: Speicherreferenztemperatur
#         unit_of_measurement: °C
#         scale: 0.1
#         slave: 1
#         precision: 2
#         input_type: input
#         address: 33026
#         scan_interval: 30
#         unique_id: 087a2731-548c-4bf2-a938-3877ee764a24

#       - name: Heizungspuffertemperatur oben
#         unit_of_measurement: °C
#         scale: 0.1
#         slave: 1
#         precision: 2
#         input_type: input
#         address: 33027
#         scan_interval: 30
#         unique_id: a122f6d4-0b4e-40d8-9b65-dc975863523f

#       - name: Aussentemperatur
#         unit_of_measurement: °C
#         scale: 0.1
#         slave: 1
#         precision: 2
#         input_type: input
#         address: 33033
#         scan_interval: 30
#         unique_id: d72b9673-c054-4b26-acd9-a6999db9e38c

#       - name: Heizungspuffertemperatur unten
#         unit_of_measurement: °C
#         scale: 0.1
#         slave: 1
#         precision: 2
#         input_type: input
#         address: 33032
#         scan_interval: 30
#         unique_id: 687da60c-65a9-4aa9-9475-2271aff27f7c

#       - name: Zirkulationsdurchfluss
#         unit_of_measurement: °C
#         scale: 0.1
#         slave: 1
#         precision: 2
#         input_type: input
#         address: 33034
#         scan_interval: 30
#         unique_id: 674b5fcc-055f-4827-b094-1c7797992f08

#       - name: Vorlauftemperatur
#         unit_of_measurement: °C
#         scale: 0.1
#         slave: 1
#         precision: 2
#         input_type: input
#         address: 33035
#         scan_interval: 30
#         unique_id: 1528c6e6-215a-4de6-ac45-518011d87d35

#       - name: Kaltwassertemperatur
#         unit_of_measurement: °C
#         scale: 0.1
#         slave: 1
#         precision: 2
#         input_type: input
#         address: 33038
#         scan_interval: 30
#         unique_id: 77a7e6e2-e4e7-47ff-bf2b-cbcd1125abbd

#       - name: Durchfluss Warmwasserzirkualation
#         unit_of_measurement: l/min
#         slave: 1
#         precision: 2
#         scale: 0.1
#         input_type: input
#         address: 33041
#         scan_interval: 30
#         unique_id: c4742a62-9d0d-4bb9-96f8-7036519b11c3

#       - name: Laufzeit Brenner
#         unit_of_measurement: h
#         slave: 1
#         precision: 0
#         input_type: input
#         address: 33536
#         scan_interval: 30
#         unique_id: 67f36d04-fff6-4122-b8f3-d7ec81b76573

#       - name: Brennerstarts
#         unit_of_measurement: Starts
#         slave: 1
#         precision: 0
#         input_type: input
#         address: 33537
#         scan_interval: 30
#         unique_id: 448a4499-97e6-4b65-af69-12562322f16d

#       - name: Brennerleistung
#         unit_of_measurement: kW
#         scale: 0.1
#         slave: 1
#         precision: 2
#         input_type: input
#         address: 33539
#         scan_interval: 30
#         unique_id: 97711598-49a3-4a37-908a-6603504d7bc8

#       - name: Ionisationsstrom
#         unit_of_measurement: mA
#         slave: 1
#         scale: 0.1
#         precision: 1
#         input_type: input
#         address: 33540
#         scan_interval: 30
#         unique_id: 9ac2a93c-cb44-4456-aaa4-62bd31a95a9c

#       - name: A01.Pumpe Zirkulation
#         slave: 1
#         unit_of_measurement: V
#         scale: 0.01
#         precision: 0
#         input_type: input
#         address: 33280
#         scan_interval: 30
#         unique_id: 4cbacfac-841a-4967-a2f9-7b9f8859c853

#       - name: A02.Pumpe Warmwasser
#         slave: 1
#         unit_of_measurement: V
#         scale: 0.01
#         precision: 0
#         input_type: input
#         address: 33281
#         scan_interval: 30
#         unique_id: 50106c32-d031-47df-9746-e182526c1ca3

#       - name: A03.Pumpe HK1
#         slave: 1
#         unit_of_measurement: V
#         scale: 0.01
#         precision: 0
#         input_type: input
#         address: 33282
#         scan_interval: 30
#         unique_id: 35ac2931-e593-4e63-9afe-85d30d4a79a0

#       - name: A05.Pumpe Zirkulation
#         slave: 1
#         unit_of_measurement: V
#         scale: 0.01
#         precision: 0
#         input_type: input
#         address: 33284
#         scan_interval: 30
#         unique_id: e3abf1c9-aaea-4797-b4ad-d8ec47465461

#       - name: A12.Brennerstatus
#         slave: 1
#         unit_of_measurement: V
#         scale: 0.01
#         precision: 0
#         input_type: input
#         address: 33291
#         scan_interval: 30
#         unique_id: 02602bb6-06d1-4e15-9bde-d273a20c0553

#       - name: WW Nachheizung 2322
#         slave: 1
#         #unit_of_measurement: V
#         #scale: 0.01
#         #precision: 0
#         input_type: holding
#         address: 2322
#         scan_interval: 30
#         unique_id: f2e642f4-11f0-4949-8fa8-86241d23cdfb

#       - name: HKR1 Betriebsart
#         slave: 1
#         input_type: holding
#         address: 2818
#         scan_interval: 30
#         unique_id: e240a16b-563a-409f-929a-088010822ade

#       # ab hier 300 Sekunden Poll Interval

#       - name: HKR1 Absenktemperatur Nacht
#         unit_of_measurement: °C
#         slave: 1
#         input_type: holding
#         address: 2821
#         scan_interval: 300
#         unique_id: b6550eb0-6f0f-4019-a708-65b1cd4ecbf7

#       - name: HKR1 Solltemperatur Tag
#         unit_of_measurement: °C
#         slave: 1
#         input_type: holding
#         address: 2820
#         scan_interval: 300
#         unique_id: cc08dfc7-3f45-409c-b50f-a241f5d63169

#       - name: DigIn Stoerungen
#         slave: 1
#         input_type: input
#         address: 33045
#         scan_interval: 300
#         unique_id: 45d195db-ce3b-4498-8015-566e45f115b6

#       - name: WW Solltemperatur
#         unit_of_measurement: °C
#         slave: 1
#         input_type: holding
#         address: 2305
#         scan_interval: 300
#         unique_id: 0a76a76a-a0b6-40a8-b20d-2245a60fdd39

#       - name: VersionSC2
#         slave: 1
#         scale: 0.01
#         precision: 2
#         input_type: input
#         address: 32770
#         scan_interval: 300
#         unique_id: bd96dedf-f5a3-43b9-a5b9-e31441fbae67

#       - name: VersionNBG
#         slave: 1
#         scale: 0.01
#         input_type: input
#         address: 32771
#         scan_interval: 300
#         unique_id: 1ad4554f-669b-4038-aef4-71d4e0194178

#       - name: ZirkulationBetriebsart
#         slave: 1
#         input_type: input
#         address: 2049
#         scan_interval: 300
#         unique_id: c075a802-8143-4d2c-af13-8421345ce2ad

#       - name: Raumtemperatur_HKR1
#         unit_of_measurement: °C
#         scale: 0.1
#         slave: 1
#         input_type: holding
#         address: 34304
#         scan_interval: 300
#         unique_id: 1c4b8bdf-cb08-465a-b4af-80ecc400a220

# sensor:
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
