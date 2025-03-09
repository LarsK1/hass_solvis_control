"""Fixtures for testing."""

import pytest
import logging

from unittest.mock import AsyncMock, patch, MagicMock
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException
from scapy.all import ARP, Ether
from custom_components.solvis_control.coordinator import SolvisModbusCoordinator
from homeassistant.core import HomeAssistant
from custom_components.solvis_control.const import CONF_HOST, CONF_PORT, POLL_RATE_HIGH


@pytest.fixture
def mock_coordinator(hass: HomeAssistant, mock_modbus):
    entry = MagicMock()
    entry.data = {
        CONF_HOST: "127.0.0.1",
        CONF_PORT: 502,
        POLL_RATE_HIGH: 10,
    }
    entry.runtime_data = {"modbus": mock_modbus}

    coordinator = SolvisModbusCoordinator(hass, entry)
    coordinator.modbus = mock_modbus

    return coordinator


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture(autouse=True)
def configure_logging():
    logger = logging.getLogger()
    logger.setLevel(logging.WARNING)


@pytest.fixture(autouse=True)
def mock_helpers(mocker):
    logging.warning("[DEBUG] Applying mock for get_mac()")

    # Mock for get_mac
    mocker.patch("custom_components.solvis_control.utils.helpers.get_mac", return_value="00:11:22:33:44:55")
    mocker.patch("custom_components.solvis_control.config_flow.get_mac", return_value="00:11:22:33:44:55")

    # Mock for fetch_modbus_value
    mocker.patch("custom_components.solvis_control.utils.helpers.fetch_modbus_value", new_callable=AsyncMock, return_value="12345")

    # ARP-Mock for srp
    mock_arp_response = [(([Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst="10.0.0.131", hwsrc="00:11:22:33:44:55")], None), None)]
    mocker.patch("custom_components.solvis_control.utils.helpers.srp", return_value=(mock_arp_response, None))


@pytest.fixture(autouse=True)
def mock_modbus(mocker):
    """Global Mock for ModbusClient."""
    mock_modbus_client = AsyncMock(spec=AsyncModbusTcpClient)

    mock_modbus_client.connect = AsyncMock(return_value=True)

    mock_modbus_client.close = MagicMock(return_value=True)

    mock_modbus_client.DATATYPE = type("DATATYPE", (), {"INT16": "int16"})

    async def mock_read_registers(address, count):
        response_mock = AsyncMock()
        if address == 32770:
            response_mock.registers = [12345]  # versionsc
        elif address == 32771:
            response_mock.registers = [56789]  # versionnbg
        else:
            response_mock.registers = [10001]
        return response_mock

    mock_modbus_client.read_input_registers = AsyncMock(side_effect=mock_read_registers)

    def mock_convert_from_registers(registers, data_type, word_order):
        if data_type == "int16" and word_order == "big":
            return str(registers[0])
        raise ValueError(f"Invalid conversion params: {data_type}, {word_order}")

    mock_modbus_client.convert_from_registers.side_effect = mock_convert_from_registers

    def set_mock_behavior(fail_connect=False, fail_read=False):
        if fail_connect:
            mock_modbus_client.connect.side_effect = ConnectionException("Connection failed")
        else:
            mock_modbus_client.connect.side_effect = None

        if fail_read:
            mock_modbus_client.read_input_registers.side_effect = ConnectionException("Read failed")
        else:
            mock_modbus_client.read_input_registers.side_effect = mock_read_registers

    mock_modbus_client.set_mock_behavior = set_mock_behavior

    # generic
    mocker.patch("pymodbus.client.AsyncModbusTcpClient", return_value=mock_modbus_client)

    # config_flow  # import pymodbus.client as ModbusClient
    mocker.patch("custom_components.solvis_control.config_flow.ModbusClient.AsyncModbusTcpClient", return_value=mock_modbus_client)

    # utils.helpers  # import pymodbus.client as ModbusClient
    mocker.patch("custom_components.solvis_control.utils.helpers.ModbusClient.AsyncModbusTcpClient", return_value=mock_modbus_client)

    # __init__  # from pymodbus.client import AsyncModbusTcpClient | from .coordinator import SolvisModbusCoordinator
    mocker.patch("custom_components.solvis_control.__init__.AsyncModbusTcpClient", return_value=mock_modbus_client)

    # coordinator  # import pymodbus
    mocker.patch("custom_components.solvis_control.coordinator.SolvisModbusCoordinator._async_update_data", new_callable=AsyncMock, return_value={"mocked_data": 123})

    return mock_modbus_client
