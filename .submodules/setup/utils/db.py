"""
© Ocado Group
Created on 14/04/2025 at 16:14:59(+01:00).
"""

import subprocess
from dataclasses import dataclass
from subprocess import CalledProcessError

from . import pprint
from .vscode import CodeWorkspace

PSQL_BASE_COMMAND = ["psql", "-v", "ON_ERROR_STOP=1"]
CONNECTION_OPTIONS = ["--username=root", "--host=db", "--port=5432"]
ENV = {"PGPASSWORD": "password"}
# -t: Suppresses printing of rows and column names.
# -A: Unaligned output mode (useful for scripting).
# -c: Executes the given command.
EXE_PSQL_CMD = "-tAc"


@dataclass(frozen=True)
# pylint: disable-next=too-many-instance-attributes
class Connection:
    """An SQL connection."""

    # pylint: disable=invalid-name
    previewLimit: int
    server: str
    port: int
    driver: str
    name: str
    database: str
    username: str
    password: str
    # pylint: enable=invalid-name


def postgres_user_exists(username: str):
    """Check if a PostgreSQL user exists.

    Args:
        username: The name of the user.

    Returns:
        A flag designating whether the user exists .
    """
    try:
        exists = (
            subprocess.run(
                [
                    *PSQL_BASE_COMMAND,
                    *CONNECTION_OPTIONS,
                    EXE_PSQL_CMD,
                    f"SELECT 1 FROM pg_roles WHERE rolname='{username}';",
                ],
                check=True,
                stdout=subprocess.PIPE,
                env=ENV,
            )
            .stdout.decode("utf-8")
            .strip()
        )
    except CalledProcessError:
        pprint.error("Failed to check if user exists.")
        return None

    if exists == "1":
        print("User does exist.")
        return True

    print("User does not exist.")
    return False


def create_postgres_user(username: str):
    """Create a PostgreSQL user.

    Args:
        username: The name of the user.

    Returns:
        A flag designating whether the user was created.
    """
    pprint.notice("Creating user...")

    try:
        subprocess.run(
            [
                *PSQL_BASE_COMMAND,
                *CONNECTION_OPTIONS,
                EXE_PSQL_CMD,
                f"CREATE USER {username};",
            ],
            check=True,
            env=ENV,
        )

        return True
    except CalledProcessError:
        pprint.error("Failed to create user.")
        return False


def postgres_database_exists(dbname: str):
    """Check if a PostgreSQL database exists.

    Args:
        dbname: The name of the database.

    Returns:
        A flag designating whether the database exists .
    """
    try:
        exists = (
            subprocess.run(
                [
                    *PSQL_BASE_COMMAND,
                    *CONNECTION_OPTIONS,
                    EXE_PSQL_CMD,
                    f"SELECT 1 FROM pg_database WHERE datname='{dbname}';",
                ],
                check=True,
                stdout=subprocess.PIPE,
                env=ENV,
            )
            .stdout.decode("utf-8")
            .strip()
        )
    except CalledProcessError:
        pprint.error("Failed to check if database exists.")
        return None

    if exists == "1":
        print("Database does exist.")
        return True

    print("Database does not exist.")
    return False


def create_postgres_database(username: str, dbname: str):
    """Create a PostgreSQL database and grant a user all privileges to it.

    Args:
        username: The name of the user.
        dbname: The name of the database.

    Returns:
        A flag designating whether the database was created.
    """
    pprint.notice("Creating database...")

    try:
        subprocess.run(
            ["createdb", *CONNECTION_OPTIONS, dbname],
            check=True,
            env=ENV,
        )

        subprocess.run(
            [
                *PSQL_BASE_COMMAND,
                *CONNECTION_OPTIONS,
                EXE_PSQL_CMD,
                f"GRANT ALL PRIVILEGES ON DATABASE {dbname} TO {username};",
            ],
            check=True,
            env=ENV,
            stdout=subprocess.DEVNULL,
        )

        return True
    except CalledProcessError:
        pprint.error("Failed to create database.")
        return False


def create_postgres_users_and_databases(code_workspace: CodeWorkspace):
    """Create multiple PostgreSQL users and databases.

    Args:
        code_workspace: The code workspace to read the SQL connections from.

    Returns:
        A flag designating whether any error occurred during the process.
    """
    error = False

    connections = code_workspace["settings"].get("sqltools.connections")

    try:
        assert isinstance(connections, list)
        assert all(isinstance(connection, dict) for connection in connections)
        connections = [Connection(**connection) for connection in connections]
    except (AssertionError, TypeError):
        return False

    connections = [
        connection for connection in connections if connection.driver == "PostgreSQL"
    ]

    for i, connection in enumerate(connections, start=1):
        pprint.header(f"Database ({i}/{len(connections)}): {connection.name}")

        created_user = True
        if not postgres_user_exists(username=connection.username):
            created_user = create_postgres_user(username=connection.username)

        created_db = True
        if created_user and not postgres_database_exists(
            dbname=connection.database,
        ):
            created_db = create_postgres_database(
                username=connection.username,
                dbname=connection.database,
            )

        if not error and (not created_user or not created_db):
            error = True

        print()

    return error
