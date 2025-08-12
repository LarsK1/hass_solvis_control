"""
Solvis Sensor Entity.

Version: v2.1.0
"""

import logging

from homeassistant.components import persistent_notification
from homeassistant.components.sensor import SensorEntity, SensorStateClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers import issue_registry as ir
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, CONF_NAME, CONF_HOST, DATA_COORDINATOR, DERIVATIVE_SENSORS, STORAGE_TYPE_CONFIG, CONF_OPTION_13
from .coordinator import SolvisModbusCoordinator
from .utils.helpers import async_setup_solvis_entities, generate_device_info
from .entity import SolvisEntity

_LOGGER = logging.getLogger(__name__)


class SolvisDerivativeSensor(SolvisEntity, SensorEntity):
    """Computes an derived entity from Solvis Sensor Entities"""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        host: str,
        name: str,
        source_keys: list[str],
        *,
        unit: str,
        device_class: str | None,
        state_class: SensorStateClass,
        entity_category: str | None = None,
        suggested_display_precision: int = 2,
        compute_mode: str | None,
        config_entry: ConfigEntry,
    ) -> None:
        super().__init__(
            coordinator,
            device_info,
            host,
            name,
            modbus_address=None,
            supported_version=coordinator.supported_version,
            enabled_by_default=True,
            data_processing=0,
            poll_rate=False,
        )

        self._attr_unique_id = f"{host}_{name}"
        self.source_keys = source_keys

        self._attr_native_unit_of_measurement = unit
        self._attr_device_class = device_class
        self._attr_state_class = state_class
        self._attr_entity_category = entity_category
        self._attr_suggested_display_precision = suggested_display_precision
        self.compute_mode = compute_mode
        self.config_entry = config_entry

        self._attr_native_value = None
        self._attr_extra_state_attributes = {}
        self.coordinator = coordinator

        # register listener
        self.coordinator.async_add_listener(self._async_update_from_coordinator)

    def _compute_combined(self) -> float | None:
        data = self.coordinator.data
        _LOGGER.debug("DerivateSensor–Daten: %s", {k: data.get(k) for k in self.source_keys})
        try:
            values = [data[key] for key in self.source_keys]
        except KeyError:
            return None

        match self.compute_mode:
            case "stored_energy_12":
                return self._compute_stored_energy_12(values)
            case _:
                # fallback
                return sum(values)

    def _compute_stored_energy_12(self, values: list[float]) -> float:

        storage_type = self.config_entry.data.get(CONF_OPTION_13)
        _LOGGER.debug(f"storage_type: {storage_type}")

        volumes = STORAGE_TYPE_CONFIG.get(storage_type, {}).get("volumes")
        _LOGGER.debug(f"volumes from config: {volumes}")

        if not volumes or len(volumes) != 3:
            _LOGGER.debug(f"invalid volumes: return 0")
            return 0.0

        v1, v2, v3 = volumes

        rho = 1.0
        c = 4.186
        t1, t2, t3, t4 = values
        t_zone1 = (t1 + t2) / 2
        t_zone2 = (t2 + t3) / 2
        t_zone3 = (t3 + t4) / 2

        e1 = v1 * rho * c * (t_zone1 - 12)  # Referenz-Temp 12 °C
        e2 = v2 * rho * c * (t_zone2 - 12)
        e3 = v3 * rho * c * (t_zone3 - 12)
        total_energy = e1 + e2 + e3

        return total_energy / 3600

    def _async_update_from_coordinator(self) -> None:
        combined = self._compute_combined()
        if combined is None:
            self._attr_native_value = None
            self._attr_extra_state_attributes = {}
            return
        else:
            self._attr_native_value = round(combined, self.suggested_display_precision)
            raw_attrs = {key: self.coordinator.data.get(key) for key in self.source_keys}
            self._attr_extra_state_attributes = {"raw_values": raw_attrs}

        self.async_write_ha_state()

    @callback
    def _handle_coordinator_update(self) -> None:
        return


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Solvis sensor entities."""
    await async_setup_solvis_entities(
        hass,
        entry,
        async_add_entities,
        entity_cls=SolvisSensor,
        input_type=0,  # sensor
    )

    storage_type = entry.data.get(CONF_OPTION_13)

    if storage_type is None:
        # create persistent notification
        persistent_notification.create(
            hass,
            "Die Integration „Solvis Control“ benötigt in der aktuellen Version zusätzlich die genaue Angabe des vorhandenen Schichtenspeichers. "
            "Bitte wählen Sie Einstellungen → Integrationen → Solvis Control → Konfigurieren und vervollständigen die Konfiguration.",
            title="Solvis Control: Speichertyp fehlt",
            notification_id="solvis_storage_type_missing",
        )
        # cancel further setup due to missing config_option
        return False

    # Setup SolvisDerivativeSensor
    coordinator: SolvisModbusCoordinator = hass.data[DOMAIN][entry.entry_id][DATA_COORDINATOR]
    host = entry.data.get(CONF_HOST)
    name = entry.data.get(CONF_NAME)

    device_info = generate_device_info(entry, host, name)

    sdc_instances: list[SolvisDerivativeSensor] = []
    for key, cfg in DERIVATIVE_SENSORS.items():
        sdc_instances.append(
            SolvisDerivativeSensor(
                coordinator=coordinator,
                device_info=device_info,
                host=host,
                name=key,
                source_keys=cfg["source_keys"],
                unit=cfg["unit"],
                device_class=cfg["device_class"],
                state_class=cfg["state_class"],
                entity_category=cfg.get("entity_category"),
                suggested_display_precision=cfg.get("suggested_display_precision", 2),
                compute_mode=cfg.get("compute_mode", "sum"),
                config_entry=entry,
            )
        )

    async_add_entities(sdc_instances)


class SolvisSensor(SolvisEntity, SensorEntity):
    """Representation of a Solvis sensor."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        host: str,
        name: str,
        hkr1_name: str | None = None,
        hkr2_name: str | None = None,
        hkr3_name: str | None = None,
        unit_of_measurement: str | None = None,
        device_class: str | None = None,
        state_class: str | None = None,
        entity_category: str | None = None,
        enabled_by_default: bool = True,
        data_processing: int = 0,
        poll_rate: bool = False,
        supported_version: int = 1,
        modbus_address: int | None = None,
        suggested_precision: int | None = 1,
    ) -> None:
        """Initialize the Solvis sensor."""
        super().__init__(
            coordinator,
            device_info,
            host,
            name,
            modbus_address,
            supported_version,
            enabled_by_default,
            data_processing,
            poll_rate,
            hkr1_name=hkr1_name,
            hkr2_name=hkr2_name,
            hkr3_name=hkr3_name,
        )

        self._attr_native_value = None
        self._attr_entity_category = EntityCategory.DIAGNOSTIC if entity_category == "diagnostic" else None
        self.device_class = device_class
        self.state_class = state_class
        self._attr_native_unit_of_measurement = unit_of_measurement
        self.suggested_display_precision = suggested_precision

    def _update_value(self, value, extra_attrs):
        match self.data_processing:
            case 2:
                if value != 0:
                    self._attr_native_value = (1 / (value / 60)) * 1000 / 2 / 42
                else:
                    _LOGGER.debug(f"Division by zero for {self._response_key} with value {value}")
                    self._attr_native_value = 0
            case 3:
                if value != 0:
                    self._attr_native_value = (1 / (value / 60)) * 1000 / 42
                else:
                    _LOGGER.debug(f"Division by zero for {self._response_key} with value {value}")
                    self._attr_native_value = 0
            case _:
                self._attr_native_value = value
        self._attr_extra_state_attributes = {"unprocessed_value": value}
        _LOGGER.debug(f"[{self._response_key}] Successfully updated native value: {self._attr_native_value} (Raw: {value})")

    def _reset_value(self):
        self._attr_extra_state_attributes = {}
