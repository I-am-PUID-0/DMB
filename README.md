<div align="center" style="max-width: 100%; height: auto;">
  <h1>🎬 Debrid Media Bridge 🎬</h1>
  <a href="https://github.com/I-am-PUID-0/DMB">
    <picture>
      <source media="(prefers-color-scheme: dark)" srcset="https://github.com/I-am-PUID-0/DMB/assets/36779668/d0cbc785-2e09-41da-b226-924fdfcc1f21">
      <img alt="DMB" src="https://github.com/I-am-PUID-0/DMB/assets/36779668/d0cbc785-2e09-41da-b226-924fdfcc1f21" style="max-width: 100%; height: auto;">
    </picture>
  </a>
</div>

## 📜 Description
**Debrid Media Bridge (DMB)** is an All-In-One (AIO) docker image for the unified deployment of **[Riven Media's](https://github.com/rivenmedia)**, **[yowmamasita's](https://github.com/yowmamasita)**, and **[ncw's](https://github.com/ncw)** projects -- **[Riven](https://github.com/rivenmedia/riven)**, **[zurg](https://github.com/debridmediamanager/zurg-testing)**, and **[rclone](https://github.com/rclone/rclone)**.

> ⚠️ **IMPORTANT**: Docker Desktop **CANNOT** be used to run DMB. Docker Desktop does not support the [mount propagation](https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation) required for rclone mounts.
>
> ![image](https://github.com/I-am-PUID-0/DMB/assets/36779668/aff06342-1099-4554-a5a4-72a7c82cb16e)
>
> See the wiki for [alternative solutions](https://github.com/I-am-PUID-0/DMB/wiki/Setup-Guides) to run DMB on Windows through WSL2.

## 🌟 Features
See the DMB [Wiki](https://github.com/I-am-PUID-0/DMB/wiki) for a full list of features and settings.

## 🐳 Docker Hub
A prebuilt image is hosted on [Docker Hub](https://hub.docker.com/r/iampuid0/dmb).

## 🏷️ GitHub Container Registry
A prebuilt image is hosted on [GitHub Container Registry](https://github.com/I-am-PUID-0/DMB/pkgs/container/DMB).

## 🛠️ Docker-compose

> [!NOTE] 
> The below examples are not exhaustive and are intended to provide a starting point for deployment.
> Additionally, the host directories used in the examples are based on [Define the directory structure](https://github.com/I-am-PUID-0/DMB/wiki/Setup-Guides#define-the-directory-structure) and provided for illustrative purposes and can be changed to suit your needs.

```YAML
version: "3.8"

services:
  DMB:
    container_name: DMB
    image: iampuid0/dmb:latest
    ## Optionally, specify a specific version of DMB
    # image: iampuid0/dmb:2.0.0 #etc...
    stdin_open: true # docker run -i
    tty: true        # docker run -t    
    volumes:
      ## Location of configuration files. If a Zurg config.yml and/or Zurg app is placed here, it will be used to override the default configuration and/or app used at startup. 
      - ~/docker/DMB/config:/config
      ## Location for logs
      - ~/docker/DMB/log:/log
      ## Location for Zurg RealDebrid active configuration
      - ~/docker/DMB/Zurg/RD:/zurg/RD
      ## Location for Zurg AllDebrid active configuration - Riven does not currently support AllDebrid   
      - ~/docker/DMB/Zurg/AD:/zurg/AD   
      ## Location for rclone mount to host
      - ~/docker/DMB/Zurg/mnt:/data:shared  
      ## Location for Riven backend data
      - ~/docker/DMB/Riven/data:/riven/backend/data
      ## Location for Riven symlinks
      - ~/docker/DMB/Riven/mnt:/mnt
    environment:
      - TZ=
      ## Zurg Required Settings
      - ZURG_ENABLED=true      
      - RD_API_KEY=
      ## Zurg Optional Settings
     # - ZURG_LOG_LEVEL=DEBUG
     # - GITHUB_TOKEN=       #Use with private Zurg repo
     # - ZURG_VERSION=v0.9.2-hotfix.4
     # - ZURG_UPDATE=true
     # - ZURG_USER=
     # - ZURG_PASS=
     # - ZURG_PORT=8800
      ## Rclone Required Settings
      - RCLONE_MOUNT_NAME=DMB
      ## Rclone Optional Settings - See rclone docs for full list
     # - RCLONE_UID=1000
     # - RCLONE_GID=1000
     # - NFS_ENABLED=true
     # - NFS_PORT=8000
     # - RCLONE_LOG_LEVEL=DEBUG
     # - RCLONE_CACHE_DIR=/cache
     # - RCLONE_DIR_CACHE_TIME=10s
     # - RCLONE_VFS_CACHE_MODE=full
     # - RCLONE_VFS_CACHE_MAX_SIZE=100G
     # - RCLONE_BUFFER_SIZE=32M
     # - RCLONE_VFS_CACHE_MAX_AGE=4h
      ## Riven Backend Required Settings
      - RIVEN_BACKEND_ENABLED=true
      ## Riven Frontend Required Settings
      - RIVEN_FRONTEND_ENABLED=true
      - ORIGIN=http://0.0.0.0:3000 # See Riven documentation for more details
      ## Riven Optional Settings
     # - RIVEN_ENABLED=true
     # - RIVEN_BACKEND_BRANCH=main
     # - RIVEN_FRONTEND_BRANCH=main
     # - RIVEN_BACKEND_VERSION=v0.8.4
     # - RIVEN_FRONTEND_VERSION=v0.2.5
     # - RIVEN_BACKEND_UPDATE=true
     # - RIVEN_FRONTEND_UPDATE=true
     # - RIVEN_LOG_LEVEL=DEBUG
     # - RIVEN_BACKEND_URL=http://127.0.0.1:8080 # Default is http://127.0.0.1:8080 when not enabled
     # - RIVEN_DATABASE_HOST=sqlite:////riven/backend/data/media.db # Default is sqlite:////riven/backend/data/media.db when not enabled
     # - RIVEN_DATABASE_URL=/riven/backend/data/media.db  # Default is /riven/backend/data/media.db when not enabled
     # - RIVEN_FRONTEND_DIALECT=sqlite
     # - PLEX_TOKEN=
     # - PLEX_ADDRESS=
     # - SEERR_API_KEY=
     # - SEERR_ADDRESS=
      ## Special Features
     # - AUTO_UPDATE_INTERVAL=12
     # - DUPLICATE_CLEANUP=true
     # - CLEANUP_INTERVAL=1
     # - DMB_LOG_LEVEL=DEBUG  # Master log level for all program logs in DMB
     # - DMB_LOG_COUNT=2
     # - DMB_LOG_SIZE=10M
     # - COLOR_LOG_ENABLED=true
    # Example to attach to gluetun vpn container if realdebrid blocks IP address 
    # network_mode: container:gluetun  
    ports:
      - "3000:3000"
    devices:
      - /dev/fuse:/dev/fuse:rwm
    cap_add:
      - SYS_ADMIN     
    security_opt:
      - apparmor:unconfined    
      - no-new-privileges
```

## 🎥 Example Plex Docker-compose
```YAML
version: "3.8"

services:
  plex:
    image: plexinc/pms-docker:latest
    container_name: plex
    devices:
      - /dev/dri:/dev/dri    
    volumes:
      - ~/docker/plex/library:/config
      - ~/docker/plex/transcode:/transcode
      - ~/docker/DMB/Zurg/mnt:/data # rclone mount location from DMB must be shared to Plex container. Don't add to plex library
      - ~/docker/DMB/Riven/mnt:/mnt  # Riven symlink location from DMB must be shared to Plex container. Add to plex library    
    environment:
      - TZ=${TZ}
    ports:
      - "32400:32400"
```

## 🔨 Docker Build

### Docker CLI

```
docker build -t your-image-name https://github.com/I-am-PUID-0/DMB.git
```


## 🌐 Environment Variables

To customize some properties of the container, the following environment
variables can be passed via the `-e` parameter (one for each variable), or via the docker-compose file within the ```environment:``` section, or with a .env file saved to the config directory -- See the wiki for more info on using the [.env](https://github.com/I-am-PUID-0/DMB/wiki/Settings#use-of-env-file-for-setting-environment-variables).  Value
of this parameter has the format `<VARIABLE_NAME>=<VALUE>`.

| Variable       | Description                                  | Default | Used w/ rclone| Used w/ Riven| Used w/ zurg|
|----------------|----------------------------------------------|---------|:-:|:-:|:-:|
|`TZ`| [TimeZone](http://en.wikipedia.org/wiki/List_of_tz_database_time_zones) used by the container |  |
|`RD_API_KEY`| [RealDebrid API key](https://real-debrid.com/apitoken) | `none` | | :heavy_check_mark:| :heavy_check_mark:|
|`AD_API_KEY`| [AllDebrid API key](https://alldebrid.com/apikeys/) | `none` | | :heavy_check_mark:| :heavy_check_mark:|
|`RCLONE_MOUNT_NAME`| A name for the rclone mount | `none` | :heavy_check_mark:|
|`RCLONE_LOG_LEVEL`| [Log level](https://rclone.org/docs/#log-level-level) for rclone | `NOTICE` | :heavy_check_mark:|
|`RCLONE_LOG_FILE`| [Log file](https://rclone.org/docs/#log-file-file) for rclone |`none`  | :heavy_check_mark: |
|`RCLONE_DIR_CACHE_TIME`| [How long a directory should be considered up to date and not refreshed from the backend](https://rclone.org/commands/rclone_mount/#vfs-directory-cache) #optional, but recommended is 10s. | `10s` | :heavy_check_mark:|
|`RCLONE_CACHE_DIR`| [Directory used for caching](https://rclone.org/docs/#cache-dir-dir). |`none`  | :heavy_check_mark:|
|`RCLONE_VFS_CACHE_MODE`| [Cache mode for VFS](https://rclone.org/commands/rclone_mount/#vfs-file-caching) |`none`  | :heavy_check_mark:|
|`RCLONE_VFS_CACHE_MAX_SIZE`| [Max size of the VFS cache](https://rclone.org/commands/rclone_mount/#vfs-file-caching) |`none` | :heavy_check_mark:|
|`RCLONE_VFS_CACHE_MAX_AGE`| [Max age of the VFS cache](https://rclone.org/commands/rclone_mount/#vfs-file-caching) |`none`  | :heavy_check_mark:|
|`PLEX_TOKEN`| The [Plex Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) associated with your Plex user |`none`  || :heavy_check_mark:|
|`PLEX_ADDRESS`| The URL of your Plex server. Example: http://192.168.0.100:32400 or http://plex:32400 - format must include ```http://``` or ```https://``` and have no trailing characters after the port number (32400). E.g., ```/``` |`none`|| :heavy_check_mark:|
|`RIVEN_ENABLED`| Set the value "true" to enable the Riven backend and frontend processes | `false ` | | :heavy_check_mark: | |
|`RIVEN_BACKEND_ENABLED`| Set the value "true" to enable the Riven backend process | `false ` | | :heavy_check_mark: | |
|`RIVEN_FRONTEND_ENABLED`| Set the value "true" to enable the Riven frontend process | `false ` | | :heavy_check_mark: | |
|`RIVEN_BACKEND_BRANCH`| Set the value to the appropriate branch  | `main` | | :heavy_check_mark: | |
|`RIVEN_FRONTEND_BRANCH`| Set the value to the appropriate branch  | `main` | | :heavy_check_mark: | |
|`RIVEN_BACKEND_VERSION`| The version of Riven backend to use. If enabled, the value should contain v0.8.x format | `latest` | | :heavy_check_mark: | |
|`RIVEN_FRONTEND_VERSION`| The version of Riven frontend to use. If enabled, the value should contain v0.8.x format | `latest` | | :heavy_check_mark: | |
|`RIVEN_LOGFILE`| Log file for Riven. The log file will appear in the ```/config``` as ```Riven.log```. If used, the value must be ```true``` or ```false``` | `false` || :heavy_check_mark:| |
|`RIVEN_BACKEND_UPDATE`| Enable automatic updates of the Riven backend. Adding this variable will enable automatic updates to the latest version of Riven locally within the container.| `false` || :heavy_check_mark:|
|`RIVEN_FRONTEND_UPDATE`| Enable automatic updates of the Riven frontend. Adding this variable will enable automatic updates to the latest version of Riven locally within the container.| `false` || :heavy_check_mark:|
|`ORIGIN`| The origin URL for the Riven frontend | http://0.0.0.0:3000 | | :heavy_check_mark: | |
|`RIVEN_BACKEND_URL`| The URL for the Riven backend | http://127.0.0.1:8080 | | :heavy_check_mark: | |
|`RIVEN_DATABASE_HOST`| The database host for Riven backend | `sqlite:////riven/backend/data/media.db` | | :heavy_check_mark: | |
|`RIVEN_DATABASE_URL`| The database URL for Riven frontend | `/riven/backend/data/media.db` | | :heavy_check_mark: | |
|`RIVEN_FRONTEND_DIALECT`| The dialect for the Riven frontend | `sqlite` | | :heavy_check_mark: | |
|`AUTO_UPDATE_INTERVAL`| Interval between automatic update checks in hours. Vaules can be any positive [whole](https://www.oxfordlearnersdictionaries.com/us/definition/english/whole-number) or [decimal](https://www.oxfordreference.com/display/10.1093/oi/authority.20110803095705740;jsessionid=3FDC96CC0D79CCE69702661D025B9E9B#:~:text=The%20separator%20used%20between%20the,number%20expressed%20in%20decimal%20representation.) point based number. Ex. a value of .5 would yield thirty minutes, and 1.5 would yield one and a half hours | `24` || :heavy_check_mark:| :heavy_check_mark:|
|`DUPLICATE_CLEANUP`| Automated cleanup of duplicate content in Plex.  | `false` |
|`CLEANUP_INTERVAL`| Interval between duplicate cleanup in hours. Values can be any positive [whole](https://www.oxfordlearnersdictionaries.com/us/definition/english/whole-number) or [decimal](https://www.oxfordreference.com/display/10.1093/oi/authority.20110803095705740;jsessionid=3FDC96CC0D79CCE69702661D025B9E9B#:~:text=The%20separator%20used%20between%20the,number%20expressed%20in%20decimal%20representation.) point based number. Ex. a value of .5 would yield thirty minutes and 1.5 would yield one and a half hours | `24` || :heavy_check_mark: | :heavy_check_mark:|
|`DMB_LOG_LEVEL`| The level at which logs should be captured. See the python [Logging Levels](https://docs.python.org/3/library/logging.html#logging-levels) documentation for more details  | `INFO` |
|`DMB_LOG_COUNT`| The number logs to retain. Result will be value + current log  | `2` |
|`DMB_LOG_SIZE`| The size of the log file before it is rotated. Valid options are 'K' (kilobytes), 'M' (megabytes), and 'G' (gigabytes)  | `10M` |
|`COLOR_LOG_ENABLED`| Enable color logging for DMB.  | `false` | | | |
|`ZURG_ENABLED`| Set the value "true" to enable the Zurg process | `false ` | | | :heavy_check_mark:|
|`GITHUB_TOKEN`| GitHub Personal Token for use with Zurg private repo. Requires Zurg [sponsorship](https://github.com/sponsors/debridmediamanager) | `false ` | | | :heavy_check_mark:|
|`ZURG_VERSION`| The version of Zurg to use. If enabled, the value should contain v0.9.x or v0.9.x-hotfix.x format or "nightly" if wanting the nightly builds from Zurg private repo (requires GITHUB_TOKEN)  | `latest` | | | :heavy_check_mark: |
|`ZURG_UPDATE`| Enable automatic updates of Zurg. Adding this variable will enable automatic updates to the latest version of Zurg locally within the container. | `false` | | | :heavy_check_mark:|
|`ZURG_LOG_LEVEL`| Set the log level for Zurg | `INFO` | | | :heavy_check_mark:|
|`SEERR_API_KEY`| The Overseerr API Key |`none`|| :heavy_check_mark:||
|`SEERR_ADDRESS`| The URL of your Overseerr server. Example: http://192.168.0.102:5055 or http://Overseerr:5055 - format must include ```http://``` or ```https://``` and have no trailing characters after the port number (5055). E.g., ```/``` |`none`| | :heavy_check_mark:|
|`ZURG_USER`| The username to be used for protecting the Zurg endpoints.  | `none `| | | :heavy_check_mark: |
|`ZURG_PASS`| The password to be used for protecting the Zurg endpoints.  | `none `  | | | :heavy_check_mark: |
|`ZURG_PORT`| The port to be used for the Zurg server | `random ` | | | :heavy_check_mark: |
|`NFS_ENABLED`| Set the value "true" to enable the NFS server for rclone | `false ` | :heavy_check_mark:| | |
|`NFS_PORT`| The port to be used for the rclone NFS server | `random ` | :heavy_check_mark:| | |



## 📂 Data Volumes

The following table describes the data volumes used by the container.  The mappings
are set via the `-v` parameter or via the docker-compose file within the ```volumes:``` section.  Each mapping is specified with the following
format: `<HOST_DIR>:<CONTAINER_DIR>[:PERMISSIONS]`.

| Container path  | Permissions | Description |
|-----------------|-------------|-------------|
|`/config`| rw | This is where the application stores the rclone.conf, and any files needing persistence. CAUTION: rclone.conf is overwritten upon start/restart of the container. Do NOT use an existing rclone.conf file if you have other rclone services |
|`/log`| rw | This is where the application stores its log files |
|`/data`| shared  | This is where rclone will be mounted. Not required when only utilizing Riven   |
|`/zurg/RD`| rw| This is where Zurg will store the active configuration and data for RealDebrid. Not required when only utilizing Riven   |
|`/zurg/AD`| rw | This is where Zurg will store the active configuration and data for AllDebrid. Not required when only utilizing Riven   |
|`/riven/data`| rw | This is where Riven will store its data. Not required when only utilizing Zurg   |
|`/riven/mnt`| rw | This is where Riven will set its symlinks. Not required when only utilizing Zurg   |



## 🗝️ Docker Secrets

DMB supports the use of docker secrets for the following environment variables:

| Variable       | Description                                  | Default | Used w/ rclone| Used w/ Riven| Used w/ zurg|
|----------------|----------------------------------------------|---------|:-:|:-:|:-:|
|`GITHUB_TOKEN`| [GitHub Personal Token](https://github.com/settings/tokens) | ` ` | | | :heavy_check_mark:|
|`RD_API_KEY`| [RealDebrid API key](https://real-debrid.com/apitoken) | ` ` | | :heavy_check_mark:| :heavy_check_mark:|
|`AD_API_KEY`| [AllDebrid API key](https://alldebrid.com/apikeys/) | ` ` | | | :heavy_check_mark:|
|`PLEX_TOKEN`| The [Plex Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) associated with  | ` ` || :heavy_check_mark:|
|`PLEX_ADDRESS`| The URL of your Plex server. Example: http://192.168.0.100:32400 or http://plex:32400 - format must include ```http://``` or ```https://``` and have no trailing characters after the port number (32400). E.g., ```/``` | ` ` || :heavy_check_mark:|
|`SEERR_API_KEY`| The Jellyseerr or Overseerr API Key | ` ` || :heavy_check_mark:||
|`SEERR_ADDRESS`| The URL of your Jellyseerr or Overseerr server. Example: http://192.168.0.102:5055 or http://Overseerr:5055 - format must include ```http://``` or ```https://``` and have no trailing characters after the port number (8096). E.g., ```/``` | ` ` || :heavy_check_mark:|

To utilize docker secrets, remove the associated environment variables from the docker-compose, create a file with the case-sensitive naming convention identified and secret value, then reference the file in the docker-compose file as shown below:
```YAML
version: '3.8'

services:
  DMB:
    image: iampuid0/DMB:latest
    secrets:
      - github_token
      - rd_api_key
      - ad_api_key
      - plex_token
      - plex_address
      - seerr_api_key
      - seerr_address

secrets:
  github_token:
    file: ./path/to/github_token.txt
  rd_api_key:
    file: ./path/to/rd_api_key.txt
  ad_api_key:
    file: ./path/to/ad_api_key.txt
  plex_token:
    file: ./path/to/plex_token.txt
  plex_address:
    file: ./path/to/plex_address.txt
  seerr_api_key:
    file: ./path/to/seerr_api_key.txt
  seerr_address:
    file: ./path/to/seerr_address.txt
```



## 📝 TODO

See the [DMB roadmap](https://github.com/users/I-am-PUID-0/projects/6) for a list of planned features and enhancements.



## 🚀 Deployment

DMB allows for the simultaneous or individual deployment of Riven and/or Zurg w/ rclone

For additional details on deployment, see the [DMB Wiki](https://github.com/I-am-PUID-0/DMB/wiki/Setup-Guides#deployment-options)



## 🌍 Community

### DMB
- For questions related to DMB, see the GitHub [discussions](https://github.com/I-am-PUID-0/DMB/discussions)
- or create a new [issue](https://github.com/I-am-PUID-0/DMB/issues) if you find a bug or have an idea for an improvement.
- or join the DMB [discord server](https://discord.gg/8dqKUBtbp5)

### Riven Media
- For questions related to Riven, see the GitHub [discussions](https://github.com/orgs/rivenmedia/discussions) 
- or create a new [issue](https://github.com/rivenmedia/riven/issues) if you find a bug or have an idea for an improvement.
- or join the Riven [discord server](https://discord.gg/rivenmedia) 


## 🍻 Buy **[Riven Media](https://github.com/rivenmedia)** a beer/coffee? :)

If you enjoy the underlying projects and want to buy Riven Media a beer/coffee, feel free to use the [GitHub sponsor link](https://github.com/sponsors/dreulavelle/)

## 🍻 Buy **[yowmamasita](https://github.com/yowmamasita)** a beer/coffee? :)

If you enjoy the underlying projects and want to buy yowmamasita a beer/coffee, feel free to use the [GitHub sponsor link](https://github.com/sponsors/debridmediamanager)

## 🍻 Buy **[ncw](https://github.com/ncw)** a beer/coffee? :) 

If you enjoy the underlying projects and want to buy Nick Craig-Wood a beer/coffee, feel free to use the website's [sponsor links](https://rclone.org/sponsor/)

## ✅ GitHub Workflow Status
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/I-am-PUID-0/DMB/docker-image.yml)
