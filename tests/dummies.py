"""
Dummies for Testing

Version: v2.0.0
"""

import pytest
import asyncio
from unittest.mock import MagicMock
from homeassistant.helpers import entity_registry as er
from custom_components.solvis_control.coordinator import SolvisModbusCoordinator
from pymodbus.exceptions import ConnectionException, ModbusException, ConnectionException
from custom_components.solvis_control.const import (
    DOMAIN,
    CONF_NAME,
    CONF_HOST,
    CONF_PORT,
    POLL_RATE_DEFAULT,
    POLL_RATE_HIGH,
    POLL_RATE_SLOW,
    CONF_OPTION_1,
    CONF_OPTION_2,
    CONF_OPTION_3,
    CONF_OPTION_4,
    CONF_OPTION_5,
    CONF_OPTION_6,
    CONF_OPTION_7,
    CONF_OPTION_8,
    DEVICE_VERSION,
    SolvisDeviceVersion,
)


class DummyConfigEntry:
    def __init__(self, data=None):
        if data is None:
            self.data = {
                CONF_NAME: "TestDevice",
                CONF_HOST: "127.0.0.1",
                CONF_PORT: 502,
                DEVICE_VERSION: 1,
                POLL_RATE_DEFAULT: 30,
                POLL_RATE_SLOW: 300,
                POLL_RATE_HIGH: 10,
                CONF_OPTION_1: True,
                CONF_OPTION_2: True,
                CONF_OPTION_3: True,
                CONF_OPTION_4: True,
                CONF_OPTION_5: True,
                CONF_OPTION_6: True,
                CONF_OPTION_7: True,
                CONF_OPTION_8: True,
            }
        else:
            self.data = data
        self.runtime_data = {}
        self.entry_id = "dummy_entry"
        self.version = 1
        self.minor_version = 0
        self.options = {}


class DummyEntities:
    def __init__(self, entities):
        self._entities = entities

    def __getitem__(self, key):
        return self._entities[key]

    def __iter__(self):
        return iter(self._entities)

    def values(self):
        return self._entities.values()

    def get(self, key):
        return self._entities.get(key)

    def pop(self, key, default=None):
        return self._entities.pop(key, default)


class DummyEntityRegistry:
    def __init__(self, entities=None):
        self.entities = DummyEntities(entities if entities is not None else {})

    async def async_load(self):
        return self

    def async_remove(self, entity_id):
        self.entities.pop(entity_id, None)


class DummyEntity:
    def __init__(self, unique_id, entity_id, config_entry_id="dummy_entry", disabled=False):
        self.unique_id = unique_id
        self.entity_id = entity_id
        self.config_entry_id = config_entry_id
        self.disabled = disabled


class DummyModbusResponse:
    def __init__(self, registers, error=False):
        self.registers = registers
        self._error = error

    def isError(self):
        return self._error


class DummyModbusClient:
    def __init__(
        self, registers=None, write_response=None, connect_success=True, raise_on_connect=False, host="127.0.0.1", port=502, raise_on_close=False, raise_on_write=False, raise_generic_on_write=False
    ):
        self.connected = False
        self.DATATYPE = type("DATATYPE", (), {"INT16": "int16"})
        self.registers = registers if registers is not None else [123]
        self.write_response = write_response
        self.connect_success = connect_success
        self.called_close = False
        self.host = host
        self.port = port
        self.raise_on_connect = raise_on_connect
        self.raise_on_close = raise_on_close
        self.raise_on_write = raise_on_write
        self.raise_generic_on_write = raise_generic_on_write

    async def connect(self):
        if self.raise_on_connect:
            raise ConnectionException(f"Failed to connect to Modbus device at {self.host}:{self.port}")
        if not self.connect_success:
            return False
        self.connected = True
        return True

    async def read_input_registers(self, address, count):
        return DummyModbusResponse(self.registers)

    async def read_holding_registers(self, address, count):
        return DummyModbusResponse(self.registers)

    async def write_register(self, address, value, slave=1):
        if self.raise_generic_on_write:
            raise Exception("Generic error")
        elif self.raise_on_write:
            raise ModbusException("Test modbus error")
        return self.write_response if self.write_response is not None else DummyModbusResponse(self.registers)

    def convert_from_registers(self, registers, data_type, word_order):
        if not registers:
            return None
        return registers[0]

    def close(self):
        self.called_close = True
        self.connected = False
        if self.raise_on_close:
            raise Exception("Close failed")


class DummyResponseObj:
    def __init__(self, hwsrc):
        self.hwsrc = hwsrc


class DummyRegister:
    def __init__(
        self,
        name,
        address,
        conf_option,
        supported_version,
        poll_rate=10,
        poll_time=10,
        reg=1,  # 1: input, else holding
        multiplier=1.0,
        absolute_value=False,
        byte_swap=False,
    ):
        self.name = name
        self.address = address
        self.conf_option = conf_option
        self.supported_version = supported_version
        self.poll_rate = poll_rate
        self.poll_time = poll_time
        self.register = reg
        self.multiplier = multiplier
        self.absolute_value = absolute_value
        self.byte_swap = byte_swap


def dummy_srp(packet, timeout, verbose):
    return [((None, DummyResponseObj("AA:BB:CC:DD:EE:FF")),)]


def dummy_srp_empty(packet, timeout, verbose):
    return []
