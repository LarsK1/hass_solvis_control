"""
Diagnostics support for Solvis Device.

Version: v2.1.3
"""

import asyncio
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from pymodbus.exceptions import ModbusException, ConnectionException
from custom_components.solvis_control.const import REGISTERS

import pymodbus.client as ModbusClient

AsyncModbusTcpClient = ModbusClient.AsyncModbusTcpClient

REGISTER_TYPE_INPUT = "input"
REGISTER_TYPE_HOLDING = "holding"
REGISTER_TYPE_BOTH = "both"


def convert_formats(raw_uint16: int) -> dict[str, Any]:
    """Convert a 16-bit register value into common representations."""
    value_int16 = raw_uint16 if raw_uint16 < 32768 else raw_uint16 - 65536

    return {
        "raw_uint16": raw_uint16,
        "int16": value_int16,
        "factor10": value_int16 / 10.0,
        "hex": f"0x{raw_uint16:04X}",
        "binary": f"{raw_uint16:016b}",
    }


async def _read_registers(
    client: AsyncModbusTcpClient,
    register_type: str,
    address: int,
    count: int,
    slave_id: int,
):
    """Read input or holding registers from the Modbus client."""
    if register_type == REGISTER_TYPE_INPUT:
        return await client.read_input_registers(address=address, count=count, slave=slave_id)

    return await client.read_holding_registers(address=address, count=count, slave=slave_id)


def _append_scan_results(
    results: list[dict[str, Any]],
    register_type: str,
    address: int,
    values: list[int],
) -> None:
    """Append successfully read register values to the scan response."""
    for offset, raw_value in enumerate(values):
        results.append(
            {
                "register": address + offset,
                "type": register_type,
                **convert_formats(raw_value),
            }
        )


async def scan_modbus_range(
    host: str,
    port: int,
    start_address: int,
    end_address: int,
    register_type: str = REGISTER_TYPE_BOTH,
    slave_id: int = 1,
    delay: float = 0.05,
    batch_size: int = 20,
) -> dict[str, Any]:
    """Scan a Modbus register range with batched reads and per-register fallback."""
    if end_address < start_address:
        raise ValueError("end_address must be greater than or equal to start_address")

    register_types = []
    if register_type in (REGISTER_TYPE_INPUT, REGISTER_TYPE_BOTH):
        register_types.append(REGISTER_TYPE_INPUT)
    if register_type in (REGISTER_TYPE_HOLDING, REGISTER_TYPE_BOTH):
        register_types.append(REGISTER_TYPE_HOLDING)

    results: dict[str, Any] = {
        "host": host,
        "port": port,
        "slave_id": slave_id,
        "start_address": start_address,
        "end_address": end_address,
        "register_type": register_type,
        "batch_size": batch_size,
        "delay": delay,
        "results": [],
        "errors": [],
    }

    async with AsyncModbusTcpClient(
        host=host,
        port=port,
        timeout=5.0,
        retries=3,
        reconnect_delay=1.0,
        reconnect_delay_max=10.0,
    ) as client:
        for current_type in register_types:
            address = start_address

            while address <= end_address:
                count = min(batch_size, end_address - address + 1)

                try:
                    response = await _read_registers(client, current_type, address, count, slave_id)
                except (ConnectionException, ModbusException) as exc:
                    results["errors"].append(
                        {
                            "type": current_type,
                            "register": address,
                            "count": count,
                            "error": str(exc),
                        }
                    )
                    response = None

                if response and not response.isError():
                    _append_scan_results(results["results"], current_type, address, response.registers)
                else:
                    for single_address in range(address, address + count):
                        try:
                            single_response = await _read_registers(
                                client,
                                current_type,
                                single_address,
                                1,
                                slave_id,
                            )
                        except (ConnectionException, ModbusException) as exc:
                            results["errors"].append(
                                {
                                    "type": current_type,
                                    "register": single_address,
                                    "count": 1,
                                    "error": str(exc),
                                }
                            )
                            single_response = None

                        if single_response and not single_response.isError():
                            _append_scan_results(
                                results["results"],
                                current_type,
                                single_address,
                                single_response.registers,
                            )

                        if delay > 0:
                            await asyncio.sleep(delay)

                if response and not response.isError() and delay > 0:
                    await asyncio.sleep(delay)

                address += count

    return results


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
