"""Solvis Modbus Data Coordinator"""

import logging
import struct
from datetime import timedelta

import pymodbus
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
from pymodbus.client import AsyncModbusTcpClient  # see https://pymodbus.readthedocs.io/en/latest/source/client.html?
from pymodbus.exceptions import ConnectionException, ModbusException

from .const import DOMAIN, REGISTERS
from .utils.helpers import conf_options_map_coordinator

_LOGGER = logging.getLogger(__name__)


class SolvisModbusCoordinator(DataUpdateCoordinator):
    """Coordinates data updates from a Solvis device via Modbus."""

    def __init__(
        self,
        hass,
        host: str,
        port: int,
        supported_version: int,
        option_hkr2: bool,
        option_hkr3: bool,
        option_solar: bool,
        option_heatpump: bool,
        option_heatmeter: bool,
        option_room_temperature_sensor: bool,
        option_write_temperature_sensor: bool,
        poll_rate_default: int,
        poll_rate_slow: int,
        poll_rate_high: int,
    ):
        """Initializes the Solvis Modbus data coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_rate_high),
        )
        self.host = host
        self.port = port
        self.option_hkr2 = option_hkr2
        self.option_hkr3 = option_hkr3
        self.option_solar = option_solar
        self.option_heatpump = option_heatpump
        self.option_heatmeter = option_heatmeter
        self.option_room_temperature_sensor = option_room_temperature_sensor
        self.option_write_temperature_sensor = option_write_temperature_sensor
        self.supported_version = supported_version
        self.poll_rate_default = poll_rate_default
        self.poll_rate_slow = poll_rate_slow
        self.poll_rate_high = poll_rate_high

        _LOGGER.debug("Creating Modbus client")
        self.modbus = AsyncModbusTcpClient(host=host, port=port)

    async def _async_update_data(self):
        """Fetches and processes data from the Solvis device."""

        _LOGGER.debug("Polling data")
        parsed_data = {}

        try:
            if not self.modbus.connected:
                await self.modbus.connect()
            _LOGGER.debug("Connected to Modbus for Solvis")  # Moved here for better context
            for register in REGISTERS:
                _LOGGER.debug(f"Checking register {register.name}/{register.address} - conf_option: {register.conf_option}")
                if isinstance(register.conf_option, tuple):
                    for option in register.conf_option:
                        _LOGGER.debug(f"Checking conf_option: {option} / type: {type(option)}")
                    if not all(getattr(self, conf_options_map_coordinator[int(option)]) for option in register.conf_option):
                        continue
                else:
                    if register.conf_option == 0:
                        pass
                    elif not getattr(self, conf_options_map_coordinator.get(register.conf_option)):
                        continue

                # Device SC3 - entity SC2
                if int(self.supported_version) == 1 and int(register.supported_version) == 2:
                    _LOGGER.debug(f"Supported version: {self.supported_version} / Register version: {register.supported_version}")
                    _LOGGER.debug(f"Skipping SC2 entity for SC3 device: {register.name}/{register.address}")
                    continue
                # Device SC2 - entity SC3
                if int(self.supported_version) == 2 and int(register.supported_version) == 1:
                    _LOGGER.debug(f"Supported version: {self.supported_version} / Register version: {register.supported_version}")
                    _LOGGER.debug(f"Skipping SC3 entity for SC2 device: {register.name}/{register.address}")
                    continue
                # Calculation for passing entites, which are in SLOW_POLL_GROUP or STANDARD_POLL_GROUP
                if register.poll_rate == 1:
                    if register.poll_time > 0:
                        register.poll_time -= self.poll_rate_default
                        _LOGGER.debug(f"Skipping entity {register.name}/{register.address} due to slow poll rate. Remaining time: {register.poll_time}s")
                        continue
                    if register.poll_time <= 0:
                        register.poll_time = self.poll_rate_slow
                elif register.poll_rate == 0:
                    if register.poll_time > 0:
                        register.poll_time -= self.poll_rate_high
                        _LOGGER.debug(f"Skipping entity {register.name}/{register.address} due to standard poll rate. Remaining time: {register.poll_time}s")
                        continue
                    if register.poll_time <= 0:
                        register.poll_time = self.poll_rate_default

                if register.conf_option == 7:
                    _LOGGER.debug("Skipping entity, due to write only attribute (CONF_OPTION_7)")
                    continue
                entity_id = f"{DOMAIN}.{register.name}"
                entity_entry = self.hass.data["entity_registry"].async_get(entity_id)
                if entity_entry and entity_entry.disabled:
                    _LOGGER.debug(f"Skipping disabled entity: {entity_id}")
                    continue
                try:
                    if register.register == 1:  # read input registers
                        result = await self.modbus.read_input_registers(address=register.address, count=1)
                        _LOGGER.debug(f"Reading input register {register.name}/{register.address}")
                    else:  # read holding registers
                        result = await self.modbus.read_holding_registers(address=register.address, count=1)
                        _LOGGER.debug(f"Reading holding register {register.name}/{register.address}")
                    if isinstance(result, pymodbus.pdu.ExceptionResponse):  # better type checking
                        _LOGGER.error(f"Modbus error reading register {register.name}/{register.address}: {result}")
                        continue
                    if not result or not hasattr(result, "registers") or not result.registers:  # additionally check for invalid results
                        _LOGGER.error(f"Invalid Modbus response for register {register.name}/{register.address}: {result}")
                        continue
                    try:
                        data_from_register = self.modbus.convert_from_registers(registers=result.registers, data_type=self.modbus.DATATYPE.INT16, word_order="big")
                        if register.byte_swap == 1:  # little endian
                            data_from_register = struct.unpack("<h", struct.pack(">h", data_from_register))[0]
                        _LOGGER.debug(f"raw value: {data_from_register}")
                        value = round(data_from_register * register.multiplier, 2)
                        parsed_data[register.name] = abs(value) if register.absolute_value else value
                    except (struct.error, ValueError) as err:
                        _LOGGER.error(f"Data conversion error for register {register.name}/{register.address}: {err}")
                        parsed_data[register.name] = -300
                except ModbusException as error:
                    _LOGGER.error(f"Modbus error reading register {register.name}/{register.address}: {error}")
        except ConnectionException:
            _LOGGER.warning("Couldn't connect to Solvis device")
        finally:
            self.modbus.close()
        _LOGGER.debug(f"Returned data: {parsed_data}")
        return parsed_data
