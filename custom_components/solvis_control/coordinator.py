"""
Solvis Modbus Data Coordinator

Version: v2.1.3
"""

import logging
import struct
from datetime import timedelta
import asyncio

import pymodbus
from pymodbus.client import AsyncModbusTcpClient
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from homeassistant.helpers import entity_registry as er
from homeassistant.exceptions import ConfigEntryNotReady
from pymodbus.exceptions import ConnectionException, ModbusException, ModbusIOException
from .utils.helpers import conf_options_map_coordinator, should_skip_register, ensure_connected
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
    CONF_OPTION_9,
    CONF_OPTION_10,
    CONF_OPTION_11,
    CONF_OPTION_12,
    CONF_OPTION_13,
    POLL_RATE_SLOW,
    POLL_RATE_DEFAULT,
    POLL_RATE_HIGH,
    REGISTERS,
)

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
        self.option_hkr1_room_temperature_sensor = entry.data.get(CONF_OPTION_6)
        self.option_hkr1_write_temperature_sensor = entry.data.get(CONF_OPTION_7)
        self.option_pv2heat = entry.data.get(CONF_OPTION_8)
        self.option_hkr2_room_temperature_sensor = entry.data.get(CONF_OPTION_9)
        self.option_hkr2_write_temperature_sensor = entry.data.get(CONF_OPTION_10)
        self.option_hkr3_room_temperature_sensor = entry.data.get(CONF_OPTION_11)
        self.option_hkr3_write_temperature_sensor = entry.data.get(CONF_OPTION_12)
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

        # SC2-devices: reconnect
        if int(self.supported_version) == 2:
            _LOGGER.debug("SC2-device: Modbus reconnect...")

            try:
                self.modbus.close()
                await asyncio.sleep(0.1)
                connected = await self.modbus.connect()
                await asyncio.sleep(0.1)

                if not connected:
                    raise RuntimeError("Modbus (re)connect failed: connect() returned False")

                _LOGGER.debug("SC2-device: Modbus reconnected")

            except (ConnectionException, ModbusIOException, ModbusException) as err:
                _LOGGER.error("Modbus connect failed: %s", err)
                raise ConfigEntryNotReady("Solvis Control not reachable. Try again later...") from err

        # check connection
        if not await ensure_connected(self.modbus):
            _LOGGER.error("Initial Modbus (re)connect failed, aborting update")
            raise UpdateFailed("Initial Modbus (re)connect failed")

        for register in REGISTERS:
            _LOGGER.debug(f"[{register.name} | {register.address}] Checking...")

            # skip by config or device version
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

            # skip disabled entities
            if entity_entry and entity_entry.disabled:
                _LOGGER.debug(f"[{register.name} | {register.address}] Skipping disabled entity")
                continue

            # check connection / reconnect
            if not await ensure_connected(self.modbus):
                _LOGGER.error(f"[{register.name} | {register.address}] Skipping read: no connection")
                continue

            # READ
            try:
                # read input registers
                if register.register == 1:
                    _LOGGER.debug(f"[{register.name} | {register.address}] Reading input register...")
                    result = await self.modbus.read_input_registers(address=register.address, count=1)

                # read holding registers
                else:
                    _LOGGER.debug(f"[{register.name} | {register.address}] Reading holding register...")
                    result = await self.modbus.read_holding_registers(address=register.address, count=1)

                # slow down on SC2-devices
                if int(self.supported_version) == 2:
                    _LOGGER.debug(f"[{register.name} | {register.address}] Sleep after read (SC2)")
                    await asyncio.sleep(0.3)

            except (ConnectionException, ModbusIOException, ModbusException) as err:
                _LOGGER.error(f"[{register.name} | {register.address}] Exception during read: {err} - skipping read")
                raise UpdateFailed(f"[{register.name} | {register.address}] Exception during read") from err

            # check for error response
            if not result or hasattr(result, "isError") and result.isError():
                _LOGGER.error(f"[{register.name} | {register.address}] Modbus error while reading register: {result}")
                raise UpdateFailed(f"[{register.name} | {register.address}] Modbus error while reading register")

            # check for invalid results
            if not hasattr(result, "registers") or not result.registers:
                _LOGGER.error(f"[{register.name} | {register.address}] Invalid Modbus response: {result}")
                raise UpdateFailed(f"[{register.name} | {register.address}] Invalid Modbus response")

            # conversion
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
                raise UpdateFailed(f"[{register.name} | {register.address}] Data conversion error") from err

        _LOGGER.debug(f"Returned data: {parsed_data}")

        return parsed_data
