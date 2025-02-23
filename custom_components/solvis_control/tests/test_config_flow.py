import pytest
from unittest.mock import AsyncMock
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType

from custom_components.solvis_control.const import (
    DOMAIN,
    CONF_HOST,
    POLL_RATE_DEFAULT,
    POLL_RATE_HIGH,
    POLL_RATE_SLOW,
    CONF_OPTION_6,
    CONF_OPTION_7,
)
from custom_components.solvis_control.config_flow import SolvisConfigFlow
from voluptuous.error import Invalid


@pytest.mark.asyncio
async def test_full_flow(hass: HomeAssistant) -> None:
    """ Test: complete config flow """
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    user_input = {CONF_HOST: "10.0.0.131"}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Solvis Heizung"
    assert result["data"] == user_input


@pytest.mark.asyncio
async def test_invalid_host(hass: HomeAssistant, mocker) -> None:
    """ Test: invalid Host """
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    # simulate connection issue
    mocker.patch(
        "custom_components.solvis_control.config_flow.ModbusClient.AsyncModbusTcpClient.connect",
        side_effect=Exception("Connection failed"),
    )

    user_input = {CONF_HOST: "10.0.0.999"}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"]["base"] == "cannot_connect"


@pytest.mark.asyncio
async def test_duplicate_entry(hass: HomeAssistant) -> None:
    """ Test: existing ConfigEntry """

    existing_entry = config_entries.ConfigEntry(
        1, DOMAIN, "Test", {CONF_HOST: "10.0.0.131"}, "test", False, {}
    )
    hass.config_entries._async_schedule_save = AsyncMock()
    hass.config_entries._entries = [existing_entry]

    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    user_input = {CONF_HOST: "10.0.0.131"}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"


@pytest.mark.asyncio
async def test_modbus_exception(hass: HomeAssistant, mocker) -> None:
    """ Test: Modbus error """
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    assert result["type"] is FlowResultType.FORM

    mocker.patch(
        "custom_components.solvis_control.config_flow.ModbusClient.AsyncModbusTcpClient.read_input_registers",
        side_effect=Exception("Modbus read failed"),
    )

    user_input = {CONF_HOST: "10.0.0.131"}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"]["base"] == "unknown"


@pytest.mark.asyncio
async def test_poll_rate_validation() -> None:
    """ Test: invalid poll rate config """
    from custom_components.solvis_control.config_flow import validate_poll_rates

    valid_data = {POLL_RATE_HIGH: 5, POLL_RATE_DEFAULT: 10, POLL_RATE_SLOW: 30}
    invalid_data = {POLL_RATE_HIGH: 10, POLL_RATE_DEFAULT: 15, POLL_RATE_SLOW: 30}  # 
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
async def test_conflict_option_6_and_7(hass: HomeAssistant) -> None:
    """ Test: conflict option 6 and 7 """
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    user_input = {CONF_HOST: "10.0.0.131"}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "features"

    conflicting_input = {CONF_OPTION_6: True, CONF_OPTION_7: True}

    result = await hass.config_entries.flow.async_configure(result["flow_id"], conflicting_input)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"]["base"] == "only_one_temperature_sensor"


@pytest.mark.asyncio
async def test_generic_exception(hass: HomeAssistant, mocker) -> None:
    """ Test: unexpected error """
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    assert result["type"] is FlowResultType.FORM

    mocker.patch(
        "custom_components.solvis_control.config_flow.SolvisConfigFlow.async_step_user",
        side_effect=Exception("Unexpected error"),
    )

    user_input = {CONF_HOST: "10.0.0.131"}
    result = await hass.config_entries.flow.async_configure(result["flow_id"], user_input)

    assert result["type"] is FlowResultType.FORM
    assert result["errors"]["base"] == "unknown"


@pytest.mark.asyncio
async def test_user_cancels_flow(hass: HomeAssistant) -> None:
    """ Test: flow canceled by user """
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"

    # user cancels flow (no input, no `async_configure()`)
    await hass.config_entries.flow.async_abort(result["flow_id"])
    assert len(hass.config_entries.flow.async_progress()) == 0


@pytest.mark.asyncio
async def test_options_flow(hass: HomeAssistant) -> None:
    """ Test: options flow """
    config_entry = config_entries.ConfigEntry(
        1, DOMAIN, "Test", {CONF_HOST: "10.0.0.131"}, "test", False, {}
    )

    flow = config_entries.OptionsFlow(config_entry)
    result = await flow.async_step_init()

    assert result["type"] is FlowResultType.FORM
