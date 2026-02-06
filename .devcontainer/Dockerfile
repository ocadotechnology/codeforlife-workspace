# https://hub.docker.com/r/microsoft/devcontainers-base
FROM mcr.microsoft.com/devcontainers/base:ubuntu-22.04

# Install PostgreSQL (psql) client.
# https://www.postgresql.org/download/linux/ubuntu/
RUN echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list && \
  wget -qO- https://www.postgresql.org/media/keys/ACCC4CF8.asc > /etc/apt/trusted.gpg.d/pgdg.asc && \
  apt-get update && \
  export DEBIAN_FRONTEND=noninteractive && \
  apt-get -y install --no-install-recommends postgresql-client-17

# Install LocalStack CLI.
# https://docs.localstack.cloud/getting-started/installation/#installing-localstack-cli
RUN curl --output localstack-cli.tar.gz --location https://github.com/localstack/localstack-cli/releases/download/v4.3.0/localstack-cli-4.3.0-linux-amd64-onefile.tar.gz && \
  tar xvzf localstack-cli.tar.gz -C /usr/local/bin

# Install GCloud CLI.
# https://docs.cloud.google.com/sdk/docs/install#deb
RUN curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo gpg --dearmor -o /usr/share/keyrings/cloud.google.gpg && \
  echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | sudo tee /etc/apt/sources.list.d/google-cloud-sdk.list && \
  apt-get update && \
  export DEBIAN_FRONTEND=noninteractive && \
  apt-get install -y google-cloud-cli=547.0.0-0

# Install Snyk CLI.
# https://docs.snyk.io/snyk-cli/install-or-update-the-snyk-cli#install-with-standalone-executables
RUN curl --compressed https://downloads.snyk.io/cli/stable/snyk-linux -o snyk && \
  chmod +x ./snyk && \
  mv ./snyk /usr/local/bin/

# Install Google Chrome and ChromeDriver.
# https://googlechromelabs.github.io/chrome-for-testing/
RUN apt-get update && \
  export DEBIAN_FRONTEND=noninteractive && \
  # 1. Install dependencies for Google Chrome
  # https://pptr.dev/troubleshooting#chrome-doesnt-launch-on-linux
  # https://source.chromium.org/chromium/chromium/src/+/main:chrome/installer/linux/debian/dist_package_versions.json
  apt-get install -y --no-install-recommends \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libc6 \
    libcairo2 \
    libcups2 \
    libdbus-1-3 \
    libexpat1 \
    libfontconfig1 \
    libgbm1 \
    libgcc1 \
    libglib2.0-0 \
    libgtk-3-0 \
    libnspr4 \
    libnss3 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libstdc++6 \
    libx11-6 \
    libx11-xcb1 \
    libxcb1 \
    libxcomposite1 \
    libxcursor1 \
    libxdamage1 \
    libxext6 \
    libxfixes3 \
    libxi6 \
    libxrandr2 \
    libxrender1 \
    libxss1 \
    libxtst6 \
    lsb-release \
    wget \
    xdg-utils \
    curl \
    unzip \
    jq && \
  # 2. Fetch URLs for Stable Google Chrome and ChromeDriver
  JSON_URL="https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json" && \
  CHROME_URL=$(curl -s "$JSON_URL" | jq -r '.channels.Stable.downloads.chrome[] | select(.platform=="linux64") | .url') && \
  DRIVER_URL=$(curl -s "$JSON_URL" | jq -r '.channels.Stable.downloads.chromedriver[] | select(.platform=="linux64") | .url') && \
  # 3. Download and Install Google Chrome
  wget -q -O /tmp/chrome.zip "$CHROME_URL" && \
  unzip /tmp/chrome.zip -d /opt/ && \
  ln -s /opt/chrome-linux64/chrome /usr/bin/google-chrome && \
  # 4. Download and Install ChromeDriver
  wget -q -O /tmp/chromedriver.zip "$DRIVER_URL" && \
  unzip /tmp/chromedriver.zip -d /opt/ && \
  ln -s /opt/chromedriver-linux64/chromedriver /usr/bin/chromedriver && \
  # 5. Cleanup
  rm /tmp/chrome.zip /tmp/chromedriver.zip && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*
