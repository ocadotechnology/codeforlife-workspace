---
description: Common working environment setup for all the repositories.
---

# Common Setup

All the repositories are Python and Django based, so you need to get Python set up. The following section provides a step-by-step guide to setting up your working environment. If you bump into any issue, please check our [Common Issues](common-issues.md) section first for help.&#x20;

## Python installation

First, check whether you've got Python installed:

```bash
python --version
```

or

```
python3 --version
```

We are currently on **Python 3.8.x**.

## Install dependencies

Add apt repository for older versions of python:

```
sudo add-apt-repository ppa:deadsnakes/ppa
```

Then, run the following command:

```bash
sudo apt install \
    build-essential \
    curl \
    libbz2-dev \
    libffi-dev \
    liblzma-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libssl-dev \
    libxml2-dev \
    libxmlsec1-dev \
    llvm \
    make \
    python3.8-distutils \
    tk-dev \
    wget \
    xz-utils \
    zlib1g-dev
```

## Install git

Install git by running `sudo apt install git` on Ubuntu or `brew install git` on Mac.

## sqlite3 (Mac only)

{% hint style="info" %}
If you're on Mac, you may have an old or incompatible sqlite3 version, and it's recommended to first upgrade your sqlite3 and follow the next steps. Otherwise, you can skip ahead.  This should be done before running `pyenv install` (below) or Python will not use the correct version of sqlite3
{% endhint %}

Upgrade sqlite3 with `brew install sqlite3`. Then follow the instructions in `brew info sqlite3` e.g.

```
If you need to have sqlite first in your PATH, run:
  echo 'export PATH="/usr/local/opt/sqlite/bin:$PATH"' >> ~/.zshrc

For compilers to find sqlite you may need to set:
  export LDFLAGS="-L/usr/local/opt/sqlite/lib"
  export CPPFLAGS="-I/usr/local/opt/sqlite/include"
```

## Python versions with pyenv

If you don't have Python 3.8, we'd highly recommend using [pyenv](https://github.com/pyenv/pyenv#readme) to manage multiple versions of Python.&#x20;

Please follow the [installation instruction](https://github.com/pyenv/pyenv#installation)[ for Mac](https://github.com/pyenv/pyenv#installation) or [the one for Linux](https://itslinuxfoss.com/install-use-pyenv-ubuntu/).

Check your pyenv installation:

```bash
pyenv versions
```

Install the required python version: (this process may take a while)

```bash
pyenv install 3.8.16
```

{% hint style="info" %}
At the point of writing, we are using either `3.8.16`. Feel free to try the latest patch version of `3.8` if a new one has come up.
{% endhint %}

Switch pyenv to using the 3.8.x:

```bash
pyenv global 3.8.16
```

This tells your system and the next steps in this page to use the selected Python version. You can double check by running `pyenv versions` again. The star `*` sign shows the selected version.

You can switch back to other Python version if you need to later. We use this Python version to build our virtual environment with `pipenv` in the next steps. Once the virtual environment is built, we don't need pyenv anymore.

## pip - Python package management

Next up, you need to have `pip`. `pip` is Python standard package management system, used to install and manage software packages.

On Mac, `pip` should come with your Python installation.

On Ubuntu, run `sudo apt-get install python3-pip`.

Check that you've got pip installed:

```bash
pip --version
```

## pipenv - Python virtual environment

Next, install `pipenv`. `pipenv` creates and manages virtual environment for the project. It installs and removes packages from the `Pipfile` in an isolated working environment, so it doesn't mess with your system.&#x20;

On Mac, run `brew install pipenv`.

On Ubuntu, run `sudo pip install pipenv`.

## Clone the repo

Please follow our [Development Guidelines](../developer-guide/development-guidelines.md#opening-a-pull-request) for the detail on how to clone or fork a repository.

## Build and activate the virtual environment

Once you have the repo locally, `cd` into the folder, and run:

```bash
pipenv install --dev
```

This builds the virtual environment for the project. The process may take a few minutes.

## Activate the virtual environment

{% hint style="info" %}
If you've done everything right, all the steps above only have to be done once. And this is the point where you need to start from when you leave and come back, or start a new shell.
{% endhint %}

In the directory of the repo, run:

```bash
pipenv shell
```

This activates the virtual environment for this repo. Depending on your shell, you should see the difference in the shell prompt when you're inside a virtual environment.&#x20;

## Build portal frontend (if running the portal repo)

If working on the portal repo, you need to build the react frontend and move it to a static folder inside portal.

You will need yarn to build those. Install them by running:

```
sudo apt install npm
sudo npm install --global yarn
```

{% hint style="warning" %}
The following steps need node >= 14, make sure that is the version you are using.
{% endhint %}

Now to build the files, go into the directory `portal_frontend` and run the yarn commands:

```
cd portal_frontend
yarn
yarn build
```

Then move the build files into the portal static directory:

```
mv build ../portal/frontend
```

## Run the web server

Finally, inside the folder, run:

```bash
./run
```

This command will:

* sync the database
* collect the static files
* run a development web server

You should see output like the following:

```bash
Django version 3.2.19, using settings 'settings'
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

At this point the portal will be accessible with your browser at `http://localhost:8000/.`

The steps above are the same for all three repositories and the minimum to get the portal running. `aimmo` has some extras as it uses `kubernetes` and `minikube` so please check the aimmo setup for more detail.  &#x20;

_Please do not hesitate to ask questions if you found any difficulties to get things up and running. Github Discussion is the perfect place for this. It is monitored by the core developers and your questions may help other contributors who bump into the same issues._

