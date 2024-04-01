from dataclasses import dataclass

DOMAIN = "solvis_control"

CONF_NAME = "name"
CONF_HOST = "host"
CONF_PORT = "port"

DATA_COORDINATOR = "coordinator"
MANUFACTURER = "Solvis"


@dataclass(frozen=True)
class ModbusFieldConfig:
    name: str
    address: int
    unit: str
    device_class: str
    state_class: str
    multiplier: float = 0.1
    # 1 = INPUT, 2 = HOLDING
    register: int = 1
    negative: bool = False
    entity_category: str = None
    enabled_by_default: bool = True


PORT = 502
REGISTERS = [
    ModbusFieldConfig(  # Brennerleistung
        name="gas_power",
        address=33539,
        unit="kW",
        device_class="power",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # Außentemperatur
        name="outdoor_air_temp",
        address=33033,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(
        name="roof_air_temp",
        address=33031,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        enabled_by_default=False,
    ),
    ModbusFieldConfig(  # Zirkulationsdurchfluss
        name="cold_water_temp",
        address=33034,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        multiplier=0.1,
    ),
    ModbusFieldConfig(  # Vorlauftemperatur
        name="flow_water_temp",
        address=33035,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # Warmwassertemperatur
        name="domestic_water_temp",
        address=33025,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(
        name="solar_water_temp",
        address=33030,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        enabled_by_default=False,
    ),
    ModbusFieldConfig(
        name="solar_heat_exchanger_in_water_temp",
        address=33029,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        enabled_by_default=False,
    ),
    ModbusFieldConfig(
        name="solar_heat_exchanger_out_water_temp",
        address=33028,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        enabled_by_default=False,
    ),
    ModbusFieldConfig(  # Speicherreferenztemperatur
        name="tank_layer1_water_temp",
        address=33026,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # Heizungspuffertemperatur unten
        name="tank_layer2_water_temp",
        address=33032,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        negative=True,
    ),
    ModbusFieldConfig(  # Heizungspuffertemperatur oben
        name="tank_layer3_water_temp",
        address=33027,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # Warmwasserpuffer
        name="tank_layer4_water_temp",
        address=33024,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # Kaltwassertemperatur
        name="cold_water_temperatur",
        address=33038,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # Laufzeit Brenner
        name="runtime_gasburner",
        address=33536,
        unit="h",
        device_class="time",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # Brennerstarts
        name="number_gas_burner_start",
        address=33537,
        unit="",
        device_class="",
        state_class="measurement",
        negative=True,
        multiplier=1,
    ),
    ModbusFieldConfig(  # Ionisationsstrom
        name="ionisation_voltage",
        address=33540,
        unit="mV",
        device_class="voltage",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # A01.Pumpe Zirkulation
        name="A01_Pumpe_Zirkulation",
        address=33280,
        unit="V",
        device_class="voltage",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # A02.Pumpe Warmwasser
        name="A02_Pumpe_Warmwasser",
        address=33281,
        unit="V",
        device_class="voltage",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # A03.Pumpe HK1
        name="A03_Pumpe_HK1",
        address=33282,
        unit="V",
        device_class="voltage",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # A05.Pumpe Zirkulation
        name="A05_Pumpe_Zirkulation",
        address=33284,
        unit="V",
        device_class="voltage",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # A12.Brennerstatus
        name="A12_Brennerstatus",
        address=33291,
        unit="V",
        device_class="voltage",
        state_class="measurement",
    ),
    ModbusFieldConfig(  # WW Nachheizung 2322
        name="WW_Nachheizung_2322",
        address=2322,
        unit="V",
        device_class="voltage",
        state_class="measurement",
        register=2,
    ),
    ModbusFieldConfig(
        name="solar_water_flow",
        address=33040,
        unit="l/min",
        device_class=None,
        state_class="measurement",
        enabled_by_default=False,
    ),
    ModbusFieldConfig(  # Durchfluss Warmwasserzirkualation
        name="domestic_water_flow",
        address=33041,
        unit="l/min",
        device_class=None,
        state_class="measurement",
    ),
    ModbusFieldConfig(  # HKR1 Betriebsart
        name="HKR1_Betriebsart",
        address=2818,
        unit="",
        device_class=None,
        state_class=None,
        register=2,
        multiplier=1,
    ),
    ModbusFieldConfig(  # HKR1 Absenktemperatur Nacht
        name="HKR1_Absenktemperatur_Nacht",
        address=2821,
        unit="°C",
        device_class="temperatur",
        state_class="measurement",
        register=2,
        multiplier=1,
    ),
    ModbusFieldConfig(  # HKR1 Solltemperatur Tag
        name="HKR1_Solltemperatur_Tag",
        address=2820,
        unit="°C",
        device_class="temperatur",
        state_class="measurement",
        register=2,
        multiplier=1,
    ),
    ModbusFieldConfig(  # DigIn Stoerungen
        name="DigIn_Stoerungen",
        address=33045,
        unit="",
        device_class=None,
        state_class=None,
        multiplier=1,
        entity_category="diagnostic",
    ),
    ModbusFieldConfig(  # WW Solltemperatur
        name="WW_Solltemperatur",
        address=2305,
        unit="°C",
        device_class="temperatur",
        state_class="measurement",
        register=2,
        multiplier=1,
    ),
    ModbusFieldConfig(  # VersionSC2
        name="VersionSC2",
        address=32770,
        unit="",
        device_class=None,
        state_class="measurement",
        multiplier=1,
        entity_category="diagnostic",
    ),
    ModbusFieldConfig(  # VersionNBG
        name="VersionNBG",
        address=32771,
        unit="",
        device_class=None,
        state_class="measurement",
        multiplier=1,
        entity_category="diagnostic",
    ),
    ModbusFieldConfig(  # ZirkulationBetriebsart
        name="ZirkulationBetriebsart",
        address=2049,
        unit="",
        device_class=None,
        state_class=None,
        multiplier=1,
    ),
    ModbusFieldConfig(  # Raumtemperatur_HKR1
        name="Raumtemperatur_HKR1",
        address=34304,
        unit="°C",
        device_class="temperatur",
        state_class="measurement",
        register=2,
    ),
]
