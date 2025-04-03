# https://hub.docker.com/r/microsoft/devcontainers-base
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Install PostgreSQL (psql) client.
# https://www.postgresql.org/download/linux/ubuntu/
RUN echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
  wget -qO- https://www.postgresql.org/media/keys/ACCC4CF8.asc > /etc/apt/trusted.gpg.d/pgdg.asc && \
  apt-get update && \
  export DEBIAN_FRONTEND=noninteractive && \
  apt-get -y install --no-install-recommends postgresql-client-17

# Install Snyk CLI.
# https://docs.snyk.io/snyk-cli/install-or-update-the-snyk-cli#install-with-standalone-executables
RUN curl --compressed https://downloads.snyk.io/cli/stable/snyk-linux -o snyk && \
  chmod +x ./snyk && \
  mv ./snyk /usr/local/bin/
