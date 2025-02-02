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
from pymodbus.payload import BinaryPayloadDecoder, Endian
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
    DEVICE_VERSION,
    POLL_RATE_DEFAULT,
    POLL_RATE_SLOW,
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
    if data[POLL_RATE_SLOW] % data[POLL_RATE_DEFAULT] != 0:
        raise vol.Invalid(cv.string("poll_rate_invalid"))
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
        }
    )


def get_solvis_devices(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(DEVICE_VERSION, default=str(SolvisDeviceVersion.SC3)): SolvisVersionSelect,
            vol.Required(POLL_RATE_DEFAULT, default=30): vol.All(vol.Coerce(int), vol.Range(min=30)),
            vol.Required(POLL_RATE_SLOW, default=300): vol.All(vol.Coerce(int), vol.Range(min=60)),
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
        }
    )


def get_solvis_devices_options(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(DEVICE_VERSION, default=str(SolvisDeviceVersion.SC3)): SolvisVersionSelect,
            vol.Required(POLL_RATE_DEFAULT, default=30): vol.All(vol.Coerce(int), vol.Range(min=30)),
            vol.Required(POLL_RATE_SLOW, default=300): vol.All(vol.Coerce(int), vol.Range(min=60)),
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
    MINOR_VERSION = 0

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
                errors["device"] = exc
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )

            except ModbusException as exc:
                errors["base"] = "unknown"
                errors["device"] = exc
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )
            except Exception as exc:
                errors["base"] = "unknown"
                errors["device"] = exc
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )
            else:
                try:
                    versionsc = await modbussocket.read_input_registers(32770, 1, 1)
                    versionsc = str(BinaryPayloadDecoder.fromRegisters(versionsc.registers, byteorder=Endian.BIG).decode_16bit_int())
                    versionnbg = await modbussocket.read_input_registers(32771, 1, 1)
                    versionnbg = str(BinaryPayloadDecoder.fromRegisters(versionnbg.registers, byteorder=Endian.BIG).decode_16bit_int())
                except ConnectionException as exc:
                    errors["base"] = "cannot_connect"
                    errors["device"] = exc
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
    MINOR_VERSION = 0

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
                errors["device"] = exc
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )
            except ModbusException as exc:
                errors["base"] = "unknown"
                errors["device"] = exc
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )
            except Exception as exc:
                errors["base"] = "unknown"
                errors["device"] = exc
                return self.async_show_form(
                    step_id="user",
                    data_schema=get_host_schema_config(self.data),
                    errors=errors,
                )
            else:
                versionsc = await modbussocket.read_input_registers(32770, 1, 1)
                versionsc = str(BinaryPayloadDecoder.fromRegisters(versionsc.registers, byteorder=Endian.BIG).decode_16bit_int())
                versionnbg = await modbussocket.read_input_registers(32771, 1, 1)
                versionnbg = str(BinaryPayloadDecoder.fromRegisters(versionnbg.registers, byteorder=Endian.BIG).decode_16bit_int())
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
            self.data.update(user_input)
            self.hass.config_entries.async_update_entry(self.config, data=self.data)
            return self.async_create_entry(title=self.data[CONF_NAME], data=self.data)
        return self.async_show_form(step_id="features", data_schema=get_solvis_modules_options(self.data))
