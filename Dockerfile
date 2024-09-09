FROM rclone/rclone:latest AS rclone-stage

FROM python:3.11-alpine
LABEL name="DMB" \
    description="Debrid Media Bridge" \
    url="https://github.com/I-am-PUID-0/DMB"
COPY --from=rclone-stage /usr/local/bin/rclone /usr/local/bin/rclone

WORKDIR /

ADD https://raw.githubusercontent.com/debridmediamanager/zurg-testing/main/config.yml /zurg/
ADD https://raw.githubusercontent.com/debridmediamanager/zurg-testing/main/plex_update.sh /zurg/
ADD https://github.com/rivenmedia/riven-frontend/archive/refs/heads/main.zip /riven-frontend-main.zip

RUN \
  apk add --update --no-cache gcompat libstdc++ libxml2-utils curl tzdata nano ca-certificates wget fuse3 build-base linux-headers py3-cffi libffi-dev rust cargo openssl openssl-dev pkgconfig git npm ffmpeg postgresql-dev postgresql-client postgresql dotnet-sdk-8.0 postgresql-contrib && \
  mkdir -p /log /riven /riven/frontend && \
  if [ -f /riven-frontend-main.zip ]; then echo "File exists"; else echo "File does not exist"; fi && \
  unzip /riven-frontend-main.zip -d /riven && \
  mv /riven/riven-frontend-main/* /riven/frontend && \
  rm -rf /riven/riven-frontend-main

WORKDIR /riven/frontend

RUN \ 
  npm install -g pnpm && pnpm install && \
  pnpm run build && pnpm prune --prod

WORKDIR /

COPY . /./

ENV \
  XDG_CONFIG_HOME=/config \
  TERM=xterm

RUN \
  python3 -m venv /venv && \
  source /venv/bin/activate && \
  pip install --upgrade pip && \
  pip install -r /requirements.txt

HEALTHCHECK --interval=60s --timeout=10s \
  CMD ["/bin/sh", "-c", "source /venv/bin/activate && python /healthcheck.py"]

ENTRYPOINT ["/bin/sh", "-c", "source /venv/bin/activate && python /main.py"]
