FROM python:3.13-slim-trixie

# Set before the apt step so it can point /etc/localtime at the same zone.
ENV TZ=America/Vancouver

# tzdata-legacy carries the backward-compatibility aliases (Canada/Pacific,
# US/Pacific), split out of tzdata in Debian 13. /etc/localtime is repointed
# because TZ alone leaves it at Etc/UTC.
RUN apt-get update \
    && apt-get install -y --no-install-recommends tzdata tzdata-legacy \
    && ln -sf "/usr/share/zoneinfo/$TZ" /etc/localtime \
    && echo "$TZ" > /etc/timezone \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY . .
ENTRYPOINT ["python3", "cli.py"]
