"""
Solvis Modbus Data Coordinator

Version: v2.0.0-beta.1
"""

import logging
import struct
from datetime import timedelta

import pymodbus
from pymodbus.client import AsyncModbusTcpClient
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from homeassistant.helpers import entity_registry as er
from pymodbus.exceptions import ConnectionException, ModbusException

from .const import (
    CONF_HOST,
    CONF_PORT,
    DOMAIN,
    DEVICE_VERSION,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
    CONF_OPTION_5,
    CONF_OPTION_6,
    CONF_OPTION_7,
    CONF_OPTION_8,
    POLL_RATE_SLOW,
    POLL_RATE_DEFAULT,
    POLL_RATE_HIGH,
)
from .const import REGISTERS
from .utils.helpers import conf_options_map_coordinator, should_skip_register

_LOGGER = logging.getLogger(__name__)


class SolvisModbusCoordinator(DataUpdateCoordinator):
    """Coordinates data updates from a Solvis device via Modbus."""

    def __init__(self, hass, entry):
        """Initializes the Solvis Modbus data coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.data.get(POLL_RATE_HIGH)),
        )
        self.config_entry = entry  # !
        self.host = entry.data.get(CONF_HOST)
        self.port = entry.data.get(CONF_PORT)
        self.option_hkr2 = entry.data.get(CONF_OPTION_1)
        self.option_hkr3 = entry.data.get(CONF_OPTION_2)
        self.option_solar = entry.data.get(CONF_OPTION_3)
        self.option_heatpump = entry.data.get(CONF_OPTION_4)
        self.option_heatmeter = entry.data.get(CONF_OPTION_5)
        self.option_room_temperature_sensor = entry.data.get(CONF_OPTION_6)
        self.option_write_temperature_sensor = entry.data.get(CONF_OPTION_7)
        self.option_pv2heat = entry.data.get(CONF_OPTION_8)
        self.supported_version = entry.data.get(DEVICE_VERSION)
        self.poll_rate_default = entry.data.get(POLL_RATE_DEFAULT)
        self.poll_rate_slow = entry.data.get(POLL_RATE_SLOW)
        self.poll_rate_high = entry.data.get(POLL_RATE_HIGH)

        _LOGGER.debug("Creating Modbus client")
        self.modbus = entry.runtime_data["modbus"]

    async def _async_update_data(self):
        """Fetches and processes data from the Solvis device."""

        _LOGGER.debug("Polling data...")
        parsed_data = {}

        try:
            if not self.modbus.connected:
                await self.modbus.connect()
            _LOGGER.debug("Connected to Modbus for Solvis")  # Moved here for better context

            for register in REGISTERS:
                _LOGGER.debug(f"[{register.name} | {register.address}] Checking...")

                if should_skip_register(self.config_entry.data, register):
                    _LOGGER.debug(f"[{register.name} | {register.address}] Skipping register based on configuration and device version.")
                    continue

                # Calculation for passing entites, which are in SLOW_POLL_GROUP or STANDARD_POLL_GROUP
                if register.poll_rate == 1:  # SLOW_POLL_GROUP
                    if register.poll_time > 0:
                        register.poll_time -= self.poll_rate_high  # formerly: self.poll_rate_default
                        _LOGGER.debug(f"[{register.name} | {register.address}] Skipping entity due to slow poll rate. Remaining time: {register.poll_time}s")
                        continue
                    else:  # register.poll_time <= 0:
                        register.poll_time = self.poll_rate_slow

                elif register.poll_rate == 0:  # DEFAULT_POLL_GROUP
                    if register.poll_time > 0:
                        register.poll_time -= self.poll_rate_high
                        _LOGGER.debug(f"[{register.name} | {register.address}] Skipping entity due to standard poll rate. Remaining time: {register.poll_time}s")
                        continue
                    else:  # if register.poll_time <= 0:
                        register.poll_time = self.poll_rate_default

                entity_id = f"{DOMAIN}.{register.name}"
                entity_registry = er.async_get(self.hass)
                entity_entry = entity_registry.entities.get(entity_id)

                if entity_entry and entity_entry.disabled:
                    _LOGGER.debug(f"[{register.name} | {register.address}] Skipping disabled entity")
                    continue

                try:
                    if register.register == 1:  # read input registers
                        result = await self.modbus.read_input_registers(address=register.address, count=1)
                        _LOGGER.debug(f"[{register.name} | {register.address}] Reading input register")

                    else:  # read holding registers
                        result = await self.modbus.read_holding_registers(address=register.address, count=1)
                        _LOGGER.debug(f"[{register.name} | {register.address}] Reading holding register")

                    if isinstance(result, pymodbus.pdu.ExceptionResponse):  # better type checking
                        _LOGGER.error(f"[{register.name} | {register.address}] Modbus error while reading register: {result}")
                        continue

                    if not result or not hasattr(result, "registers") or not result.registers:  # additionally check for invalid results
                        _LOGGER.error(f"[{register.name} | {register.address}] Invalid Modbus response: {result}")
                        continue

                    try:
                        data_from_register = self.modbus.convert_from_registers(registers=result.registers, data_type=self.modbus.DATATYPE.INT16, word_order="big")

                        if register.byte_swap == 1:  # little endian
                            _LOGGER.debug(f"[{register.name} | {register.address}] Converting to Little Endian: {data_from_register}")
                            data_from_register = struct.unpack("<h", struct.pack(">h", data_from_register))[0]

                        _LOGGER.debug(f"[{register.name} | {register.address}] Raw value: {data_from_register}")

                        value = round(data_from_register * register.multiplier, 2)
                        parsed_data[register.name] = abs(value) if register.absolute_value else value

                    except (struct.error, ValueError) as err:
                        _LOGGER.error(f"[{register.name} | {register.address}] Data conversion error: {err}")
                        parsed_data[register.name] = -300

                except ModbusException as error:
                    _LOGGER.error(f"[{register.name} | {register.address}] Modbus error while reading register: {error}")

        except ConnectionException:
            _LOGGER.warning("Couldn't connect to Solvis device.")

        finally:
            try:
                self.modbus.close()
                _LOGGER.debug("Modbus for Solvis disconnected.")

            except Exception as e:
                _LOGGER.error(f"Error while closing modbus: {e}")

        _LOGGER.debug(f"Parsed data keys: {list(parsed_data.keys())}")
        _LOGGER.debug(f"Returned data: {parsed_data}")

        return parsed_data
