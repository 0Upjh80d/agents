# Project Structure

To get a better sense of our project, here is the project structure:

- [`.dvc/`](../.dvc): contains placeholders to track data files and directories.

- [`.githooks/`](../.githooks): contains custom Git hooks.

  - [`commit-msg`](../.githooks/commit-msg): a custom commit message hook which enforces Conventional Commits style for our commit messages.

  - [`pre-push`](../.githooks/pre-push): a custom pre-push hook which enforces proper branch naming convention.

- [`.github/`](../.github): contains configuration files for GitHub Actions, Dependabot, and templates for pull requests and issues.

- [`app/`](../app): contains folders acting as a logical separation between backend and frontend logic.

  - [`backend/`](../app/backend/): contains the backend logic.

    - [`app/`](../app/backend/app): contains the backend application code.

      - [`core/`](../app/backend/app/core/): contains the configuration for the application.

      - [`models/`](../app/backend/app/models/): contains the models for the application.

      - [`routers/`](../app/backend/app/routers/): contains the routers for the application.

      - [`schema/`](../app/backend/app/schema/): contains the schema for the application.

      - [`tests/`](../app/backend/app/tests/): contains the tests for the application.

  - [`frontend`](../app/frontend/): contains the frontend logic.

- [`docs/`](../docs): contains documentation for the project.

- [`infra/`](../infra): contains infrastructure files and code for the project.

  - [`abbreviations.json`](../infra/abbreviations.json): contains a list of abbreviations used in [`main.bicep`](../infra/main.bicep).

  - [`main.bicep`](../infra/main.bicep): contains the Azure Resource Manager (ARM) (i.e. Bicep Infrastrucure-as-Code) template for the project.

  - [`main.parameters.json`](../infra/main.parameters.json): contains the parameters used in [`main.bicep`](../infra/main.bicep).

- [`media/`](../media): contains media files (i.e. images) for the project.

- [`notebooks/`](../notebooks): contains Jupyter notebooks for experimentation or learning for the project.

- [`scripts/`](../scripts): contains scripts for the project.

  - [`setup_hooks.*`](../scripts/setup_hooks.sh): contains the bash and PowerShell scripts for setting up Git hooks.

  - [`start.*`](../scripts/start.sh): contains the bash and PowerShell scripts for starting up the application locally.

- [`tests/`](../tests): contains tests for the project.
