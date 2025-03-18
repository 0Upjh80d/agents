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

      - [`main.py`](../app/backend/app/main.py): the main file of the FastAPI application. It contains the FastAPI app instance and the main entry point of the application.

      - [`core/`](../app/backend/app/core/): contains the configuration for the application.

      - [`models/`](../app/backend/app/models/): contains the models for the application that will be stored in the database.

      - [`routers/`](../app/backend/app/routers/): contains the routers for the application.

      - [`schemas/`](../app/backend/app/schemas/): contains Pydantic schemas that will be used to validate request and response data.

      - [`tests/`](../app/backend/app/tests/): contains the tests for the application.

  - [`frontend`](../app/frontend/): contains the frontend logic.

- [`data/`](../data): contains data files — usually `.dvc` files — for the project.

- [`docs/`](../docs): contains documentation for the project.

- [`infra/`](../infra): contains infrastructure files and code for the project.

  - [`abbreviations.json`](../infra/abbreviations.json): contains a list of abbreviations used in [`main.bicep`](../infra/main.bicep).

  - [`main.bicep`](../infra/main.bicep): contains the Azure Resource Manager (ARM) (i.e. Bicep Infrastrucure-as-Code) template for the project.

  - [`main.parameters.json`](../infra/main.parameters.json): contains the parameters used in [`main.bicep`](../infra/main.bicep).

- [`media/`](../media): contains media files (i.e. images) for the project.

- [`notebooks/`](../notebooks): contains Jupyter notebooks for experimentation or learning for the project.

- [`scripts/`](../scripts): contains scripts for the project.

  - [`fetch_sas_token.py`](../scripts/fetch_sas_token.py): contains the Python executable script for fetching the SAS token from Azure Key Vault.

  - [`format_bicep.*`](../scripts/format_bicep.sh): contains the bash and PowerShell scripts for formatting Bicep files.

  - [`get_data.*`](../scripts/get_data.sh): contains the bash and PowerShell scripts for getting the version-controlled data.

  - [`postprovision.*`](../scripts/postprovision.sh): contains the bash and PowerShell scripts for that runs after provisioning the Azure resources.

  - [`setup_dvc.*`](../scripts/setup_dvc.sh): contains the bash and PowerShell scripts for setting up DVC.

  - [`setup_hooks.*`](../scripts/setup_hooks.sh): contains the bash and PowerShell scripts for setting up Git hooks.

  - [`start.*`](../scripts/start.sh): contains the bash and PowerShell scripts for starting up the application locally.

  - [`test.*`](../scripts/test.sh): contains the bash and PowerShell scripts to run tests on the Azure infrastructure.

- [`tests/`](../tests): contains Azure infrastructure tests for the project.

  - [`test_deployments.py`](../tests/test_deployments.py): Python script containing the tests to ensure the Azure deployments have been deployed successfully.

  - [`utils.py`](../tests/utils.py): Python script containing utility functions for the tests.
