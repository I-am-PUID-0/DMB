####################################################################################################################################################
# Stage 1: pgadmin-builder (Ubuntu 24.04)
####################################################################################################################################################
FROM ubuntu:24.04 AS pgadmin-builder
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y software-properties-common && \
    add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && \
    apt-get install -y \
    python3.11 \
    python3.11-venv \
    python3-pip && \
    rm -rf /var/lib/apt/lists/*
RUN python3.11 -m venv /pgadmin/venv && \
    /pgadmin/venv/bin/python -m pip install --upgrade pip && \
    /pgadmin/venv/bin/python -m pip install pgadmin4

####################################################################################################################################################
# Stage 2: systemstats-builder (Ubuntu 24.04)
####################################################################################################################################################
FROM ubuntu:24.04 AS systemstats-builder
ARG SYS_STATS_TAG
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/usr/lib/postgresql16/bin:$PATH"
RUN apt-get update && apt-get install -y software-properties-common wget gnupg2 lsb-release && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    apt-get install -y build-essential postgresql-server-dev-16 curl unzip jq && \
    rm -rf /var/lib/apt/lists/*
RUN find /usr -name pg_config && \
    /usr/bin/pg_config --version && \
    /usr/bin/pg_config --includedir && \
    /usr/bin/pg_config --libdir && \
    /usr/bin/pg_config --sharedir && \
    curl -L https://github.com/EnterpriseDB/system_stats/archive/refs/tags/${SYS_STATS_TAG}.zip -o system_stats-latest.zip && \
    unzip system_stats-latest.zip && \
    mv system_stats-*/ system_stats && \
    cd system_stats && export PATH="/usr/bin:$PATH" && \
    make USE_PGXS=1 && make install USE_PGXS=1 && \
    mkdir -p /usr/share/postgresql16/extension && \
    cp system_stats.control /usr/share/postgresql16/extension/ && \
    cp system_stats--*.sql /usr/share/postgresql16/extension/ && \
    cd .. && rm -rf system_stats system_stats-latest.zip

####################################################################################################################################################
# Stage 3: zilean-builder (Ubuntu 24.04 .NET SDK)
####################################################################################################################################################
FROM ubuntu:24.04 AS zilean-builder
ARG TARGETARCH
ARG ZILEAN_TAG
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y software-properties-common wget gnupg2 lsb-release && \
    add-apt-repository ppa:deadsnakes/ppa -y && add-apt-repository ppa:dotnet/backports -y && apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3.11-dev curl jq unzip dotnet-sdk-9.0 && \
    rm -rf /var/lib/apt/lists/*
RUN curl -L https://github.com/iPromKnight/zilean/archive/refs/tags/${ZILEAN_TAG}.zip -o zilean-latest.zip && \
    unzip zilean-latest.zip && \
    mv zilean-*/ /zilean && \
    echo $ZILEAN_TAG > /zilean/version.txt && \
    cd /zilean && \
    dotnet restore -a $TARGETARCH && \
    cd /zilean/src/Zilean.ApiService && \
    dotnet publish -c Release --no-restore -a $TARGETARCH -o /zilean/app/ && \
    cd /zilean/src/Zilean.Scraper && \
    dotnet publish -c Release --no-restore -a $TARGETARCH -o /zilean/app/ && \
    cd /zilean && \
    python3.11 -m venv /zilean/venv && \
    . /zilean/venv/bin/activate && \
    pip install -r /zilean/requirements.txt

####################################################################################################################################################
# Stage 4: riven-frontend-builder (Ubuntu 24.04 with Node.js)
####################################################################################################################################################
FROM ubuntu:24.04 AS riven-frontend-builder
ARG RIVEN_FRONTEND_TAG
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y curl unzip gnupg2 lsb-release && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    node -v && npm install -g npm@10 && npm -v && \
    npm install -g pnpm@latest-10 && pnpm -v && \
    rm -rf /var/lib/apt/lists/*
RUN curl -L https://github.com/rivenmedia/riven-frontend/archive/refs/tags/${RIVEN_FRONTEND_TAG}.zip -o riven-frontend.zip && \
    unzip riven-frontend.zip && \
    mkdir -p /riven/frontend && \
    mv riven-frontend-*/* /riven/frontend && rm riven-frontend.zip && \
    cd /riven/frontend && \
    sed -i '/export default defineConfig({/a\    build: {\n        minify: false\n    },' vite.config.ts && \
    sed -i "s#/riven/version.txt#/riven/frontend/version.txt#g" src/routes/settings/about/+page.server.ts && \
    sed -i "s/export const prerender = true;/export const prerender = false;/g" src/routes/settings/about/+page.server.ts && \
    echo "store-dir=./.pnpm-store" > /riven/frontend/.npmrc && \
    pnpm install && \
    pnpm run build && \
    pnpm prune --prod

####################################################################################################################################################
# Stage 5: riven-backend-builder (Ubuntu 24.04 with Python 3.11)
####################################################################################################################################################
FROM ubuntu:24.04 AS riven-backend-builder
ARG RIVEN_TAG
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y software-properties-common wget gnupg2 lsb-release unzip && \
    add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3.11-dev \
    curl gcc build-essential libxml2-utils linux-headers-generic  && \
    rm -rf /var/lib/apt/lists/*
RUN curl -L https://github.com/rivenmedia/riven/archive/refs/tags/${RIVEN_TAG}.zip -o riven.zip && \
    unzip riven.zip && \
    mkdir -p /riven/backend && \
    mv riven-*/* /riven/backend && rm riven.zip && \
    cd /riven/backend && \
    python3.11 -m venv /riven/backend/venv && \
    . /riven/backend/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --without dev

####################################################################################################################################################
# Stage 6: dmb-frontend-builder (Ubuntu 24.04 with Node.js)
####################################################################################################################################################
FROM ubuntu:24.04 AS dmb-frontend-builder
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y curl unzip build-essential gnupg2 lsb-release && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    node -v && npm install -g npm@10 && npm -v && \
    npm install -g pnpm@latest-10 && pnpm -v && \
    rm -rf /var/lib/apt/lists/*
RUN curl -L https://github.com/nicocapalbo/dmbdb/archive/refs/heads/main.zip -o dmb-frontend.zip && \
    unzip dmb-frontend.zip && \
    mkdir -p dmb/frontend && \
    mv dmbdb*/* /dmb/frontend && rm dmb-frontend.zip && \
    cd dmb/frontend && \
    echo "store-dir=./.pnpm-store" > /dmb/frontend/.npmrc && \
    pnpm install --reporter=verbose && \
    pnpm run build --log-level verbose

####################################################################################################################################################
# Stage 7: requirements-builder (Ubuntu 24.04 with Python 3.11)
####################################################################################################################################################
FROM ubuntu:24.04 AS requirements-builder
ENV DEBIAN_FRONTEND=noninteractive
COPY requirements.txt .
RUN apt-get update && apt-get install -y software-properties-common wget gnupg2 lsb-release && \
    add-apt-repository ppa:deadsnakes/ppa -y && apt-get update && \
    apt-get install -y python3.11 python3.11-venv python3.11-dev curl gcc build-essential libxml2-utils linux-headers-generic && \
    rm -rf /var/lib/apt/lists/* && \
    python3.11 -m venv /venv && \
    . /venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt

####################################################################################################################################################
# Stage 8: final-stage (Ubuntu 24.04 with Python 3.11, .NET SDK, PostgreSQL, pgAdmin4, Node.js, Rclone, Zilean, SystemStats, Riven, & DMB)
####################################################################################################################################################
FROM ubuntu:24.04 AS final-stage
ARG TARGETARCH
ENV DEBIAN_FRONTEND=noninteractive
ENV PATH="/usr/lib/postgresql/16/bin:$PATH"
LABEL name="DMB" \
      description="Debrid Media Bridge" \
      url="https://github.com/I-am-PUID-0/DMB" \
      maintainer="I-am-PUID-0"
      
RUN apt-get update && \
    apt-get install -y software-properties-common && \
    add-apt-repository ppa:dotnet/backports -y && \
    add-apt-repository ppa:deadsnakes/ppa -y && \
    apt-get update && \
    apt-get install -y \
      curl tzdata nano ca-certificates wget fuse3 \
      build-essential linux-headers-generic libpython3.11 python3.11 python3.11-venv python3-pip python3-dev \
      libxml2-utils git htop pkg-config libffi-dev libboost-filesystem-dev libboost-thread-dev \
      ffmpeg jq openssl bash unzip gnupg2 lsb-release dotnet-sdk-9.0 locales && \ 
    locale-gen en_US.UTF-8 && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.11 1 && \
    update-alternatives --install /usr/bin/pip pip /usr/bin/pip3 1 && \
    ln -sf /usr/lib/$(uname -m)-linux-gnu/libpython3.11.so.1 /usr/local/lib/libpython3.11.so.1 && \
    ln -sf /usr/lib/$(uname -m)-linux-gnu/libpython3.11.so.1.0 /usr/local/lib/libpython3.11.so.1.0 && \
    wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add - && \
    echo "deb http://apt.postgresql.org/pub/repos/apt/ $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
    apt-get update && \
    apt-get install -y \
      postgresql-client-16 postgresql-16 postgresql-contrib-16 pgagent && \
    rm -rf /var/lib/apt/lists/* && \
    curl -fsSL https://deb.nodesource.com/setup_22.x | bash - && \
    apt-get install -y nodejs && \
    node -v && npm install -g npm@10 && npm -v && \
    npm install -g pnpm@latest-10 && pnpm -v

WORKDIR /

RUN echo "export PATH=/usr/lib/postgresql/16/bin:$PATH" >> /etc/profile.d/postgresql.sh
RUN echo "export PATH=/usr/lib/postgresql/16/bin:$PATH" >> /root/.bashrc

COPY --from=requirements-builder /venv /venv
COPY --from=pgadmin-builder /pgadmin/venv /pgadmin/venv
COPY --from=systemstats-builder /usr/share/postgresql/16/extension/system_stats* /usr/share/postgresql/16/extension/
COPY --from=systemstats-builder /usr/lib/postgresql/16/lib/system_stats.so /usr/lib/postgresql/16/lib/
COPY --from=zilean-builder /zilean /zilean
COPY --from=riven-frontend-builder /riven/frontend /riven/frontend
COPY --from=riven-backend-builder /riven/backend /riven/backend
COPY --from=dmb-frontend-builder /dmb/frontend /dmb/frontend
COPY --from=rclone/rclone:latest /usr/local/bin/rclone /usr/local/bin/rclone
ADD https://raw.githubusercontent.com/debridmediamanager/zurg-testing/main/config.yml /zurg/
ADD https://raw.githubusercontent.com/debridmediamanager/zurg-testing/main/scripts/plex_update.sh /zurg/

COPY . /./

ENV XDG_CONFIG_HOME=/config \
    TERM=xterm

HEALTHCHECK --interval=60s --timeout=10s \
  CMD ["/bin/bash", "-c", ". /venv/bin/activate && python /healthcheck.py"]

ENTRYPOINT ["/bin/bash", "-c", ". /venv/bin/activate && python /main.py"]
