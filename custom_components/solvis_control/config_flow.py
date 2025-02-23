import logging

import pymodbus.client as ModbusClient
import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import selector
from homeassistant.helpers.typing import ConfigType
from pymodbus import ModbusException
from pymodbus.exceptions import ConnectionException
from voluptuous.schema_builder import Schema

from .const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    DOMAIN,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
    CONF_OPTION_5,
    CONF_OPTION_6,
    CONF_OPTION_7,
    DEVICE_VERSION,
    POLL_RATE_DEFAULT,
    POLL_RATE_SLOW,
    POLL_RATE_HIGH,
    SolvisDeviceVersion,
)

_LOGGER = logging.getLogger(__name__)

SolvisVersionSelect = selector.SelectSelector(
    selector.SelectSelectorConfig(
        options=[
            selector.SelectOptionDict(value=str(SolvisDeviceVersion.SC3), label="SC3"),
            selector.SelectOptionDict(
                value=str(SolvisDeviceVersion.SC2),
                label="SC2",
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
    if not (data[POLL_RATE_HIGH] < data[POLL_RATE_DEFAULT] < data[POLL_RATE_SLOW]):
        raise vol.Invalid(cv.string("poll_rate_invalid_order"))

    return data


def get_host_schema_config(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default="Solvis Heizung"): str,
            vol.Required(CONF_HOST, default=data.get(CONF_HOST)): str,
            vol.Required(CONF_PORT, default=502): int,
        }
    )


def get_solvis_modules(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(CONF_OPTION_1, default=False): bool,  # HKR 2
            vol.Required(CONF_OPTION_2, default=False): bool,  # HKR 3
            vol.Required(CONF_OPTION_3, default=False): bool,  # solar collectors
            vol.Required(CONF_OPTION_4, default=False): bool,  # heat pump
            vol.Required(CONF_OPTION_5, default=False): bool,  # heat meter
            vol.Required(CONF_OPTION_6, default=False): bool,  # room temperatur sensor
            vol.Required(CONF_OPTION_7, default=False): bool,  # write room temperatur sensor
        }
    )


def get_solvis_devices(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(DEVICE_VERSION, default=str(SolvisDeviceVersion.SC3)): SolvisVersionSelect,
            vol.Required(POLL_RATE_DEFAULT, default=30): vol.All(vol.Coerce(int), vol.Range(min=2)),
            vol.Required(POLL_RATE_SLOW, default=300): vol.All(vol.Coerce(int), vol.Range(min=10)),
            vol.Required(POLL_RATE_HIGH, default=10): vol.All(vol.Coerce(int), vol.Range(min=10)),
        },
        extra=vol.ALLOW_EXTRA,
    )


def get_solvis_modules_options(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(CONF_OPTION_1, default=data.get(CONF_OPTION_1, False)): bool,  # HKR 2
            vol.Required(CONF_OPTION_2, default=data.get(CONF_OPTION_2, False)): bool,  # HKR 3
            vol.Required(CONF_OPTION_3, default=data.get(CONF_OPTION_3, False)): bool,  # solar collectors
            vol.Required(CONF_OPTION_4, default=data.get(CONF_OPTION_4, False)): bool,  # heat pump
            vol.Required(CONF_OPTION_5, default=data.get(CONF_OPTION_5, False)): bool,  # heat meter
            vol.Required(CONF_OPTION_6, default=data.get(CONF_OPTION_6, False)): bool,  # room temperatur sensor
            vol.Required(CONF_OPTION_7, default=data.get(CONF_OPTION_7, False)): bool,  # write room temperatur sensor
        }
    )


def get_solvis_devices_options(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(DEVICE_VERSION, default=str(SolvisDeviceVersion.SC3)): SolvisVersionSelect,
            vol.Required(POLL_RATE_DEFAULT, default=30): vol.All(vol.Coerce(int), vol.Range(min=2)),
            vol.Required(POLL_RATE_SLOW, default=300): vol.All(vol.Coerce(int), vol.Range(min=10)),
            vol.Required(POLL_RATE_HIGH, default=10): vol.All(vol.Coerce(int), vol.Range(min=10)),
        },
        extra=vol.ALLOW_EXTRA,
    )


def get_host_schema_options(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=data.get(CONF_HOST)): str,
            vol.Required(CONF_PORT, default=data.get(CONF_PORT)): int,
        }
    )


class SolvisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 2
    MINOR_VERSION = 2

    def __init__(self) -> None:
        """Init the ConfigFlow."""
        _LOGGER.info("Initialize config flow for %s", DOMAIN)
        self.data: ConfigType = {}
        self.client = None

    async def async_step_user(self, user_input: ConfigType | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            self.data = user_input
            self._abort_if_unique_id_configured()
            modbussocket = ModbusClient.AsyncModbusTcpClient(host=user_input[CONF_HOST], port=user_input[CONF_PORT])
            try:
                await modbussocket.connect()
                _LOGGER.debug("Connected to Modbus for Solvis")
            except ConnectionException as exc:
                errors["base"] = "cannot_connect"
                errors["device"] = str(exc)
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )

            except ModbusException as exc:
                errors["base"] = "unknown"
                errors["device"] = str(exc)
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )
            except Exception as exc:
                errors["base"] = "unknown"
                errors["device"] = str(exc)
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )
            else:
                try:
                    versionsc = await modbussocket.read_input_registers(address=32770, count=1)
                    versionsc = str(modbussocket.convert_from_registers(versionsc.registers, data_type=modbussocket.DATATYPE.INT16, word_order="big"))
                    versionnbg = await modbussocket.read_input_registers(address=32771, count=1)
                    versionnbg = str(modbussocket.convert_from_registers(versionnbg.registers, data_type=modbussocket.DATATYPE.INT16, word_order="big"))
                except ConnectionException as exc:
                    errors["base"] = "cannot_connect"
                    errors["device"] = str(exc)
                    return self.async_show_form(
                        step_id="user",
                        data_schema=get_host_schema_config(self.data),
                        errors=errors,
                    )
                else:
                    _LOGGER.debug(f"Solvis hardware version: {versionnbg} / Solvis software version: {versionsc}")
                    user_input["VERSIONSC"] = f"{versionsc[0]}.{versionsc[1:3]}.{versionsc[3:5]}"
                    user_input["VERSIONNBG"] = f"{versionnbg[0]}.{versionnbg[1:3]}.{versionnbg[3:5]}"
                    modbussocket.close()
            return await self.async_step_device()

        return self.async_show_form(step_id="user", data_schema=get_host_schema_config(self.data), errors=errors)

    async def async_step_device(self, user_input: ConfigType | None = None) -> FlowResult:
        """Handle the device step."""
        errors = {}
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
            data_schema=get_solvis_devices(self.data),
            errors=errors,
        )

    async def async_step_features(self, user_input: ConfigType | None = None) -> FlowResult:
        """Handle the feature step."""
        if user_input is None:
            return self.async_show_form(step_id="features", data_schema=get_solvis_modules(self.data))
        if self.data[CONF_OPTION_6] is True and self.data[CONF_OPTION_7] is True:
            raise vol.Invalid(cv.string("only_one_temperature_sensor"))
        self.data.update(user_input)
        return self.async_create_entry(title=self.data[CONF_NAME], data=self.data)

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return SolvisOptionsFlow(config_entry)


class SolvisOptionsFlow(config_entries.OptionsFlow):
    VERSION = 2
    MINOR_VERSION = 2

    def __init__(self, config) -> None:
        """Init the ConfigFlow."""
        self.config: ConfigType = config
        self.data = dict(config.data)
        self.client = None

    async def async_step_init(self, user_input: ConfigType | None = None) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        _LOGGER.debug(f"Options flow values_1: {str(self.data)}", DOMAIN)
        if user_input is not None:
            self.data.update(user_input)
            modbussocket: ModbusClient.AsyncModbusTcpClient = ModbusClient.AsyncModbusTcpClient(host=user_input[CONF_HOST], port=user_input[CONF_PORT])
            try:
                await modbussocket.connect()
                _LOGGER.debug("Connected to Modbus for Solvis")
            except ConnectionException as exc:
                errors["base"] = "cannot_connect"
                errors["device"] = str(exc)
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )
            except ModbusException as exc:
                errors["base"] = "unknown"
                errors["device"] = str(exc)
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )
            except Exception as exc:
                errors["base"] = "unknown"
                errors["device"] = str(exc)
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )
            else:
                versionsc = await modbussocket.read_input_registers(address=32770, count=1)
                versionsc = str(modbussocket.convert_from_registers(versionsc.registers, data_type=modbussocket.DATATYPE.INT16, word_order="big"))
                versionnbg = await modbussocket.read_input_registers(address=32771, count=1)
                versionnbg = str(modbussocket.convert_from_registers(versionnbg.registers, data_type=modbussocket.DATATYPE.INT16, word_order="big"))
                user_input["VERSIONSC"] = f"{versionsc[0]}.{versionnbg[1:3]}.{versionsc[3:5]}"
                user_input["VERSIONNBG"] = f"{versionnbg[0]}.{versionnbg[1:3]}.{versionnbg[3:5]}"
                modbussocket.close()
            return await self.async_step_device()

        return self.async_show_form(
            step_id="init",
            data_schema=get_host_schema_options(self.data),
            errors=errors,
        )

    async def async_step_device(self, user_input: ConfigType | None = None) -> FlowResult:
        """Handle the device step."""
        errors = {}
        _LOGGER.debug(f"Options flow values_1: {str(self.data)}", DOMAIN)
        if user_input is not None:
            try:
                self.data.update(user_input)
                validate_poll_rates(self.data)
                return await self.async_step_features()
            except vol.Invalid as exc:
                errors["base"] = str(exc)
                errors["device"] = exc
        return self.async_show_form(
            step_id="device",
            data_schema=get_solvis_devices(self.data),
            errors=errors,
        )

    async def async_step_features(self, user_input: ConfigType | None = None) -> FlowResult:
        """Handle the feature step."""
        _LOGGER.debug(f"Options flow values_2: {str(self.data)}", DOMAIN)
        if user_input is not None:
            if self.data[CONF_OPTION_6] is True and self.data[CONF_OPTION_7] is True:
                raise vol.Invalid(cv.string("only_one_temperature_sensor"))
            self.data.update(user_input)
            self.hass.config_entries.async_update_entry(self.config, data=self.data)
            return self.async_create_entry(title=self.data[CONF_NAME], data=self.data)
        return self.async_show_form(step_id="features", data_schema=get_solvis_modules_options(self.data))
