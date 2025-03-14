"""Fixtures for testing."""

import pytest
import logging

from unittest.mock import AsyncMock, patch, MagicMock
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException
from scapy.all import ARP, Ether
from custom_components.solvis_control.coordinator import SolvisModbusCoordinator
from homeassistant.core import HomeAssistant
from datetime import timedelta
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
    logger.setLevel(logging.DEBUG)


@pytest.fixture
def mock_get_mac(mocker, request):

    param = getattr(request, "param", {})
    patch_target = param.get("_patch", "config_flow")
    mac_value = param.get("mac", "00:11:22:33:44:55")

    patch_paths = {
        "config_flow": "custom_components.solvis_control.config_flow.get_mac",
        "helpers": "custom_components.solvis_control.utils.helpers.get_mac",
    }

    return mocker.patch(patch_paths[patch_target], return_value=mac_value)


@pytest.fixture(scope="session")
def patch_modbus_client():

    def mock_modbus_factory(host="127.0.0.1", port=502):
        mock_modbus_client = AsyncMock(spec=AsyncModbusTcpClient)
        mock_modbus_client.host = host
        mock_modbus_client.port = port
        mock_modbus_client.connect.return_value = True  # None
        mock_modbus_client.connected = True
        mock_modbus_client.close.return_value = True  # None
        mock_modbus_client.DATATYPE = type("DATATYPE", (), {"INT16": "int16"})

        async def mock_read_registers(address, count):
            response_mock = AsyncMock()
            response_mock.registers = {32770: [12345], 32771: [56789]}.get(address, [10001])
            return response_mock

        mock_modbus_client.read_input_registers.side_effect = mock_read_registers
        mock_modbus_client.read_holding_registers.side_effect = mock_read_registers
        mock_modbus_client.convert_from_registers.side_effect = lambda registers, data_type, word_order: registers[0]

        def set_mock_behavior(fail_connect=False, fail_read=False):
            if fail_connect:
                mock_modbus_client.connect.side_effect = ConnectionException("Connection failed")
            else:
                mock_modbus_client.connect.side_effect = None

            if fail_read:
                mock_modbus_client.read_input_registers.side_effect = ConnectionException("Read failed")
                mock_modbus_client.read_holding_registers.side_effect = ConnectionException("Read failed")
            else:
                mock_modbus_client.read_input_registers.side_effect = mock_read_registers
                mock_modbus_client.read_holding_registers.side_effect = mock_read_registers

        mock_modbus_client.set_mock_behavior = set_mock_behavior

        @property
        def connected():
            return True

        mock_modbus_client.connected = connected

        return mock_modbus_client

    return mock_modbus_factory


@pytest.fixture(autouse=True)
def patch_modbus(mocker, patch_modbus_client):

    mock_client_instance = patch_modbus_client("127.0.0.1", 502)

    patch_targets = [
        "pymodbus.client.AsyncModbusTcpClient",
        "custom_components.solvis_control.utils.helpers.ModbusClient.AsyncModbusTcpClient",
        "custom_components.solvis_control.config_flow.ModbusClient.AsyncModbusTcpClient",
        # "custom_components.solvis_control.__init__.AsyncModbusTcpClient",
    ]

    for target in patch_targets:
        # mocker.patch(target, side_effect=lambda host, port: patch_modbus_client(host, port))
        mocker.patch(target, return_value=mock_client_instance)

    # neu
    _LOGGER = logging.getLogger("custom_components.solvis_control.coordinator")

    # neu
    def mock_init(self, hass, entry):
        super(SolvisModbusCoordinator, self).__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=entry.data.get(POLL_RATE_HIGH)),
        )
        self.config_entry = entry
        self.hass = hass
        self.modbus = mock_client_instance
        self.host = entry.data.get(CONF_HOST, "127.0.0.1")
        self.port = entry.data.get(CONF_PORT, 502)
        self.option_hkr2 = entry.data.get(CONF_OPTION_1, False)
        self.option_hkr3 = entry.data.get(CONF_OPTION_2, False)
        self.option_solar = entry.data.get(CONF_OPTION_3, False)
        self.option_heatpump = entry.data.get(CONF_OPTION_4, False)
        self.option_heatmeter = entry.data.get(CONF_OPTION_5, False)
        self.option_room_temperature_sensor = entry.data.get(CONF_OPTION_6, False)
        self.option_write_temperature_sensor = entry.data.get(CONF_OPTION_7, False)
        self.option_pv2heat = entry.data.get(CONF_OPTION_8, False)
        self.supported_version = entry.data.get(DEVICE_VERSION, 1)
        self.poll_rate_default = entry.data.get(POLL_RATE_DEFAULT, 10)
        self.poll_rate_slow = entry.data.get(POLL_RATE_SLOW, 30)
        self.poll_rate_high = entry.data.get(POLL_RATE_HIGH, 5)

    mocker.patch("custom_components.solvis_control.coordinator.SolvisModbusCoordinator.__init__", mock_init)


@pytest.fixture
def mock_modbus(request, patch_modbus_client):

    if patch_modbus_client is None:
        raise RuntimeError("patch_modbus_client was not initialized properly")

    param = getattr(request, "param", {})

    mock_modbus_client = patch_modbus_client("127.0.0.1", 502)

    async def mock_read_registers(address, count):
        if param.get("fail_read", False):
            raise ConnectionException("Read failed")
        response_mock = AsyncMock()
        response_mock.registers = param.get(str(address), [10001])
        return response_mock

    mock_modbus_client.read_input_registers.side_effect = mock_read_registers
    mock_modbus_client.read_holding_registers.side_effect = mock_read_registers

    if param.get("fail_connect", False):
        mock_modbus_client.connect.side_effect = ConnectionException("Connection failed")

    return mock_modbus_client
