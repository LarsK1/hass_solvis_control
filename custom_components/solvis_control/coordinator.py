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
    ):
        """Initializes the Solvis Modbus data coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=30),
        )
        self.host = host
        self.port = port
        self.option_hkr2 = option_hkr2
        self.option_hkr3 = option_hkr3
        self.option_solar = option_solar
        self.option_heatpump = option_heatpump
        self.supported_version = supported_version

        _LOGGER.debug("Creating Modbus client")
        self.modbus = ModbusClient.AsyncModbusTcpClient(host=host, port=port)

    async def _async_update_data(self):
        """Fetches and processes data from the Solvis device."""

        _LOGGER.debug("Polling data")
        parsed_data = {}

        try:
            await self.modbus.connect()
            _LOGGER.debug(
                "Connected to Modbus for Solvis"
            )  # Moved here for better context

            for register in REGISTERS:
                if not self.option_hkr2 and register.conf_option == 1:
                    continue
                if not self.option_hkr3 and register.conf_option == 2:
                    continue
                if not self.option_solar and register.conf_option == 3:
                    continue
                if not self.option_heatpump and register.conf_option == 4:
                    continue
                if self.supported_version == 1 and register.supported_version == 2:
                    continue
                elif self.supported_version == 2 and register.supported_version == 1:
                    continue

                entity_id = f"{DOMAIN}.{register.name}"
                entity_entry = self.hass.data["entity_registry"].async_get(entity_id)
                if entity_entry and entity_entry.disabled:
                    _LOGGER.debug(f"Skipping disabled entity: {entity_id}")
                    continue
                try:
                    if register.register == 1:
                        result = await self.modbus.read_input_registers(
                            register.address, 1, 1
                        )
                        _LOGGER.debug(f"Reading input register {register.name}")
                    else:
                        result = await self.modbus.read_holding_registers(
                            register.address, 1, 1
                        )
                        _LOGGER.debug(
                            f"Reading holding register {register.name}/{register.address}"
                        )

                    decoder = BinaryPayloadDecoder.fromRegisters(
                        result.registers, byteorder=Endian.BIG
                    )
                    try:
                        value = round(
                            decoder.decode_16bit_int() * register.multiplier, 2
                        )
                    except struct.error:
                        parsed_data[register.name] = -300
                    else:
                        parsed_data[register.name] = (
                            abs(value) if register.absolute_value else value
                        )

                except ModbusException as error:
                    _LOGGER.error(
                        f"Modbus error reading register {register.name}: {error}"
                    )

        except ConnectionException:
            _LOGGER.warning("Couldn't connect to Solvis device")
        finally:
            self.modbus.close()
        _LOGGER.debug(f"Returned data: {parsed_data}")
        return parsed_data
