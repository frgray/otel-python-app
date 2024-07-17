FROM --platform=linux/amd64 python:3.10-slim

SHELL ["/bin/bash", "-c"]

USER root

# Install build dependencies / Add ssh fingerprints for trusted hosts and set permissions
RUN /usr/bin/apt update \
    && DEBIAN_FRONTEND=noninteractive TZ=Etc/UTC /usr/bin/apt install -y redis libdbi1 libdbd-mysql libmysql++-dev  \
    python3-mysqldb pkg-config gcc telnet iputils-ping netcat-traditional

# Create web user / Create directories
RUN /usr/sbin/useradd -r -d /opt/site -u 998 -s /bin/bash web -k /etc/skel -m -U \
    && chown web:web -R /opt/site

USER web

COPY --chown=web:web ./bin/ /opt/site/bin/
COPY --chown=web:web ./src/ /opt/site/code/

RUN /usr/local/bin/pip install -r /opt/site/code/requirements.txt

USER root

RUN chown web:web -R /opt/site \
    && chmod +x /opt/site/bin/entrypoint.sh

WORKDIR /opt/site

USER web

EXPOSE 5000 8080

ENTRYPOINT ["/opt/site/bin/entrypoint.sh"]