"""Solvis Number Sensor."""

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.entity import DeviceInfo
from pymodbus.exceptions import ConnectionException

from custom_components.solvis_control.const import (
    DOMAIN,
    MANUFACTURER,
    DEVICE_VERSION,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
    CONF_OPTION_5,
    CONF_OPTION_6,
    CONF_OPTION_7,
    CONF_OPTION_8,
)
import pymodbus.client as ModbusClient

_LOGGER = logging.getLogger(__name__)


def generate_device_info(entry: ConfigEntry, host: str, name: str) -> DeviceInfo:
    """Generate device info."""
    _LOGGER.debug(f"Generating device info for {host}")
    _LOGGER.debug(f"Entry data: {entry.data}")
    model = {
        1: "Solvis Control 3",
        2: "Solvis Control 2",
    }.get(int(entry.data.get(DEVICE_VERSION)), "Solvis Control (unbekannt)")

    info = {
        "identifiers": {(DOMAIN, host)},
        "name": name,
        "manufacturer": MANUFACTURER,
        "model": model,
    }

    if "VERSIONSC" in entry.data:
        info["sw_version"] = entry.data["VERSIONSC"]
    if "VERSIONNBG" in entry.data:
        info["hw_version"] = entry.data["VERSIONNBG"]

    return DeviceInfo(**info)


async def fetch_modbus_value(register: int, register_type: int, host: str, port: int, datatype="INT16", order="big") -> int:
    modbussocket: ModbusClient.AsyncModbusTcpClient = ModbusClient.AsyncModbusTcpClient(host=host, port=port)
    try:
        await modbussocket.connect()
        _LOGGER.debug("Connected to Modbus for Solvis")
        if register_type == 1:
            data = await modbussocket.read_input_registers(address=register, count=1)
        else:
            data = await modbussocket.read_holding_registers(address=register, count=1)
        modbussocket.close()
        return modbussocket.convert_from_registers(data.registers, data_type=modbussocket.DATATYPE.INT16, word_order=order)
    except ConnectionException:
        raise
    except ModbusException:
        raise
    except:
        raise


conf_options_map = {
    1: CONF_OPTION_1,
    2: CONF_OPTION_2,
    3: CONF_OPTION_3,
    4: CONF_OPTION_4,
    5: CONF_OPTION_5,
    6: CONF_OPTION_6,
    7: CONF_OPTION_7,
    8: CONF_OPTION_8,
}
conf_options_map_coordinator = {
    1: "option_hkr2",
    2: "option_hkr3",
    3: "option_solar",
    4: "option_heatpump",
    5: "option_heatmeter",
    6: "option_room_temperature_sensor",
    7: "option_write_temperature_sensor",
    8: "option_pv2heat",
}
