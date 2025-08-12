"""
Solvis Switch Entity.

Version: v2.1.0
"""

import logging

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import SolvisModbusCoordinator
from .utils.helpers import async_setup_solvis_entities, write_modbus_value
from .entity import SolvisEntity

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback) -> None:
    """Set up Solvis switch entities."""

    await async_setup_solvis_entities(
        hass,
        entry,
        async_add_entities,
        entity_cls=SolvisSwitch,
        input_type=3,  # switch
    )


class SolvisSwitch(SolvisEntity, SwitchEntity):
    """Representation of a Solvis switch."""

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
        """Initialize the Solvis switch entity."""
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

        self._attr_current_option = None

    def _update_value(self, value, extra_attrs) -> None:
        """Update state from coordinator data."""
        self._attr_current_option = str(value)
        self._attr_is_on = bool(value)
        self._attr_extra_state_attributes = extra_attrs
        _LOGGER.debug(f"[{self._response_key}] Successfully updated current option: {self._attr_current_option} (Raw: {value})")

    def _reset_value(self) -> None:
        """Reset state if data is not available."""
        self._attr_extra_state_attributes = {}

    async def _async_set_state(self, value: int, state: bool, action: str) -> None:
        """Helper to set switch state."""
        success = await write_modbus_value(self.coordinator.modbus, self.modbus_address, value)
        if success:
            self._attr_is_on = state
        else:
            _LOGGER.error(f"[{self._response_key}] Failed to turn {action} (write value {value}) at register {self.modbus_address}")
        self.async_write_ha_state()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn the switch on."""
        await self._async_set_state(1, True, "on")

    async def async_turn_off(self, **kwargs) -> None:
        """Turn the switch off."""
        await self._async_set_state(0, False, "off")
