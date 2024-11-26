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
**Debrid Media Bridge (DMB)** is an All-In-One (AIO) docker image for the unified deployment of **[Riven Media's](https://github.com/rivenmedia)**, **[yowmamasita's](https://github.com/yowmamasita)**, **[iPromKnight's](https://github.com/iPromKnight/zilean)**, **[Nick Craig-Wood's](https://github.com/ncw)**, **[Michael Stonebraker's](https://en.wikipedia.org/wiki/Michael_Stonebraker)**, and **[Dave Page's](https://github.com/dpage)** projects -- **[Riven](https://github.com/rivenmedia/riven)**, **[Zurg](https://github.com/debridmediamanager/zurg-testing)**, **[Zilean](https://github.com/iPromKnight/zilean)**, **[rclone](https://github.com/rclone/rclone)**, **[PostgreSQL](https://www.postgresql.org/)**, and **[pgAdmin 4](https://www.pgadmin.org/)**.

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
services:
  DMB:
    container_name: DMB
    image: iampuid0/dmb:latest                                       ## Optionally, specify a specific version of DMB w/ image: iampuid0/dmb:2.0.0 
    stop_grace_period: 30s                                           ## Adjust as need to allow for graceful shutdown of the container
    stdin_open: true                                                 ## docker run -i
    tty: true                                                        ## docker run -t    
    volumes:   
      - /home/username/docker/DMB/config:/config                     ## Location of configuration files. If a Zurg config.yml and/or Zurg app is placed here, it will be used to override the default configuration and/or app used at startup. 
      - /home/username/docker/DMB/log:/log                           ## Location for logs
      - /home/username/docker/DMB/Zurg/RD:/zurg/RD                   ## Location for Zurg RealDebrid active configuration  
      - /home/username/docker/DMB/Zurg/mnt:/data:shared              ## Location for rclone mount to host
      - /home/username/docker/DMB/Riven/data:/riven/backend/data     ## Location for Riven backend data
      - /home/username/docker/DMB/Riven/mnt:/mnt                     ## Location for Riven symlinks
      - /home/username/docker/DMB/PostgreSQL/data:/postgres_data     ## Location for PostgreSQL database
      - /home/username/docker/DMB/pgAdmin4/data:/pgadmin/data        ## Location for pgAdmin 4 data
      - /home/username/docker/DMB/Zilean/data:/zilean/app/data       ## Location for Zilean data
    environment:
      - TZ=
      - PUID=
      - PGID=
      - ZURG_ENABLED=true      
      - RD_API_KEY=
      - RCLONE_MOUNT_NAME=DMB
      - ZILEAN_ENABLED=true
      - RIVEN_ENABLED=true
      - ORIGIN=http://0.0.0.0:3000                                  ## See Riven documentation for more details
      - PGADMIN_SETUP_EMAIL=                                        ## Set if using pgAdmin 4 - Ex. PGADMIN_SETUP_EMAIL=DMB@DMB.DMB
      - PGADMIN_SETUP_PASSWORD=                                     ## Set if using pgAdmin 4
    # network_mode: container:gluetun                               ## Example to attach to gluetun vpn container if realdebrid blocks IP address 
    ports:
      - "3000:3000"                                                 ## Riven frontend
      - "5050:5050"                                                 ## pgAdmin 4
    devices:
      - /dev/fuse:/dev/fuse:rwm
    cap_add:
      - SYS_ADMIN     
    security_opt:
      - apparmor:unconfined    
      - no-new-privileges
```

## 🎥 Example Plex Docker-compose

> [!NOTE] 
> The Plex server must be started after the rclone mount is available.  The below example uses the ```depends_on``` parameter to delay the start of the Plex server until the rclone mount is available.  The rclone mount must be shared to the Plex container.  The rclone mount location should not be added to the Plex library.  The Riven symlink location must be shared to the Plex container and added to the Plex library.

```YAML
services:
  plex:
    image: plexinc/pms-docker:latest
    container_name: plex
    devices:
      - /dev/dri:/dev/dri    
    volumes:
      - /home/username/docker/plex/library:/config
      - /home/username/docker/plex/transcode:/transcode
      - /home/username/docker/DMB/Zurg/mnt:/data            ## rclone mount location from DMB must be shared to Plex container. Don't add to plex library
      - /home/username/docker/DMB/Riven/mnt:/mnt            ## Riven symlink location from DMB must be shared to Plex container. Add to plex library    
    environment:
      - TZ=${TZ}
    ports:
      - "32400:32400"
    healthcheck:
      test: curl --connect-timeout 15 --silent --show-error --fail http://localhost:32400/identity
      interval: 1m00s
      timeout: 15s
      retries: 3
      start_period: 1m00s
    depends_on:                                            ## Used to delay the startup of plex to ensure the rclone mount is available.
      DMB:                                                 ## set to the name of the container running rclone
        condition: service_healthy
        restart: true                                      ## Will automatically restart the plex container if the DMB container restarts
```


## 📦 Docker Run

### Docker CLI

```bash
docker run -d \
  --name=DMB \
  --restart unless-stopped \
  -e TZ= \
  -e PUID= \
  -e PGID= \
  -e ZURG_ENABLED=true \
  -e RD_API_KEY= \
  -e RCLONE_MOUNT_NAME=DMB \
  -e ZILEAN_ENABLED=true \
  -e RIVEN_ENABLED=true \
  -e ORIGIN=http://
  -e PGADMIN_SETUP_EMAIL= \
  -e PGADMIN_SETUP_PASSWORD= \
  -v /path/to/config:/config \
  -v /path/to/log:/log \
  -v /path/to/Zurg/RD:/zurg/RD \
  -v /path/to/Zurg/mnt:/data:shared \
  -v /path/to/Riven/data:/riven/backend/data \
  -v /path/to/Riven/mnt:/mnt \
  -v /path/to/PostgreSQL/data:/postgres_data \
  -v /path/to/pgAdmin4/data:/pgadmin/data \
  -v /path/to/Zilean/data:/zilean/app/data \
  -p 3000:3000 \
  -p 5050:5050 \
  --device /dev/fuse:/dev/fuse:rwm \
  --cap-add SYS_ADMIN \
  --security-opt apparmor:unconfined \
  --security-opt no-new-privileges \
  iampuid0/dmb:latest
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

| Variable       | Description                                  | Default | Used w/ rclone| Used w/ Riven| Used w/ Zurg|
|----------------|----------------------------------------------|---------|:-:|:-:|:-:|
|`TZ`| [TimeZone](http://en.wikipedia.org/wiki/List_of_tz_database_time_zones) used by the container |  |
|`PUID`| The user ID of the user running the container | `1001` | :heavy_check_mark:| :heavy_check_mark:| :heavy_check_mark:|
|`PGID`| The group ID of the user running the container | `1001` | :heavy_check_mark:| :heavy_check_mark:| :heavy_check_mark:|
|`RD_API_KEY`| [RealDebrid API key](https://real-debrid.com/apitoken) | `none` | | :heavy_check_mark:| :heavy_check_mark:|
|`AD_API_KEY`| [AllDebrid API key](https://alldebrid.com/apikeys/) | `none` | | :heavy_check_mark:| :heavy_check_mark:|
|`RCLONE_MOUNT_NAME`| A name for the rclone mount | `none` | :heavy_check_mark:|
|`RCLONE_DIR`| The parent directory for the rclone mount | `/data` | :heavy_check_mark:|
|`RCLONE_LOGS`| Set value to OFF To disable the rclone process logging | `ON` | :heavy_check_mark:|
|`RCLONE_LOG_LEVEL`| [Log level](https://rclone.org/docs/#log-level-level) for rclone - To suppress logs set value to OFF | `NOTICE` | :heavy_check_mark:|
|`RCLONE_LOG_FILE`| [Log file](https://rclone.org/docs/#log-file-file) for rclone |`none`  | :heavy_check_mark: |
|`RCLONE_DIR_CACHE_TIME`| [How long a directory should be considered up to date and not refreshed from the backend](https://rclone.org/commands/rclone_mount/#vfs-directory-cache) #optional, but recommended is 10s. | `10s` | :heavy_check_mark:|
|`RCLONE_CACHE_DIR`| [Directory used for caching](https://rclone.org/docs/#cache-dir-dir). |`none`  | :heavy_check_mark:|
|`RCLONE_VFS_CACHE_MODE`| [Cache mode for VFS](https://rclone.org/commands/rclone_mount/#vfs-file-caching) |`none`  | :heavy_check_mark:|
|`RCLONE_VFS_CACHE_MAX_SIZE`| [Max size of the VFS cache](https://rclone.org/commands/rclone_mount/#vfs-file-caching) |`none` | :heavy_check_mark:|
|`RCLONE_VFS_CACHE_MAX_AGE`| [Max age of the VFS cache](https://rclone.org/commands/rclone_mount/#vfs-file-caching) |`none`  | :heavy_check_mark:|
|`PLEX_TOKEN`| The [Plex Token](https://support.plex.tv/articles/204059436-finding-an-authentication-token-x-plex-token/) associated with your Plex user |`none`  || :heavy_check_mark:|
|`PLEX_ADDRESS`| The URL of your Plex server. Example: http://192.168.0.100:32400 or http://plex:32400 - format must include ```http://``` or ```https://``` and have no trailing characters after the port number (32400). E.g., ```/``` |`none`|| :heavy_check_mark:|
|`POSTGRES_DATA`| The location of the PostgreSQL database |`/postgres_data`|| :heavy_check_mark:|
|`POSTGRES_USER`| The username for the PostgreSQL database |`DMB`|| :heavy_check_mark:|
|`POSTGRES_PASSWORD`| The password for the PostgreSQL database |`postgres`|| :heavy_check_mark:|
|`POSTGRES_DB`| The name of the PostgreSQL database |`riven`|| :heavy_check_mark:|
|`PGADMIN_SETUP_EMAIL`| The email for the pgAdmin setup - must be set for pgAdmin 4 to run |`none`|| :heavy_check_mark:|
|`PGADMIN_SETUP_PASSWORD`| The password for the pgAdmin setup - must be set for pgAdmin 4 to run |`none`|| :heavy_check_mark:|
|`RIVEN_ENABLED`| Set the value "true" to enable the Riven backend and frontend processes | `false ` | | :heavy_check_mark: | |
|`RIVEN_BACKEND_ENABLED`| Set the value "true" to enable the Riven backend process | `false ` | | :heavy_check_mark: | |
|`RIVEN_FRONTEND_ENABLED`| Set the value "true" to enable the Riven frontend process | `false ` | | :heavy_check_mark: | |
|`RIVEN_BACKEND_BRANCH`| Set the value to the appropriate branch  | `main` | | :heavy_check_mark: | |
|`RIVEN_FRONTEND_BRANCH`| Set the value to the appropriate branch  | `main` | | :heavy_check_mark: | |
|`RIVEN_BACKEND_VERSION`| The version of Riven backend to use. If enabled, the value should contain v0.8.x format | `latest` | | :heavy_check_mark: | |
|`RIVEN_FRONTEND_VERSION`| The version of Riven frontend to use. If enabled, the value should contain v0.8.x format | `latest` | | :heavy_check_mark: | |
|`RIVEN_LOG_LEVEL`| Log level for Riven  | `INFO` || :heavy_check_mark:| |
|`FRONTEND_LOGS`| Set value to OFF To disable the frontend process logging | `ON` || :heavy_check_mark:| |
|`BACKEND_LOGS`| Set value to OFF To disable the backend process logging | `ON` || :heavy_check_mark:| |
|`RIVEN_BACKEND_UPDATE`| Enable automatic updates of the Riven backend. Adding this variable will enable automatic updates to the latest version of Riven locally within the container.| `false` || :heavy_check_mark:|
|`RIVEN_FRONTEND_UPDATE`| Enable automatic updates of the Riven frontend. Adding this variable will enable automatic updates to the latest version of Riven locally within the container.| `false` || :heavy_check_mark:|
|`ORIGIN`| The origin URL for the Riven frontend | http://0.0.0.0:3000 | | :heavy_check_mark: | |
|`RIVEN_BACKEND_URL`| The URL for the Riven backend | http://127.0.0.1:8080 | | :heavy_check_mark: | |
|`RIVEN_DATABASE_HOST`| The database host for Riven backend | `postgresql+psycopg2://DMB:postgres@127.0.0.1/riven` | | :heavy_check_mark: | |
|`RIVEN_DATABASE_URL`| The database URL for Riven frontend | `postgres://DMB:postgres@127.0.0.1/riven` | | :heavy_check_mark: | |
|`RIVEN_FRONTEND_DIALECT`| The dialect for the Riven frontend - default w/o backend is sqlite, default w/ backend is postgres | `sqlite or postgres` | | :heavy_check_mark: | |
|`HARD_RESET`| Set true to reset the database for Riven | `false` | | :heavy_check_mark: | |
|`AUTO_UPDATE_INTERVAL`| Interval between automatic update checks in hours. Values can be any positive [whole](https://www.oxfordlearnersdictionaries.com/us/definition/english/whole-number) or [decimal](https://www.oxfordreference.com/display/10.1093/oi/authority.20110803095705740;jsessionid=3FDC96CC0D79CCE69702661D025B9E9B#:~:text=The%20separator%20used%20between%20the,number%20expressed%20in%20decimal%20representation.) point based number. Ex. a value of .5 would yield thirty minutes, and 1.5 would yield one and a half hours | `24` || :heavy_check_mark:| :heavy_check_mark:|
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
|`ZURG_LOG_LEVEL`| Set the log level for Zurg - To suppress logs set value to OFF  | `INFO` | | | :heavy_check_mark:|
|`SEERR_API_KEY`| The Overseerr API Key |`none`|| :heavy_check_mark:||
|`SEERR_ADDRESS`| The URL of your Overseerr server. Example: http://192.168.0.102:5055 or http://Overseerr:5055 - format must include ```http://``` or ```https://``` and have no trailing characters after the port number (5055). E.g., ```/``` |`none`| | :heavy_check_mark:|
|`ZURG_USER`| The username to be used for protecting the Zurg endpoints.  | `none `| | | :heavy_check_mark: |
|`ZURG_PASS`| The password to be used for protecting the Zurg endpoints.  | `none `  | | | :heavy_check_mark: |
|`ZURG_PORT`| The port to be used for the Zurg server | `random ` | | | :heavy_check_mark: |
|`NFS_ENABLED`| Set the value "true" to enable the NFS server for rclone | `false ` | :heavy_check_mark:| | |
|`NFS_PORT`| The port to be used for the rclone NFS server | `random ` | :heavy_check_mark:| | |
|`ZILEAN_ENABLED`| Set the value "true" to enable the Zilean process - Will only run when Riven backend is enabled | `false ` | | :heavy_check_mark:||
|`ZILEAN_VERSION`| The version of Zilean to use. If enabled, the value should contain v1.x.x format | `latest` | | :heavy_check_mark: | |
|`ZILEAN_BRANCH`| The branch of Zilean to use.  | `main` | | :heavy_check_mark: | |
|`ZILEAN_UPDATE`| Enable automatic updates of Zilean. Adding this variable will enable automatic updates to the latest version of Zilean locally within the container. | `false` | | :heavy_check_mark: | |
|`ZILEAN_LOGS`| Set value to OFF To disable the Zilean process logging | `ON` | | :heavy_check_mark:| |


## 🌐 Ports Used

> [!NOTE] 
> The below examples are default and may be configurable with the use of additional environment variables.

The following table describes the ports used by the container.  The mappings are set via the `-p` parameter or via the docker-compose file within the ```ports:``` section.  Each mapping is specified with the following format: `<HOST_PORT>:<CONTAINER_PORT>[:PROTOCOL]`.

| Container port | Protocol | Description |
|----------------|----------|-------------|
|`3000`| TCP | Riven frontend - A web UI is accessible at the assigned port|
|`8080`| TCP | Riven backend - The API is accessible at the assigned port|
|`5432`| TCP | PostgreSQL - The SQL server is accessible at the assigned port|
|`5050`| TCP | pgAdmin 4 - A web UI is accessible at the assigned port|
|`8182`| TCP | Zilean - The API and Web Ui (/swagger/index.html) is accessible at the assigned port|
|`Random (9001-9999)`| TCP | Zurg - A web UI is accessible at the assigned port|


## 📂 Data Volumes

The following table describes the data volumes used by the container.  The mappings
are set via the `-v` parameter or via the docker-compose file within the ```volumes:``` section.  Each mapping is specified with the following
format: `<HOST_DIR>:<CONTAINER_DIR>[:PERMISSIONS]`.

| Container path  | Permissions | Description |
|-----------------|-------------|-------------|
|`/config`| rw | This is where the application stores the rclone.conf, and any files needing persistence. CAUTION: rclone.conf is overwritten upon start/restart of the container. Do NOT use an existing rclone.conf file if you have other rclone services |
|`/log`| rw | This is where the application stores its log files |
|`/data`| shared  | This is where rclone will be mounted.|
|`/zurg/RD`| rw| This is where Zurg will store the active configuration and data for RealDebrid. Not required when only utilizing Riven   |
|`/zurg/AD`| rw | This is where Zurg will store the active configuration and data for AllDebrid. Not required when only utilizing Riven   |
|`/riven/data`| rw | This is where Riven will store its data. Not required when only utilizing Zurg   |
|`/riven/mnt`| rw | This is where Riven will set its symlinks. Not required when only utilizing Zurg   |
|`/postgres_data`| rw | This is where PostgreSQL will store its data. Not required when only utilizing Zurg   |
|`/pgadmin/data`| rw | This is where pgAdmin 4 will store its data. Not required when only utilizing Zurg   |



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
|`ZURG_USER`| The username to be used for protecting the Zurg endpoints.  | ` ` | | | :heavy_check_mark: |
|`ZURG_PASS`| The password to be used for protecting the Zurg endpoints.  | ` `  | | | :heavy_check_mark: |
|`PGADMIN_SETUP_EMAIL`| The email for the pgAdmin setup | ` ` || :heavy_check_mark:|
|`PGADMIN_SETUP_PASSWORD`| The password for the pgAdmin setup | ` ` || :heavy_check_mark:|

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
  zurg_user:
    file: ./path/to/zurg_user.txt
  zurg_pass:
    file: ./path/to/zurg_pass.txt
  pgadmin_setup_email:
    file: ./path/to/pgadmin_setup_email.txt
  pgadmin_setup_password:
    file: ./path/to/pgadmin_setup_password.txt
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
- or join the Riven [discord server](https://discord.gg/VtYd42mxgb) 


## 🍻 Buy **[Riven Media](https://github.com/rivenmedia)** a beer/coffee? :)

If you enjoy the underlying projects and want to buy Riven Media a beer/coffee, feel free to use the [GitHub sponsor link](https://github.com/sponsors/dreulavelle/)

## 🍻 Buy **[yowmamasita](https://github.com/yowmamasita)** a beer/coffee? :)

If you enjoy the underlying projects and want to buy yowmamasita a beer/coffee, feel free to use the [GitHub sponsor link](https://github.com/sponsors/debridmediamanager)

## 🍻 Buy **[Nick Craig-Wood](https://github.com/ncw)** a beer/coffee? :) 

If you enjoy the underlying projects and want to buy Nick Craig-Wood a beer/coffee, feel free to use the website's [sponsor links](https://rclone.org/sponsor/)

## 🍻 Buy **[PostgreSQL](https://www.postgresql.org)** a beer/coffee? :)

If you enjoy the underlying projects and want to buy PostgreSQL a beer/coffee, feel free to use the [sponsor link](https://www.postgresql.org/about/donate/)

## ✅ GitHub Workflow Status
![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/I-am-PUID-0/DMB/docker-image.yml)
