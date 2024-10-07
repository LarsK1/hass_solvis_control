import logging

from pymodbus import ModbusException
import pymodbus.client as ModbusClient
from pymodbus.exceptions import ConnectionException
import voluptuous as vol
from voluptuous.schema_builder import Schema

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.typing import ConfigType

from .const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PORT,
    DOMAIN,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
)

_LOGGER = logging.getLogger(__name__)


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


def get_solvis_modules_options(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(CONF_OPTION_1, default=data.get(CONF_OPTION_1)): bool,  # HKR 2
            vol.Required(CONF_OPTION_2, default=data.get(CONF_OPTION_2)): bool,  # HKR 3
            vol.Required(
                CONF_OPTION_3, default=data.get(CONF_OPTION_3)
            ): bool,  # solar collectors
            vol.Required(
                CONF_OPTION_4, default=data.get(CONF_OPTION_4)
            ): bool,  # heat pump
        }
    )


def get_host_schema_options(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(CONF_HOST, default=data.get(CONF_HOST)): str,
            vol.Required(CONF_PORT, default=data.get(CONF_PORT)): int,
        }
    )


class SolvisConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    VERSION = 1
    MINOR_VERSION = 2

    def __init__(self) -> None:
        """Init the ConfigFlow."""
        _LOGGER.info("Initialize config flow for %s", DOMAIN)
        self.data: ConfigType = {}
        self.client = None

    async def async_step_user(
        self, user_input: dict[str, str, int] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            self.data = user_input
            # try:
            #     self.client = ModbusClient.AsyncModbusTcpClient(
            #         user_input[CONF_HOST], user_input[CONF_PORT]
            #     )
            #     await self.client.connect()
            #     # Perform a simple read to check the connection
            #     await self.client.read_holding_registers(2818, 1, 1)
            # except (ConnectionException, ModbusException) as exc:
            #     _LOGGER.error(f"Modbus connection failed: {exc}")
            #     errors["base"] = "cannot_connect"
            # else:
            #     await self.client.close()
            #     await self.async_set_unique_id(
            #         self.data[CONF_HOST], raise_on_progress=False
            #     )
            self._abort_if_unique_id_configured()
            return await self.async_step_features()

        return self.async_show_form(
            step_id="user", data_schema=get_host_schema_config(self.data), errors=errors
        )

    async def async_step_features(
        self, user_input: dict[bool, bool, bool] | None = None
    ) -> FlowResult:
        """Handle the feature step."""
        if user_input is None:
            return self.async_show_form(
                step_id="features", data_schema=get_solvis_modules(self.data)
            )
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
    VERSION = 1
    MINOR_VERSION = 2

    def __init__(self, config) -> None:
        """Init the ConfigFlow."""
        self.config: ConfigType = config
        self.data = dict(config.data)
        self.client = None

    async def async_step_init(
        self, user_input: dict[str, int] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            self.data = user_input
            # try:
            #     self.client = ModbusClient.AsyncModbusTcpClient(
            #         user_input[CONF_HOST], user_input[CONF_PORT]
            #     )
            #     await self.client.connect()
            #     # Perform a simple read to check the connection
            #     await self.client.read_holding_registers(2818, 1, 1)
            # except (ConnectionException, ModbusException) as exc:
            #     _LOGGER.error(f"Modbus connection failed: {exc}")
            #     errors["base"] = "cannot_connect"
            # else:
            #     await self.client.close()
            return await self.async_step_features()

        return self.async_show_form(
            step_id="init",
            data_schema=get_host_schema_options(self.data),
            errors=errors,
        )

    async def async_step_features(
        self, user_input: dict[bool, bool, bool] | None = None
    ) -> FlowResult:
        """Handle the feature step."""
        if user_input is None:
            return self.async_show_form(
                step_id="features", data_schema=get_solvis_modules_options(self.data)
            )
        self.data.update(user_input)
        return self.async_create_entry(title=self.config.get(CONF_NAME), data=self.data)
