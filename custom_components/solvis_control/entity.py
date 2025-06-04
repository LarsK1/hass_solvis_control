"""
Solvis Base Entity.

Version v2.1.0
"""

import logging
from homeassistant.core import callback
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from .utils.helpers import generate_unique_id, process_coordinator_data
from homeassistant.helpers.translation import async_get_translations
from .const import DOMAIN
from homeassistant.helpers import entity_registry as er


_LOGGER = logging.getLogger(__name__)


class SolvisEntity(CoordinatorEntity):
    """Base class for all Solvis entities."""

    def __init__(
        self,
        coordinator,
        device_info,
        host: str,
        name: str,
        modbus_address: int = None,
        supported_version: int = 1,
        enabled_by_default: bool = True,
        data_processing: int = 0,
        poll_rate: bool = False,
        hkr1_name: str | None = None,
        hkr2_name: str | None = None,
        hkr3_name: str | None = None,
    ) -> None:
        """Initialize the Solvis entity."""
        super().__init__(coordinator)
        self._host = host
        self.modbus_address = modbus_address
        self._response_key = name
        self.entity_registry_enabled_default = enabled_by_default
        self.device_info = device_info
        self._attr_has_entity_name = True
        self.supported_version = supported_version
        self._attr_unique_id = generate_unique_id(modbus_address, supported_version, name)
        self._attr_translation_key = name
        self.data_processing = data_processing
        self.poll_rate = poll_rate
        self._attr_available = False
        self._register_name = name
        self._hkr1_name = hkr1_name
        self._hkr2_name = hkr2_name
        self._hkr3_name = hkr3_name

    async def async_added_to_hass(self) -> None:
        await super().async_added_to_hass()
        all_translations = await async_get_translations(
            self.hass,
            self.hass.config.language,
            "entity",
            [DOMAIN],
        )
        self._set_dynamic_name(all_translations)

        registry = er.async_get(self.hass)
        entry = registry.async_get(self.entity_id)
        custom = getattr(self, "_attr_name", None)

        if custom:
            if entry and entry.original_name != custom:
                registry.async_update_entity(self.entity_id, name=custom)
        else:
            if custom == "" and hasattr(self, "_attr_name"):
                delattr(self, "_attr_name")
            if entry and entry.name is not None:
                registry.async_update_entity(self.entity_id, name=None)

        self.async_write_ha_state()

    def _set_dynamic_name(self, translations_for_entity: dict) -> None:
        key = self._register_name.lower()
        _LOGGER.debug(f"[{key}] Processing entity with translations: {bool(translations_for_entity)}")
        translated_name = self._find_translation(key, translations_for_entity)

        if not translated_name:
            _LOGGER.debug(f"[{key}] No translation found, keeping _attr_name = None")
            return
        _LOGGER.debug(f"[{key}] Found translation: '{translated_name}'")

        # replacements
        if key.startswith("hkr1_") and self._hkr1_name:
            new_name = self._replace_hkr_prefix(translated_name, "HKR1", self._hkr1_name)
            self._attr_name = new_name
            self._attr_translation_key = None
            _LOGGER.debug(f"[{key}] HKR1 replacement: '{translated_name}' -> '{new_name}'")
            return

        if key.startswith("hkr2_") and self._hkr2_name:
            new_name = self._replace_hkr_prefix(translated_name, "HKR2", self._hkr2_name)
            self._attr_name = new_name
            self._attr_translation_key = None
            _LOGGER.debug(f"[{key}] HKR2 replacement: '{translated_name}' -> '{new_name}'")
            return

        if key.startswith("hkr3_") and self._hkr3_name:
            new_name = self._replace_hkr_prefix(translated_name, "HKR3", self._hkr3_name)
            self._attr_name = new_name
            self._attr_translation_key = None
            _LOGGER.debug(f"[{key}] HKR3 replacement: '{translated_name}' -> '{new_name}'")
            return

        _LOGGER.debug(f"[{key}] No HKR replacement needed, keeping translation_key")

    def _find_translation(self, key: str, translations: dict) -> str | None:
        for platform in ("sensor", "switch", "binary_sensor", "number", "select"):
            flat_key = f"component.{DOMAIN}.entity.{platform}.{key}.name"
            if flat_key in translations:
                return translations[flat_key]
        return None

    def _replace_hkr_prefix(self, translated_name: str, old_prefix: str, new_prefix: str) -> str:
        if translated_name.startswith(old_prefix + " "):
            return translated_name.replace(old_prefix + " ", new_prefix + " ", 1)

        if translated_name.startswith(old_prefix + ":"):
            return translated_name.replace(old_prefix + ":", new_prefix + ":", 1)

        if translated_name.startswith(old_prefix + "-"):
            return translated_name.replace(old_prefix + "-", new_prefix + "-", 1)

        if old_prefix in translated_name:
            _LOGGER.warning(f"Fallback replacement of '{old_prefix}' in '{translated_name}'")
            return translated_name.replace(old_prefix, new_prefix, 1)

        _LOGGER.warning(f"No '{old_prefix}' prefix found in '{translated_name}', prepending '{new_prefix}'")
        return f"{new_prefix} {translated_name}"

    @callback
    def _handle_coordinator_update(self) -> None:
        available, value, extra_attrs = process_coordinator_data(self.coordinator.data, self._response_key)
        if available is None:
            return
        self._attr_available = available
        if available:
            self._update_value(value, extra_attrs)
        else:
            self._reset_value()
        self.schedule_update_ha_state()

    def _update_value(self, value, extra_attrs):
        """Implement entity-specific value processing in subclasses."""
        raise NotImplementedError

    def _reset_value(self):
        """Optional: Reset value if data is not available."""
        pass
