# Code for Life Workspace - AI Agent Instructions

This document provides instructions for AI coding agents to effectively contribute to the Code for Life workspace.

## 1. High-Level Architecture

This is a monorepo containing multiple services for the Code for Life platform. The project is divided into three main parts:

-   `frontend/`: A TypeScript/React monorepo using Yarn workspaces.
-   `backend/`: A Python/Django monorepo using `pipenv` for dependency management.
-   `legacy/`: Older services that are being phased out.

The entire workspace is managed as a collection of Git submodules. The main entry point for development in VS Code is the `codeforlife.code-workspace` file.

## 2. Key Development Workflows

All development tasks are orchestrated through a set of powerful shell scripts located in `/workspace/frontend/scripts` and `/workspace/backend/scripts`. **You must use these scripts for all tasks**, as they ensure that the correct configurations and tools are used.

### Frontend Workflow (`/workspace/frontend`)

The frontend is a modern TypeScript/React setup using Vite and Vitest.

-   **Setup:** To install all dependencies, navigate to a service's directory (e.g., `/workspace/frontend/portal`) and run:
    ```bash
    /workspace/frontend/scripts setup
    ```

-   **Running Checks:** To run all quality checks (linting, formatting, type checking, and tests), use the `check` command from a service's directory:
    ```bash
    /workspace/frontend/scripts check
    ```

-   **Running the Dev Server:** To start the development server for a specific service:
    ```bash
    /workspace/frontend/scripts run:dev
    ```

-   **Running Tests:** To run tests for a service:
    ```bash
    /workspace/frontend/scripts test
    ```

### Backend Workflow (`/workspace/backend`)

The backend consists of several Django services.

-   **Setup:** To set up the Python environment and install dependencies for a service, navigate to its directory (e.g., `/workspace/backend/portal`) and run:
    ```bash
    /workspace/backend/scripts setup
    ```

-   **Running Checks:** To run all quality checks (imports, formatting, type checking, linting, migrations, and tests), use the `check` command from a service's directory:
    ```bash
    /workspace/backend/scripts check
    ```

-   **Running the Django Server:** To start the local Django development server:
    ```bash
    /workspace/backend/scripts run:django
    ```

-   **Running Tests:** To run tests for a service:
    ```bash
    /workspace/backend/scripts test
    ```

-   **Database Migrations:** The backend uses Django migrations. When you change a model, you'll need to create a migration. The `check` script verifies that no migrations are pending.

## 3. Project-Specific Conventions

-   **Always use the provided scripts.** Do not run `yarn`, `vite`, `pipenv`, `pytest`, etc., directly. The wrapper scripts in `/workspace/frontend/scripts` and `/workspace/backend/scripts` are the source of truth for all development commands.
-   **Configuration is centralized.** Frontend configuration is managed in `/workspace/frontend/package.json` and `tsconfig.base.json`. Backend tool configuration (e.g., `black`, `pylint`, `pytest`) is in `/workspace/backend/pyproject.toml`.
-   **Work within service directories.** Most commands should be run from within the specific service directory you are working on (e.g., `/workspace/frontend/portal` or `/workspace/backend/sso`).
-   **Git Submodules:** Be mindful of the submodule structure. Changes within a service need to be committed within that submodule, and the change to the submodule reference needs to be committed in the parent `codeforlife-workspace` repository.

By following these guidelines, you will be able to navigate the codebase and contribute effectively.
