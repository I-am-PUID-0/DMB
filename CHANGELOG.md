# Changelog

## [6.13.0](https://github.com/I-am-PUID-0/DMB/compare/6.12.1...6.13.0) (2025-06-17)


### ✨ Features

* **api:** add service update request [#78](https://github.com/I-am-PUID-0/DMB/issues/78) ([a2e4a04](https://github.com/I-am-PUID-0/DMB/commit/a2e4a0415185e582f721305952a1d0d434d9e273))
* **decypharr:** add decypharr_enabled flag and update rclone setup logic ([650557f](https://github.com/I-am-PUID-0/DMB/commit/650557f43b4fe26b6523cdf89bb1bde82f080a65))
* **decypharr:** add support for Decypharr configuration and setup ([fd3b284](https://github.com/I-am-PUID-0/DMB/commit/fd3b284840d33400fa7511c8bd79e5c743a61107)), closes [#158](https://github.com/I-am-PUID-0/DMB/issues/158)


### 🐛 Bug Fixes

* **cli_battery:** add PYTHONPATH to environment variables in config ([8667c56](https://github.com/I-am-PUID-0/DMB/commit/8667c564988f230435e4088b195ddcf6f7c244fb))
* **workflow:** update Git configuration and improve Dependabot rebase process ([c59b5dd](https://github.com/I-am-PUID-0/DMB/commit/c59b5dda848b610a5e71768b640f3f040e874191))


### 🤡 Other Changes

* **deps:** bump h11 from 0.14.0 to 0.16.0 in the pip group ([#143](https://github.com/I-am-PUID-0/DMB/issues/143)) ([f1707c2](https://github.com/I-am-PUID-0/DMB/commit/f1707c2629ad8a6d3e85f4bcd77faf44de2405c0))
* **deps:** bump jsonschema from 4.23.0 to 4.24.0 ([#162](https://github.com/I-am-PUID-0/DMB/issues/162)) ([9d814ee](https://github.com/I-am-PUID-0/DMB/commit/9d814ee6148f97bbe596ff893eab5fb5b732dae8))
* **deps:** bump pydantic from 2.11.4 to 2.11.7 ([#169](https://github.com/I-am-PUID-0/DMB/issues/169)) ([b80059c](https://github.com/I-am-PUID-0/DMB/commit/b80059c544984a122654d8f468beb2693d681476))
* **deps:** bump ruamel-yaml from 0.18.10 to 0.18.14 ([#168](https://github.com/I-am-PUID-0/DMB/issues/168)) ([c02d252](https://github.com/I-am-PUID-0/DMB/commit/c02d2522741d2c0ab40360a8d55cc4e15e79ed55))
* **deps:** bump uvicorn from 0.34.2 to 0.34.3 ([#165](https://github.com/I-am-PUID-0/DMB/issues/165)) ([950bbf6](https://github.com/I-am-PUID-0/DMB/commit/950bbf6946fddcf0e272eaa288373b1bbd173456))


### 🚀 CI/CD Pipeline

* **dependabot:** add workflow for testing combined Dependabot updates ([09b8cd7](https://github.com/I-am-PUID-0/DMB/commit/09b8cd7c2ffe8e83c021b4311ee1a32f3e32929a))


### 🛠️ Refactors

* **api:** use auto-update functionality and error handling ([a2e4a04](https://github.com/I-am-PUID-0/DMB/commit/a2e4a0415185e582f721305952a1d0d434d9e273))

## [6.12.1](https://github.com/I-am-PUID-0/DMB/compare/6.12.0...6.12.1) (2025-05-09)


### 🐛 Bug Fixes

* **auto_update:** release version handling for nightly and prerelease updates ([c9e205f](https://github.com/I-am-PUID-0/DMB/commit/c9e205fd0eec9c783db7fad5754ded34f6911eb8))

## [6.12.0](https://github.com/I-am-PUID-0/DMB/compare/6.11.0...6.12.0) (2025-05-09)


### ✨ Features

* **rclone:** adds multiple debrid service support for direct connections using webdav or ftp ([e5b5390](https://github.com/I-am-PUID-0/DMB/commit/e5b539098bcfe879a46b7c1626b297f8b64084e7))


### 🐛 Bug Fixes

* **funding:** correct syntax for GitHub funding configuration ([590c109](https://github.com/I-am-PUID-0/DMB/commit/590c1092c5fdb1979835ff807088a9c6108d2fa0))


### 🤡 Other Changes

* **funding:** add initial funding configuration for GitHub sponsors ([88bc9b9](https://github.com/I-am-PUID-0/DMB/commit/88bc9b9b13a75cb22b2542bd9ca9c0c7054de8d1))

## [6.11.0](https://github.com/I-am-PUID-0/DMB/compare/6.10.0...6.11.0) (2025-05-08)


### ✨ Features

* **api process:** add static URLs for services and include repository URL in process list ([af3f4b6](https://github.com/I-am-PUID-0/DMB/commit/af3f4b662c9de75182b17ef97a063ffb5827831f))

## [6.10.0](https://github.com/I-am-PUID-0/DMB/compare/6.9.3...6.10.0) (2025-05-08)


### ✨ Features

* **auto-update:** enhance logging and version handling for updates; support prerelease and nightly checks ([60dd280](https://github.com/I-am-PUID-0/DMB/commit/60dd2804dffdc17c5148c5fb6ea3f732c04da21d))

## [6.9.3](https://github.com/I-am-PUID-0/DMB/compare/6.9.2...6.9.3) (2025-05-07)


### 🐛 Bug Fixes

* **rclone:** Fixes mount directory ownership ([1fee36e](https://github.com/I-am-PUID-0/DMB/commit/1fee36e0432c7f74d4e52b28c0f9c21e72f2a7a2))
* **setup:** add check to prevent duplicate venv path in exclude_dirs ([3acd131](https://github.com/I-am-PUID-0/DMB/commit/3acd1317bce502b2061a576998b5036d63e3ef8c))

## [6.9.2](https://github.com/I-am-PUID-0/DMB/compare/6.9.1...6.9.2) (2025-05-06)


### 🐛 Bug Fixes

* **api process:** include config key in fetch_process response ([7598b73](https://github.com/I-am-PUID-0/DMB/commit/7598b733957cb277d828f0b8e4168965177a7b58))
* **api process:** rename key to config_key in fetch_process response - because words matter [@nicocapalbo](https://github.com/nicocapalbo) :P ([20a2f9a](https://github.com/I-am-PUID-0/DMB/commit/20a2f9acc2bb89b9d6bc8436d9b7dbf48b9063a4))

## [6.9.1](https://github.com/I-am-PUID-0/DMB/compare/6.9.0...6.9.1) (2025-05-06)


### 🐛 Bug Fixes

* **api process:** ensure project setup is completed before restarting the service ([f7a500c](https://github.com/I-am-PUID-0/DMB/commit/f7a500c933ebce462784ae17d25d2d6b732dce7c))
* **logger:** remove redundant environment variable assignments for log level ([e19b9f2](https://github.com/I-am-PUID-0/DMB/commit/e19b9f2a9f7b377e0975442696716a9b7399546a))
* **processes:** set log level in environment for 'zurg' key in process handler ([e19b9f2](https://github.com/I-am-PUID-0/DMB/commit/e19b9f2a9f7b377e0975442696716a9b7399546a))
* **rclone:** add cache directory option to rclone command in rclone_setup ([d11daad](https://github.com/I-am-PUID-0/DMB/commit/d11daad96ca7d91169aa55226a4122e7fbeb3d8b))
* **setup:** add log level option to rclone command in rclone setup ([e19b9f2](https://github.com/I-am-PUID-0/DMB/commit/e19b9f2a9f7b377e0975442696716a9b7399546a))
* **setup:** update riven_backend command handling to ensure port substitution ([ff63b14](https://github.com/I-am-PUID-0/DMB/commit/ff63b14b2cb1b555e270cfb18e316754320480bb))
* **workflows:** correct typo in echo command for CLI_DEBRID_TAG in fetch-latest-tags ([d2a47b7](https://github.com/I-am-PUID-0/DMB/commit/d2a47b7cd33bb16d187e90352e7d8ad9a9ad926d))


### 🛠️ Refactors

* **rclone:** updates rclone command generation ([d0972b2](https://github.com/I-am-PUID-0/DMB/commit/d0972b234d3f235138fa9fb37b5348b8e2191957))
* rearranges config loading and process updates ([16b9a5a](https://github.com/I-am-PUID-0/DMB/commit/16b9a5ab7c13a38ee36cbbda31ebacdee37d391e))

## [6.9.0](https://github.com/I-am-PUID-0/DMB/compare/6.8.2...6.9.0) (2025-04-30)


### ✨ Features

* **cli_battery:** add configuration for CLI Battery integration ([1c73a60](https://github.com/I-am-PUID-0/DMB/commit/1c73a60e8965a1e48e1e95e0cc2eb594ead57748))
* **cli_debrid:** adds cli_debrid integration ([d7b4314](https://github.com/I-am-PUID-0/DMB/commit/d7b4314bbde1fee31df88ea153010f59ac22dcf0))
* **phalanx_db:** adds Phalanx DB integration ([f697942](https://github.com/I-am-PUID-0/DMB/commit/f697942ce6f355af666b6c0338f925aba25d79e1))
* **setup:** add symlink creation for wwwroot directory in Zilean setup ([49f0897](https://github.com/I-am-PUID-0/DMB/commit/49f08974828c8b983001b9ccec8f21dad38be7ff))


### 🐛 Bug Fixes

* **main:** update version extraction from pyproject.toml to align with poetry structure ([619b37f](https://github.com/I-am-PUID-0/DMB/commit/619b37f8c02c55c589baa4afedaab1472dce24e0))
* **phalanx_db:** set default release_version in dmb_config.json to v0.50 ([5d0661a](https://github.com/I-am-PUID-0/DMB/commit/5d0661a75b8d667708c81a5f4325bd9467e0117c))


### 🤡 Other Changes

* **deps:** bump packaging from 24.2 to 25.0 ([#142](https://github.com/I-am-PUID-0/DMB/issues/142)) ([75dcaa2](https://github.com/I-am-PUID-0/DMB/commit/75dcaa20ff5d64f9b4dd2a84f629807a51c9a0ec))
* **deps:** bump plexapi from 4.16.1 to 4.17.0 ([#140](https://github.com/I-am-PUID-0/DMB/issues/140)) ([3fdbdb5](https://github.com/I-am-PUID-0/DMB/commit/3fdbdb54a07fb17bde3e3bd6def5331f12e4c5af))
* **deps:** bump pydantic from 2.11.2 to 2.11.3 ([#139](https://github.com/I-am-PUID-0/DMB/issues/139)) ([73d28fc](https://github.com/I-am-PUID-0/DMB/commit/73d28fce9b6dff3ba237be2e42ddcf04a0f00256))
* **deps:** bump pydantic from 2.11.3 to 2.11.4 ([#145](https://github.com/I-am-PUID-0/DMB/issues/145)) ([93046ab](https://github.com/I-am-PUID-0/DMB/commit/93046abbf18bcd6a6c0b57d8419c113300f3c37e))
* **deps:** bump uvicorn from 0.34.0 to 0.34.2 ([#141](https://github.com/I-am-PUID-0/DMB/issues/141)) ([70bea2d](https://github.com/I-am-PUID-0/DMB/commit/70bea2db23d8ddf594afd393f82b78b55886f3e2))
* **docs:** change rclone mount permissions for `shared` to `rshared` and clarify ORIGIN address instructions ([08622ea](https://github.com/I-am-PUID-0/DMB/commit/08622ea9ef9d36f8f03611557b705e3913060ea0))
* **license:** switch to GPL-3.0 ([4b4ddfb](https://github.com/I-am-PUID-0/DMB/commit/4b4ddfb5228516268f361c0d4c206b43830f8179))
* **poetry:** update dev dependencies and enhance post-create command for devcontainer ([a40b082](https://github.com/I-am-PUID-0/DMB/commit/a40b0825114ecec5f14640d01865c083506bac21))


### 🛠️ Refactors

* **phalanx:** refactors Phalanx setup ([17837bd](https://github.com/I-am-PUID-0/DMB/commit/17837bdf071856041a89dad0f6d0e87c9e99c279))

## [6.8.2](https://github.com/I-am-PUID-0/DMB/compare/6.8.1...6.8.2) (2025-04-16)


### 🐛 Bug Fixes

* **config_loader:** remove unused regex import ([34fe0b2](https://github.com/I-am-PUID-0/DMB/commit/34fe0b2bc56ec13e0a0ccae95d0f460912941d19))
* **config:** implement update_config_with_top_level_defaults to merge default config ([bb7aa31](https://github.com/I-am-PUID-0/DMB/commit/bb7aa3112523c8b7af2c99d420bfc4de77709dce))

## [6.8.1](https://github.com/I-am-PUID-0/DMB/compare/6.8.0...6.8.1) (2025-04-16)


### 🐛 Bug Fixes

* **devcontainer:** add plex_debrid config mount to devcontainer configuration ([50a7872](https://github.com/I-am-PUID-0/DMB/commit/50a787268653aa2526a3b3559200b2a52844d34e))
* **main:** handle missing plex_debrid config by providing default empty dict ([4d8959b](https://github.com/I-am-PUID-0/DMB/commit/4d8959b12e4fc6cd5226aadf356a4134e18473df))
* **plex-debrid:** update settings file path in Dockerfile and add config copying in setup.py ([f69545d](https://github.com/I-am-PUID-0/DMB/commit/f69545d19bac40cd2be186b523feff69f69c0765))
* **setup:** refactor plex_debrid setup and update config file path ([fbd96ab](https://github.com/I-am-PUID-0/DMB/commit/fbd96aba1a8d283e91336f2427f18bf87ddefae6))

## [6.8.0](https://github.com/I-am-PUID-0/DMB/compare/6.7.3...6.8.0) (2025-04-15)


### ✨ Features

* **plex_debrid:** add support for Plex Debrid integration and auto-update functionality ([ed948ed](https://github.com/I-am-PUID-0/DMB/commit/ed948ed7424c5a1855131d57895dc16a35122542))


### 🐛 Bug Fixes

* **api:** change shell from sh to bash for health check execution ([04e33c1](https://github.com/I-am-PUID-0/DMB/commit/04e33c102df08f076c1b4807eddba87e3da7316a))
* **docker-image:** add unzip to dependencies for plex_debrid-builder ([ad8f163](https://github.com/I-am-PUID-0/DMB/commit/ad8f1633552896cafad83fc12613cd1b9378319f))
* **docker-image:** include PLEX_DEBRID_TAG in the build process ([b4b8a37](https://github.com/I-am-PUID-0/DMB/commit/b4b8a3729dfef5b66856093393b6351c8741b478))
* **docker-image:** normalize branch name format by replacing slashes with dashes ([6d1d228](https://github.com/I-am-PUID-0/DMB/commit/6d1d228c46bf912e43b90f145205c37d9a767d06))
* **docker-image:** update requirements file path for Plex Debrid installation ([cfc3608](https://github.com/I-am-PUID-0/DMB/commit/cfc36080e233343ffdf9f339501114f1af542bc0))
* **user-management:** add plex_debrid directory to ownership change in create_system_user ([b3f3146](https://github.com/I-am-PUID-0/DMB/commit/b3f31463b22ce9fb1258f7f9c8728c5b5000947e))


### 📖 Documentation

* **README:** update plex_debrid references and add configuration details ([b823711](https://github.com/I-am-PUID-0/DMB/commit/b82371151cefddb8c79a0681e23bf9124282f932))

## [6.7.3](https://github.com/I-am-PUID-0/DMB/compare/6.7.2...6.7.3) (2025-04-15)


### 🐛 Bug Fixes

* **logs:** Fixes DMB log filtering and improves error handling ([fdefd62](https://github.com/I-am-PUID-0/DMB/commit/fdefd628bb22a02b5cd06322438da728ece3d898))

## [6.7.2](https://github.com/I-am-PUID-0/DMB/compare/6.7.1...6.7.2) (2025-04-12)


### 🐛 Bug Fixes

* **rclone:** update dir-cache-time to use 10s ([5257cdb](https://github.com/I-am-PUID-0/DMB/commit/5257cdbe9ae8eed7ea52e26468928595f15d5a4a))

## [6.7.1](https://github.com/I-am-PUID-0/DMB/compare/6.7.0...6.7.1) (2025-04-11)


### 🐛 Bug Fixes

* **postgres:** pgagent process ([ee27aba](https://github.com/I-am-PUID-0/DMB/commit/ee27aba0aa92466bcdfe88245ca0a7ba254dde0b))
* **workflows:** escape newlines in Discord announcement body ([a04def8](https://github.com/I-am-PUID-0/DMB/commit/a04def83f4109aaeeefd7eb58ab6d7f298cd608b))
* **workflows:** remove unnecessary newlines in Discord announcement body ([2a74d62](https://github.com/I-am-PUID-0/DMB/commit/2a74d627ae06ff18dd1416f5644008d5e9143a86))


### 🤡 Other Changes

* **workflows:** update announcement body format for Discord notifications ([c4e6af1](https://github.com/I-am-PUID-0/DMB/commit/c4e6af13bf43092cfa4c883494ddb6a4815fcbe9))

## [6.7.0](https://github.com/I-am-PUID-0/DMB/compare/6.6.0...6.7.0) (2025-04-09)


### ✨ Features

* **api:** add fetch_process endpoint ([d86e385](https://github.com/I-am-PUID-0/DMB/commit/d86e385feed431a3ff0731fa3f433710695c7108))


### 🐛 Bug Fixes

* **workflows:** revert dependabot.ym; rtfm ([b1918d9](https://github.com/I-am-PUID-0/DMB/commit/b1918d9d1ee26036604c831598e071fb63233569))


### 🤡 Other Changes

* **workflows:** add devcontainers to dependabot.yml ([bc812e1](https://github.com/I-am-PUID-0/DMB/commit/bc812e1cf503c524d2c07e179b78cfba2e6d8362))
* **workflows:** update dependabot.yml ([bc6cfee](https://github.com/I-am-PUID-0/DMB/commit/bc6cfeed7c921ff6503e47d608a0dab454457947))


### 📖 Documentation

* **readme:** add badges for stars, issues, license, contributors, Docker pulls, and Discord ([83ebef1](https://github.com/I-am-PUID-0/DMB/commit/83ebef1486f00a84bb3dc9c51cbb41a878c7672b))
* **readme:** update plex example ([f680386](https://github.com/I-am-PUID-0/DMB/commit/f68038651b3cbe3dad6c3619fe2abef02474b155))

## [6.6.0](https://github.com/I-am-PUID-0/DMB/compare/6.5.0...6.6.0) (2025-04-08)


### ✨ Features

* enable poetry-based release flow ([7e7d948](https://github.com/I-am-PUID-0/DMB/commit/7e7d948b42487df12f4183886834de9caeefaffd))


### 🐛 Bug Fixes

* **docker:** add libpq-dev and pkg-config to dependencies; remove requirements.txt ([5d61381](https://github.com/I-am-PUID-0/DMB/commit/5d61381d606d1e6325f918ea7da04b5109fbecb4))
* **setup:** add validation for missing API key in Zurg instance setup ([9b96c30](https://github.com/I-am-PUID-0/DMB/commit/9b96c304cd388d5255e426c8d601b7da13bf6b08))

## [6.5.0](https://github.com/I-am-PUID-0/DMB/compare/6.4.0...6.5.0) (2025-04-07)


### ✨ Features

* **api:** add version retrieval and scalar API documentation endpoint ([a1dcbc1](https://github.com/I-am-PUID-0/DMB/commit/a1dcbc13516e2e0b99177576b5831512d3c98bf7))


### 🐛 Bug Fixes

* **process:** remove unused import of sys.version ([5ca0312](https://github.com/I-am-PUID-0/DMB/commit/5ca0312db593f4f32e04e8e5f1ac516d9167750e))

## [6.4.0](https://github.com/I-am-PUID-0/DMB/compare/6.3.0...6.4.0) (2025-04-04)


### ✨ Features

* **api/processes:** 🚀 Adds process version info ([200c08c](https://github.com/I-am-PUID-0/DMB/commit/200c08c9c3fd680377731722bcc2b1929f29188e))


### 🐛 Bug Fixes

* **api/processes:** update config assignment in fetch_processes function ([fe85e25](https://github.com/I-am-PUID-0/DMB/commit/fe85e25fef5724271da5a4acfa658ba7dbc0169d))


### 📖 Documentation

* update README with new documentation links and environment variable details ([9a87604](https://github.com/I-am-PUID-0/DMB/commit/9a87604728561253f0f316378de475c6628e25c5))

## [6.3.0](https://github.com/I-am-PUID-0/DMB/compare/6.2.0...6.3.0) (2025-03-18)


### ✨ Features

* **api:** add logging router and functionality to retrieve and filter service log files ([90f5766](https://github.com/I-am-PUID-0/DMB/commit/90f576660fc9a159eec4510b51eb7dd1796b5936))

## [6.2.0](https://github.com/I-am-PUID-0/DMB/compare/6.1.8...6.2.0) (2025-03-17)


### ✨ Features

* **dmb_frontend:** add release/branch/autoupdate functions for DMB Frontend ([c18de38](https://github.com/I-am-PUID-0/DMB/commit/c18de3833af956622dce3b63cde87b319ca73005))


### 🐛 Bug Fixes

* **auto_update:** prevent infinite loop during shutdown in automatic update process ([c13c075](https://github.com/I-am-PUID-0/DMB/commit/c13c0756dc31630793720fbd5b593052424a0c04))
* **workflow:** update merged PRs to remove 'autorelease: pending' label and add 'autorelease: tagged' for all PRs ([7a131f5](https://github.com/I-am-PUID-0/DMB/commit/7a131f521ab17deb22e8df92b6d081d545560450))

## [6.1.8](https://github.com/I-am-PUID-0/DMB/compare/6.1.7...6.1.8) (2025-03-16)


### 🐛 Bug Fixes

* **user_management:** enhance password setting by using LD_PRELOAD for better entropy ([802af70](https://github.com/I-am-PUID-0/DMB/commit/802af70d4b507c7dc4d5e89e92a50e978e409f6f))
* **user_management:** entropy for arc4random when using python secrets on synology host ([820b4ae](https://github.com/I-am-PUID-0/DMB/commit/820b4ae1f3a6407a48c1c36efbb4d1bf6cc99a4d)), closes [#106](https://github.com/I-am-PUID-0/DMB/issues/106)
* **user_management:** securely hash user passwords using OpenSSL ([1949460](https://github.com/I-am-PUID-0/DMB/commit/19494606109b0ca1f13d55189bbc2228af5e5e77))
* **workflow:** enable provenance for Docker image builds ([8c71c8f](https://github.com/I-am-PUID-0/DMB/commit/8c71c8f92018bc3600f5d8c77c2a3467798ad263))
* **workflow:** enable sbom for Docker image builds ([3453b9e](https://github.com/I-am-PUID-0/DMB/commit/3453b9e6287895e1944797fcccaf09c773c8aef5))


### 🤡 Other Changes

* **CODEOWNERS:** add user as code owner for repository ([ebc6936](https://github.com/I-am-PUID-0/DMB/commit/ebc6936a29ff2cc6c0468a7ae036bce1bda900af))

## [6.1.7](https://github.com/I-am-PUID-0/DMB/compare/6.1.6...6.1.7) (2025-03-14)


### 🐛 Bug Fixes

* **Dockerfile:** comment out on_library_update in config.yml to disable automatic script execution ([25b897c](https://github.com/I-am-PUID-0/DMB/commit/25b897ca1a79d2964d9721a6adb8971dec46411b))
* **fetch-latest-tags:** use restore-keys ([eb2a6b2](https://github.com/I-am-PUID-0/DMB/commit/eb2a6b2da18629a1198bc8261bd04457fd96e46b))
* **logger:** file handling in CustomRotatingFileHandler to prevent reentrant call ([6f91ab8](https://github.com/I-am-PUID-0/DMB/commit/6f91ab8fb3bdab1e79e7b8d0c69f4e155f35e8f3)), closes [#104](https://github.com/I-am-PUID-0/DMB/issues/104)
* **process-handler:** improve process wait handling and logging for non-existent processes ([7dd5352](https://github.com/I-am-PUID-0/DMB/commit/7dd5352f46224514d0f606e8aab1922074e0fc5c))
* **workflow:** add conditional for fetch-latest-tags job based on workflow dispatch and merged PR title ([cc257f0](https://github.com/I-am-PUID-0/DMB/commit/cc257f093bfb2dc5461a75db4c0c1a2b618d7ccf))

## [6.1.6](https://github.com/I-am-PUID-0/DMB/compare/6.1.5...6.1.6) (2025-03-07)


### 📖 Documentation

* **docker-compose:** update ([5418722](https://github.com/I-am-PUID-0/DMB/commit/5418722140f6644ab654df9ccb7bf77e75236893))


### 🛠️ Refactors

* **devcontainer:** update to pull latest image ([02ba0d2](https://github.com/I-am-PUID-0/DMB/commit/02ba0d2eda584a4807a6327d1892a1a09fd829a6))
* **dmb_config:** remove additional rclone instances not yet supported ([a2edd21](https://github.com/I-am-PUID-0/DMB/commit/a2edd217c139982dd550dd1f4617407bd09ee099))

## [6.1.5](https://github.com/I-am-PUID-0/DMB/compare/6.1.4...6.1.5) (2025-03-07)


### 📖 Documentation

* **changelog:** update changelog ([f4891ee](https://github.com/I-am-PUID-0/DMB/commit/f4891ee7a9c8f72ae299489e51037db935c556a8))
* **readme:** update image tag ([1a0413b](https://github.com/I-am-PUID-0/DMB/commit/1a0413b7702e7b03964245a4244dad35f8bdd1ab))

## [6.1.4](https://github.com/I-am-PUID-0/DMB/compare/6.1.3...6.1.4) (2025-03-07)

### 📖 Documentation

- **readme:** RIVEN_FRONTEND_ENV_ORIGIN ([65f10d2](https://github.com/I-am-PUID-0/DMB/commit/65f10d2ca5a26baec333394fac2292146f8a8bce))

### 🛠️ Refactors

- **dockerfile:** update dmb-frontend-builder to use repo tag ([b747bf8](https://github.com/I-am-PUID-0/DMB/commit/b747bf84a085eafda7bf1ac7b7e223147ce6e7c9))
- **fetch-latest-tags:** change cron job to run every 3 hours ([6068fc0](https://github.com/I-am-PUID-0/DMB/commit/6068fc0d57f80589016372f47d2327ab49e973d9))

## [6.1.0] - 2025-03-03 🚀

### ✨ Features

- feat(riven_backend): add port assignment
- feat(riven_frontend): add port assignment
- feat(zilean): add port assignment

### 🐛 Bug Fixes

- fix(dockerfile): set pnpm store local to each project w/ `store-dir=./.pnpm-store in .npmrc`
- fix(versions): version_check & version_write use key vs. process_name
- fix(qemu): Set `cache-image: false`
- fix(postgres): re-add pgAgent
- fix(postgres): system_stats, paths, permissions
- fix(postgres): `locales && locale-gen en_US.UTF-8` added to dockerfile
- fix(dockerfile): pgadmin-builder venv path
- fix(healthcheck): update `/healthcheck/running_processes.json`
- fix(setup): resolved missing argument for setup of branch_enabled
- fix(postgres): `check_postgresql_started` updated port used when not default
- fix(user_management): add auto-generated user password to support use of su by default user
- fix(clear_directory): always exclude venv directory if present
- fix(find_service_config): recursive search
- fix(find_schema): recursive search
- fix(save_config_file): yaml.dump
- fix(api_state): api status update

### 🚀 CI/CD Pipeline

- ci(github): update push event configuration in Docker image workflow
- ci(github): add release-please, fetch-latest-tags, conventional-commits
- ci(devcontainer): add dns configuration and git path
- ci(docker-image): add job summary for build

### 🛠️ Refactors

- refactor(dockerfile): change base image to Ubuntu 24.04
- refactor(dmb_config): dynamic update of the `ConnectionString` for zilean
- refactor(dmb_config): add `ORIGIN` to riven_frontend
- refactor(dockerfile): pull dmb_frontend from @nicocapalbo repo
- refactor(base): removed base module, add imports to modules
- refactor(dmb_config): removed riven_backend default envs
- refactor(dockerfile): pin pnpm version 10.x `npm install -g pnpm@latest-10`
- refactor(dockerfile): pin node version 23.x `curl -fsSL https://deb.nodesource.com/setup_23.x | bash -`
- refactor(main): add version.txt file
- refactor(api_service): on_event moved to lifespan

### 🤡 Other Changes

- chore(deps): bump actions/checkout from 3 to 4

## [6.0.1] - 2025-01-09 🚀

### Fixed 🛠️

- Zurg: download

## [6.0.0] - 2025-01-09 🚀

### Breaking Changes ⚠️

- DO NOT UPDATE UNTIL YOU HAVE REVIEWED THE CHANGES!
- Changed most, if not all, environment variables - new dmb_config.json - see Notes

### Changed 🔄

- Refactor: EVERYTHING!
- Refactor: Improved shutdown process execution time
- [Issue #80](https://github.com/I-am-PUID-0/DMB/issues/80) FastAPI - Add real time logs view
- [Issue #83](https://github.com/I-am-PUID-0/DMB/issues/83) FastAPI - Update healthcheck

### Fixed 🛠️

- PostgreSQL: Retry logic during server startup
- PostgreSQL: Init all databases on the first run - prevents Zilean and Riven database issues on the first run
- PostgreSQL: automatically remove postmaster.pid file retained from an improper shutdown

### Added ✨

- Config: Added dmb_config.json to the `/config` directory for complete control over DMB
- Riven: Added init function for first run of Riven Backend - mitigates first run startup issues
- Zurg: Unlimited simultaneous deployments of Zurg - simply add another Zurg "instance" in the dmb_config.json
- rclone: Unlimited simultaneous deployments of rclone - simply add another rclone "instance" in the dmb_config.json
- rclone: More robust stale mount handling
- PostgreSQL: Any setting within the postgresql.conf can be set from within the dmb_config.json

### Removed

- rclone: Removed NFS mounts for now
- Duplicate Cleanup: Removed for now

### Notes 📝

- A dmb_config.json has been added to DMB to allow for more granular control over the processes within and configuration of DMB.
- DMB will respect and prioritize variables provided though environment variables, a .env file, docker secrets, and the dmb_config.json
- environment variables, a .env file, and docker secrets are held at the same level and will override any setting in the dmb_config.json
- DMB will now come pre-configured to run all processes once at least one debrid service API key is entered through any of the above mentioned methods
- Multiple simultaneous debrid services are not currently supported for Riven
- Zurg currently only supports RealDebrid

## [5.4.5] - 2024-11-22 🚀

### Fixed 🛠️

- [PR #88](https://github.com/I-am-PUID-0/DMB/pull/88) Zilean: Add database connection timeouts 🐛 - Thanks @skeet70 🙏

## [5.4.4] - 2024-11-16 🚀

### Changed 🔄

- Zilean: Update to dotnet 9 🔄
- Zilean: Update to support both Zilean.Scraper & Zilean.DmmScraper for older version of Zilean 🔄

### Notes 📝

- Zilean: Only Zilean v2.1.0 and newer are supported due to dotnet update to version 9 🚨

## [5.4.3] - 2024-11-01 🚀

### Changed 🔄

- Riven Frontend: Updated the name and location of the `server-config.json` file to `server.json` and to be transferred to the /riven/frontend/config directory on startup 🔄
- Re-enabled reaping of zombie processes 🔄

## [5.4.2] - 2024-10-29 🚀

### Fixed 🛠️

- [Issue #72](https://github.com/I-am-PUID-0/DMB/issues/72) Zilean Permissions Issue 🐛

## [5.4.1] - 2024-10-28 🚀

### Fixed 🛠️

- [Issue #71](https://github.com/I-am-PUID-0/DMB/issues/71) PostgreSQL Graceful Shutdown 🐛

## [5.4.0] - 2024-10-25 🚀

### Fixed 🛠️

- [Issue #14](https://github.com/I-am-PUID-0/DMB/issues/14) Add Riven build process to Dockerfile ✨
- [Issue #65](https://github.com/I-am-PUID-0/DMB/issues/65) Zilean Enabled when ZILEAN_ENABLED=false 🐛
- [Issue #66](https://github.com/I-am-PUID-0/DMB/issues/66) Dockerfile pulls from Riven Frontend main branch vs. latest release 🐛
- [Issue #67](https://github.com/I-am-PUID-0/DMB/issues/67) Future releases for Riven Frontend and Backend will require an API Key 🐛

### Added ✨

- Riven Backend: Added the Riven backend build process to the Dockerfile 📦
- Riven Frontend: Added the server-config.json to the be saved in /config and transferred to the Riven Frontend when using the API key 📦
- Zilean: Added the Zilean build process to the Dockerfile 📦

### Changed 🔄

- Riven Backend: Settings are now loaded with or without the API key depending on the version of Riven used 🔄
- Refactor: Refactored the utils and version checks 🔄
- Utils: Added description to reaped processes 🔄
- Logging: Added thread lock to rollover 🔄

### Notes 📝

- Future releases for Riven Frontend and Backend will require an API Key to be set 🚨
- With these changes, you can now use the latest development versions of Riven Frontend and Backend 🌙
- Use the RIVEN_BACKEND_BRANCH=release-please--branches--main and RIVEN_FRONTEND_BRANCH=release-please--branches--main environment variables to test the current development versions of Riven 🌙

## [5.3.2] - 2024-10-18 🚀

### Fixed 🛠️

- [Issue #60](https://github.com/I-am-PUID-0/DMB/issues/60) Does not correctly handle deleted files in new Riven releases 🐛
- [Issue #61](https://github.com/I-am-PUID-0/DMB/issues/61) Riven Backend v0.16.0 Broke Settings Update 🐛
- [Issue #62](https://github.com/I-am-PUID-0/DMB/issues/62) Riven Frontend v0.14.0 Broke VersionFilePath 🐛
- [Issue #63](https://github.com/I-am-PUID-0/DMB/issues/63) Riven Frontend v0.16.0 Broke Frontend Build 🐛 - This may be a temporary fix...

## [5.3.1] - 2024-10-15 🚀

### Fixed 🛠️

- [Issue #59](https://github.com/I-am-PUID-0/DMB/issues/59) Zombie dotnet Processes Accumulating Over Time 🐛

## [5.3.0] - 2024-10-03 🚀

### Added ✨

- pgAdmin 4: Added system_stats extension to pgAdmin 4 for host system monitoring 📦
- pgAdmin 4: Added pgAgent extension to pgAdmin 4 for job scheduling 📦

### Fixed 🛠️

- pgAdmin 4: Fixed the pgAdmin 4 config_local.py SSL settings 🐛

### Changed 🔄

- RIVEN_BACKEND_URL: Linked to the Riven backend load_settings function. [PR #57](https://github.com/I-am-PUID-0/DMB/pull/57) Thanks @FunkeCoder23 🙏

## [5.2.0] - 2024-10-01 🚀

### Added ✨

- pgAdmin 4: Added pgAdmin 4 to the DMB image for PostgreSQL management 📦 - Resolves [Issue #49](https://github.com/I-am-PUID-0/DMB/issues/49)

### Notes 📝

- pgAdmin 4 is enabled by setting the `PGADMIN_SETUP_EMAIL` and `PGADMIN_SETUP_PASSWORD` environment variables 🆔🔐
- The DMB PostgreSQL server is automatically added to pgAdmin4 Servers🗄️
- On the first access of pgAdmin 4, the DMB PostgreSQL server password will need to be set in pgAdmin 4 🗄️ - the default PostgreSQL server password is `postgres` or set with `POSTGRES_PASSWORD` 🔐
- To access pgAdmin 4, navigate to `http://<DMB_IP>:5050` in your browser 🌐
- The pgAdmin 4 data is stored in the `/pgadmin/data` directory - though, not required to mounted to the host 📁
- The pgAdmin 4 config_local.py is stored in the `/pgadmin/data` directory and symlinked at startup 📝 - review the [pgAdmin 4 documentation](https://www.pgadmin.org/docs/pgadmin4/latest/config_py.html) for additional configuration options 📚
- Backups of the PostgreSQL database can be made using pgAdmin 4 and are stored in the `/pgadmin/storage` directory 🗄️
- The following message can be ignored on initial startup: `ERROR - PostgreSQL subprocess: relation "version" does not exist at character 75`

## [5.1.10] - 2024-09-24 🚀

### Fixed 🛠️

- logger: Fixed obfuscation of sensitive data in logs 🐛

## [5.1.9] - 2024-09-23 🚀

### Fixed 🛠️

- Riven Backend: Enabled not set to `true` for applied subordinate dictionary values - seriously this time 🐛
- Riven Frontend: Set the default path for the frontend version.txt in dockerfile 🐛
- [Issue #54](https://github.com/I-am-PUID-0/DMB/issues/54) An error occurred in the Zilean setup: 'NoneType' object has no attribute 'lower'

## [5.1.8] - 2024-09-23 🚀

### Fixed 🛠️

- Riven Backend: Enabled not set to `true` for applied subordinate dictionary values 🐛

## [5.1.7] - 2024-09-23 🚀

### Fixed 🛠️

- [Issue #40](https://github.com/I-am-PUID-0/DMB/issues/40) Postgres. role "root" does not exist. 🐛 - Thanks @lukemuller 🙏

### Added ✨

- Riven Backend: Added the use of .env file for Riven backend settings 📝

### Changed 🔄

- Main Process: Refactored the main process to handle exceptions - graceful shutdown 🔄
- Logger: Clean up logging 📝
- Riven Backend: DEBUG is now linked to the DMB_LOG_LEVEL 🔄

### Notes 📝

- To use the .env file for Riven backend settings, create a .env file in the Riven data directory with settings in the format of `KEY=VALUE` as shown in the [env.example](https://github.com/rivenmedia/riven/blob/main/.env.example)📝

## [5.1.6] - 2024-09-13 🚀

### Changed 🔄

- Riven Frontend: Set the default path for the frontend version.txt to /riven/frontend 🔄

## [5.1.5] - 2024-09-13 🚀

### Fixed 🛠️

- Riven Frontend: Fixed the default DIALECT set for node build process 🐛
- Riven Frontend: Set the default path for the frontend version.txt 🐛

### Added ✨

- RIVEN_FRONTEND_OWNER: Environment variable to set the owner of the Riven frontend repository; Default is rivenmedia 🆔

## [5.1.4] - 2024-09-12 🚀

### Fixed 🛠️

- [Issue #51](https://github.com/I-am-PUID-0/DMB/issues/51) Duplicate start_process when update applied during initial startup 🐛

## [5.1.3] - 2024-09-12 🚀

### Fixed 🛠️

- [Issue #43](https://github.com/I-am-PUID-0/DMB/issues/43) Node issue when setting Riven frontend version 🐛

### Notes 📝

- The Riven frontend automatic update / branch / version should now work again 📦

## [5.1.2] - 2024-09-10 🚀

### Fixed 🛠️

- Healthcheck: Fixed healthcheck for Zilean 🩺

## [5.1.1] - 2024-09-10 🚀

### Fixed 🛠️

- Zilean: `PostgreSQL subprocess: ... CEST [490] FATAL:  role "postgres" does not exist` 🐛

### Notes 📝

- On first run of Zilean, the PostgreSQL will create the database named zilean, so the message `PostgreSQL subprocess: ... CEST [596] FATAL:  database "zilean" does not exist` can be ignored 🗄️

## [5.1.0] - 2024-09-09 🚀

### Added ✨

- [Issue #48](https://github.com/I-am-PUID-0/DMB/issues/48) Added Zilean to the DMB image for caching of the DebridMediaManager shared hashlists 📦
- ZILEAN_ENABLED: Environment variable to enable Zilean; Default is false 🔄
- ZILEAN_UPDATE: Environment variable to update Zilean; Default is false 🔄
- ZILEAN_BRANCH: Environment variable to set the Zilean branch; Default is main 🔄
- ZILEAN_VERSION: Environment variable to set the Zilean version; Default is latest 🔄
- ZILEAN_LOGS: Environment variable to disable the Zilean logging when value is set to OFF; Default is ON 📝

## [5.0.1] - 2024-09-06 🚀

### Fixed 🛠️

- [Issue #47](https://github.com/I-am-PUID-0/DMB/issues/47) Error when RCLONE_LOG_LEVEL is not enabled 🐛

## [5.0.0] - 2024-09-05 🚀

### Breaking Changes ⚠️

- PostgreSQL: The default database user has been changed from postgres to DMB 📉 - Please delete the existing PostgreSQL data directory before starting the new version of DMB 🗑️

### Added ✨

- FRONTEND_LOGS: Environment variable to disable the Riven frontend logging when value is set to OFF; Default is ON 📝
- BACKEND_LOGS: Environment variable to disable the Riven backend logging when value is set to OFF; Default is ON 📝
- Riven: Added shutdown for Riven backend and frontend processes 🛑

### Fixed 🛠️

- [Issue #44](https://github.com/I-am-PUID-0/DMB/issues/44) Add graceful shutdown for Riven frontend and backend ✨
- [Issue #45](https://github.com/I-am-PUID-0/DMB/issues/45) Fix permissions for npm_install 🐛
- [Issue #46](https://github.com/I-am-PUID-0/DMB/issues/46) Zurg config.yml not chown'd to the correct user 🐛
- PostgreSQL: Fixed permissions for PostgreSQL 🐛 - Thanks @Unlearned6688 🙏
- Zurg: Fixed automatic updates for Zurg nightly builds 🐛

### Changed 🔄

- Refactor: Refactored the use of ProcessHandler for consistent process management 🔄

### Notes 📝

- Add `stop_grace_period: 60s` to your compose file to allow for a 60 second grace period for all of the processes to shutdown before the container is stopped 🛑
- [Issue #43](https://github.com/I-am-PUID-0/DMB/issues/43) Node issue when setting Riven frontend version 🐛 has not been resolved in this release 🚨, so please ensure to only use Riven frontend version that is built into the image - No automatic update / branch / version 📦
- There may be an issue with the Riven frontend when trying to access settings; the logs will show `TypeError: Cannot read properties of undefined (reading 'enabled')` when trying to access settings - this is a known issue and you will need to delete the riven settings.json 🚨

## [4.1.0] - 2024-08-29 🚀

### Added ✨

- RCLONE_LOGS: Environment variable to disable the rclone process logging when value is set to OFF; Default is ON 📝
- RCLONE_DIR: Environment variable to set the rclone directory; Default is /data 📁

### Fixed 🛠️

- [Issue #36](https://github.com/I-am-PUID-0/DMB/issues/36) Setting RCLONE_LOG_LEVEL=OFF causes the rclone process to fail 🐛
- [Issue #37](https://github.com/I-am-PUID-0/DMB/issues/37) Error when PUID/PGID are set without values: PGID= 🐛
- [Issue #38](https://github.com/I-am-PUID-0/DMB/issues/38) Recursive chown of /data throws errors if the mount is still present 🐛
- [Issue #39](https://github.com/I-am-PUID-0/DMB/issues/39) Make rclone mount base path a variable - /data --> /user-defined ✨
- [Issue #41](https://github.com/I-am-PUID-0/DMB/issues/41) Add healthcheck for PostgreSQL process ✨
- [Issue #42](https://github.com/I-am-PUID-0/DMB/issues/42) Add clean shutdown for PostgreSQL server ✨

## [4.0.0] - 2024-08-28 🚀

### Breaking Changes ⚠️

- Riven: Riven backend no longer supports sqlite as a database option; PostgreSQL is now the only supported database option 📉
- PostgreSQL: To ensure the database files are persisted, a volume must be mounted to /postgres_data 📂

### Added ✨

- PUID & PGID: Environment variables to set the user and group IDs for the DMB container; Default is 1001 🆔
- POSTGRES_DATA: Environment variable to set the path for the PostgreSQL database files; Default is /postgres_data 📁
- POSTGRES_PASSWORD: Environment variable to set the password for the PostgreSQL database; Default is postgres 🔐
- POSTGRES_USER: Environment variable to set the user for the PostgreSQL database; Default is postgres 👤
- POSTGRES_DB: Environment variable to set the database name for the PostgreSQL database; Default is riven 🗄️

### Changed 🔄

- Riven: Riven backend now uses PostgreSQL as the database option; Default is postgresql+psycopg2://postgres:postgres@127.0.0.1/riven 🔧
- Riven: Riven frontend now uses PostgreSQL as the database option; Default is postgres://postgres:postgres@127.0.0.1/riven 🔄

### Fixed 🛠️

- [Issue #8](https://github.com/I-am-PUID-0/DMB/issues/8) Add support for PUID/GUID ✨
- [Issue #34](https://github.com/I-am-PUID-0/DMB/issues/34) Add PostgreSQL option for Riven backend ✨
- [Issue #35](https://github.com/I-am-PUID-0/DMB/issues/35) Riven frontend not properly connecting to the database 🐛

### Notes 📝📌

- If the Riven backend shows errors related to the database or alembic, then the Riven data directory may need to be deleted before starting the new version of Riven w/ PostgreSQL 🗑️ - backup your settings.json before deleting the data directory 📂

## [3.5.0] - 2024-08-08 🚀

### Added ✨

- Suppress Logs: If the LOG_LEVEL for a process is set to OFF, then logs will be suppressed for the process 🤫
- Riven Frontend: Added the latest version of the Riven frontend to the Dockerfile for image build 📦

### Notes 📝

- The DMB image is built nightly and will include the latest version of the Riven frontend at the time of build 🌙

## [3.4.0] - 2024-08-05 🚀

### Fixed 🛠️

- [Issue #27](https://github.com/I-am-PUID-0/DMB/issues/27) DATABASE_URL was not being set correctly for the Riven frontend 🐛
- healthcheck: Fixed healthcheck to properly check for Riven frontend setup completion 🩺

### Changed 🔄

- Riven setup: Refactored backend and frontend setup to use ProcessHandler for consistent logging 🔄

### Added ✨

- [Issue #9](https://github.com/I-am-PUID-0/DMB/issues/9) Obfuscate sensitive data in logs
- Riven backend: UPDATERS_PLEX_ADDRESS linked to PLEX_ADDRESS 🔄
- Riven backend: UPDATERS_PLEX_TOKEN linked to PLEX_TOKEN 🔄

## [3.3.2] - 2024-08-03 🚀

### Fixed 🛠️

- [Issue #27](https://github.com/I-am-PUID-0/DMB/issues/27) Riven frontend needed a database connection to function properly 🐛

### Added ✨

- RIVEN_DATABASE_URL: Environment variable to set the Riven frontend database URL; Default is sqlite:////riven/backend/data/media.db 🗃️

### Changed 🔄

- GITHUB_TOKEN: Can be added to the environment variables to allow for repository downloads without rate limits 🔄

## [3.3.1] - 2024-08-01 🚀

### Fixed 🛠️

- healthcheck: Reverted healthcheck, for now 🐛

## [3.3.0] - 2024-08-01 🚀

### Fixed 🛠️

- [Issue #23](https://github.com/I-am-PUID-0/DMB/issues/23) Processes not properly killed during automatic updates 🐛
- [Issue #24](https://github.com/I-am-PUID-0/DMB/issues/24) Riven automatic update extracts to wrong directory 🐛
- [Issue #25](https://github.com/I-am-PUID-0/DMB/issues/25) Automatic update initiates update check multiple times for each instance 🐛
- [Issue #26](https://github.com/I-am-PUID-0/DMB/issues/26) Riven Frontend breaking change requires DIALECT=sqlite env variable 🐛

### Added ✨

- Automatic Update: Enabled automatic updates for Riven branches - expands automatic updates to include branches 🔄
- RIVEN_FRONTEND_DIALECT: Environment variable to set the Riven frontend database dialect; Default is sqlite - not required to be set in default configuration 🗃️
- Riven Frontend: Set npm max_old_space_size to 2048MB for Riven frontend build process - limits resource usage 📦
- Riven Frontend: Set vite minification to false for Riven frontend build process - speeds up build process and reduces resource usage 📦

### Changed 🔄

- healthcheck: Waits for Riven frontend setup to complete 🩺

## [3.2.0] - 2024-07-30 🚀

### Changed 🔄

- Update process: Refactored update process to apply updates to Zurg and Riven before starting the processes 🔄
- Zurg: Disabling plex_update.sh in config file has been disabled, for now. Comment out the line in the config file to disable the Zurg based plex update process if desired 🔄

### Added ✨

- Zurg: Allow nightly release custom versions for ZURG_VERSION
- Zurg: Add plex_update.sh from Zurg to working directory for Zurg use 📦

### Fixed 🛠️

- Logging: Fixed logging for Zurg to ensure log levels are properly set 📝

## [3.1.0] - 2024-07-26 🚀

### Added ✨

- Shutdown: Added a shutdown function to gracefully stop the DMB container; e.g., unmount the rclone mounts 🛑

## [3.0.0] - 2024-07-26 🚀

### Breaking Changes ⚠️

- BACKEND_URL: Environment variable has been changed to RIVEN_BACKEND_URL to better reflect the environment variable's purpose; please update your compose file accordingly

### Added ✨

- Ratelimit for GitHub API requests ⏳
- Retries for GitHub API requests 🔄

### Fixed 🛠️

- RIVEN_ENABLED: Environment variable has been fixed to correctly enable the Riven backend and frontend; Default is false 🤞
- RIVEN_UPDATE: Environment variable has been fixed to correctly update the Riven backend and frontend; Default is false 🤞
- RIVEN_BACKEND_UPDATE: Environment variable has been fixed to correctly update the Riven backend; Default is false 🤞
- RIVEN_FRONTEND_UPDATE: Environment variable has been fixed to correctly update the Riven frontend; Default is false 🤞
- RIVEN_DATABASE_HOST: Environment variable has been fixed to correctly set the Riven database host; Default is sqlite:////riven/backend/data/media.db 🗃️
- [Issue #22](https://github.com/I-am-PUID-0/DMB/issues/22) 🐛

### Notes 📝

- BACKEND_URL has been changed to RIVEN_BACKEND_URL. The value is automatically set when the variable is not enabled. The default value is http://127.0.0.1:8080 🌐
- RIVEN_DATABASE_HOST value is automatically set when the variable is not enabled. The default value is sqlite:////riven/backend/data/media.db 🗃️

## [2.0.0] - 2024-07-25

### Breaking Changes

- Riven: Directory structure has changed to allow for split riven instances - backend and frontend - please update your compose file volumes accordingly
- RIVEN_BRANCH: Is now split into RIVEN_FRONTEND_BRANCH and RIVEN_BACKEND_BRANCH
- RIVEN_ENABLED: Environment variable will enable the Riven backend and frontend without the need to set the RIVEN_FRONTEND_ENABLED and RIVEN_BACKEND_ENABLED variables
- RIVEN_UPDATE: Environment variable to update the Riven backend and frontend; Default is false

### Added

- RIVEN_BACKEND_ENABLED: Environment variable to enable the Riven backend; Default is false
- RIVEN_FRONTEND_ENABLED: Environment variable to enable the Riven frontend; Default is false
- RIVEN_BACKEND_BRANCH: Environment variable to set the Riven backend branch; Default is main
- RIVEN_FRONTEND_BRANCH: Environment variable to set the Riven frontend branch; Default is main
- RIVEN_BACKEND_UPDATE: Environment variable to update the Riven backend; Default is false
- RIVEN_FRONTEND_UPDATE: Environment variable to update the Riven frontend; Default is false
- RIVEN_BACKEND_VERSION: Environment variable to set the Riven backend version; Default is latest
- RIVEN_FRONTEND_VERSION: Environment variable to set the Riven frontend version; Default is latest
- BACKEND_URL: Environment variable to set the Riven backend URL; Default is http://127.0.0.1:8080
- RIVEN_DATABASE_HOST: Environment variable to set the Riven database host; Default is sqlite:////riven/backend/data/media.db
- COLOR_LOG_ENABLED: Environment variable to enable color logging; Default is false
- ffmpeg: Added ffmpeg to the Dockerfile for Zurg use of ffprobe to extract media information from files, enhancing media metadata accuracy.

### Notes

- **Delete all Riven files and directories within the data directory before starting the new version of Riven!**
- **Automatic updates for Riven backend and frontend are not functional yet; will be fixed in a follow-on release.**
- **Other features may also not be functional yet; will be fixed in a follow-on release.**
- This release resolves [Issue #19](https://github.com/I-am-PUID-0/DMB/issues/19), [Issue #20](https://github.com/I-am-PUID-0/DMB/issues/20), and [Issue #10](https://github.com/I-am-PUID-0/DMB/issues/10)

## [1.2.0] - 2024-07-19

### Added

- [Issue #18](https://github.com/I-am-PUID-0/DMB/issues/18): Added DMB_LOG_SIZE environment variable to set the maximum size of the log file; Default is 10MB

## [1.1.0] - 2024-07-17

### Changed

- Rclone: WebDAV URL check for Zurg startup processes accepts any 200 status code as a valid response
- DMB: Refactored to use common functions under utils

## [1.0.3] - 2024-07-16

### Fixed

- Rclone: Fixed WebDAV URL check for Zurg startup processes when Zurg user and password are set in config.yml

## [1.0.2] - 2024-07-16

### Fixed

- Zurg: Fixed the removal of Zurg user and password if previously set in config.yml

## [1.0.1] - 2024-07-16

### Fixed

- DMB: Introduced a Riven startup check for the symlinked directory to ensure the Zurg startup processes have finished before starting Riven
- DMB: Introduced a Rclone startup check for the Zurg WebDAV URL to ensure the Zurg startup processes have finished before starting Rclone

## [1.0.0] - 2024-06-25

### Breaking Changes

- DMB: Updated PDZURG_LOG_LEVEL to DMB_LOG_LEVEL
- DMB: Updated PDZURG_LOG_COUNT to DMB_LOG_COUNT

### Changed

- [Issue #5](https://github.com/I-am-PUID-0/DMB/issues/5): Added initial sleep time to allow for services to start
- [Issue #6](https://github.com/I-am-PUID-0/DMB/issues/6): Disabled Zurg plex_update.sh - not needed
- [Issue #7](https://github.com/I-am-PUID-0/DMB/issues/7): Cleanup Riven logging

### Added

- [Issue #1](https://github.com/I-am-PUID-0/DMB/issues/1): All Riven settings now assignable with environment variables
- Riven: RIVEN_LOG_LEVEL environment variable - Riven log level is only configurable to DEBUG or INFO; Default is INFO

### Removed

- [Issue #3](https://github.com/I-am-PUID-0/DMB/issues/3): Removed Jellyfin environment variables
- [Issue #2](https://github.com/I-am-PUID-0/DMB/issues/2): Removed PLEX_REFRESH environment variable

## [0.2.0] - 2024-06-22

### Added

- Zurg: GITHUB_TOKEN environment variable to use for access to the private sponsored zurg repository

### Removed

- Zurg: PLEX_REFRESH environment variable
- Zurg: PLEX_MOUNT environment variable

## [0.1.0] - 2024-06-22

### Added

- Riven: RIVEN_BRANCH environment variable to select the branch to use for the riven repository

### Fixed

- rclone: Fixed rclone process w/ Riven
- Healthcheck: Fixed healthcheck process w/ Riven

## [0.0.1] - 2024-06-21

### Added

- Initial Push
