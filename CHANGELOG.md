# Changelog

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
