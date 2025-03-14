"""
Solvis Modbus Data Coordinator

Version: 1.2.0-alpha11
"""

import logging
import struct
from datetime import timedelta

import pymodbus
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator
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
from .utils.helpers import conf_options_map_coordinator

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

        _LOGGER.debug(f"Modbus-Client Typ: {type(self.modbus)}")  # Prüfen, ob es ein Mock ist
        _LOGGER.debug(f"Modbus-Client Methoden: {dir(self.modbus)}")

        _LOGGER.debug("Polling data")
        parsed_data = {}

        try:
            if not self.modbus.connected:
                _LOGGER.debug(f"Type of modbus client: {type(self.modbus)}")
                await self.modbus.connect()
            _LOGGER.debug("Connected to Modbus for Solvis")  # Moved here for better context
            for register in REGISTERS:
                _LOGGER.debug(f"Checking register {register.name}/{register.address} - conf_option: {register.conf_option}")

                if isinstance(register.conf_option, tuple):
                    for option in register.conf_option:
                        _LOGGER.debug(f"[{register.name}] Checking conf_option: {option} / type: {type(option)}")

                    all_options_enabled = all(getattr(self, conf_options_map_coordinator[int(option)], None) for option in register.conf_option)
                    if not all_options_enabled:
                        _LOGGER.debug(f"[{register.name}] Skipping register because not all conf_options are enabled: {register.conf_option}")
                        continue
                else:
                    _LOGGER.debug(f"[{register.name}] Single conf_option detected: {register.conf_option} / type: {type(register.conf_option)}")

                    if register.conf_option in (0, 7):
                        _LOGGER.debug(f"[{register.name}] conf_option {register.conf_option} allows processing. Continuing...")
                        pass
                    else:
                        conf_option_value = getattr(self, conf_options_map_coordinator.get(register.conf_option), None)
                        _LOGGER.debug(f"[{register.name}] Retrieved conf_option value: {conf_option_value}")

                        if not conf_option_value:
                            _LOGGER.debug(f"[{register.name}] Skipping register because conf_option {register.conf_option} is not enabled.")
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
                if register.poll_rate == 1:  # SLOW_POLL_GROUP
                    if register.poll_time > 0:
                        register.poll_time -= self.poll_rate_high  # formerly: self.poll_rate_default
                        _LOGGER.debug(f"Skipping entity {register.name}/{register.address} due to slow poll rate. Remaining time: {register.poll_time}s")
                        continue
                    if register.poll_time <= 0:
                        register.poll_time = self.poll_rate_slow

                elif register.poll_rate == 0:  # DEFAULT_POLL_GROUP
                    if register.poll_time > 0:
                        register.poll_time -= self.poll_rate_high
                        _LOGGER.debug(f"Skipping entity {register.name}/{register.address} due to standard poll rate. Remaining time: {register.poll_time}s")
                        continue
                    if register.poll_time <= 0:
                        register.poll_time = self.poll_rate_default

                # no special treat for treat conf_option 7 necessary
                # if register.conf_option == 7:
                #     _LOGGER.debug("Skipping entity, due to write only attribute (CONF_OPTION_7)")
                #     continue

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
