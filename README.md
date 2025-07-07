<div align="center" style="max-width: 100%; height: auto;">
  <h1>🎬 Debrid Media Bridge 🎬</h1>
  <a href="https://github.com/I-am-PUID-0/DMB">
    <picture>
      <source srcset="https://github.com/I-am-PUID-0/DMB/assets/36779668/d0cbc785-2e09-41da-b226-924fdfcc1f21">
      <img
        alt="DMB"
        src="https://github.com/I-am-PUID-0/DMB/assets/36779668/d0cbc785-2e09-41da-b226-924fdfcc1f21"
        style="max-width: 100%; height: auto;">
    </picture>
  </a>
</div>
<div align="center" style="margin-top: 1em;">
  <a href="https://github.com/I-am-PUID-0/DMB/stargazers">
    <img
      alt="GitHub Repo stars"
      src="https://img.shields.io/github/stars/I-am-PUID-0/DMB?style=for-the-badge"
    /></a>
  <a href="https://github.com/I-am-PUID-0/DMB/issues">
    <img
      alt="Issues"
      src="https://img.shields.io/github/issues/I-am-PUID-0/DMB?style=for-the-badge"
    /></a>
  <a href="https://github.com/I-am-PUID-0/DMB/blob/master/COPYING">
    <img
      alt="License"
      src="https://img.shields.io/github/license/I-am-PUID-0/DMB?style=for-the-badge"
    /></a>
  <a href="https://github.com/I-am-PUID-0/DMB/graphs/contributors">
    <img
      alt="Contributors"
      src="https://img.shields.io/github/contributors/I-am-PUID-0/DMB?style=for-the-badge"
    /></a>
  <a href="https://hub.docker.com/r/iampuid0/dmb">
    <img
      alt="Docker Pulls"
      src="https://img.shields.io/docker/pulls/iampuid0/dmb?style=for-the-badge&logo=docker&logoColor=white"
    /></a>
  <a href="https://github.com/I-am-PUID-0/DMB/actions?query=workflow%3A%22Docker+Image+CI%22">
    <img
      alt="GitHub Workflow Status"
      src="https://img.shields.io/github/actions/workflow/status/I-am-PUID-0/DMB/docker-image.yml?style=for-the-badge&label=Docker%20build"
    /></a>
  <a href="https://discord.gg/8dqKUBtbp5">
    <img
      alt="Join Discord"
      src="https://img.shields.io/badge/Join%20us%20on%20Discord-5865F2?style=for-the-badge&logo=discord&logoColor=white"
    /></a>
</div>


> [!CAUTION]
> Docker Desktop **CANNOT** be used to run DMB. Docker Desktop does not support the [mount propagation](https://docs.docker.com/storage/bind-mounts/#configure-bind-propagation) required for rclone mounts.
>
> ![image](https://github.com/I-am-PUID-0/DMB/assets/36779668/aff06342-1099-4554-a5a4-72a7c82cb16e)
>
> You might have some success provided the `:rshared` flag is omitted from the `/mnt/debird` bind mount. 
> Which is means you can not use Decypharr.

> [!CAUTION]
> See the DMB Docs for [alternative deployment options](https://i-am-puid-0.github.io/DMB/deployment/wsl) to run DMB on Windows through WSL2.


## 📜 Description

**Debrid Media Bridge (DMB)** is an All-In-One (AIO) docker image for the unified deployment of the following projects/tools, with the caveat of no media servers included.

If you want a media server included check out [DUMB (Debrid Unlimited Media Bridge)](https://github.com/I-am-PUID-0/DUMB)

## 📦 Projects Included

> [!NOTE]
> You are free to use whichever components you like. Not all are required, and some may provide overlapping functionality in different ways.

| Project                                                        | Author                                                                   | Community / Docs / Support                                                                                 | 🍻 Support Dev                                                                                       |
| -------------------------------------------------------------- | ------------------------------------------------------------------------ | ---------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------------------------------------- |
| [cli_debrid](https://github.com/godver3/cli_debrid)            | [godver3](https://github.com/godver3)                                    | [Discord](https://discord.gg/jAmqZJCZJ4)                                                                   | [Sponsor](https://github.com/sponsors/godver3)                                                        |
| [dmbdb](https://github.com/nicocapalbo/dmbdb)                  | [nicocapalbo](https://github.com/nicocapalbo)                            | [Issues](https://github.com/nicocapalbo/dmbdb/issues)                                                      | —                                                                                                     |
| [Decypharr](https://github.com/sirrobot01/decypharr)           | [Mukhtar Akere](https://github.com/sirrobot01)                           | [Docs](https://sirrobot01.github.io/decypharr/) • [Issues](https://github.com/sirrobot01/decypharr/issues) | [Sponsor](https://github.com/sponsors/sirrobot01)                                                     |
| [pgAdmin 4](https://www.pgadmin.org/)                          | [pgAdmin Team](https://www.pgadmin.org/development/)                     | [Docs](https://www.pgadmin.org/docs/) • [Support](https://www.pgadmin.org/support/)                        | [Donate](https://www.pgadmin.org/donate/)                                                             |
| [phalanx_db](https://github.com/godver3/phalanx_db_hyperswarm) | [godver3](https://github.com/godver3)                                    | [Discord](https://discord.gg/jAmqZJCZJ4)                                                                   | [Sponsor](https://github.com/sponsors/godver3)                                                        |
| [plex_debrid](https://github.com/itsToggle/plex_debrid)        | [itsToggle](https://github.com/itsToggle)                                | [Discord](https://discord.gg/u3vTDGjeKE) • [Issues](https://github.com/itsToggle/plex_debrid/issues)       | [Affiliate](http://real-debrid.com/?id=5708990) • [PayPal](https://www.paypal.com/paypalme/oidulibbe) |
| [PostgreSQL](https://www.postgresql.org/)                      | [Michael Stonebraker](https://en.wikipedia.org/wiki/Michael_Stonebraker) | [Docs](https://www.postgresql.org/docs/)                                                                   | [Donate](https://www.postgresql.org/about/donate/)                                                    |
| [rclone](https://github.com/rclone/rclone)                     | [Nick Craig-Wood](https://github.com/ncw)                                | [Docs](https://rclone.org/)                                                                                | [Sponsor](https://rclone.org/sponsor/)                                                                |
| [Riven](https://github.com/rivenmedia/riven)                   | [Riven Media](https://github.com/rivenmedia)                             | [Discord](https://discord.gg/VtYd42mxgb) • [Discussions](https://github.com/orgs/rivenmedia/discussions)   | [Sponsor](https://github.com/sponsors/dreulavelle/)                                                   |
| [Zilean](https://github.com/iPromKnight/zilean)                | [iPromKnight](https://github.com/iPromKnight)                            | [Docs](https://ipromknight.github.io/zilean/) • [Issues](https://github.com/iPromKnight/zilean/issues)     | —                                                                                                     |
| [Zurg](https://github.com/debridmediamanager/zurg-testing)     | [yowmamasita](https://github.com/yowmamasita)                            | [Wiki](https://github.com/debridmediamanager/zurg-testing/wiki)                                            | [Sponsor](https://github.com/sponsors/debridmediamanager)                                             |


## 🤩 Want the Media Server Built-In?

**DMB does not include a Media Server within the image.**  
This project is designed to manage and prepare media through debrid services, but assumes that you will run your media server (like Plex, Jellyfin, or Emby) separately.

> [!TIP]
> ### If you're looking for an **all-in-one solution** that includes a media server directly inside the container — fully integrated with Riven, Zurg, rclone, and more!?
> 
> ### Check out [**📦 DUMB (Debrid Unlimited Media Bridge)**](https://github.com/I-am-PUID-0/DUMB):


⚙️ DUMB includes:
* Plex Media Server preconfigured with mount support
* Built-in support for Real-Debrid workflows
* Single-container deployment for easier onboarding
* Tight integration between media prep, serving, and metadata handling

📦 [**View DUMB on GitHub **](https://github.com/I-am-PUID-0/DUMB)

## 🌟 Features

See the DMB [Docs](https://i-am-puid-0.github.io/DMB/features) for a full list of features and settings.

## 🐳 Docker Hub

A prebuilt image is hosted on [Docker Hub](https://hub.docker.com/r/iampuid0/dmb).

## 🏷️ GitHub Container Registry

A prebuilt image is hosted on [GitHub Container Registry](https://github.com/I-am-PUID-0/DMB/pkgs/container/DMB).

## 🐳 Docker-compose

> [!NOTE]
> The below examples are not exhaustive and are intended to provide a starting point for deployment.

```YAML
services:
  DMB:
    container_name: DMB
    image: iampuid0/dmb:latest                                       ## Optionally, specify a specific version of DMB w/ image: iampuid0/dmb:2.0.0
    stop_grace_period: 30s                                           ## Adjust as need to allow for graceful shutdown of the container
    shm_size: 128mb                                                  ## Increased for PostgreSQL
    stdin_open: true                                                 ## docker run -i
    tty: true                                                        ## docker run -t
    volumes:
      - /home/username/docker/DMB/config:/config                     ## Location of configuration files. If a Zurg config.yml and/or Zurg app is placed here, it will be used to override the default configuration and/or app used at startup.
      - /home/username/docker/DMB/log:/log                           ## Location for logs
      - /home/username/docker/DMB/Zurg/RD:/zurg/RD                   ## Location for Zurg RealDebrid active configuration
      - /home/username/docker/DMB/Zurg/mnt:/data:rshared             ## Location for rclone mount to host
      - /home/username/docker/DMB/Riven/data:/riven/backend/data     ## Location for Riven backend data
      - /home/username/docker/DMB/Riven/mnt:/mnt                     ## Location for Riven symlinks
      - /home/username/docker/DMB/PostgreSQL/data:/postgres_data     ## Location for PostgreSQL database
      - /home/username/docker/DMB/pgAdmin4/data:/pgadmin/data        ## Location for pgAdmin 4 data
      - /home/username/docker/DMB/Zilean/data:/zilean/app/data       ## Location for Zilean data
      - /home/username/docker/DMB/plex_debrid:/plex_debrid/config    ## Location for plex_debrid data
      - /home/username/docker/DMB/cli_debrid:/cli_debrid/data        ## Location for cli_debrid data
      - /home/username/docker/DMB/phalanx_db:/phalanx_db/data        ## Location for phalanx_db data
      - /home/username/docker/DMB/decypharr:/decypharr               ## Location for decypharr data
    environment:
      - TZ=
      - PUID=
      - PGID=
      - DMB_LOG_LEVEL=INFO
      - ZURG_INSTANCES_REALDEBRID_API_KEY=
      - RIVEN_FRONTEND_ENV_ORIGIN=http://0.0.0.0:3000               ## See Riven documentation for more details
    # network_mode: container:gluetun                               ## Example to attach to gluetun vpn container if realdebrid blocks IP address
    ports:
      - "3005:3005"                                                 ## DMB Frontend
      - "3000:3000"                                                 ## Riven Frontend
      - "5050:5050"                                                 ## pgAdmin 4
      - "5000:5000"                                                 ## CLI Debrid Frontend      
      - "8282:8282"                                                 ## Decypharr Frontend         
    devices:
      - /dev/fuse:/dev/fuse:rwm
    cap_add:
      - SYS_ADMIN
    security_opt:
      - apparmor:unconfined
      - no-new-privileges
```

## 🎥 Example Plex Docker-compose

> [!IMPORTANT]
> The Plex server must be started after the rclone mount is available.  
> The below example uses the `depends_on` parameter to delay the start of the Plex server until the rclone mount is available.  
> The rclone mount must be shared to the Plex container.  
> The rclone mount location should not be added to the Plex library.  
> The Riven (If being used) symlink location must be shared to the Plex container and added to the Plex library.  
>
> Note: for `depends_on` to work this needs to be within the same docker compose file.

```YAML
services:
  DMB:
    ...
      {{ DMB CONFIG HERE }}
    ...
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
      - TZ=
      - PLEX_UID=                                           ## Same as PUID
      - PLEX_GID=                                           ## Same as PGID
      - PLEX_CLAIM=claimToken                               ## Need for the first run of Plex - get claimToken here https://www.plex.tv/claim/
    ports:
      - "32400:32400"
    healthcheck:
      test: curl --connect-timeout 15 --silent --show-error --fail http://localhost:32400/identity
      interval: 1m00s
      timeout: 15s
      retries: 3
      start_period: 1m00s
    depends_on:                                             ## Used to delay the startup of plex to ensure the rclone mount is available.
      DMB:                                                  ## The name of the container running rclone
        condition: service_healthy
        restart: true                                       ## Will automatically restart the plex container if the DMB container restarts
```

## 🌐 Environment Variables

The following table lists the required environment variables used by the container.  
The environment variables are set via the `-e` parameter or via the docker-compose file within the `environment:` section or with a .env file saved to the config directory.  
Value of this parameter is listed as `<VARIABLE_NAME>=<Value>`

Variables required by DMB:
| Variable                            | Default               | Description                                                                                                               | Required for DMB |
| ----------------------------------- | --------------------- | ------------------------------------------------------------------------------------------------------------------------- | ---------------- |
| `PUID`                              | `1000`                | Your User ID                                                                                                              | ✔️             |
| `PGID`                              | `1000`                | Your Group ID                                                                                                             | ✔️             |
| `TZ`                                | `(null)`              | Your time zone listed as `Area/Location`                                                                                  | ✔️             |
| `ZURG_INSTANCES_REALDEBRID_API_KEY` | `(null)`              | Enter your Real-Debrid API Token                                                                                          | ✔️             |
| `RIVEN_FRONTEND_ENV_ORIGIN`         | `http://0.0.0.0:3000` | The IP address used to access the DMB frontend.  Change this to the IP address you use in the browser for Riven Frontend. | ✔️             |

See the [.env.example](https://github.com/I-am-PUID-0/DMB/blob/master/.env.example) for more.

## 🌐 Ports Used

> [!NOTE]
> The below examples are default and may be configurable with the use of additional environment variables.

The following table describes the ports used by the container. The mappings are set via the `-p` parameter or via the docker-compose file within the `ports:` section. Each mapping is specified with the following format: `<HOST_PORT>:<CONTAINER_PORT>[:PROTOCOL]`.

| Container port | Protocol | Description                                                                          |
| -------------- | -------- | ------------------------------------------------------------------------------------ |
| `3005`         | TCP      | DMB frontend - a web UI is accessible at the assigned port                           |
| `3000`         | TCP      | Riven frontend - A web UI is accessible at the assigned port                         |
| `8080`         | TCP      | Riven backend - The API is accessible at the assigned port                           |
| `5432`         | TCP      | PostgreSQL - The SQL server is accessible at the assigned port                       |
| `5050`         | TCP      | pgAdmin 4 - A web UI is accessible at the assigned port                              |
| `8182`         | TCP      | Zilean - The API and Web Ui (/swagger/index.html) is accessible at the assigned port |
| `9090`         | TCP      | Zurg - A web UI is accessible at the assigned port                                   |
| `5000`         | TCP      | CLI Debrid - A web UI is accessible at the assigned port                             |
| `8888`         | TCP      | Phalanx DB - The API is accessible at the assigned port                              |
| `8282`         | TCP      | Decypharr - A web UI is accessible at the assigned port                              |

## 📂 Data Volumes

The following table describes the data volumes used by the container. The mappings
are set via the `-v` parameter or via the docker-compose file within the `volumes:` section. Each mapping is specified with the following
format: `<HOST_DIR>:<CONTAINER_DIR>[:PERMISSIONS]`.

| Container path        | Permissions | Description                                                                                                                                                                                                                                 |
| --------------------- | ----------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `/config`             | rw          | This is where the application stores the rclone.conf, and any files needing persistence. CAUTION: rclone.conf is overwritten upon start/restart of the container. Do NOT use an existing rclone.conf file if you have other rclone services |
| `/log`                | rw          | This is where the application stores its log files                                                                                                                                                                                          |
| `/data`               | rshared     | This is where rclone will be mounted.                                                                                                                                                                                                       |
| `/zurg/RD`            | rw          | This is where Zurg will store the active configuration and data for RealDebrid.                                                                                                                                                             |
| `/riven/data`         | rw          | This is where Riven will store its data.                                                                                                                                                                                                    |
| `/riven/mnt`          | rw          | This is where Riven will set its symlinks.                                                                                                                                                                                                  |
| `/postgres_data`      | rw          | This is where PostgreSQL will store its data.                                                                                                                                                                                               |
| `/pgadmin/data`       | rw          | This is where pgAdmin 4 will store its data.                                                                                                                                                                                                |
| `/plex_debrid/config` | rw          | This is where plex_debrid will store its data.                                                                                                                                                                                              |
| `/cli_debrid/data`    | rw          | This is where cli_debrid will store its data.                                                                                                                                                                                               |
| `/phalanx_db/data`    | rw          | This is where phalanx_db will store its data.                                                                                                                                                                                               |
| `/decypharr`          | rw          | This is where decypharr will store its data.                                                                                                                                                                                                |

## 📝 TODO

See the [DMB roadmap](https://github.com/users/I-am-PUID-0/projects/6) for a list of planned features and enhancements.


## 🚀 Deployment

DMB allows for the simultaneous or individual deployment of any of the services

For additional details on deployment, see the [DMB Docs](https://i-am-puid-0.github.io/DMB/services/)

## 🌍 Community

- For questions related to DMB, see the GitHub [discussions](https://github.com/I-am-PUID-0/DMB/discussions)
- or create a new [issue](https://github.com/I-am-PUID-0/DMB/issues) if you find a bug or have an idea for an improvement.
- or join the DMB [discord server](https://discord.gg/8dqKUBtbp5)


## 🛠️ Developmnent

### Development support:

- The repo contains a devcontainer for use with vscode.
- Bind mounts will need to be populated with content from this repo

