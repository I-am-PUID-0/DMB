FROM python:3.11-alpine AS pgagent-builder
ARG PGAGENT_TAG
RUN apk add --update --no-cache --virtual .build-deps \
    cmake boost-dev build-base linux-headers postgresql16-dev-16.6-r0 curl unzip jq && \
    curl -L https://github.com/pgadmin-org/pgagent/archive/refs/tags/${PGAGENT_TAG}.zip -o pgagent-latest.zip && \
    unzip pgagent-latest.zip && \
    mv pgagent-*/ pgagent && \
    cd pgagent && mkdir build && cd build && \
    cmake -DCMAKE_INSTALL_PREFIX=/usr/local .. && make && make install && \
    mkdir -p /usr/share/postgresql16/extension && \
    cp ../sql/pgagent*.sql /usr/share/postgresql16/extension/ && \
    cp ../pgagent.control.in /usr/share/postgresql16/extension/pgagent.control && \
    PGAGENT_VERSION=$(ls /usr/share/postgresql16/extension/pgagent--*.sql | sed -E 's/.*pgagent--([0-9]+\.[0-9]+).*/\1/' | sort -V | tail -n 1) && \
    sed -i "s/\${MAJOR_VERSION}.\${MINOR_VERSION}/$PGAGENT_VERSION/" /usr/share/postgresql16/extension/pgagent.control && \
    mkdir /pgadmin && cd /pgadmin && python3 -m venv /pgadmin/venv && \
    source /pgadmin/venv/bin/activate && \
    pip install pip==24.0 setuptools==66.0.0 && \
    pip install pgadmin4 && \
    cd ../.. && rm -rf pgagent pgagent-latest.zip && \
    apk del .build-deps 


FROM alpine:3.20 AS systemstats-builder
ARG SYS_STATS_TAG
RUN apk add --update --no-cache --virtual .build-deps \
    build-base postgresql16-dev-16.6-r0 curl unzip jq && \
    curl -L https://github.com/EnterpriseDB/system_stats/archive/refs/tags/${SYS_STATS_TAG}.zip -o system_stats-latest.zip && \
    unzip system_stats-latest.zip && \
    mv system_stats-*/ system_stats && \
    cd system_stats && export PATH="/usr/bin:$PATH" && \
    make USE_PGXS=1 && make install USE_PGXS=1 && \
    mkdir -p /usr/share/postgresql16/extension && \
    cp system_stats.control /usr/share/postgresql16/extension/ && \
    cp system_stats--*.sql /usr/share/postgresql16/extension/ && \
    cd .. && rm -rf system_stats system_stats-latest.zip && \
    apk del .build-deps


FROM --platform=$BUILDPLATFORM mcr.microsoft.com/dotnet/sdk:9.0-alpine AS zilean-builder
ARG TARGETARCH
ARG ZILEAN_TAG
RUN echo "https://dl-cdn.alpinelinux.org/alpine/v3.18/main" > /etc/apk/repositories && \
    echo "https://dl-cdn.alpinelinux.org/alpine/v3.18/community" >> /etc/apk/repositories && \
    apk add --update --no-cache curl jq python3=~3.11 py3-pip=~23.1 && \
    curl -L https://github.com/iPromKnight/zilean/archive/refs/tags/${ZILEAN_TAG}.zip -o zilean-latest.zip && \
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
    python3 -m venv /zilean/venv && \
    source /zilean/venv/bin/activate && \
    pip install -r /zilean/requirements.txt


FROM python:3.11-alpine AS riven-frontend-builder
ARG RIVEN_FRONTEND_TAG
RUN apk add --no-cache curl npm && \
    curl -L https://github.com/rivenmedia/riven-frontend/archive/refs/tags/${RIVEN_FRONTEND_TAG}.zip -o riven-frontend.zip && \
    unzip riven-frontend.zip && \
    mkdir -p /riven/frontend && \
    mv riven-frontend-*/* /riven/frontend && rm riven-frontend.zip && \
    cd /riven/frontend && \
    sed -i '/export default defineConfig({/a\    build: {\n        minify: false\n    },' /riven/frontend/vite.config.ts && \
    sed -i "s#/riven/version.txt#/riven/frontend/version.txt#g" /riven/frontend/src/routes/settings/about/+page.server.ts && \
    sed -i "s/export const prerender = true;/export const prerender = false;/g" /riven/frontend/src/routes/settings/about/+page.server.ts && \
    npm install -g pnpm && \
    pnpm install && \
    pnpm run build && \
    pnpm prune --prod


FROM python:3.11-alpine AS riven-backend-builder
ARG RIVEN_TAG
RUN apk add --no-cache curl gcc musl-dev python3-dev gcompat libstdc++ libxml2-utils linux-headers && \
    curl -L https://github.com/rivenmedia/riven/archive/refs/tags/${RIVEN_TAG}.zip -o riven.zip && \
    unzip riven.zip && \
    mkdir -p /riven/backend && \
    mv riven-*/* /riven/backend && rm riven.zip && \
    cd /riven/backend && \
    python3 -m venv /riven/backend/venv && \
    source /riven/backend/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --without dev


FROM python:3.11-alpine AS requirements-builder
COPY requirements.txt .
RUN apk add --no-cache curl gcc musl-dev python3-dev gcompat libstdc++ libxml2-utils linux-headers && \
    python3 -m venv /venv && \
    source /venv/bin/activate && \
    pip install --upgrade pip && \
    pip install -r requirements.txt


FROM python:3.11-alpine AS final-stage
ARG TARGETARCH
LABEL name="DMB" \
    description="Debrid Media Bridge" \
    url="https://github.com/I-am-PUID-0/DMB"

RUN apk add --update --no-cache gcompat libstdc++ libxml2-utils curl tzdata nano ca-certificates wget fuse3 build-base \
    linux-headers py3-cffi libffi-dev rust cargo jq openssl pkgconfig npm boost-filesystem boost-thread \
    ffmpeg postgresql16-client=16.6-r0 postgresql16=16.6-r0 postgresql16-contrib=16.6-r0

RUN npm install -g pnpm

RUN ARCH=$(case "$TARGETARCH" in \
        "amd64") echo "x64" ;; \
        "arm64") echo "arm64" ;; \
        *) echo "$TARGETARCH" ;; \
    esac) && \
    curl -L --retry 5 --retry-delay 5 https://dotnetcli.azureedge.net/dotnet/Sdk/9.0.100/dotnet-sdk-9.0.100-linux-musl-${ARCH}.tar.gz -o dotnet-sdk.tar.gz && \
    ls -lh dotnet-sdk.tar.gz && \
    file dotnet-sdk.tar.gz && \
    mkdir -p /usr/share/dotnet && \
    tar -C /usr/share/dotnet -xzf dotnet-sdk.tar.gz && \
    ln -s /usr/share/dotnet/dotnet /usr/bin/dotnet && \
    rm dotnet-sdk.tar.gz && \
    dotnet --version

WORKDIR /
COPY --from=rclone/rclone:latest /usr/local/bin/rclone /usr/local/bin/rclone
COPY --from=pgagent-builder /usr/local/bin/pgagent /usr/local/bin/pgagent
COPY --from=pgagent-builder /usr/share/postgresql16/extension/pgagent* /usr/share/postgresql16/extension/
COPY --from=pgagent-builder /pgadmin/venv /pgadmin/venv
COPY --from=systemstats-builder /usr/share/postgresql16/extension/system_stats* /usr/share/postgresql16/extension/
COPY --from=systemstats-builder /usr/lib/postgresql16/system_stats.so /usr/lib/postgresql16/
COPY --from=zilean-builder /zilean /zilean
COPY --from=riven-frontend-builder /riven/frontend /riven/frontend
COPY --from=riven-backend-builder /riven/backend /riven/backend
ADD https://raw.githubusercontent.com/debridmediamanager/zurg-testing/main/config.yml /zurg/
ADD https://raw.githubusercontent.com/debridmediamanager/zurg-testing/main/scripts/plex_update.sh /zurg/
COPY --from=requirements-builder /venv /venv
COPY . /./

ENV \
  XDG_CONFIG_HOME=/config \
  TERM=xterm 


HEALTHCHECK --interval=60s --timeout=10s \
  CMD ["/bin/sh", "-c", "source /venv/bin/activate && python /healthcheck.py"]

ENTRYPOINT ["/bin/sh", "-c", "source /venv/bin/activate && python /main.py"]
