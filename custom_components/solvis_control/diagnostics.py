"""
Diagnostics support for Solvis Device.

Version: v2.1.0
"""

from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from pymodbus.exceptions import ModbusException, ConnectionException
from custom_components.solvis_control.const import REGISTERS

import pymodbus.client as ModbusClient

AsyncModbusTcpClient = ModbusClient.AsyncModbusTcpClient


async def scan_modbus_registers(host: str, port: int, register_type: int) -> dict[str, Any]:
    """Scan Modbus registers defined in REGISTERS for the given register type and return their values."""
    addresses = sorted({r.address for r in REGISTERS if r.register == register_type})
    result = {}

    async with AsyncModbusTcpClient(
        host=host,
        port=port,
        timeout=5.0,
        retries=3,
        reconnect_delay=1.0,
        reconnect_delay_max=10.0,
    ) as client:
        for address in addresses:
            try:
                if register_type == 1:
                    response = await client.read_input_registers(address=address, count=1)
                else:
                    response = await client.read_holding_registers(address=address, count=1)
            except ConnectionException as exc:
                result["error"] = str(exc)
                continue

            if not response or response.isError():
                result[f"register_{address}"] = "Error"
            else:
                decoder = client.convert_from_registers(response.registers, data_type=client.DATATYPE.INT16, word_order="big")
                result[f"register_{address}"] = float(decoder)

    return result


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    modbus_data_input = await scan_modbus_registers(entry.data["host"], entry.data["port"], 1)
    modbus_data_holding = await scan_modbus_registers(entry.data["host"], entry.data["port"], 2)

    return {
        "entry_data": entry.data,
        "modbus_data_input": modbus_data_input,
        "modbus_data_holding": modbus_data_holding,
    }


# async def async_get_device_diagnostics(hass: HomeAssistant, entry: ConfigEntry, device: DeviceEntry) -> dict[str, Any]:
#     """Return diagnostics for a device."""
#     appliance = _get_appliance_by_device_id(hass, device.id)
#     return {
#         "details": appliance.raw_data,
#         "data": appliance.data,
#     }
