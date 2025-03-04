# Changelog

## [2.0.0-alpha.11](https://github.com/LarsK1/hass_solvis_control/compare/v2.0.0-alpha.10...v2.0.0-alpha.11) (2025-03-04)


### Features

* Add config-flow-test-coverage ([df5f5df](https://github.com/LarsK1/hass_solvis_control/commit/df5f5df7df279552ca5dda22e48db2c0dfb775ac))
* add configflow option 8 - pv2heat ([0a47eda](https://github.com/LarsK1/hass_solvis_control/commit/0a47eda0168ebe7417594f433e3163c248df64cd)), closes [#183](https://github.com/LarsK1/hass_solvis_control/issues/183)
* Add new & change existing entities ([a5b0ca2](https://github.com/LarsK1/hass_solvis_control/commit/a5b0ca273a99ecb46f1b7b29698af216390107cc)), closes [#55](https://github.com/LarsK1/hass_solvis_control/issues/55)
* Add new & change existing entities ([24bdfec](https://github.com/LarsK1/hass_solvis_control/commit/24bdfec3118daac944415767f64b850340ac36d5)), closes [#55](https://github.com/LarsK1/hass_solvis_control/issues/55)
* Add new entities ([0a13960](https://github.com/LarsK1/hass_solvis_control/commit/0a13960ea56b6f481096dc1c7b9ebd12fcd07134)), closes [#173](https://github.com/LarsK1/hass_solvis_control/issues/173)
* Add new entities ([19de1fa](https://github.com/LarsK1/hass_solvis_control/commit/19de1fa45c78b1ced04c5432f4834ae228822c62)), closes [#173](https://github.com/LarsK1/hass_solvis_control/issues/173)
* Add PV2Heat energy ([42c77be](https://github.com/LarsK1/hass_solvis_control/commit/42c77be952f5902682e2aab091b84fde818e3e76)), closes [#173](https://github.com/LarsK1/hass_solvis_control/issues/173) [#54](https://github.com/LarsK1/hass_solvis_control/issues/54)
* Add PV2Heat energy ([413f233](https://github.com/LarsK1/hass_solvis_control/commit/413f2330aec4785299b0dcbd26818ff91ccf742c)), closes [#54](https://github.com/LarsK1/hass_solvis_control/issues/54)
* add pv2heat_power_electric (reg. 33548) ([1307633](https://github.com/LarsK1/hass_solvis_control/commit/1307633c8e5efd99776977867a6b72b628420bd0)), closes [#55](https://github.com/LarsK1/hass_solvis_control/issues/55)
* add pv2heat_power_electric (reg. 33548) ([2a94879](https://github.com/LarsK1/hass_solvis_control/commit/2a94879b9791037c2d30eb87562a7ce43e7a1a47)), closes [#55](https://github.com/LarsK1/hass_solvis_control/issues/55)
* Adjust release-please-config ([7df403b](https://github.com/LarsK1/hass_solvis_control/commit/7df403b1a54d1ec052afed8e7ca37b7d39e61cf2))
* Adjust release-please-config ([cf01676](https://github.com/LarsK1/hass_solvis_control/commit/cf01676b4865039041508add93b5f2d09e6369be))
* Convert entites HKRx_flow_type to select ([ecec8db](https://github.com/LarsK1/hass_solvis_control/commit/ecec8dba4c666bea18c1d00d53e232dc957db558)), closes [#156](https://github.com/LarsK1/hass_solvis_control/issues/156)
* Device network discovery ([#179](https://github.com/LarsK1/hass_solvis_control/issues/179)) ([7b7424c](https://github.com/LarsK1/hass_solvis_control/commit/7b7424c4ef2c87d2549781782bf2b3f247bff06a))
* final changes for config flow tests ([9366272](https://github.com/LarsK1/hass_solvis_control/commit/93662729ba7bd27bb85ea26d2d89748866bd899b))
* Move modbus-handling from config_flow.py to helpers ([bffde99](https://github.com/LarsK1/hass_solvis_control/commit/bffde99f325ce59d59e535fe8d6a626fd63d09ba))
* Naming completely revised and standardized ([#192](https://github.com/LarsK1/hass_solvis_control/issues/192)) ([82685b4](https://github.com/LarsK1/hass_solvis_control/commit/82685b4c885ad410e44b587781a44d6471a685be))
* Try to autodetect amount of hkr using modbus values ([72538c3](https://github.com/LarsK1/hass_solvis_control/commit/72538c356c76f9e031410265f356987aa002e639)), closes [#188](https://github.com/LarsK1/hass_solvis_control/issues/188)
* Update latest firmware version ([4d8b2c4](https://github.com/LarsK1/hass_solvis_control/commit/4d8b2c4962281d2143f52da2d8b95591e34cf504))
* use data_description [#160](https://github.com/LarsK1/hass_solvis_control/issues/160) ([4736c16](https://github.com/LarsK1/hass_solvis_control/commit/4736c163e8f2e97dd288e2e5a78dc05fdb1a7a83))
* use runtime-data [#160](https://github.com/LarsK1/hass_solvis_control/issues/160) and cleanup of __init__.py [#159](https://github.com/LarsK1/hass_solvis_control/issues/159) ([9ce6550](https://github.com/LarsK1/hass_solvis_control/commit/9ce6550b8473c1f0660df3adb4b82b9511754bad))
* various cleanup for release ([3591db5](https://github.com/LarsK1/hass_solvis_control/commit/3591db594765b6d0a5ef85f9506cc60f69ed75d5))


### Bug Fixes

* adjust release-please-config.json ([8f9e705](https://github.com/LarsK1/hass_solvis_control/commit/8f9e70576383e228d64266d9294b9ee035e17124))
* catch more errors in ConfigFlow ([def635f](https://github.com/LarsK1/hass_solvis_control/commit/def635fcf2157340db0e8a3bf1e554ab9221e546))
* change entites for modbus-writting temperature sensor (Fix for [#168](https://github.com/LarsK1/hass_solvis_control/issues/168)) ([a3974e0](https://github.com/LarsK1/hass_solvis_control/commit/a3974e08f89a895904838d6bdd09d93203e30681))
* Change state_classes for energy devices to total_increasing ([5abe139](https://github.com/LarsK1/hass_solvis_control/commit/5abe1399313e814bb2f418fcaed7eed34e031666))
* correction for wrong spelling ([97cc2a9](https://github.com/LarsK1/hass_solvis_control/commit/97cc2a94914894e561982f6040c833fd0722261c))
* hkr1 write feature ([24b7f70](https://github.com/LarsK1/hass_solvis_control/commit/24b7f7055776a0918e3075e19dd448559623a3da))
* hkr1_room_temperature write feature ([e18a3ae](https://github.com/LarsK1/hass_solvis_control/commit/e18a3aed412ab8beeccada506f662847c6e8cb9e))
* hkr1_room_temperature write feature ([e18a3ae](https://github.com/LarsK1/hass_solvis_control/commit/e18a3aed412ab8beeccada506f662847c6e8cb9e))
* linting errors ([82ea91f](https://github.com/LarsK1/hass_solvis_control/commit/82ea91f6df3456bacac53ad47ad3ffb0a90181a1))
* manual installation instructions in readme.md ([16922f1](https://github.com/LarsK1/hass_solvis_control/commit/16922f19fbe87af14dd8cb40071d27f0f2f745fd))
* remove deprecated strings.json ([fe7cb30](https://github.com/LarsK1/hass_solvis_control/commit/fe7cb3047023495eab8f13a1324f93879413c9ba))
* set warm_water_pump_o5_status to enabled by default ([9e6c27c](https://github.com/LarsK1/hass_solvis_control/commit/9e6c27c6c6191fbe0c9df731c8b8b2f907922ad4))
* small adjustments ([f8675c9](https://github.com/LarsK1/hass_solvis_control/commit/f8675c9fc65f4966bf7a6ae043b7f0c568b92b49))
* small adjustments ([e09b2f1](https://github.com/LarsK1/hass_solvis_control/commit/e09b2f14567e22f0f42f150089e063bde1f3a7ff))


### Miscellaneous Chores

* release 2.0.0-alpha.11 ([2e1002a](https://github.com/LarsK1/hass_solvis_control/commit/2e1002a16fae9640af80e019fe837614201fffbe))

## [2.0.0-alpha.10](https://github.com/LarsK1/hass_solvis_control/compare/v2.0.0-alpha.9...v2.0.0-alpha.10) (2025-02-23)


### Bug Fixes

* respect entities without specific configuration ([7daf748](https://github.com/LarsK1/hass_solvis_control/commit/7daf748483d53bc85c8b2ba67eb7d258218eabc3))


### Miscellaneous Chores

* release 2.0.0-alpha.10 ([db8be87](https://github.com/LarsK1/hass_solvis_control/commit/db8be87444c13fbac826ff633aa0475c4b927fbc))

## [2.0.0-alpha.9](https://github.com/LarsK1/hass_solvis_control/compare/v2.0.0-alpha.8...v2.0.0-alpha.9) (2025-02-23)


### Features

* Add Analog Out Ox ([#147](https://github.com/LarsK1/hass_solvis_control/issues/147)) ([13d3cd3](https://github.com/LarsK1/hass_solvis_control/commit/13d3cd32bce3643475aa8f932ff4b023e70eed06))
* added new feature toggle for heat meter ([db43bd6](https://github.com/LarsK1/hass_solvis_control/commit/db43bd6fa015bde1905d24ea0cbd96c55d9ef0ec)), closes [#146](https://github.com/LarsK1/hass_solvis_control/issues/146)
* completed changing names in const.py ([7ffab96](https://github.com/LarsK1/hass_solvis_control/commit/7ffab96f61b3f003295617e2bdba129d3e2a76f2))
* comprehensive name changes; completely revised Analog Out Ox Status & Ausgänge Ax; added A6, A7, A10, A11, A13 as binary sensors ([#140](https://github.com/LarsK1/hass_solvis_control/issues/140)) ([c3431ea](https://github.com/LarsK1/hass_solvis_control/commit/c3431ea293c8e6e9b29032d83b5175afb87d616d))
* initial changes for consistent entity names ([02b8e78](https://github.com/LarsK1/hass_solvis_control/commit/02b8e786ee7e15b6485ae0fac44a4b053563ae5f))
* more changes for consistent entity names ([3f666f6](https://github.com/LarsK1/hass_solvis_control/commit/3f666f657e2fb1e25f6dee6c2ea7ef7a1fc13ebc))
* restructured feature_checking and allow for and conditions ins entity feature check ([7154cb2](https://github.com/LarsK1/hass_solvis_control/commit/7154cb282ff9cd6b348c05b13f3ecce4e4cb8e44)), closes [#10](https://github.com/LarsK1/hass_solvis_control/issues/10)
* Store raw or unprocessed values in entities extra attributes ([#149](https://github.com/LarsK1/hass_solvis_control/issues/149)) ([1a9df57](https://github.com/LarsK1/hass_solvis_control/commit/1a9df5702bc32f89e3255df54d06bb0d212dca55))


### Bug Fixes

* added missing migration for new entites ([ae0a33a](https://github.com/LarsK1/hass_solvis_control/commit/ae0a33af77d4cb16e629e1155b0445b8a8e65be5))
* adjust mixed tab / spaces ([0e3096a](https://github.com/LarsK1/hass_solvis_control/commit/0e3096a33e8fe4d44ab4e8a88a576c012b247fcc))
* Adjustments for strings.json, icons.json, and sync to de.json ([72c9b37](https://github.com/LarsK1/hass_solvis_control/commit/72c9b37fef635a66846246361b9e80067958b4aa))
* change release-please-config ([de05302](https://github.com/LarsK1/hass_solvis_control/commit/de053022d003b5bc8f2d698eb1c1e0418baab087))
* changed logic order ([8e91585](https://github.com/LarsK1/hass_solvis_control/commit/8e915856e6425859508c7d879fbf582aba7868ee))
* correct interpretation of register 33045 ([#135](https://github.com/LarsK1/hass_solvis_control/issues/135)) ([c856f11](https://github.com/LarsK1/hass_solvis_control/commit/c856f11fedc803caf463003529e0a585a8432307))
* debug-logging ([095538d](https://github.com/LarsK1/hass_solvis_control/commit/095538d5651ffa0e761eb4a4c1aeee7eda4885ff))
* enshure, coordinator has time values in all cases ([d46b577](https://github.com/LarsK1/hass_solvis_control/commit/d46b57746ff0f84cda01875721b18400ba43289b))
* fully add documentation for naming-convention ([0433529](https://github.com/LarsK1/hass_solvis_control/commit/04335298559cb5a8f72c847ecf96a775d293bdb8))
* invert wrong condition ([85f7b68](https://github.com/LarsK1/hass_solvis_control/commit/85f7b68762cfe269016ae6e32c58520e5cfafdf8))
* lint fixes ([8ef8fb2](https://github.com/LarsK1/hass_solvis_control/commit/8ef8fb284a705bc1a590543bac4e1d6ff29229af))
* more fixes ([a96bc48](https://github.com/LarsK1/hass_solvis_control/commit/a96bc48513eca69de3bf8a063a1eeb8a96242e0d))
* more fixes ([88cbfa1](https://github.com/LarsK1/hass_solvis_control/commit/88cbfa12c636c3a61a61fae64c5e83fa5c8bfe47))
* respect entities without specific configuration ([0e348d5](https://github.com/LarsK1/hass_solvis_control/commit/0e348d5ab9f687dff2aa741c150768a22f8a7437))
* Update release-please.yml ([8e38403](https://github.com/LarsK1/hass_solvis_control/commit/8e384037364f0ad7f35a109deb87bf3b520d0225))
* wrong identation in icons.json ([4f8cd6b](https://github.com/LarsK1/hass_solvis_control/commit/4f8cd6b48a6ebf2ec079a29fd51c86bb0c489730))
* wrong identation in icons.json ([1521f3d](https://github.com/LarsK1/hass_solvis_control/commit/1521f3d01124fbb772e94fadc55ecc051c472a09))


### Miscellaneous Chores

* release 2.0.0-alpha.9 ([1caa4d2](https://github.com/LarsK1/hass_solvis_control/commit/1caa4d291e54c87e24dfe52abb1ad08fe1b8b4c4))

## [2.0.0-alpha.8](https://github.com/LarsK1/hass_solvis_control/compare/2.0.0-alpha6...v2.0.0-alpha.8) (2025-02-16)


### Features

* added custom icons to all entites ([f283273](https://github.com/LarsK1/hass_solvis_control/commit/f2832732825aed80ae9668a1ddba8e44bc51e3ad))
* added new entity ([#96](https://github.com/LarsK1/hass_solvis_control/issues/96)) ([1fdaf3d](https://github.com/LarsK1/hass_solvis_control/commit/1fdaf3d105cb7e3077862829e6d38f699efa7f74))
* automatic version update on release ([022b319](https://github.com/LarsK1/hass_solvis_control/commit/022b31931bc8a5c6810be7792d2836b374d2ad57))
* automatically close issue, that didn't use the issue reporting template ([f8c55eb](https://github.com/LarsK1/hass_solvis_control/commit/f8c55eb95e705f2186f98077c4ea353323476f1c))
* remove debug-logging and provide raw values in extra-state-attributes ([caca534](https://github.com/LarsK1/hass_solvis_control/commit/caca534910cd73e1aa558c72951b2905db5a0603))
* set entites to unavailable, if fetching data fails. ([608af2d](https://github.com/LarsK1/hass_solvis_control/commit/608af2d119f4a69eb95afbc6547a1db8c0fd16f0))


### Bug Fixes

* Added multiplier to A8/9 Mischer Heizkreis 1 auf / zu ([ed2f5d6](https://github.com/LarsK1/hass_solvis_control/commit/ed2f5d66aae7eaa165a879615fe277d428564cf7))
* Adjusted correct spelling for icon ([42758ea](https://github.com/LarsK1/hass_solvis_control/commit/42758eace8d694e80af2c8d333e49ba69963bd78))
* auto-labelling for translations ([97196ad](https://github.com/LarsK1/hass_solvis_control/commit/97196ad795028f1a105539bc8645d11dbe354c22))
* Changed attribute to correct name ([720e3b2](https://github.com/LarsK1/hass_solvis_control/commit/720e3b245ed82eeb36efdce901b66e044f59a3ab))
* compatibility with &gt;HA 2025.2.x ([323d6c2](https://github.com/LarsK1/hass_solvis_control/commit/323d6c243f771a26d9714e5fae184e7f754417ca))
* lint-errors ([a290b8a](https://github.com/LarsK1/hass_solvis_control/commit/a290b8a32e724f323ef632abfd7000247bdce3ec))
* more fixes for autoclose-issues.yml ([60ec6bb](https://github.com/LarsK1/hass_solvis_control/commit/60ec6bb8dd68a4e983500cff69492d6886a46b00))
* more fixes for autoclose-issues.yml ([0cd4288](https://github.com/LarsK1/hass_solvis_control/commit/0cd42885bcbfd7bc852a9d65a24706b461486e81))
* Release alpha7 ([989ea8f](https://github.com/LarsK1/hass_solvis_control/commit/989ea8fe9dd2ec76ec4e94139e296364c9ce5bed))
* Remove autoclose due to not working ([6e17f2c](https://github.com/LarsK1/hass_solvis_control/commit/6e17f2c73c4a7ceed7e9d0255d67d9c91a1ff379))
* use SemVer ([48975d7](https://github.com/LarsK1/hass_solvis_control/commit/48975d73d5d59420127803e32bc3cbeae5780c01))
* wrong file name ([84725b9](https://github.com/LarsK1/hass_solvis_control/commit/84725b9243e48a8c91191a1cd5e802e30d95d667))


### Miscellaneous Chores

* release 2.0.0-alpha.8 ([6c0b357](https://github.com/LarsK1/hass_solvis_control/commit/6c0b357542f163aaf69cae8f36dbc49a1cd8879a))
