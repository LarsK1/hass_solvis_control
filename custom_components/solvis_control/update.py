"""
Solvis Update Entity.

Version: v2.0.0
"""

import logging

from homeassistant.components.update import UpdateEntity, UpdateDeviceClass
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import DOMAIN, LATEST_SW_VERSION
from .coordinator import SolvisModbusCoordinator
from .utils.helpers import async_setup_solvis_entities
from .entity import SolvisEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Solvis update entities."""
    await async_setup_solvis_entities(
        hass,
        entry,
        async_add_entities,
        entity_cls=SolvisUpdateEntity,
        input_type=5,  # update
    )


class SolvisUpdateEntity(SolvisEntity, UpdateEntity):
    """Representation of a Solvis update entity."""

    def __init__(
        self,
        coordinator: SolvisModbusCoordinator,
        device_info: DeviceInfo,
        host: str,
        name: str,
        hkr1_name: str | None = None,
        hkr2_name: str | None = None,
        hkr3_name: str | None = None,
        enabled_by_default: bool = True,
        modbus_address: int = None,
        data_processing: int = 0,
        poll_rate: bool = False,
        supported_version: int = 1,
    ) -> None:
        """Initialize the Solvis update entity."""
        super().__init__(
            coordinator,
            device_info,
            host,
            name,
            modbus_address,
            supported_version,
            enabled_by_default,
            data_processing,
            poll_rate
        )

        self._attr_device_class = UpdateDeviceClass.FIRMWARE
        self._attr_title = "Solvis Controller"  # Default title
        if self.modbus_address == 32770:
            self._attr_title = "Controller Firmware"
        else:  # self.modbus_address == 32771
            self._attr_title = "Network Board Firmware"

    def _update_value(self, value, extra_attrs) -> None:
        """Update state from coordinator data."""
        if value is None or len(str(value)) != 5:
            _LOGGER.warning("Couldn't process version string to Version.")
            self._attr_installed_version = None
            self._attr_latest_version = None
            return

        value_str = str(value)
        installed_version = f"{value_str[0]}.{value_str[1:3]}.{value_str[3:5]}"
        self._attr_installed_version = installed_version

        device_registry = dr.async_get(self.hass)
        device = device_registry.async_get_device(self.device_info["identifiers"])

        if device is not None:
            if self.modbus_address == 32770:  # VERSIONSC
                self._attr_latest_version = LATEST_SW_VERSION
                device_registry.async_update_device(device.id, sw_version=installed_version)
            else:  # elif self.modbus_address == 32771:  # VERSIONNBG
                self._attr_latest_version = installed_version  # No "latest" for HW
                device_registry.async_update_device(device.id, hw_version=installed_version)

        _LOGGER.debug(f"[{self._response_key}] Successfully updated version to {installed_version}")

    def _reset_value(self) -> None:
        """Reset state if data is not available."""
        self._attr_installed_version = None
        self._attr_latest_version = None
