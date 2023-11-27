---
description: Common issues and problems that we know of.
---

# Common Issues

These are some of the common issues that we know of. Let us know if you find other issues not listed here.

## django.db.utils.IntegrityError on Mac

If you see something like below when running the web server:

> **django.db.utils.IntegrityError: The row in table 'common\_class' with primary key '1' has an invalid foreign key: common\_class.teacher\_id contains a value '1' that does not have a corresponding value in portal\_teacher.id.**

The error is potentially caused by a wrong or incompatible sqlite3 version. You can check the sqlite3 version from a python shell with:

```
import sqlite3
sqlite3.sqlite_version.
```

{% hint style="info" %}
At the point of writing, sqlite3 version is at `3.35.5`.
{% endhint %}

You need to install/update sqlite3 with brew: `brew install sqlite3`. Then follow the instructions in `brew info sqlite3` before installing a python version with `pyenv`.

```
If you need to have sqlite first in your PATH, run:
  echo 'export PATH="/usr/local/opt/sqlite/bin:$PATH"' >> ~/.zshrc

For compilers to find sqlite you may need to set:
  export LDFLAGS="-L/usr/local/opt/sqlite/lib"
  export CPPFLAGS="-I/usr/local/opt/sqlite/include"
```

If you already installed a python version using pyenv and the virtual environment with pipenv, you need to clear them up:

```
pyenv versions
pyenv uninstall <PYTHON VERSION>
pipenv --rm
```

Check if the db has been created, and if the file exists, delete it:

```
rm example_project/db.sqlite3
```

Then repeat the steps in [Common Setup](common-setup.md) from the beginning. You will need to reinstall Python (`pyenv install`) so that it is aware of the updated sqlite3 version.  You can test this by running&#x20;

`sqlite3 -version`

and ensuring that it matches the output of&#x20;

`python -c "import sqlite3; print(sqlite3.sqlite_version)`

## Import Error: No module named '...'

If you get an error complaining about a missing module when running `run`, e.g.

```
File "/usr/lib/python3.7/imp.py", line 296, in find_module
    raise ImportError(_ERR_MSG.format(name), name=name)
ImportError: No module named 'portal'
```

Try the following:&#x20;

* exit out of pipenv
* remove the virtual env with `pipenv --rm`&#x20;
* reinstall with `pipenv install --dev`&#x20;
* re-enter pipenv: `pipenv shell`

## When running the game I get `no module named google.auth`

If you get an error when running the command `./run.py` or `./run.py -k` locally that states, somewhere in the traceback, `no module named google.auth`; then rerun the command again and the dependency should be detected. This is a [logged issue](https://github.com/ocadotechnology/aimmo/issues/449).

## When running the game I get `ImportError: No module named django.conf`

Run a pip install command to install django before running the project. Django should then resolve all the other dependencies specified in the setup file. To do this run: `pip install django=={version}`. You can find `version` from the `setup.py` file at the time.

## Localisation

If you have problems seeing the portal on machines with different locale (e.g. Polish), check the terminal for errors mentioning `ValueError: unknown locale: UTF-8`. If you see them, you need to have environment variables `LANG` and `LC_ALL` both set to `en_US.UTF-8`.

* Either export them in your `.bashrc` or `.bash_profile`
* or restart the portal with command `LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8 ./run`.
