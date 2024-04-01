DOMAIN = "solvis_control"

from dataclasses import dataclass

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
    ),
    ModbusFieldConfig(  # Zirkulationsdurchfluss
        name="cold_water_temp",
        address=33034,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
        multiplier=0.01,
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
    ),
    ModbusFieldConfig(
        name="solar_heat_exchanger_in_water_temp",
        address=33029,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
    ),
    ModbusFieldConfig(
        name="solar_heat_exchanger_out_water_temp",
        address=33028,
        unit="°C",
        device_class="temperature",
        state_class="measurement",
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
    # ModbusFieldConfig(
    #     name="solar_water_flow",
    #     address=33040,
    #     unit="l/min",
    #     device_class="speed",
    #     state_class="measurement",
    # ),
    # ModbusFieldConfig( # Durchfluss Warmwasserzirkualation
    #     name="domestic_water_flow",
    #     address=33041,
    #     unit="l/min",
    #     device_class="speed",
    #     state_class="measurement",
    # ),
]


#       - name: HKR1 Betriebsart
#         slave: 1
#         input_type: holding
#         address: 2818
#         scan_interval: 30
#         unique_id: e240a16b-563a-409f-929a-088010822ade

#       # ab hier 300 Sekunden Poll Interval

#       - name: HKR1 Absenktemperatur Nacht
#         unit_of_measurement: °C
#         slave: 1
#         input_type: holding
#         address: 2821
#         scan_interval: 300
#         unique_id: b6550eb0-6f0f-4019-a708-65b1cd4ecbf7

#       - name: HKR1 Solltemperatur Tag
#         unit_of_measurement: °C
#         slave: 1
#         input_type: holding
#         address: 2820
#         scan_interval: 300
#         unique_id: cc08dfc7-3f45-409c-b50f-a241f5d63169

#       - name: DigIn Stoerungen
#         slave: 1
#         input_type: input
#         address: 33045
#         scan_interval: 300
#         unique_id: 45d195db-ce3b-4498-8015-566e45f115b6

#       - name: WW Solltemperatur
#         unit_of_measurement: °C
#         slave: 1
#         input_type: holding
#         address: 2305
#         scan_interval: 300
#         unique_id: 0a76a76a-a0b6-40a8-b20d-2245a60fdd39

#       - name: VersionSC2
#         slave: 1
#         scale: 0.01
#         precision: 2
#         input_type: input
#         address: 32770
#         scan_interval: 300
#         unique_id: bd96dedf-f5a3-43b9-a5b9-e31441fbae67

#       - name: VersionNBG
#         slave: 1
#         scale: 0.01
#         input_type: input
#         address: 32771
#         scan_interval: 300
#         unique_id: 1ad4554f-669b-4038-aef4-71d4e0194178

#       - name: ZirkulationBetriebsart
#         slave: 1
#         input_type: input
#         address: 2049
#         scan_interval: 300
#         unique_id: c075a802-8143-4d2c-af13-8421345ce2ad

#       - name: Raumtemperatur_HKR1
#         unit_of_measurement: °C
#         scale: 0.1
#         slave: 1
#         input_type: holding
#         address: 34304
#         scan_interval: 300
#         unique_id: 1c4b8bdf-cb08-465a-b4af-80ecc400a220
