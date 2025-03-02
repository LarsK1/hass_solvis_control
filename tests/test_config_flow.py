import pytest
from unittest.mock import AsyncMock
from pymodbus.client import AsyncModbusTcpClient
from pymodbus.exceptions import ConnectionException
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from scapy.all import ARP, Ether

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
    DEVICE_VERSION,
    SolvisDeviceVersion,
)


from voluptuous.error import Invalid


@pytest.fixture
def mock_modbus():
    """Mock for AsyncModbusTcpClient"""
    mock_client = AsyncMock(spec=AsyncModbusTcpClient)
    mock_client.connect.return_value = True  # mock successful connection

    mock_client.DATATYPE = AsyncMock()

    mock_client.DATATYPE.INT16 = "int16"

    # mock different register-readings
    async def mock_read_registers(address, count):
        if address == 32770:
            return AsyncMock(registers=[12345])  # versionsc
        elif address == 32771:
            return AsyncMock(registers=[56789])  # versionnbg
        return AsyncMock(registers=[10001])

    mock_client.read_input_registers.side_effect = mock_read_registers

    # mock convert_from_registers()
    def mock_convert_from_registers(registers, data_type, word_order):
        if data_type == "int16" and word_order == "big":  # Hier direkt "int16" vergleichen
            return str(registers[0])  # Simuliert die echte Umwandlung
        raise ValueError(f"Unexpected parameters for convert_from_registers: {data_type}, {word_order}")

    mock_client.convert_from_registers.side_effect = mock_convert_from_registers

    return mock_client


@pytest.mark.asyncio
async def test_full_flow(hass, mocker, mock_modbus) -> None:
    """Test complete config flow"""

    # mock ModbusClient
    mocker.patch("custom_components.solvis_control.config_flow.ModbusClient.AsyncModbusTcpClient", return_value=mock_modbus)

    # user starts config flow
    mock_result = [([Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst="10.0.0.131", hwsrc="00:11:22:33:44:55")], None)]
    with pytest.patch("custom_components.solvis_control.utils.helpers.srp", return_value=mock_result):
        result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # user input - step "user"
    user_input = {CONF_NAME: "Solvis Heizung Test", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # check if next step "device" is reached
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "device"

    # user input step "device"
    device_input = {
        DEVICE_VERSION: str(SolvisDeviceVersion.SC3),
        POLL_RATE_HIGH: 10,
        POLL_RATE_DEFAULT: 30,
        POLL_RATE_SLOW: 300,
    }

    result = await hass.config_entries.flow.async_configure(result["flow_id"], device_input)

    # check if next step "features" is reached
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "features"

    # user input step "features"
    feature_input = {
        CONF_OPTION_1: False,
        CONF_OPTION_2: False,
        CONF_OPTION_3: False,
        CONF_OPTION_4: False,
        CONF_OPTION_5: False,
        CONF_OPTION_6: False,
        CONF_OPTION_7: False,
    }

    result = await hass.config_entries.flow.async_configure(result["flow_id"], feature_input)

    # check if config entry is created
    assert result["type"] == FlowResultType.CREATE_ENTRY
    assert result["title"] == "Solvis Heizung Test"
    assert result["data"] == {
        **user_input,
        **device_input,
        **feature_input,
        "VERSIONSC": "1.23.45",
        "VERSIONNBG": "5.67.89",
    }


@pytest.mark.asyncio
async def test_invalid_host(hass, mocker) -> None:
    """Test invalid host"""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    # simulate connection issue
    mocker.patch(
        "custom_components.solvis_control.config_flow.ModbusClient.AsyncModbusTcpClient.connect",
        side_effect=ConnectionException("Connection failed"),
    )

    user_input = {CONF_HOST: "10.0.0.999"}
    mock_result = [([Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst="10.0.0.999", hwsrc="00:11:22:33:44:55")], None)]
    with pytest.patch("custom_components.solvis_control.utils.helpers.srp", return_value=mock_result):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"


@pytest.mark.asyncio
async def test_duplicate_entry(hass) -> None:
    """Test existing ConfigEntry"""
    existing_entry = config_entries.ConfigEntry(
        version=1,
        minor_version=0,  # see https://developers.home-assistant.io/blog/2023/12/18/config-entry-minor-version/   required since ha 2024.3+
        domain=DOMAIN,
        title="Test",
        data={CONF_HOST: "10.0.0.131"},
        source=config_entries.SOURCE_USER,
        options={},
        entry_id="1",
        unique_id="test",
    )

    hass.config_entries._async_schedule_save = AsyncMock()
    hass.config_entries._entries = {existing_entry.entry_id: existing_entry}

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    user_input = {CONF_HOST: "10.0.0.131"}
    mock_result = [([Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst="10.0.0.131", hwsrc="00:11:22:33:44:55")], None)]
    with pytest.patch("custom_components.solvis_control.utils.helpers.srp", return_value=mock_result):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.asyncio
async def test_modbus_exception(hass, mocker) -> None:
    """Test Modbus error"""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    assert result["type"] is FlowResultType.FORM

    mocker.patch(
        "custom_components.solvis_control.config_flow.ModbusClient.AsyncModbusTcpClient.connect",
        side_effect=ConnectionException("Connection failed"),
    )

    user_input = {CONF_HOST: "10.0.0.131"}
    mock_result = [([Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst="10.0.0.131", hwsrc="00:11:22:33:44:55")], None)]
    with pytest.patch("custom_components.solvis_control.utils.helpers.srp", return_value=mock_result):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    assert result["errors"]["base"] == "cannot_connect"


@pytest.mark.asyncio
async def test_poll_rate_validation() -> None:
    """Test invalid poll rate config"""
    from custom_components.solvis_control.config_flow import validate_poll_rates

    valid_data = {POLL_RATE_HIGH: 5, POLL_RATE_DEFAULT: 10, POLL_RATE_SLOW: 30}
    invalid_data = {POLL_RATE_HIGH: 10, POLL_RATE_DEFAULT: 15, POLL_RATE_SLOW: 30}
    invalid_data_2 = {POLL_RATE_HIGH: 10, POLL_RATE_DEFAULT: 10, POLL_RATE_SLOW: 10}  # All equal
    invalid_data_3 = {POLL_RATE_HIGH: 15, POLL_RATE_DEFAULT: 5, POLL_RATE_SLOW: 30}  # Wrong order
    invalid_data_4 = {POLL_RATE_HIGH: 3, POLL_RATE_DEFAULT: 5, POLL_RATE_SLOW: 10}  # Non-multiples

    assert validate_poll_rates(valid_data) == valid_data

    with pytest.raises(Invalid):
        validate_poll_rates(invalid_data)
    with pytest.raises(Invalid):
        validate_poll_rates(invalid_data_2)
    with pytest.raises(Invalid):
        validate_poll_rates(invalid_data_3)
    with pytest.raises(Invalid):
        validate_poll_rates(invalid_data_4)


@pytest.mark.asyncio
async def test_conflict_option_6_and_7(hass, mocker, mock_modbus) -> None:
    """Test conflict option 6 and 7"""

    # mock ModbusClient
    mocker.patch("custom_components.solvis_control.config_flow.ModbusClient.AsyncModbusTcpClient", return_value=mock_modbus)

    # user starts config flow
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "user"

    # user input - step "user"
    user_input = {CONF_NAME: "Solvis Heizung Test", CONF_HOST: "10.0.0.131", CONF_PORT: 502}
    mock_result = [([Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst="10.0.0.131", hwsrc="00:11:22:33:44:55")], None)]
    with pytest.patch("custom_components.solvis_control.utils.helpers.srp", return_value=mock_result):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    # check if next step "device" is reached
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "device"

    # user input step "device"
    device_input = {
        DEVICE_VERSION: str(SolvisDeviceVersion.SC3),
        POLL_RATE_HIGH: 10,
        POLL_RATE_DEFAULT: 30,
        POLL_RATE_SLOW: 300,
    }

    result = await hass.config_entries.flow.async_configure(result["flow_id"], device_input)

    # check if next step "features" is reached
    assert result["type"] == FlowResultType.FORM
    assert result["step_id"] == "features"

    conflicting_input = {CONF_OPTION_6: True, CONF_OPTION_7: True}

    result = await hass.config_entries.flow.async_configure(result["flow_id"], conflicting_input)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"]["base"] == "only_one_temperature_sensor"


@pytest.mark.asyncio
async def test_generic_exception(hass, mocker) -> None:
    """Test unexpected error"""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    assert result["type"] is FlowResultType.FORM

    async def mock_async_step_user(self, user_input):
        raise Exception("Unexpected error")
        mocker.patch.object(SolvisConfigFlow, "async_step_user", mock_async_step_user)

    user_input = {CONF_HOST: "10.0.0.131"}
    mock_result = [([Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst="10.0.0.131", hwsrc="00:11:22:33:44:55")], None)]
    with pytest.patch("custom_components.solvis_control.utils.helpers.srp", return_value=mock_result):
        result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"]["base"] == "unknown"


@pytest.mark.asyncio
async def test_user_cancels_flow(hass) -> None:
    """Test flow canceled by user"""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    assert result["type"] is FlowResultType.FORM
    assert "errors" in result
    assert result["step_id"] == "user"

    # user cancels flow (no input, no `async_configure()`)
    hass.config_entries.flow.async_abort(result["flow_id"])
    assert len(hass.config_entries.flow.async_progress()) == 0


@pytest.mark.asyncio
async def test_options_flow(hass) -> None:
    """Test options flow"""

    config_entry = config_entries.ConfigEntry(
        version=1,
        minor_version=0,  # see https://developers.home-assistant.io/blog/2023/12/18/config-entry-minor-version/   required since ha 2024.3+
        domain=DOMAIN,
        title="Test",
        data={CONF_HOST: "10.0.0.131"},
        source=config_entries.SOURCE_USER,
        options={},
        entry_id="1",
        unique_id="test",
    )

    hass.config_entries._entries[config_entry.entry_id] = config_entry

    result = await hass.config_entries.options.async_init(config_entry.entry_id)

    assert result["type"] == FlowResultType.FORM
