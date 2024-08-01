# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).



## Version [3.3.0] - 2024-08-01 🚀

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


## Version [3.2.0] - 2024-07-30 🚀

### Changed 🔄

- Update process: Refactored update process to apply updates to Zurg and Riven before starting the processes 🔄
- Zurg: Disabling plex_update.sh in config file has been disbaled, for now. Comment out the line in the config file to disable the Zurg based plex update process if desired 🔄

### Added ✨

- Zurg: Allow nightly release custom versions for ZURG_VERSION
- Zurg: Add plex_update.sh from Zurg to working directory for Zurg use 📦

### Fixed 🛠️

- Logging: Fixed logging for Zurg to ensure log levels are properly set 📝


## Version [3.1.0] - 2024-07-26 🚀

### Added ✨

- Shutdown: Added a shutdown function to gracefully stop the DMB container; e.g., unmount the rclone mounts 🛑


## Version [3.0.0] - 2024-07-26 🚀

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



## Version [2.0.0] - 2024-07-25

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
- **Automatic updates for Riven backend and frontend are not funtioal yet; will be fixed in a follow-on release.**
- **Other features may also not be functional yet; will be fixed in a follow-on release.**
- This release resolves [Issue #19](https://github.com/I-am-PUID-0/DMB/issues/19), [Issue #20](https://github.com/I-am-PUID-0/DMB/issues/20), and [Issue #10](https://github.com/I-am-PUID-0/DMB/issues/10)



## Version [1.2.0] - 2024-07-19

### Added

- [Issue #18](https://github.com/I-am-PUID-0/DMB/issues/18): Added DMB_LOG_SIZE environment variable to set the maximum size of the log file; Default is 10MB


## Version [1.1.0] - 2024-07-17

### Changed

- Rclone: WebDAV URL check for Zurg startup processes accepts any 200 status code as a valid response
- DMB: Refactored to use common functions under utils 


## Version [1.0.3] - 2024-07-16

### Fixed

- Rclone: Fixed WebDAV URL check for Zurg startup processes when Zurg user and password are set in config.yml


## Version [1.0.2] - 2024-07-16

### Fixed

- Zurg: Fixed the removal of Zurg user and password if previously set in config.yml


## Version [1.0.1] - 2024-07-16

### Fixed

- DMB: Introduced a Riven startup check for the symlinked directory to ensure the Zurg startup processes have finished before starting Riven
- DMB: Introduced a Rclone startup check for the Zurg WebDAV URL to ensure the Zurg startup processes have finished before starting Rclone


## Version [1.0.0] - 2024-06-25

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


## Version [0.2.0] - 2024-06-22

### Added

- Zurg: GITHUB_TOKEN environment variable to use for access to the private sponsored zurg repository

### Removed

- Zurg: PLEX_REFRESH environment variable
- Zurg: PLEX_MOUNT environment variable


## Version [0.1.0] - 2024-06-22

### Added

- Riven: RIVEN_BRANCH environment variable to select the branch to use for the riven repository

### Fixed

- rclone: Fixed rclone process w/ Riven
- Healthcheck: Fixed healthcheck process w/ Riven


## Version [0.0.1] - 2024-06-21

### Added

- Initial Push