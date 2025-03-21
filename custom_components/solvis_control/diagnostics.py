"""
Diagnostics support for Solvis Device.

Version: 1.2.0-alpha11
"""

from typing import Any

import pymodbus.client as ModbusClient
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from pymodbus.exceptions import ModbusException


async def scan_modbus_registers(host: str, port: int, addressrange: range, register_type: int) -> dict[str, Any]:
    """Scan Modbus registers and return their values."""
    result = {}
    client = ModbusClient.AsyncModbusTcpClient(host=host, port=port)
    try:
        await client.connect()
        for register in addressrange:  # range of registers to scan
            if register_type == 1:
                response = await client.read_input_registers(address=register, count=1)
            else:
                response = await client.read_holding_registers(address=register, count=1)
            if response.isError():
                result[f"register_{register}"] = "Error"
            else:
                decoder = client.convert_from_registers(response.registers, data_type=client.DATATYPE.INT16, word_order="big")
                result[f"register_{register}"] = float(decoder)
    except ModbusException as exc:
        result["error"] = str(exc)
    finally:
        client.close()
    return result


async def async_get_config_entry_diagnostics(hass: HomeAssistant, entry: ConfigEntry) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    modbus_data_input = await scan_modbus_registers(entry.data["host"], entry.data["port"], range(2000, 5000), 1)
    modbus_data_input.update(await scan_modbus_registers(entry.data["host"], entry.data["port"], range(32000, 34000), 1))
    modbus_data_holding = await scan_modbus_registers(entry.data["host"], entry.data["port"], range(1000, 4000), 2)
    modbus_data_holding.update(await scan_modbus_registers(entry.data["host"], entry.data["port"], range(34000, 35000), 2))

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
