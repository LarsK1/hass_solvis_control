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

from .const import CONF_HOST, CONF_NAME, CONF_PORT, DOMAIN

_LOGGER = logging.getLogger(__name__)


def get_host_schema_config(data: ConfigType) -> Schema:
    return vol.Schema(
        {
            vol.Required(CONF_NAME, default="Solvis Heizung"): str,
            vol.Required(CONF_HOST, default=data.get(CONF_HOST)): str,
            vol.Required(CONF_PORT, default=502): int,
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
    MINOR_VERSION = 1

    def __init__(self) -> None:
        """Init the ConfigFlow."""
        _LOGGER.info("Initialize config flow for %s", DOMAIN)
        self.data: ConfigType = {}
        self.client = None

    # @staticmethod
    # @callback
    # def async_get_options_flow(
    #     entry: config_entries.ConfigEntry,
    # ) -> config_entries.OptionsFlow:
    #     """Get the options flow for this handler."""
    #     _LOGGER.debug(f'config_flow.py:ConfigFlow.async_get_options_flow: {entry}')
    #     return SolvisOptionsFlow(entry)

    async def async_step_user(
        self, user_input: dict[str, str, int] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=get_host_schema_config(self.data)
            )
        self.data = user_input
        await self.async_set_unique_id(self.data[CONF_HOST], raise_on_progress=False)
        self._abort_if_unique_id_configured()

        return self.async_create_entry(
                    title=self.data[CONF_NAME], data=self.data)
    @staticmethod
    @callback
    def async_get_options_flow(config_entry: config_entries.ConfigEntry,) -> config_entries.OptionsFlow:
        """Create the options flow."""
        return SolvisOptionsFlow(config_entry)

        # TODO: add check for valid data
        # errors = {}
        # try:
        #     self.client = ModbusClient.AsyncModbusTcpClient(
        #         user_input[CONF_HOST], user_input[CONF_PORT]
        #     )
        #     await self.client.connect()
        # except ConnectionException:
        #     errors["base"] = "Es konnte keine Verbinung aufgebaut werden"
        # else:
        #     try:
        #         await self.client.read_coils(32770, 3, slave=1)
        #     except ModbusException as exc:
        #         _LOGGER.debug(f"Received ModbusException({exc}) from library")
        #     else:
        #         await self.client.close()
                
        #     errors["base"] = "cannot_connect"

        # return self.async_show_form(
        #     step_id="user", data_schema=get_host_schema_config(self.data), errors=errors
        # )


class SolvisOptionsFlow(config_entries.OptionsFlow, domain=DOMAIN):
    # The schema version of the entries that it creates
    # Home Assistant will call your migrate method if the version changes
    VERSION = 1
    MINOR_VERSION = 1

    def __init__(self, config) -> None:
        """Init the ConfigFlow."""
        self.data: ConfigType = config
        self.client = None

    async def async_step_init(
        self, user_input: dict[str, int] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=get_host_schema_options(self.data)
            )
        self.data = user_input
        return self.async_create_entry(
                    title=self.data[CONF_NAME], data=self.data
                )
        # errors = {}
        # try:
        #     self.client = ModbusClient.AsyncModbusTcpClient(
        #         user_input[CONF_HOST], user_input[CONF_PORT]
        #     )
        #     await self.client.connect()
        # except ConnectionException:
        #     errors["base"] = "Es konnte keine Verbinung aufgebaut werden"
        # else:
        #     try:
        #         rr = await self.client.read_coils(32770, 3, slave=1)
        #     except ModbusException as exc:
        #         print(f"Received ModbusException({exc}) from library")
        #     finally:
        #         await self.client.close()
        #     errors["base"] = "cannot_connect"

        # return self.async_show_form(
        #     step_id="init", data_schema=self.data_schema, errors=errors
        # )
