# Changelog

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
