FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Install PostgreSQL (psql) client.
RUN apt-get update && \
  export DEBIAN_FRONTEND=noninteractive && \
  apt-get -y install --no-install-recommends postgresql-client
