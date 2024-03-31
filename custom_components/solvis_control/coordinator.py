"""Solvis Modbus Data Coordinator"""

from datetime import timedelta
import logging

from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from pymodbus import ModbusException
import pymodbus.client as ModbusClient
from pymodbus.exceptions import ConnectionException
from pymodbus.payload import BinaryPayloadDecoder, Endian

from .const import DOMAIN, REGISTERS

_LOGGER = logging.getLogger(__name__)


class SolvisModbusCoordinator(DataUpdateCoordinator):
    """My custom coordinator."""

    def __init__(self, hass, conf_host, conf_port):
        """Initialize my coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            # Name of the data. For logging purposes.
            name=DOMAIN,
            # Polling interval. Will only be polled if there are subscribers.
            update_interval=timedelta(seconds=5),
        )
        self.logger.debug("Creating client")
        self.modbus = ModbusClient.AsyncModbusTcpClient(conf_host, conf_port)

    async def _async_update_data(self):
        """Fetch data from API endpoint.

        This is the place to pre-process the data to lookup tables
        so entities can quickly look up their data.
        """
        self.logger.debug("Polling data")

        parsed_data: dict = {}
        try:
            await self.modbus.connect()
        except ConnectionException:
            self.logger.warning("Couldn't connect to device")
        if self.modbus.connected:
            for register in REGISTERS:
                result = await self.modbus.read_holding_registers(register, 1, 1)
                d = BinaryPayloadDecoder.fromRegisters(result.registers, byteorder=Endian.BIG)
                parsed_data[register.name] = round(d.decode_16bit_int() * register.multiplier, 2)
        await self.modbus.close()

        # Pass data back to sensors
        return parsed_data
