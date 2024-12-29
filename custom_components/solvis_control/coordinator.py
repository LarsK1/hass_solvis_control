"""Solvis Modbus Data Coordinator"""

import struct
from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

import pymodbus.client as ModbusClient
from pymodbus.exceptions import ConnectionException, ModbusException
from pymodbus.payload import BinaryPayloadDecoder, Endian

from .const import DOMAIN, REGISTERS

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
        poll_rate_default: int,
        poll_rate_slow: int,
    ):
        """Initializes the Solvis Modbus data coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=poll_rate_default),
        )
        self.host = host
        self.port = port
        self.option_hkr2 = option_hkr2
        self.option_hkr3 = option_hkr3
        self.option_solar = option_solar
        self.option_heatpump = option_heatpump
        self.supported_version = supported_version
        self.poll_rate_default = poll_rate_default
        self.poll_rate_slow = poll_rate_slow

        _LOGGER.debug("Creating Modbus client")
        self.modbus = ModbusClient.AsyncModbusTcpClient(host=host, port=port)

    async def _async_update_data(self):
        """Fetches and processes data from the Solvis device."""

        _LOGGER.debug("Polling data")
        parsed_data = {}

        try:
            await self.modbus.connect()
            _LOGGER.debug("Connected to Modbus for Solvis")  # Moved here for better context

            for register in REGISTERS:
                if not self.option_hkr2 and register.conf_option == 1:
                    continue
                if not self.option_hkr3 and register.conf_option == 2:
                    continue
                if not self.option_solar and register.conf_option == 3:
                    continue
                if not self.option_heatpump and register.conf_option == 4:
                    continue
                # Deivce SC3 - entity SC2
                if self.supported_version == 1 and register.supported_version == 2:
                    continue
                # Device SC2 - entity SC3
                elif self.supported_version == 2 and register.supported_version == 1:
                    continue

                # Calculation for passing entites, which are in SLOW_POLL_GOUP
                if register.poll_rate:
                    if register.poll_time > 0:
                        register.poll_time -= self.poll_rate_default
                        _LOGGER.debug(f"Skipping entity {register.name}/{register.address} due to slow poll rate. Remaining time: {register.poll_time}s")
                        continue
                    if register.poll_time <= 0:
                        register.poll_time = self.poll_rate_slow

                entity_id = f"{DOMAIN}.{register.name}"
                entity_entry = self.hass.data["entity_registry"].async_get(entity_id)
                if entity_entry and entity_entry.disabled:
                    _LOGGER.debug(f"Skipping disabled entity: {entity_id}")
                    continue
                try:
                    if register.register == 1:

                        result = await self.modbus.read_input_registers(register.address, 1, 1)
                        _LOGGER.debug(f"Reading input register {register.name}")
                    else:
                        result = await self.modbus.read_holding_registers(register.address, 1, 1)
                        _LOGGER.debug(f"Reading holding register {register.name}/{register.address}")

                    decoder = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG)
                    try:
                        rawvalue = decoder.decode_16bit_int()
                        _LOGGER.debug(f"Decoded raw value: {rawvalue}")
                        value = round(rawvalue * register.multiplier, 2)
                    except struct.error:
                        parsed_data[register.name] = -300
                    else:
                        parsed_data[register.name] = abs(value) if register.absolute_value else value

                except ModbusException as error:
                    _LOGGER.error(f"Modbus error reading register {register.name}: {error}")

        except ConnectionException:
            _LOGGER.warning("Couldn't connect to Solvis device")
        finally:
            self.modbus.close()
        _LOGGER.debug(f"Returned data: {parsed_data}")
        return parsed_data
