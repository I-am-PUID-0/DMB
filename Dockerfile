FROM alpine:3.20 AS pgagent-builder
RUN apk add --no-cache --virtual .build-deps \
    cmake boost-dev build-base linux-headers postgresql-dev curl unzip && \
  curl -L https://github.com/pgadmin-org/pgagent/archive/refs/heads/master.zip -o pgagent.zip && \
  unzip pgagent.zip && \
  cd pgagent-master && mkdir build && cd build && \
  cmake -DCMAKE_INSTALL_PREFIX=/usr/local \
        -DBoost_INCLUDE_DIR=/usr/include \
        -DBoost_LIBRARY_DIRS=/usr/lib \
        -DCMAKE_POLICY_DEFAULT_CMP0153=NEW .. && \
  make && make install && \
  mkdir -p /usr/share/postgresql16/extension && \
  cp ../sql/pgagent*.sql /usr/share/postgresql16/extension/ && \
  cp ../pgagent.control.in /usr/share/postgresql16/extension/pgagent.control && \
  PGAGENT_VERSION=$(ls /usr/share/postgresql16/extension/pgagent--*.sql | sed -E 's/.*pgagent--([0-9]+\.[0-9]+).*/\1/' | sort -V | tail -n 1) && \
  sed -i "s/\${MAJOR_VERSION}.\${MINOR_VERSION}/$PGAGENT_VERSION/" /usr/share/postgresql16/extension/pgagent.control && \
  cd ../.. && rm -rf pgagent-master pgagent.zip && \
  apk del .build-deps


FROM alpine:3.20 AS systemstats-builder
RUN apk add --no-cache --virtual .build-deps \
    build-base postgresql-dev curl unzip && \
  curl -L https://github.com/EnterpriseDB/system_stats/archive/refs/heads/master.zip -o system_stats.zip && \
  unzip system_stats.zip && \
  cd system_stats-master && export PATH="/usr/bin:$PATH" && \
  make USE_PGXS=1 && make install USE_PGXS=1 && \
  mkdir -p /usr/share/postgresql16/extension && \
  cp system_stats.control /usr/share/postgresql16/extension/ && \
  cp system_stats--*.sql /usr/share/postgresql16/extension/ && \
  cd .. && rm -rf system_stats-master system_stats.zip && \
  apk del .build-deps

FROM --platform=$BUILDPLATFORM mcr.microsoft.com/dotnet/sdk:8.0-alpine3.19 AS zilean-builder
ARG TARGETARCH
RUN apk add --update --no-cache curl jq
RUN RELEASE_TAG=$(curl -s https://api.github.com/repos/iPromKnight/zilean/releases/latest | jq -r .tag_name) && \
    curl -L https://github.com/iPromKnight/zilean/archive/refs/tags/$RELEASE_TAG.zip -o zilean-latest.zip && \
    unzip zilean-latest.zip && \
    mv zilean-*/ /zilean && \
    echo $RELEASE_TAG > /zilean/version.txt

WORKDIR /zilean
RUN dotnet restore -a $TARGETARCH
WORKDIR /zilean/src/Zilean.ApiService
RUN dotnet publish -c Release --no-restore -a $TARGETARCH -o /zilean/app/
WORKDIR /zilean/src/Zilean.DmmScraper
RUN dotnet publish -c Release --no-restore -a $TARGETARCH -o /zilean/app/


FROM python:3.11-alpine AS final-stage
LABEL name="DMB" \
    description="Debrid Media Bridge" \
    url="https://github.com/I-am-PUID-0/DMB"


RUN apk add --update --no-cache gcompat libstdc++ libxml2-utils curl tzdata nano ca-certificates wget fuse3 build-base \
  boost-filesystem boost-thread linux-headers py3-cffi libffi-dev rust cargo jq openssl openssl-dev pkgconfig git npm \
  ffmpeg postgresql-dev postgresql-client postgresql dotnet-sdk-8.0 postgresql-contrib postgresql-client postgresql \
  dotnet-sdk-8.0 postgresql-contrib

COPY --from=rclone/rclone:latest /usr/local/bin/rclone /usr/local/bin/rclone
COPY --from=pgagent-builder /usr/local/bin/pgagent /usr/local/bin/pgagent
COPY --from=pgagent-builder /usr/share/postgresql16/extension/pgagent* /usr/share/postgresql16/extension/
COPY --from=systemstats-builder /usr/share/postgresql16/extension/system_stats* /usr/share/postgresql16/extension/
COPY --from=systemstats-builder /usr/lib/postgresql16/system_stats.so /usr/lib/postgresql16/
COPY --from=zilean-builder /zilean/app /zilean/app
COPY --from=zilean-builder /zilean/version.txt /zilean/version.txt
COPY --from=zilean-builder /zilean/requirements.txt /zilean/requirements.txt

WORKDIR /

ADD https://raw.githubusercontent.com/debridmediamanager/zurg-testing/main/config.yml /zurg/
ADD https://raw.githubusercontent.com/debridmediamanager/zurg-testing/main/plex_update.sh /zurg/

RUN RELEASE_TAG=$(curl -s https://api.github.com/repos/rivenmedia/riven-frontend/releases/latest | jq -r .tag_name) && \
  curl -L https://github.com/rivenmedia/riven-frontend/archive/refs/tags/$RELEASE_TAG.zip -o /riven-frontend-latest.zip

RUN \
  mkdir -p /log /config /riven /riven/frontend /riven/backend /zilean /pgadmin/venv /pgadmin/data && \
  if [ -f /riven-frontend-latest.zip ]; then echo "File exists"; else echo "File does not exist"; fi && \
  unzip /riven-frontend-latest.zip -d /riven && \
  mv /riven/riven-frontend-*/* /riven/frontend && \
  rm -rf /riven/riven-frontend-* && \
  rm -rf /riven-frontend-latest.zip

RUN sed -i '/export default defineConfig({/a\    build: {\n        minify: false\n    },' /riven/frontend/vite.config.ts
RUN sed -i "s#/riven/version.txt#/riven/frontend/version.txt#g" /riven/frontend/src/routes/settings/about/+page.server.ts
RUN sed -i "s/export const prerender = true;/export const prerender = false;/g" /riven/frontend/src/routes/settings/about/+page.server.ts

WORKDIR /riven/frontend

RUN npm install -g pnpm && pnpm install && pnpm run build && pnpm prune --prod

WORKDIR /

RUN RELEASE_TAG=$(curl -s https://api.github.com/repos/rivenmedia/riven/releases/latest | jq -r .tag_name) && \
  curl -L https://github.com/rivenmedia/riven/archive/refs/tags/$RELEASE_TAG.zip -o /riven-latest.zip

RUN \
  if [ -f /riven-latest.zip ]; then echo "File exists"; else echo "File does not exist"; fi && \
  unzip /riven-latest.zip -d /riven && \
  mv /riven/riven-*/* /riven/backend && \
  rm -rf /riven/riven-* && \
  rm -rf /riven-latest.zip

WORKDIR /riven/backend

RUN python3 -m venv /riven/backend/venv && \
    source /riven/backend/venv/bin/activate && \
    pip install --upgrade pip && \
    pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root --without dev 

WORKDIR /

RUN \
  python3 -m venv /zilean/venv && \
  source /zilean/venv/bin/activate && \
  pip install --upgrade pip && \
  pip install -r /zilean/requirements.txt 

WORKDIR /

COPY . /./

RUN \
  python3 -m venv /pgadmin/venv && \
  source /pgadmin/venv/bin/activate && \
  pip install pip==24.0 setuptools==66.0.0 && \
  pip install pgadmin4 && \
  deactivate

RUN \
  python3 -m venv /venv && \
  source /venv/bin/activate && \
  pip install --upgrade pip && \
  pip install -r /requirements.txt

ENV \
  XDG_CONFIG_HOME=/config \
  TERM=xterm 


HEALTHCHECK --interval=60s --timeout=10s \
  CMD ["/bin/sh", "-c", "source /venv/bin/activate && python /healthcheck.py"]

ENTRYPOINT ["/bin/sh", "-c", "source /venv/bin/activate && python /main.py"]
