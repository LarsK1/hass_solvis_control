# Reading registers

| Adresse | Sovlis Beschreibung                | Unterstützt seit V | Sensortyp | Conf.-Option | Bemerkung                   | Min | Max    | Einheit                  |
| ------- | ---------------------------------- | ------------------ | --------- | ------------ | --------------------------- | --- | ------ | ------------------------ |
| 33042   | Analog In 1                        |                    |           |              |                             |     |        | 0,1 V                    |
| 33043   | Analog In 2                        |                    |           |              |                             |     |        | 0,1 V                    |
| 33044   | Analog In 3                        |                    |           |              |                             |     |        | 0,1 V                    |
| 3840    | Analog Out 1 Status                | 1.1.0              | 0         | 0            |                             | 0   | 3      |                          |
| 3845    | Analog Out 2 Status                | 1.1.0              | 0         | 0            |                             | 0   | 3      |                          |
| 3850    | Analog Out 3 Status                | 1.1.0              | 0         | 0            |                             | 0   | 3      |                          |
| 3855    | Analog Out 4 Status                | 1.1.0              | 0         | 0            |                             | 0   | 3      |                          |
| 3860    | Analog Out 5 Status                | 1.1.0              | 0         | 0            |                             | 0   | 3      |                          |
| 3865    | Analog Out 6 Status                | 1.1.0              | 0         | 0            |                             | 0   | 3      |                          |
| 33294   | Analog Out O1                      | 2.0.0              | 0         | 0            |                             | 0   | 100    | % (PWM) / 0,1 V (0-10 V) |
| 33295   | Analog Out O2                      | 2.0.0              | 0         | 3            |                             | 0   | 100    | % (PWM) / 0,1 V (0-10 V) |
| 33296   | Analog Out O3                      | 2.0.0              | 0         | 3            |                             | 0   | 100    | % (PWM) / 0,1 V (0-10 V) |
| 33297   | Analog Out O4                      | 2.0.0              | 0         | 4            |                             | 0   | 100    | % (PWM) / 0,1 V (0-10 V) |
| 33298   | Analog Out O5                      | 2.0.0              | 0         | 0            |                             | 0   | 100    | % (PWM) / 0,1 V (0-10 V) |
| 33299   | Analog Out O6                      | 2.0.0              | 0         | 0            |                             | 0   | 100    | % (PWM) / 0,1 V (0-10 V) |
| 33280   | Ausgang A1                         | 0.1                | 4         | 0            |                             | 0   | 100    | 100                      |
| 33281   | Ausgang A2                         | 0.1                | 4         | 4            | see #53                     | 0   | 200    | 200                      |
| 33282   | Ausgang A3                         | 1.0                | 4         | 0            |                             | 0   | 100    | 100                      |
| 33283   | Ausgang A4                         | 1.0                | 4         | 1            |                             | 0   | 100    | 100                      |
| 33284   | Ausgang A5                         | 1.0                | 4         | 2            |                             | 0   | 100    | 100                      |
| 33285   | Ausgang A6                         | 2.0.0              | 4         | 2            |                             | 0   | 100    | 100                      |
| 33286   | Ausgang A7                         | 2.0.0              | 4         | 2            |                             | 0   | 100    | 100                      |
| 33287   | Ausgang A8                         | 2.0.0              | 4         | 0            |                             | 0   | 100    | 100                      |
| 33288   | Ausgang A9                         | 2.0.0              | 4         | 0            |                             | 0   | 100    | 100                      |
| 33289   | Ausgang A10                        | 2.0.0              | 4         | 1            |                             | 0   | 100    | 100                      |
| 33290   | Ausgang A11                        | 2.0.0              | 4         | 1            |                             | 0   | 100    | 100                      |
| 33291   | Ausgang A12                        | 0.1                | 4         | 0            |                             | 0   | 100    | 100                      |
| 33292   | Ausgang A13                        | 2.0.0              | 4         | 4            |                             | 0   | 100    | 100                      |
| 33293   | Ausgang A14                        | 2.0.0              | 4         | 4            |                             | 0   | 100    | 100                      |
| 33537   | Brennerstarts Stufe 1              | 0.1                | 0         | 0            |                             |     |        |                          |
| 33045   | DigIn Störungen                    | 1.1.1              | 0         | 0            |                             |     |        |                          |
| 33540   | Ionisationsstrom                   | 0.9                | 0         | 0            |                             |     |        | mA                       |
| 33536   | Laufzeit Brennerstufe 1            | 1.1.1              | 0         | 0            |                             |     |        |                          |
| 33538   | Laufzeit Brennerstufe 2            | 1.1.1              | 0         | 0            |                             |     |        |                          |
| 33550   | Wärmemengenzähler Leistung         | 2.0.0              | 0         | 0            | not in Solvis Documentation |     |        | hW                       |
| 33796   | Meldung 1 Par 1                    |                    |           |              |                             |     |        |                          |
| 33797   | Meldung 1 Par 2                    |                    |           |              |                             |     |        |                          |
| 33794   | Meldung 1 UnixZeit H               |                    |           |              |                             |     |        |                          |
| 33795   | Meldung 1 UnixZeit L               |                    |           |              |                             |     |        |                          |
| 33838   | Meldung 10 Code                    |                    |           |              |                             |     |        |                          |
| 33841   | Meldung 10 Par 1                   |                    |           |              |                             |     |        |                          |
| 33842   | Meldung 10 Par 2                   |                    |           |              |                             |     |        |                          |
| 33839   | Meldung 10 UnixZeit H              |                    |           |              |                             |     |        |                          |
| 33840   | Meldung 10 UnixZeit L              |                    |           |              |                             |     |        |                          |
| 33798   | Meldung 2 Code                     |                    |           |              |                             |     |        |                          |
| 33801   | Meldung 2 Par 1                    |                    |           |              |                             |     |        |                          |
| 33802   | Meldung 2 Par 2                    |                    |           |              |                             |     |        |                          |
| 33799   | Meldung 2 UnixZeit H               |                    |           |              |                             |     |        |                          |
| 33800   | Meldung 2 UnixZeit L               |                    |           |              |                             |     |        |                          |
| 33803   | Meldung 3 Code                     |                    |           |              |                             |     |        |                          |
| 33806   | Meldung 3 Par 1                    |                    |           |              |                             |     |        |                          |
| 33807   | Meldung 3 Par 2                    |                    |           |              |                             |     |        |                          |
| 33804   | Meldung 3 UnixZeit H               |                    |           |              |                             |     |        |                          |
| 33805   | Meldung 3 UnixZeit L               |                    |           |              |                             |     |        |                          |
| 33808   | Meldung 4 Code                     |                    |           |              |                             |     |        |                          |
| 33811   | Meldung 4 Par 1                    |                    |           |              |                             |     |        |                          |
| 33812   | Meldung 4 Par 2                    |                    |           |              |                             |     |        |                          |
| 33809   | Meldung 4 UnixZeit H               |                    |           |              |                             |     |        |                          |
| 33810   | Meldung 4 UnixZeit L               |                    |           |              |                             |     |        |                          |
| 33813   | Meldung 5 Code                     |                    |           |              |                             |     |        |                          |
| 33816   | Meldung 5 Par 1                    |                    |           |              |                             |     |        |                          |
| 33817   | Meldung 5 Par 2                    |                    |           |              |                             |     |        |                          |
| 33814   | Meldung 5 UnixZeit H               |                    |           |              |                             |     |        |                          |
| 33815   | Meldung 5 UnixZeit L               |                    |           |              |                             |     |        |                          |
| 33818   | Meldung 6 Code                     |                    |           |              |                             |     |        |                          |
| 33821   | Meldung 6 Par 1                    |                    |           |              |                             |     |        |                          |
| 33822   | Meldung 6 Par 2                    |                    |           |              |                             |     |        |                          |
| 33819   | Meldung 6 UnixZeit H               |                    |           |              |                             |     |        |                          |
| 33820   | Meldung 6 UnixZeit L               |                    |           |              |                             |     |        |                          |
| 33823   | Meldung 7 Code                     |                    |           |              |                             |     |        |                          |
| 33826   | Meldung 7 Par 1                    |                    |           |              |                             |     |        |                          |
| 33827   | Meldung 7 Par 2                    |                    |           |              |                             |     |        |                          |
| 33824   | Meldung 7 UnixZeit H               |                    |           |              |                             |     |        |                          |
| 33825   | Meldung 7 UnixZeit L               |                    |           |              |                             |     |        |                          |
| 33828   | Meldung 8 Code                     |                    |           |              |                             |     |        |                          |
| 33831   | Meldung 8 Par 1                    |                    |           |              |                             |     |        |                          |
| 33832   | Meldung 8 Par 2                    |                    |           |              |                             |     |        |                          |
| 33829   | Meldung 8 UnixZeit H               |                    |           |              |                             |     |        |                          |
| 33830   | Meldung 8 UnixZeit L               |                    |           |              |                             |     |        |                          |
| 33833   | Meldung 9 Code                     |                    |           |              |                             |     |        |                          |
| 33836   | Meldung 9 Par 1                    |                    |           |              |                             |     |        |                          |
| 33837   | Meldung 9 Par 2                    |                    |           |              |                             |     |        |                          |
| 33834   | Meldung 9 UnixZeit H               |                    |           |              |                             |     |        |                          |
| 33835   | Meldung 9 UnixZeit L               |                    |           |              |                             |     |        |                          |
| 33793   | Meldung1 Code                      |                    |           |              |                             |     |        |                          |
| 33792   | Meldungen Anzahl                   |                    |           |              |                             |     |        |                          |
| 0       | Setup 1                            |                    |           |              |                             |     |        |                          |
| 1       | Setup 2                            |                    |           |              |                             |     |        |                          |
| 33024   | Temp S1                            | 0.1                | 0         | 0            |                             |     | 0,1 °C |                          |
| 33025   | Temp S2                            | 0.1                | 0         | 0            |                             |     | 0,1 °C |                          |
| 33026   | Temp S3                            | 0.1                | 0         | 0            |                             |     | 0,1 °C |                          |
| 33027   | Temp S4                            | 0.1                | 0         | 0            |                             |     | 0,1 °C |                          |
| 33028   | Temp S5                            | 0.9                | 0         | 3            |                             |     | 0,1 °C |                          |
| 33029   | Temp S6                            | 0.9                | 0         | 3            |                             |     | 0,1 °C |                          |
| 33030   | Temp S7                            | 0.9                | 0         | 3            |                             |     | 0,1 °C |                          |
| 33031   | Temp S8                            | 0.1                | 0         | 3            |                             |     | 0,1 °C |                          |
| 33032   | Temp S9                            | 0.1                | 0         | 0            |                             |     | 0,1 °C |                          |
| 33033   | Temp S10                           | 0.1                | 0         | 0            |                             |     | 0,1 °C |                          |
| 33034   | Temp S11                           | 0.1                | 0         | 0            |                             |     | 0,1 °C |                          |
| 33035   | Temp S12                           | 1.0.0              | 0         | 0            |                             |     | 0,1 °C |                          |
| 33036   | Temp S13                           | 1.0.0              | 0         | 1            |                             |     | 0,1 °C |                          |
| 33037   | Temp S14                           |                    |           |              |                             |     | 0,1 °C |                          |
| 33038   | Temp S15                           | 0.1                | 0         | 0            |                             |     | 0,1 °C |                          |
| 33039   | Temp S16                           | 1.0                | 0         | 2            |                             |     | 0,1 °C |                          |
| 33040   | Volumenstrom S17                   | 0.9                | 0         | 3            |                             |     | l/min  |                          |
| 33041   | Volumenstrom S18                   | 0.1                | 0         | 0            |                             |     | l/min  |                          |
| 32768   | Unix Timestamp high                |                    |           |              |                             |     |        |                          |
| 32769   | Unix Timestamp low                 |                    |           |              |                             |     |        |                          |
| 32771   | Version NBG                        | 0.9                | 0         | 0            |                             |     |        |                          |
| 32770   | Version SC3                        | 0.9                | 0         | 0            |                             |     |        |                          |
| 33539   | Wärmeerzeuger SX aktuelle Leistung | 0.1                | 0         | 0            | see #54                     |     |        | W                        |
| 2049    | Zirkulation Betriebsart            | 0.9                | 0         | 0            |                             | 0   | 3      |                          |

# Holding Register

| Adresse | Sovlis Beschreibung               | Unterstützt seit V | Sensortyp | Conf.-Option | Bemerkung                           | Min  | Max   | Einheit  |
| ------- | --------------------------------- | ------------------ | --------- | ------------ | ----------------------------------- | ---- | ----- | -------- |
| 1542    | Solar primär Drehzahl max         |                    |           |              |                                     | 0    | 100   | %        |
| 1543    | Solar primär Drehzahl min         |                    |           |              |                                     | 0    | 100   | %        |
| 1798    | Solar sekundär Drehzahl max       |                    |           |              |                                     | 0    | 100   | %        |
| 1799    | Solar sekundär Drehzahl min       |                    |           |              |                                     | 0    | 100   | %        |
| 2304    | WW Modus                          |                    |           |              |                                     | 0    | 32767 |          |
| 2305    | WW Sollwert                       | 0.9                | 2         | 0            |                                     | 10   | 65    | °C       |
| 2328    | WW Nachheizung Start              | 1.1.1              | 3         | 0            | Wrong documentation, should be 2322 | 0    | 1     |          |
| 2817    | HKR1 WW Vorrang                   | 1.0.0              | 3         | 0            |                                     | 0    | 1     | aus/ein  |
| 2818    | HKR1 Betriebsart                  | 1.0.0              | 1         | 0            |                                     | 2    | 7     |          |
| 2819    | HKR1 Vorlaufart                   | 1.0.0              | 0         | 0            | not in Solvis Documentation         | 0    | 1     |          |
| 2820    | HKR1 Fix Temperatur Tag           | 1.0.0              | 2         | 0            |                                     | 5    | 75    | °C       |
| 2821    | HKR1 Fix Absenktemperatur         | 1.0.0              | 2         | 0            |                                     | 5    | 75    | °C       |
| 2822    | HKR1 Heizkurve Tag Temperatur 1   | 1.0.0              | 2         | 0            |                                     | 5    | 50    | °C       |
| 2823    | HKR1 Heizkurve Tag Temperatur 2   | 1.0.0              | 2         | 0            |                                     | 5    | 30    | °C       |
| 2824    | HKR1 Heizkurve Tag Temperatur 3   | 1.0.0              | 2         | 0            |                                     | 5    | 30    | °C       |
| 2825    | HKR1 Heizkurve Absenktemperatur   | 1.0.0              | 2         | 0            |                                     | 5    | 30    | °C       |
| 2832    | HKR1 Heizkurve Steilheit          | 1.0.0              | 2         | 0            |                                     | 20   | 250   | in 10tel |
| 2870    | HKR1 Urlaub zu Hause Temperatur   |                    |           |              |                                     | 0    | 30    | °C       |
| 2871    | HKR1 Urlaub zu Hause Dauer        |                    |           |              |                                     | 0    | 31    | Tag      |
| 2872    | HKR1 Urlaub zu Hause Heizen Start |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 2873    | HKR1 Urlaub zu Hause Heizen Stop  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 2880    | HKR1 Urlaub auswärts Temperatur   |                    |           |              |                                     | 0    | 30    | °C       |
| 2881    | HKR1 Urlaub auswärts bis Tag      |                    |           |              |                                     | 1    | 31    | Tag      |
| 2882    | HKR1 Urlaub auswärts bis Monat    |                    |           |              |                                     | 1    | 12    | Monat    |
| 2883    | HKR1 Urlaub auswärts bis Jahr     |                    |           |              |                                     | 2006 | 2099  | Jahr     |
| 3073    | HKR2 WW Vorrang                   | 1.0.0              | 3         | 0            |                                     | 0    | 1     | aus/ein  |
| 3074    | HKR2 Betriebsart                  | 1.0.0              | 1         | 0            |                                     | 2    | 7     |          |
| 3075    | HKR2 Vorlaufart                   | 1.0.0              | 0         | 0            | not in Solvis Documentation         | 0    | 1     |          |
| 3076    | HKR2 Fix Temperatur Tag           | 1.0.0              | 2         | 0            |                                     | 5    | 75    | °C       |
| 3077    | HKR2 Fix Absenktemperatur         | 1.0.0              | 2         | 0            |                                     | 5    | 75    | °C       |
| 3078    | HKR2 Heizkurve Tag Temperatur 1   | 1.0.0              | 2         | 0            |                                     | 5    | 50    | °C       |
| 3079    | HKR2 Heizkurve Tag Temperatur 2   | 1.0.0              | 2         | 0            |                                     | 5    | 30    | °C       |
| 3080    | HKR2 Heizkurve Tag Temperatur 3   | 1.0.0              | 2         | 0            |                                     | 5    | 30    | °C       |
| 3081    | HKR2 Heizkurve Absenktemperatur   | 1.0.0              | 2         | 0            |                                     | 5    | 30    | °C       |
| 3088    | HKR2 Heizkurve Steilheit          | 1.0.0              | 2         | 0            |                                     | 20   | 250   | in 10tel |
| 3126    | HKR2 Urlaub zu Hause Temperatur   |                    |           |              |                                     | 0    | 30    | °C       |
| 3127    | HKR2 Urlaub zu Hause Dauer        |                    |           |              |                                     | 0    | 31    | Tag      |
| 3128    | HKR2 Urlaub zu Hause Heizen Start |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 3129    | HKR2 Urlaub zu Hause Heizen Stop  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 3136    | HKR2 Urlaub auswärts Temperatur   |                    |           |              |                                     | 0    | 30    | °C       |
| 3137    | HKR2 Urlaub auswärts bis Tag      |                    |           |              |                                     | 1    | 31    | Tag      |
| 3138    | HKR2 Urlaub auswärts bis Monat    |                    |           |              |                                     | 1    | 12    | Monat    |
| 3139    | HKR2 Urlaub auswärts bis Jahr     |                    |           |              |                                     | 2006 | 2099  | Jahr     |
| 3329    | HKR3 WW Vorrang                   | 1.0.0              | 3         | 0            |                                     | 0    | 1     | aus/ein  |
| 3330    | HKR3 Betriebsart                  | 1.0.0              | 1         | 0            |                                     | 2    | 7     |          |
| 3331    | HKR3 Vorlaufart                   | 1.0.0              | 0         | 0            | not in Solvis Documentation         | 0    | 1     |          |
| 3332    | HKR3 Fix Temperatur Tag           | 1.0.0              | 2         | 0            |                                     | 5    | 75    | °C       |
| 3333    | HKR3 Fix Absenktemperatur         | 1.0.0              | 2         | 0            |                                     | 5    | 75    | °C       |
| 3334    | HKR3 Heizkurve Tag Temperatur 1   | 1.0.0              | 2         | 0            |                                     | 5    | 50    | °C       |
| 3335    | HKR3 Heizkurve Tag Temperatur 2   | 1.0.0              | 2         | 0            |                                     | 5    | 30    | °C       |
| 3336    | HKR3 Heizkurve Tag Temperatur 3   | 1.0.0              | 2         | 0            |                                     | 5    | 30    | °C       |
| 3337    | HKR3 Heizkurve Absenktemperatur   | 1.0.0              | 2         | 0            |                                     | 5    | 30    | °C       |
| 3344    | HKR3 Heizkurve Steilheit          | 1.0.0              | 2         | 0            |                                     | 20   | 250   | in 10tel |
| 3382    | HKR3 Urlaub zu Hause Temperatur   |                    |           |              |                                     | 0    | 30    | °C       |
| 3383    | HKR3 Urlaub zu Hause Dauer        |                    |           |              |                                     | 0    | 31    | Tag      |
| 3384    | HKR3 Urlaub zu Hause Heizen Start |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 3385    | HKR3 Urlaub zu Hause Heizen Stop  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 3392    | HKR3 Urlaub auswärts Temperatur   |                    |           |              |                                     | 0    | 30    | °C       |
| 3393    | HKR3 Urlaub auswärts bis Tag      |                    |           |              |                                     | 1    | 31    | Tag      |
| 3394    | HKR3 Urlaub auswärts bis Monat    |                    |           |              |                                     | 1    | 12    | Monat    |
| 3395    | HKR3 Urlaub auswärts bis Jahr     |                    |           |              |                                     | 2006 | 2099  | Jahr     |
| 33543   | Leistung Solarthermie             | 1.1.3              | 0         | 3            | not in Solvis Documentation         | 0    |       | kW       |
| 33544   | Wärmepumpe Leistung               | 0.9                | 0         | 4            | not in Solvis Documentation         |      |       | kW       |
| 33545   | Elektrische Wärmepumpenleistung   | 0.9                | 0         | 4            | not in Solvis Documentation         |      |       | kW       |
| 34048   | Wochenplan HK 1 Tag 1 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34049   | Wochenplan HK 1 Tag 1 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34050   | Wochenplan HK 1 Tag 1 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34051   | Wochenplan HK 1 Tag 1 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34052   | Wochenplan HK 1 Tag 1 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34053   | Wochenplan HK 1 Tag 1 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34054   | Wochenplan HK 1 Tag 2 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34055   | Wochenplan HK 1 Tag 2 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34056   | Wochenplan HK 1 Tag 2 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34057   | Wochenplan HK 1 Tag 2 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34058   | Wochenplan HK 1 Tag 2 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34059   | Wochenplan HK 1 Tag 2 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34060   | Wochenplan HK 1 Tag 3 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34061   | Wochenplan HK 1 Tag 3 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34062   | Wochenplan HK 1 Tag 3 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34063   | Wochenplan HK 1 Tag 3 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34064   | Wochenplan HK 1 Tag 3 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34065   | Wochenplan HK 1 Tag 3 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34066   | Wochenplan HK 1 Tag 4 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34067   | Wochenplan HK 1 Tag 4 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34068   | Wochenplan HK 1 Tag 4 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34069   | Wochenplan HK 1 Tag 4 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34070   | Wochenplan HK 1 Tag 4 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34071   | Wochenplan HK 1 Tag 4 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34072   | Wochenplan HK 1 Tag 5 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34073   | Wochenplan HK 1 Tag 5 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34074   | Wochenplan HK 1 Tag 5 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34075   | Wochenplan HK 1 Tag 5 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34076   | Wochenplan HK 1 Tag 5 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34077   | Wochenplan HK 1 Tag 5 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34078   | Wochenplan HK 1 Tag 6 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34079   | Wochenplan HK 1 Tag 6 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34080   | Wochenplan HK 1 Tag 6 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34081   | Wochenplan HK 1 Tag 6 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34082   | Wochenplan HK 1 Tag 6 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34083   | Wochenplan HK 1 Tag 6 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34084   | Wochenplan HK 1 Tag 7 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34085   | Wochenplan HK 1 Tag 7 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34086   | Wochenplan HK 1 Tag 7 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34087   | Wochenplan HK 1 Tag 7 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34088   | Wochenplan HK 1 Tag 7 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34089   | Wochenplan HK 1 Tag 7 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34090   | Wochenplan HK 2 Tag 1 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34091   | Wochenplan HK 2 Tag 1 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34092   | Wochenplan HK 2 Tag 1 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34093   | Wochenplan HK 2 Tag 1 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34094   | Wochenplan HK 2 Tag 1 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34095   | Wochenplan HK 2 Tag 1 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34096   | Wochenplan HK 2 Tag 2 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34097   | Wochenplan HK 2 Tag 2 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34098   | Wochenplan HK 2 Tag 2 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34099   | Wochenplan HK 2 Tag 2 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34100   | Wochenplan HK 2 Tag 2 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34101   | Wochenplan HK 2 Tag 2 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34102   | Wochenplan HK 2 Tag 3 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34103   | Wochenplan HK 2 Tag 3 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34104   | Wochenplan HK 2 Tag 3 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34105   | Wochenplan HK 2 Tag 3 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34106   | Wochenplan HK 2 Tag 3 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34107   | Wochenplan HK 2 Tag 3 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34108   | Wochenplan HK 2 Tag 4 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34109   | Wochenplan HK 2 Tag 4 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34110   | Wochenplan HK 2 Tag 4 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34111   | Wochenplan HK 2 Tag 4 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34112   | Wochenplan HK 2 Tag 4 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34113   | Wochenplan HK 2 Tag 4 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34114   | Wochenplan HK 2 Tag 5 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34115   | Wochenplan HK 2 Tag 5 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34116   | Wochenplan HK 2 Tag 5 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34117   | Wochenplan HK 2 Tag 5 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34118   | Wochenplan HK 2 Tag 5 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34119   | Wochenplan HK 2 Tag 5 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34120   | Wochenplan HK 2 Tag 6 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34121   | Wochenplan HK 2 Tag 6 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34122   | Wochenplan HK 2 Tag 6 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34123   | Wochenplan HK 2 Tag 6 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34124   | Wochenplan HK 2 Tag 6 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34125   | Wochenplan HK 2 Tag 6 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34126   | Wochenplan HK 2 Tag 7 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34127   | Wochenplan HK 2 Tag 7 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34128   | Wochenplan HK 2 Tag 7 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34129   | Wochenplan HK 2 Tag 7 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34130   | Wochenplan HK 2 Tag 7 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34131   | Wochenplan HK 2 Tag 7 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34132   | Wochenplan HK 3 Tag 1 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34133   | Wochenplan HK 3 Tag 1 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34134   | Wochenplan HK 3 Tag 1 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34135   | Wochenplan HK 3 Tag 1 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34136   | Wochenplan HK 3 Tag 1 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34137   | Wochenplan HK 3 Tag 1 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34138   | Wochenplan HK 3 Tag 2 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34139   | Wochenplan HK 3 Tag 2 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34140   | Wochenplan HK 3 Tag 2 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34141   | Wochenplan HK 3 Tag 2 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34142   | Wochenplan HK 3 Tag 2 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34143   | Wochenplan HK 3 Tag 2 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34144   | Wochenplan HK 3 Tag 3 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34145   | Wochenplan HK 3 Tag 3 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34146   | Wochenplan HK 3 Tag 3 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34147   | Wochenplan HK 3 Tag 3 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34148   | Wochenplan HK 3 Tag 3 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34149   | Wochenplan HK 3 Tag 3 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34150   | Wochenplan HK 3 Tag 4 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34151   | Wochenplan HK 3 Tag 4 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34152   | Wochenplan HK 3 Tag 4 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34153   | Wochenplan HK 3 Tag 4 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34154   | Wochenplan HK 3 Tag 4 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34155   | Wochenplan HK 3 Tag 4 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34156   | Wochenplan HK 3 Tag 5 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34157   | Wochenplan HK 3 Tag 5 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34158   | Wochenplan HK 3 Tag 5 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34159   | Wochenplan HK 3 Tag 5 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34160   | Wochenplan HK 3 Tag 5 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34161   | Wochenplan HK 3 Tag 5 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34162   | Wochenplan HK 3 Tag 6 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34163   | Wochenplan HK 3 Tag 6 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34164   | Wochenplan HK 3 Tag 6 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34165   | Wochenplan HK 3 Tag 6 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34166   | Wochenplan HK 3 Tag 6 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34167   | Wochenplan HK 3 Tag 6 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34168   | Wochenplan HK 3 Tag 7 Start 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34169   | Wochenplan HK 3 Tag 7 Stop 0      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34170   | Wochenplan HK 3 Tag 7 Start 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34171   | Wochenplan HK 3 Tag 7 Stop 1      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34172   | Wochenplan HK 3 Tag 7 Start 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34173   | Wochenplan HK 3 Tag 7 Stop 2      |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34174   | Wochenplan HK WW Tag 1 Start 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34175   | Wochenplan HK WW Tag 1 Stop 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34176   | Wochenplan HK WW Tag 1 Start 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34177   | Wochenplan HK WW Tag 1 Stop 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34178   | Wochenplan HK WW Tag 1 Start 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34179   | Wochenplan HK WW Tag 1 Stop 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34180   | Wochenplan HK WW Tag 2 Start 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34181   | Wochenplan HK WW Tag 2 Stop 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34182   | Wochenplan HK WW Tag 2 Start 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34183   | Wochenplan HK WW Tag 2 Stop 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34184   | Wochenplan HK WW Tag 2 Start 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34185   | Wochenplan HK WW Tag 2 Stop 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34186   | Wochenplan HK WW Tag 3 Start 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34187   | Wochenplan HK WW Tag 3 Stop 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34188   | Wochenplan HK WW Tag 3 Start 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34189   | Wochenplan HK WW Tag 3 Stop 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34190   | Wochenplan HK WW Tag 3 Start 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34191   | Wochenplan HK WW Tag 3 Stop 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34192   | Wochenplan HK WW Tag 4 Start 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34193   | Wochenplan HK WW Tag 4 Stop 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34194   | Wochenplan HK WW Tag 4 Start 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34195   | Wochenplan HK WW Tag 4 Stop 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34196   | Wochenplan HK WW Tag 4 Start 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34197   | Wochenplan HK WW Tag 4 Stop 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34198   | Wochenplan HK WW Tag 5 Start 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34199   | Wochenplan HK WW Tag 5 Stop 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34200   | Wochenplan HK WW Tag 5 Start 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34201   | Wochenplan HK WW Tag 5 Stop 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34202   | Wochenplan HK WW Tag 5 Start 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34203   | Wochenplan HK WW Tag 5 Stop 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34204   | Wochenplan HK WW Tag 6 Start 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34205   | Wochenplan HK WW Tag 6 Stop 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34206   | Wochenplan HK WW Tag 6 Start 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34207   | Wochenplan HK WW Tag 6 Stop 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34208   | Wochenplan HK WW Tag 6 Start 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34209   | Wochenplan HK WW Tag 6 Stop 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34210   | Wochenplan HK WW Tag 7 Start 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34211   | Wochenplan HK WW Tag 7 Stop 0     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34212   | Wochenplan HK WW Tag 7 Start 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34213   | Wochenplan HK WW Tag 7 Stop 1     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34214   | Wochenplan HK WW Tag 7 Start 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34215   | Wochenplan HK WW Tag 7 Stop 2     |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34216   | Wochenplan HK Zirk Tag 1 Start 0  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34217   | Wochenplan HK Zirk Tag 1 Stop 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34218   | Wochenplan HK Zirk Tag 1 Start 1  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34219   | Wochenplan HK Zirk Tag 1 Stop 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34220   | Wochenplan HK Zirk Tag 1 Start 2  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34221   | Wochenplan HK Zirk Tag 1 Stop 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34222   | Wochenplan HK Zirk Tag 2 Start 0  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34223   | Wochenplan HK Zirk Tag 2 Stop 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34224   | Wochenplan HK Zirk Tag 2 Start 1  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34225   | Wochenplan HK Zirk Tag 2 Stop 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34226   | Wochenplan HK Zirk Tag 2 Start 2  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34227   | Wochenplan HK Zirk Tag 2 Stop 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34228   | Wochenplan HK Zirk Tag 3 Start 0  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34229   | Wochenplan HK Zirk Tag 3 Stop 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34230   | Wochenplan HK Zirk Tag 3 Start 1  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34231   | Wochenplan HK Zirk Tag 3 Stop 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34232   | Wochenplan HK Zirk Tag 3 Start 2  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34233   | Wochenplan HK Zirk Tag 3 Stop 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34234   | Wochenplan HK Zirk Tag 4 Start 0  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34235   | Wochenplan HK Zirk Tag 4 Stop 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34236   | Wochenplan HK Zirk Tag 4 Start 1  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34237   | Wochenplan HK Zirk Tag 4 Stop 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34238   | Wochenplan HK Zirk Tag 4 Start 2  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34239   | Wochenplan HK Zirk Tag 4 Stop 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34240   | Wochenplan HK Zirk Tag 5 Start 0  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34241   | Wochenplan HK Zirk Tag 5 Stop 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34242   | Wochenplan HK Zirk Tag 5 Start 1  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34243   | Wochenplan HK Zirk Tag 5 Stop 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34244   | Wochenplan HK Zirk Tag 5 Start 2  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34245   | Wochenplan HK Zirk Tag 5 Stop 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34246   | Wochenplan HK Zirk Tag 6 Start 0  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34247   | Wochenplan HK Zirk Tag 6 Stop 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34248   | Wochenplan HK Zirk Tag 6 Start 1  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34249   | Wochenplan HK Zirk Tag 6 Stop 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34250   | Wochenplan HK Zirk Tag 6 Start 2  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34251   | Wochenplan HK Zirk Tag 6 Stop 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34252   | Wochenplan HK Zirk Tag 7 Start 0  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34253   | Wochenplan HK Zirk Tag 7 Stop 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34254   | Wochenplan HK Zirk Tag 7 Start 1  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34255   | Wochenplan HK Zirk Tag 7 Stop 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34256   | Wochenplan HK Zirk Tag 7 Start 2  |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34257   | Wochenplan HK Zirk Tag 7 Stop 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34258   | Wochenplan HK Eco Tag 1 Start 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34259   | Wochenplan HK Eco Tag 1 Stop 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34260   | Wochenplan HK Eco Tag 1 Start 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34261   | Wochenplan HK Eco Tag 1 Stop 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34262   | Wochenplan HK Eco Tag 1 Start 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34263   | Wochenplan HK Eco Tag 1 Stop 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34264   | Wochenplan HK Eco Tag 2 Start 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34265   | Wochenplan HK Eco Tag 2 Stop 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34266   | Wochenplan HK Eco Tag 2 Start 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34267   | Wochenplan HK Eco Tag 2 Stop 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34268   | Wochenplan HK Eco Tag 2 Start 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34269   | Wochenplan HK Eco Tag 2 Stop 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34270   | Wochenplan HK Eco Tag 3 Start 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34271   | Wochenplan HK Eco Tag 3 Stop 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34272   | Wochenplan HK Eco Tag 3 Start 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34273   | Wochenplan HK Eco Tag 3 Stop 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34274   | Wochenplan HK Eco Tag 3 Start 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34275   | Wochenplan HK Eco Tag 3 Stop 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34276   | Wochenplan HK Eco Tag 4 Start 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34277   | Wochenplan HK Eco Tag 4 Stop 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34278   | Wochenplan HK Eco Tag 4 Start 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34279   | Wochenplan HK Eco Tag 4 Stop 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34280   | Wochenplan HK Eco Tag 4 Start 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34281   | Wochenplan HK Eco Tag 4 Stop 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34282   | Wochenplan HK Eco Tag 5 Start 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34283   | Wochenplan HK Eco Tag 5 Stop 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34284   | Wochenplan HK Eco Tag 5 Start 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34285   | Wochenplan HK Eco Tag 5 Stop 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34286   | Wochenplan HK Eco Tag 5 Start 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34287   | Wochenplan HK Eco Tag 5 Stop 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34288   | Wochenplan HK Eco Tag 6 Start 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34289   | Wochenplan HK Eco Tag 6 Stop 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34290   | Wochenplan HK Eco Tag 6 Start 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34291   | Wochenplan HK Eco Tag 6 Stop 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34292   | Wochenplan HK Eco Tag 6 Start 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34293   | Wochenplan HK Eco Tag 6 Stop 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34294   | Wochenplan HK Eco Tag 7 Start 0   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34295   | Wochenplan HK Eco Tag 7 Stop 0    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34296   | Wochenplan HK Eco Tag 7 Start 1   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34297   | Wochenplan HK Eco Tag 7 Stop 1    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34298   | Wochenplan HK Eco Tag 7 Start 2   |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34299   | Wochenplan HK Eco Tag 7 Stop 2    |                    |           |              |                                     | 0    | 95    | 0,25h    |
| 34304   | Raumtemperatur 1                  | 1.0.0              | 0         | 0            |                                     |      |       | 0,1°C    |
| 34305   | Raumtemperatur 2                  | 1.0.0              | 0         | 1            |                                     |      |       | 0,1°C    |
| 34306   | Raumtemperatur 3                  | 1.0.0              | 0         | 2            |                                     |      |       | 0,1°C    |
