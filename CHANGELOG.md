# Changelog

## [2.1.3](https://github.com/LarsK1/hass_solvis_control/compare/v2.1.2...v2.1.3) (2025-11-01)


### Bug Fixes

* change platform for hkr*_flow_type from select to sensor ([#341](https://github.com/LarsK1/hass_solvis_control/issues/341)) ([bddaa89](https://github.com/LarsK1/hass_solvis_control/commit/bddaa8967e891bedc175f5a016a8cdbdec984bf5))

## [2.1.2](https://github.com/LarsK1/hass_solvis_control/compare/v2.1.1...v2.1.2) (2025-09-27)


### Bug Fixes

* change keyword argument from client to device_id in pymodbus write_register (pymodbus &gt;= 4.0) ([72dae17](https://github.com/LarsK1/hass_solvis_control/commit/72dae170a1693f94c68ea97f475c9d85691c691d))
* change keyword argument from client to device_id in pymodbus write_register (pymodbus &gt;= 4.0) ([4d9c92b](https://github.com/LarsK1/hass_solvis_control/commit/4d9c92b4384ebe4e391a3af8f54d51bc4f059932))
* modify tests due to keyword argument change ([9c9f444](https://github.com/LarsK1/hass_solvis_control/commit/9c9f444b47eaeb4b5d71abcf20e89c1fb1a269c5))

## [2.1.1](https://github.com/LarsK1/hass_solvis_control/compare/v2.1.0...v2.1.1) (2025-09-08)


### Features

* add config option for custom hkr* naming ([5a0bff2](https://github.com/LarsK1/hass_solvis_control/commit/5a0bff28576411e3cfa20a0b89e4d926067ce7f0)), closes [#39](https://github.com/LarsK1/hass_solvis_control/issues/39)
* add new derived non-Modbus sensor "stored_energy_12" ([#307](https://github.com/LarsK1/hass_solvis_control/issues/307)) ([de2bd01](https://github.com/LarsK1/hass_solvis_control/commit/de2bd0119d297ca17464ed1a57d596f69ae7d01e))
* Migrate version sensors to Update platform ([#321](https://github.com/LarsK1/hass_solvis_control/issues/321)) ([dbab57d](https://github.com/LarsK1/hass_solvis_control/commit/dbab57d7d8b735f07ea667d61882d21f33527a40))


### Bug Fixes

* show heatpump_energy_thermal only if heatpump is configured ([d25be75](https://github.com/LarsK1/hass_solvis_control/commit/d25be758ff0ab377d416dd85de936d927591ac6a))
* show heatpump_energy_thermal only if heatpump is configured ([0ed5308](https://github.com/LarsK1/hass_solvis_control/commit/0ed53085d2af62d1b201eb3e4e371269f630038d))

## [2.1.0](https://github.com/LarsK1/hass_solvis_control/compare/v2.0.2...v2.1.0) (2025-05-12)


### ⚠ BREAKING CHANGES

* Release 2.1.0

### Bug Fixes

* **modbus:** improve connection handling and error management ([09903b1](https://github.com/LarsK1/hass_solvis_control/commit/09903b1e6b40820fb454f981b44ca0968a918d20)), closes [#264](https://github.com/LarsK1/hass_solvis_control/issues/264)
* **modbus:** improve connection handling and error management ([32c3d7d](https://github.com/LarsK1/hass_solvis_control/commit/32c3d7dc29190c47e0bce62ce1d2b213ab13d633))
* Release 2.1.0 ([4af2fa0](https://github.com/LarsK1/hass_solvis_control/commit/4af2fa00fd9e05251abb756dd4d482acac7bceb7))


### Miscellaneous Chores

* release 2.1.0 ([b5404de](https://github.com/LarsK1/hass_solvis_control/commit/b5404def3bf655be9adeaa79953268b0b795f0f5))

## [2.0.2](https://github.com/LarsK1/hass_solvis_control/compare/v2.0.1...v2.0.2) (2025-05-08)


### Features

* Added option to manually enter mac-address ([#292](https://github.com/LarsK1/hass_solvis_control/issues/292)) ([5562bd8](https://github.com/LarsK1/hass_solvis_control/commit/5562bd86dc13399143e7899b39f80ec8771e39de))


### Bug Fixes

* failing test "options_update_listener" in test_init.py ([d90cc80](https://github.com/LarsK1/hass_solvis_control/commit/d90cc801ed5d256ccda28632c2478b959eab0e1e))

## [2.0.1](https://github.com/LarsK1/hass_solvis_control/compare/v2.0.0...v2.0.1) (2025-04-30)


### Bug Fixes

* wrong spelling in issues name ([bae4035](https://github.com/LarsK1/hass_solvis_control/commit/bae40352755ef178f58e2d3926722a702973436f))

## [2.0.0](https://github.com/LarsK1/hass_solvis_control/compare/v2.0.0-beta.1...v2.0.0) (2025-04-27)


### ⚠ BREAKING CHANGES

* Increase release to 2.0.0

### Features

* Add new config step for hkrx room temp sensors ([29cef37](https://github.com/LarsK1/hass_solvis_control/commit/29cef37b975925faa3c38538e31fa978b21c6d6d)), closes [#232](https://github.com/LarsK1/hass_solvis_control/issues/232)
* Increase release to 2.0.0 ([04794eb](https://github.com/LarsK1/hass_solvis_control/commit/04794eb473699127f247b362b45f47e66b23aed7))
* Update documentation ([90719d4](https://github.com/LarsK1/hass_solvis_control/commit/90719d425568b4b1de49428034be3a6791bca30d))


### Bug Fixes

* add missing headers and change version to 2.0.0-beta.1 ([#257](https://github.com/LarsK1/hass_solvis_control/issues/257)) ([4db542a](https://github.com/LarsK1/hass_solvis_control/commit/4db542ad9d5cc131d1500202d96118c51fa53b5f))
* change Image size ([7ee5985](https://github.com/LarsK1/hass_solvis_control/commit/7ee59859fc3bb544e6df2edc99a03055687fbcd9))
* failing tests for sensor.py after changes ([3628e00](https://github.com/LarsK1/hass_solvis_control/commit/3628e0032509cdfdb35eef6a562282492ba2d037))
* missing translation for issue-registry ([a93957e](https://github.com/LarsK1/hass_solvis_control/commit/a93957e59542b41626ba50f5f42fb23abfb89a77))
* Modbus errors on SC2 due to unsupported registers ([6f9ea1a](https://github.com/LarsK1/hass_solvis_control/commit/6f9ea1ac9b0f6cff6422fc5a5d43c5ce541c13e6))
* obsolete division by zero warning ([b3cd1e3](https://github.com/LarsK1/hass_solvis_control/commit/b3cd1e34fcfe8a07284b6c72e3f7e1858cf5a44a))
* prevent connection error on consecutive modbus reads ([b8ad75a](https://github.com/LarsK1/hass_solvis_control/commit/b8ad75ae347bf1dd412de6579bdf68d0ca5de0d5))
* trailing spaces & typo in translation for issue registry ([1aa50c9](https://github.com/LarsK1/hass_solvis_control/commit/1aa50c9f57084215b79ade737161d138d07859d6))
* Update README.md ([b7c9bb6](https://github.com/LarsK1/hass_solvis_control/commit/b7c9bb643252f4a2ab472cf0da878fce71d8769a)), closes [#171](https://github.com/LarsK1/hass_solvis_control/issues/171)


### Miscellaneous Chores

* release 2.0.0 ([edf5b0e](https://github.com/LarsK1/hass_solvis_control/commit/edf5b0e6706fa827f98fdcbe21557724bb0adeb2))

## [2.0.0-beta.1](https://github.com/LarsK1/hass_solvis_control/compare/v2.0.0-alpha.11...v2.0.0-beta.1) (2025-03-31)


### Features

* add polling groups list ([bc23344](https://github.com/LarsK1/hass_solvis_control/commit/bc23344024923bbe603deed5fb1c6f0765bab8cc))
* add polling groups list ([65841d6](https://github.com/LarsK1/hass_solvis_control/commit/65841d6f352d8982d76978a08996046b55f55b84))
* add test_coordinator.py with coverage 100% ([860f3c4](https://github.com/LarsK1/hass_solvis_control/commit/860f3c41d74ee181db7913bcad5d11d5b673fd4f))
* add test_diagnostics.py with coverage 100% ([30d6fda](https://github.com/LarsK1/hass_solvis_control/commit/30d6fdaf2168c1250d8927ed250755f10c64050b))
* add test_helpers.py with coverage 100% ([4c48cde](https://github.com/LarsK1/hass_solvis_control/commit/4c48cde874123a0fade40a89878688e2345649a5)), closes [#158](https://github.com/LarsK1/hass_solvis_control/issues/158)
* add test_init with coverage 100% ([7f0ca0e](https://github.com/LarsK1/hass_solvis_control/commit/7f0ca0ed848420f835ca86b564d9518084ce38c0))
* Added code coverage ([0327180](https://github.com/LarsK1/hass_solvis_control/commit/03271804dc2fef2b94361d0bdd2ad3df8c06e7d8))
* deduplicate code: write_modbus_value ([ce77e7c](https://github.com/LarsK1/hass_solvis_control/commit/ce77e7c90ac9932ecb991cfbad5d428a1cc2eb2f))
* extend and improve config flow texts ([bed00f7](https://github.com/LarsK1/hass_solvis_control/commit/bed00f7c3475912251822409c0ed3643c835e83f))
* extend and improve config flow texts ([def06af](https://github.com/LarsK1/hass_solvis_control/commit/def06af412da03fde935708d1e522a6676bbfbae))
* extract Modbus write operations and fix unique_id consistency ([984b8bc](https://github.com/LarsK1/hass_solvis_control/commit/984b8bc914cf8eef508fc193bfd94157a44be585))
* increase config_flow test coverage to 74% ([b47f463](https://github.com/LarsK1/hass_solvis_control/commit/b47f4634e6b3788002180abbd9f404e0d8c79a56))
* increase config_flow test coverage to 74% ([71cd5ff](https://github.com/LarsK1/hass_solvis_control/commit/71cd5ff5d47634460a567a3a36fe44ccbc6b9868))
* increase config_flow test coverage to 93% ([7583279](https://github.com/LarsK1/hass_solvis_control/commit/75832793a09067c98265291edfd4e88b53f72868))
* increase config_flow test coverage to 93% ([bca7ae9](https://github.com/LarsK1/hass_solvis_control/commit/bca7ae9b3b3b31a1ad0803bc5d2d79d7e1f665c2))
* increase config_flow test coverage to 98% ([fd40b57](https://github.com/LarsK1/hass_solvis_control/commit/fd40b570f805b87d21b0ccaa8016af2571d9c069))
* increase overall test coverage to 57% ([51e4d9d](https://github.com/LarsK1/hass_solvis_control/commit/51e4d9dcb4148045cb6846b977be3041f28f2af1))
* increase overall test coverage to 57% ([943b43a](https://github.com/LarsK1/hass_solvis_control/commit/943b43a2fa4494b8845bc90475315ae89845055f))
* increase overall test coverage to 84% ([0e19494](https://github.com/LarsK1/hass_solvis_control/commit/0e19494ffa650204fa64df78e1cd6a7ce5ab6977))
* increase test coverage ([bb40208](https://github.com/LarsK1/hass_solvis_control/commit/bb40208cecd3f63b61a35b49875114fbaf1f8709))
* Increase test coverage for config_flow.py to 100% ([758e34f](https://github.com/LarsK1/hass_solvis_control/commit/758e34f751299f1de3b638debec2e8989e1274bb))
* increase test coverage for select.py ([027f41d](https://github.com/LarsK1/hass_solvis_control/commit/027f41d1d218e1a385955377518e27063894e87b))
* increase test coverage of select.py ([0aa8fbd](https://github.com/LarsK1/hass_solvis_control/commit/0aa8fbd62672176948acd3d4bdc01145b2ac159c))
* increase test coverage of test.py to 91% ([476993f](https://github.com/LarsK1/hass_solvis_control/commit/476993fd3f2f353b2c55f97f1c43d01303cab6e8))
* refactor all sensor modules ([364c966](https://github.com/LarsK1/hass_solvis_control/commit/364c966897fbf543c4f85f555fea21888d9500ce)), closes [#159](https://github.com/LarsK1/hass_solvis_control/issues/159)
* **Sensors:** add temperatur sensor s16 (input-register 33039) ([36c268b](https://github.com/LarsK1/hass_solvis_control/commit/36c268bcbb80da3b2b79bac9c9bb0ac4b9d3f24d))
* solve misc bugs and inconsistencies ([13ad8d1](https://github.com/LarsK1/hass_solvis_control/commit/13ad8d196d62cfde03f7a0d5778a823f91fbf453))
* **test:** Increase coverage to 32% & improve testing ([74ab171](https://github.com/LarsK1/hass_solvis_control/commit/74ab171e1433b60e3fb523f57a70eac3c102aeef))


### Bug Fixes

* (only partly) hkr1_room_temp can not be set via ui ([33db8e1](https://github.com/LarsK1/hass_solvis_control/commit/33db8e14c9f5788b0d3c36d5e0a652b6550e37d7))
* (only partly) hkr1_room_temp can not be set via ui ([c1de8c0](https://github.com/LarsK1/hass_solvis_control/commit/c1de8c0fd8400d234059eb1224f780b6e591862c))
* add missing argument subentries_data ([1ef889b](https://github.com/LarsK1/hass_solvis_control/commit/1ef889b7b4e06d7a01e9ff57fb6306beecae3ffa))
* async call of async_remove & lint ([330e7c6](https://github.com/LarsK1/hass_solvis_control/commit/330e7c6d8b08c0234b84f09881022e03b74d70aa))
* await async_add_entities ([a0f790b](https://github.com/LarsK1/hass_solvis_control/commit/a0f790bbbb528575b0902bdcb1f12e4adea840f6))
* Consistent setting of unique_id using ._attr_unique_id ([cf7713f](https://github.com/LarsK1/hass_solvis_control/commit/cf7713fb9cb09de97dcdaf104107cd8b791c59f2))
* failing lint ([90d9b4e](https://github.com/LarsK1/hass_solvis_control/commit/90d9b4ea6c23b7d57c6d1884252cd36b42b7f61e))
* failing lint-check ([45b1963](https://github.com/LarsK1/hass_solvis_control/commit/45b19637fd066032c03eca4903e8fa1369fce38a))
* failing test_select ([eebf668](https://github.com/LarsK1/hass_solvis_control/commit/eebf66855ddf75178afeffd9d51bd17fc29f0b4e))
* failing tests ([ec0cd7e](https://github.com/LarsK1/hass_solvis_control/commit/ec0cd7e166621eb679778d58cc8dd133fe1418c7))
* failing tests ([e8b6e9e](https://github.com/LarsK1/hass_solvis_control/commit/e8b6e9e093b67845575e0e141b3a6e0c989c6e79))
* failing tests ([185e01c](https://github.com/LarsK1/hass_solvis_control/commit/185e01c3de34fde90cc35d2c78e55f6deb7bd924))
* failing tests - again ([c954772](https://github.com/LarsK1/hass_solvis_control/commit/c954772a1cfc332991201327a5b98e7d9ce8609a))
* failing tests and type errors ([2221d5b](https://github.com/LarsK1/hass_solvis_control/commit/2221d5b6149680558b34c18d8e218ad02bb9cb81))
* failing tests due to missing arguments ([9e668f5](https://github.com/LarsK1/hass_solvis_control/commit/9e668f562feee61b4ab151d197d44c01d69b06a8))
* failing tests due to missing import ([ab63a95](https://github.com/LarsK1/hass_solvis_control/commit/ab63a9539ce3965f8c4f6717204fe026faf67659))
* failing tests due to missing loop ([8547a04](https://github.com/LarsK1/hass_solvis_control/commit/8547a048e940bffd5349522f25a853421be1ef37))
* failing tests due to wrong mocks ([684844b](https://github.com/LarsK1/hass_solvis_control/commit/684844bd551450050cb5ae5ffc6f1a65508f96b7))
* failing tests for select.py ([d5f38fa](https://github.com/LarsK1/hass_solvis_control/commit/d5f38fae1124916b5735dacb389846f71bbf5e94))
* failing tests for select.py ([a5cbb80](https://github.com/LarsK1/hass_solvis_control/commit/a5cbb800e28af2673bfce799105d6cde09eb0dc6))
* hkrx_room_temp can not be set via ui ([bbd0a35](https://github.com/LarsK1/hass_solvis_control/commit/bbd0a35df1f5edb02e0324d3b66f4bd980fc7e1f))
* hkrx_room_temp can not be set via ui ([1904247](https://github.com/LarsK1/hass_solvis_control/commit/19042470fd23b2fa3bd5a3a9b07f519655dd8134))
* **logging:** change to f-strings ([5f1cde7](https://github.com/LarsK1/hass_solvis_control/commit/5f1cde71c9649aa0b00e0a9fc3790397843c8105))
* missing label and description for hkr in config_flow ([83ed498](https://github.com/LarsK1/hass_solvis_control/commit/83ed498ae54937dd3344c9cef10fdb9b0df721c6))
* missing label and description for hkr in config_flow ([14ed793](https://github.com/LarsK1/hass_solvis_control/commit/14ed793d55c4b4c2a6780fdbb15971f74575cca0))
* mixed up usage of entity_id and unique_id in select.py ([7ef987c](https://github.com/LarsK1/hass_solvis_control/commit/7ef987ca3da2baa12c0169ec95e9ba22cece51a7))
* rebuild testing base structure ([9101593](https://github.com/LarsK1/hass_solvis_control/commit/9101593f3463a0ef9ef79bc3af4c918e684c2a06))
* rebuild testing base structure ([fa3b059](https://github.com/LarsK1/hass_solvis_control/commit/fa3b05963b2c14b1fb436ee835d0e2d4340aae05))
* remove debug messages ([72087f4](https://github.com/LarsK1/hass_solvis_control/commit/72087f4fda0f8df2d0045c31be1c82e1316c36c0))
* resolve failing tests in test_select.py ([c5d222b](https://github.com/LarsK1/hass_solvis_control/commit/c5d222b282de26c1b135238a76ebbe80367afd0e))
* solve misc bugs and inconsistencies ([89eea23](https://github.com/LarsK1/hass_solvis_control/commit/89eea235feece1c0f7686b36c54eb8a525183667))
* use genuine hass fixture ([9cdb695](https://github.com/LarsK1/hass_solvis_control/commit/9cdb695c03dd112171fc22264e23059fc8a5dc3e))
* wrong data validation and failing tests ([26afa85](https://github.com/LarsK1/hass_solvis_control/commit/26afa85ccdf44b8740ef96a2e0e623637f9334f3))


### Miscellaneous Chores

* release 2.0.0-beta.1 ([309ac33](https://github.com/LarsK1/hass_solvis_control/commit/309ac33988370da5749fe5eb26743f5a0adff54b))

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
