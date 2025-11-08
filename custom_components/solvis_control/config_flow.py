"""
ConfigFlow for Solvis Control

Version: v2.1.3
"""

import logging

import pymodbus.client as ModbusClient
from pymodbus import ModbusException
from pymodbus.exceptions import ConnectionException

import voluptuous as vol
from voluptuous.schema_builder import Schema

from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult, section
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector
from homeassistant.helpers.typing import ConfigType
from homeassistant.helpers.device_registry import format_mac

from .utils.helpers import fetch_modbus_value, get_mac
from .const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    MAC,
    DOMAIN,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
    CONF_OPTION_5,
    CONF_OPTION_6,
    CONF_OPTION_7,
    CONF_OPTION_8,
    CONF_OPTION_9,
    CONF_OPTION_10,
    CONF_OPTION_11,
    CONF_OPTION_12,
    CONF_OPTION_13,
    DEVICE_VERSION,
    POLL_RATE_DEFAULT,
    POLL_RATE_SLOW,
    POLL_RATE_HIGH,
    SolvisDeviceVersion,
    STORAGE_TYPE_CONFIG,
    CONF_HKR1_NAME,
    CONF_HKR2_NAME,
    CONF_HKR3_NAME,
)

_LOGGER = logging.getLogger(__name__)


SolvisVersionSelect = selector.SelectSelector(
    selector.SelectSelectorConfig(
        options=[
            selector.SelectOptionDict(value=str(SolvisDeviceVersion.SC3), label="SolvisControl 3"),
            selector.SelectOptionDict(
                value=str(SolvisDeviceVersion.SC2),
                label="SolvisControl 2 mit SolvisRemote",
            ),
        ],
        mode=selector.SelectSelectorMode.DROPDOWN,
    )
)


SolvisRoomTempSelect = selector.SelectSelector(
    selector.SelectSelectorConfig(
        options=[
            selector.SelectOptionDict(
                value="0",
                label="deaktiviert",
            ),
            selector.SelectOptionDict(
                value="1",
                label="lesen",
            ),
            selector.SelectOptionDict(
                value="2",
                label="schreiben",
            ),
        ],
        mode=selector.SelectSelectorMode.DROPDOWN,
    )
)


def validate_poll_rates(data):
    if data[POLL_RATE_DEFAULT] % data[POLL_RATE_HIGH] != 0:
        raise vol.Invalid(cv.string("poll_rate_invalid_high"))
    if data[POLL_RATE_SLOW] % data[POLL_RATE_DEFAULT] != 0:
        raise vol.Invalid(cv.string("poll_rate_invalid_slow"))
    return data


def get_host_schema_config(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default="Solvis Heizung"): str,
            vol.Required(CONF_HOST, default=data.get(CONF_HOST)): str,
            vol.Required(CONF_PORT, default=502): int,
            vol.Optional(MAC, default=""): str,
        }
    )


def get_host_schema_options(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=data.get(CONF_HOST)): str,
            vol.Required(CONF_PORT, default=data.get(CONF_PORT)): int,
        }
    )


def get_solvis_devices(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(DEVICE_VERSION, default=str(SolvisDeviceVersion.SC3)): SolvisVersionSelect,
            vol.Required(POLL_RATE_HIGH, default=10): vol.All(vol.Coerce(int), vol.Range(min=2)),
            vol.Required(POLL_RATE_DEFAULT, default=30): vol.All(vol.Coerce(int), vol.Range(min=2)),
            vol.Required(POLL_RATE_SLOW, default=300): vol.All(vol.Coerce(int), vol.Range(min=10)),
        },
        extra=vol.ALLOW_EXTRA,
    )


def get_solvis_devices_options(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(DEVICE_VERSION, default=str(SolvisDeviceVersion.SC3)): SolvisVersionSelect,
            vol.Required(POLL_RATE_HIGH, default=data.get(POLL_RATE_HIGH, 10)): vol.All(vol.Coerce(int), vol.Range(min=2)),
            vol.Required(POLL_RATE_DEFAULT, default=data.get(POLL_RATE_DEFAULT, 30)): vol.All(vol.Coerce(int), vol.Range(min=2)),
            vol.Required(POLL_RATE_SLOW, default=data.get(POLL_RATE_SLOW, 300)): vol.All(vol.Coerce(int), vol.Range(min=10)),
        },
        extra=vol.ALLOW_EXTRA,
    )


def get_solvis_modules(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(CONF_OPTION_1, default=data.get(CONF_OPTION_1, False)): bool,  # HKR 2
            vol.Required(CONF_OPTION_2, default=data.get(CONF_OPTION_2, False)): bool,  # HKR 3
            vol.Required(CONF_OPTION_3, default=data.get(CONF_OPTION_3, False)): bool,  # solar collectors
            vol.Required(CONF_OPTION_4, default=data.get(CONF_OPTION_4, False)): bool,  # heat pump
            vol.Required(CONF_OPTION_8, default=data.get(CONF_OPTION_8, False)): bool,  # PV2Heat
            vol.Required(CONF_OPTION_5, default=data.get(CONF_OPTION_5, False)): bool,  # heat meter
        }
    )


def get_solvis_roomtempsensors(data: ConfigType) -> Schema:
    schema_fields = {
        vol.Required(
            "hkr1_room_temp_sensor",
            default="1",
        ): SolvisRoomTempSelect,
    }
    if data.get(CONF_OPTION_1, False):
        schema_fields[
            vol.Required(
                "hkr2_room_temp_sensor",
                default="1",
            )
        ] = SolvisRoomTempSelect
    if data.get(CONF_OPTION_2, False):
        schema_fields[
            vol.Required(
                "hkr3_room_temp_sensor",
                default="1",
            )
        ] = SolvisRoomTempSelect
    return vol.Schema(schema_fields)


def get_solvis_roomtempsensors_options(data: ConfigType) -> Schema:
    schema_fields = {
        vol.Required(
            "hkr1_room_temp_sensor",
            default="2" if data.get(CONF_OPTION_7) else ("1" if data.get(CONF_OPTION_6) else "0"),
        ): SolvisRoomTempSelect,
    }
    if data.get(CONF_OPTION_1, False):
        schema_fields[
            vol.Required(
                "hkr2_room_temp_sensor",
                default="2" if data.get(CONF_OPTION_10) else ("1" if data.get(CONF_OPTION_9) else "0"),
            )
        ] = SolvisRoomTempSelect
    if data.get(CONF_OPTION_2, False):
        schema_fields[
            vol.Required(
                "hkr3_room_temp_sensor",
                default="2" if data.get(CONF_OPTION_12) else ("1" if data.get(CONF_OPTION_11) else "0"),
            )
        ] = SolvisRoomTempSelect
    return vol.Schema(schema_fields)


def get_solvis_hkr_names(data: dict) -> vol.Schema:
    schema_fields: dict[vol.Optional, type] = {
        vol.Optional(CONF_HKR1_NAME, default=data.get(CONF_HKR1_NAME, "")): str,
    }

    if data.get(CONF_OPTION_1, False):
        schema_fields[vol.Optional(CONF_HKR2_NAME, default=data.get(CONF_HKR2_NAME, ""))] = str

    if data.get(CONF_OPTION_2, False):
        schema_fields[vol.Optional(CONF_HKR3_NAME, default=data.get(CONF_HKR3_NAME, ""))] = str

    return vol.Schema(schema_fields)


class SolvisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2
    MINOR_VERSION = 6

    def __init__(self) -> None:
        """Init the ConfigFlow."""
        _LOGGER.info(f"Initialize config flow for {DOMAIN}")
        self.data: ConfigType = {}
        self.client = None

    async def async_step_user(self, user_input: ConfigType | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            self.data = user_input
            try:
                if self.data[MAC] == "":
                    _LOGGER.debug(f"calling get_mac for {user_input[CONF_HOST]}")
                    mac_address = get_mac(user_input[CONF_HOST])

                    if not mac_address:
                        errors["base"] = "mac_error"
                        errors["device"] = "Could not find mac-address of device. Please enter the mac-address below manually."
                        return self.async_show_form(
                            step_id="user",
                            data_schema=get_host_schema_config(self.data),
                            errors=errors,
                        )
                    self.data[MAC] = format_mac(mac_address)
                    await self.async_set_unique_id(format_mac(mac_address))
                    self._abort_if_unique_id_configured()
                else:
                    self.data[MAC] = format_mac(self.data[MAC])
                    await self.async_set_unique_id(self.data[MAC])
                    self._abort_if_unique_id_configured()

                versionsc_raw, versionnbg_raw = await fetch_modbus_value([32770, 32771], 1, user_input[CONF_HOST], user_input[CONF_PORT])

            except ConnectionException as exc:
                _LOGGER.error(f"ConnectionException: {exc}")
                errors["base"] = "cannot_connect"
                errors["device"] = str(exc)
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )

            except ModbusException as exc:
                _LOGGER.error(f"ModbusException: {exc}")
                errors["base"] = "modbus_error"
                errors["device"] = str(exc)
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )

            except Exception as exc:
                _LOGGER.error(f"Unexpected error in config flow: {exc}", exc_info=True)
                errors["base"] = "unknown"
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )

            else:
                versionsc = str(versionsc_raw)
                versionnbg = str(versionnbg_raw)
                _LOGGER.debug(f"Solvis hardware version: {versionnbg} / Solvis software version: {versionsc}")
                user_input["VERSIONSC"] = f"{versionsc[0]}.{versionsc[1:3]}.{versionsc[3:5]}"
                user_input["VERSIONNBG"] = f"{versionnbg[0]}.{versionnbg[1:3]}.{versionnbg[3:5]}"

            return await self.async_step_device()  # next step: device

        return self.async_show_form(
            step_id="user",
            data_schema=get_host_schema_config(self.data),
            errors=errors,
        )

    async def async_step_device(self, user_input: ConfigType | None = None) -> FlowResult:
        """Handle the device step."""
        errors = {}
        if user_input is not None:
            try:
                self.data.update(user_input)
                validate_poll_rates(self.data)
                return await self.async_step_features()  # next step: features
            except vol.Invalid as exc:
                errors["base"] = str(exc)
                errors["device"] = exc.error_message

        return self.async_show_form(
            step_id="device",
            data_schema=get_solvis_devices(self.data),
            errors=errors,
        )

    async def async_step_features(self, user_input: ConfigType | None = None) -> FlowResult:
        """Handle the feature step."""

        if user_input is None:  # before user inputs anything

            try:
                amount_hkr = await fetch_modbus_value(2, 1, self.data[CONF_HOST], self.data[CONF_PORT], device_version=int(self.data.get(DEVICE_VERSION, 0)))
                _LOGGER.debug(f"[config_flow > async_step_features] Register 2 read from Modbus: {amount_hkr}")
            except Exception as exc:
                _LOGGER.warning("[config_flow > async_step_features] Got no value for register 2: setting default 1.")
                amount_hkr = 1

            self.data[CONF_OPTION_1] = amount_hkr > 1
            self.data[CONF_OPTION_2] = amount_hkr > 2

            _LOGGER.debug(f"[config_flow > async_step_features] CONF_OPTION_1 detected: {self.data[CONF_OPTION_1]}")
            _LOGGER.debug(f"[config_flow > async_step_features] CONF_OPTION_2 detected: {self.data[CONF_OPTION_2]}")

            return self.async_show_form(  # show form at first method call: user_input = None
                step_id="features",
                data_schema=get_solvis_modules(self.data),
            )

        self.data.update(user_input)

        _LOGGER.debug(f"[config_flow > async_step_features] CONF_OPTION_1: {self.data[CONF_OPTION_1]}")
        _LOGGER.debug(f"[config_flow > async_step_features] CONF_OPTION_2: {self.data[CONF_OPTION_2]}")
        _LOGGER.debug(f"[config_flow > async_step_features] CONF_OPTION_3: {self.data[CONF_OPTION_3]}")
        _LOGGER.debug(f"[config_flow > async_step_features] CONF_OPTION_4: {self.data[CONF_OPTION_4]}")
        _LOGGER.debug(f"[config_flow > async_step_features] CONF_OPTION_5: {self.data[CONF_OPTION_5]}")
        _LOGGER.debug(f"[config_flow > async_step_features] CONF_OPTION_8: {self.data[CONF_OPTION_8]}")

        return await self.async_step_roomtempsensors()  # next step

    async def async_step_roomtempsensors(self, user_input: ConfigType | None = None) -> FlowResult:
        errors = {}
        if user_input is not None:  # user input something

            hkr1 = user_input["hkr1_room_temp_sensor"]
            _LOGGER.debug(f"[roomtempsensors] hkr1: {hkr1}")
            self.data[CONF_OPTION_6] = hkr1 == "1"
            self.data[CONF_OPTION_7] = hkr1 == "2"

            if "hkr2_room_temp_sensor" in user_input:
                hkr2 = user_input["hkr2_room_temp_sensor"]
                _LOGGER.debug(f"[roomtempsensors] hkr2: {hkr2}")
                self.data[CONF_OPTION_9] = hkr2 == "1"
                self.data[CONF_OPTION_10] = hkr2 == "2"
            else:
                self.data[CONF_OPTION_9] = False
                self.data[CONF_OPTION_10] = False

            if "hkr3_room_temp_sensor" in user_input:
                hkr3 = user_input["hkr3_room_temp_sensor"]
                _LOGGER.debug(f"[roomtempsensors] hkr3: {hkr3}")
                self.data[CONF_OPTION_11] = hkr3 == "1"
                self.data[CONF_OPTION_12] = hkr3 == "2"
            else:
                self.data[CONF_OPTION_11] = False
                self.data[CONF_OPTION_12] = False

            return await self.async_step_storage_type()

        return self.async_show_form(  # show form at first method call: user_input = None
            step_id="roomtempsensors",
            data_schema=get_solvis_roomtempsensors(self.data),
            errors=errors,
        )

    async def async_step_storage_type(self, user_input: ConfigType | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(
                step_id="storage_type",
                data_schema=vol.Schema({vol.Required(CONF_OPTION_13): vol.In(list(STORAGE_TYPE_CONFIG.keys()))}),
            )

        self.data.update(user_input)

        return await self.async_step_hkr_names()

    async def async_step_hkr_names(self, user_input: ConfigType | None = None) -> FlowResult:
        if user_input is not None:
            for key, val in list(user_input.items()):
                if val is None or val == "":
                    continue
                self.data[key] = val

            return self.async_create_entry(title=self.data[CONF_NAME], data=self.data)

        return self.async_show_form(
            step_id="hkr_names",
            data_schema=get_solvis_hkr_names(self.data),
            errors={},
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return SolvisOptionsFlow(config_entry)


class SolvisOptionsFlow(config_entries.OptionsFlow):
    VERSION = 2
    MINOR_VERSION = 6

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Init the ConfigFlow."""
        self.entry_id = config_entry.entry_id
        # self.config_entry = config_entry
        self.data = {**config_entry.data, **config_entry.options}

    async def async_step_init(self, user_input: ConfigType | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        _LOGGER.debug(f"Options flow values step init: {str(self.data)}")

        if user_input is not None:
            self.data.update(user_input)

            try:
                versionsc_raw, versionnbg_raw = await fetch_modbus_value([32770, 32771], 1, user_input[CONF_HOST], user_input[CONF_PORT])

            except ConnectionException as exc:
                _LOGGER.error(f"ConnectionException: {exc}")
                errors["base"] = "cannot_connect"
                errors["device"] = str(exc)
                return self.async_show_form(
                    step_id="init",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )

            except ModbusException as exc:
                _LOGGER.error(f"ModbusException: {exc}")
                errors["base"] = "modbus_error"
                errors["device"] = str(exc)
                return self.async_show_form(
                    step_id="init",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )

            except Exception as exc:
                errors["base"] = "unknown"
                errors["device"] = str(exc)
                return self.async_show_form(
                    step_id="init",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )

            else:
                versionsc = str(versionsc_raw)
                versionnbg = str(versionnbg_raw)
                _LOGGER.debug(f"Solvis hardware version: {versionnbg} / Solvis software version: {versionsc}")
                user_input["VERSIONSC"] = f"{versionsc[0]}.{versionnbg[1:3]}.{versionsc[3:5]}"
                user_input["VERSIONNBG"] = f"{versionnbg[0]}.{versionnbg[1:3]}.{versionnbg[3:5]}"

            return await self.async_step_device()

        return self.async_show_form(
            step_id="init",
            data_schema=get_host_schema_options(self.data),
            errors=errors,
        )

    async def async_step_device(self, user_input: ConfigType | None = None) -> FlowResult:
        """Handle the device step."""
        errors = {}
        _LOGGER.debug(f"Options flow values step device: {str(self.data)}")
        if user_input is not None:
            try:
                self.data.update(user_input)
                validate_poll_rates(self.data)
                return await self.async_step_features()

            except vol.Invalid as exc:
                errors["base"] = str(exc)
                errors["device"] = exc.error_message

        return self.async_show_form(
            step_id="device",
            data_schema=get_solvis_devices_options(self.data),
            errors=errors,
        )

    async def async_step_features(self, user_input: ConfigType | None = None) -> FlowResult:
        """Handle the feature step."""
        _LOGGER.debug(f"Options flow values step features: {str(self.data)}")

        if user_input is not None:
            self.data.update(user_input)
            return await self.async_step_roomtempsensors()  # next step

        return self.async_show_form(
            step_id="features",
            data_schema=get_solvis_modules(self.data),
        )

    async def async_step_roomtempsensors(self, user_input: ConfigType | None = None) -> FlowResult:
        errors = {}
        if user_input is not None:  # user input something

            hkr1 = user_input["hkr1_room_temp_sensor"]
            _LOGGER.debug(f"[roomtempsensors] hrk1: {hkr1}")
            self.data[CONF_OPTION_6] = hkr1 == "1"
            self.data[CONF_OPTION_7] = hkr1 == "2"

            if "hkr2_room_temp_sensor" in user_input:
                hkr2 = user_input["hkr2_room_temp_sensor"]
                _LOGGER.debug(f"[roomtempsensors] hrk2: {hkr2}")
                self.data[CONF_OPTION_9] = hkr2 == "1"
                self.data[CONF_OPTION_10] = hkr2 == "2"
            else:
                self.data[CONF_OPTION_9] = False
                self.data[CONF_OPTION_10] = False

            if "hkr3_room_temp_sensor" in user_input:
                hkr3 = user_input["hkr3_room_temp_sensor"]
                _LOGGER.debug(f"[roomtempsensors] hrk3: {hkr3}")
                self.data[CONF_OPTION_11] = hkr3 == "1"
                self.data[CONF_OPTION_12] = hkr3 == "2"
            else:
                self.data[CONF_OPTION_11] = False
                self.data[CONF_OPTION_12] = False

            return await self.async_step_storage_type()

        return self.async_show_form(  # show form at first method call: user_input = None
            step_id="roomtempsensors",
            data_schema=get_solvis_roomtempsensors_options(self.data),
            errors=errors,
        )

    async def async_step_storage_type(self, user_input: ConfigType | None = None) -> FlowResult:
        if user_input is None:
            current = self.config_entry.options.get(CONF_OPTION_13)
            return self.async_show_form(
                step_id="storage_type",
                data_schema=vol.Schema({vol.Required(CONF_OPTION_13, default=current): vol.In(list(STORAGE_TYPE_CONFIG.keys()))}),
            )
        self.data.update(user_input)
        return self.async_create_entry(title=self.data[CONF_NAME], data=self.data)
