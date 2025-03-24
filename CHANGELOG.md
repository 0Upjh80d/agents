# Changelog

## March 21, 2025

- Integrated SQLAlchemy as the ORM framework for the project
- Implemented FastAPI endpoints:
  - **User**: `get_user`, `get_user_vaccination_records`, `get_vaccination_recommendation_for_user`
  - **Booking**: `get_booking_slot`, `get_available_booking_slots`, `schedule_vaccination_slot`, `cancel_vaccination_slot`
  - **Stock**: `get_vaccine_stock`
  - **Record**: `get_vaccine_record`
- Version-controlled updated SQLite DVC file for development data

## March 19, 2025

- Updated [Git hook](./.githooks/pre-push) to include additional regular expression check for `release/yyyy-mm-dd` and `fix/xxx` branches
  - `release` branches are for merging cherry-picked commits from `staging` to `main` (e.g., `release/2022-06-30`)
  - `fix` branches are for general administrative fixes (e.g., `fix/xxx`) that are neither bug fixes nor hotfixes
- Updated [Git hook](./.githooks/commit-msg) to include `chore(release): vX.Y.Z` commit message as valid
- Added optional Bump My Version dependency in [prerequisite section](README.md#prerequisites-) to manage project versioning

## March 18, 2025

- Modified GitHub Actions workflow files to fix stuck PR
- Added [scripts](./scripts/rolesgroup.sh) to assign RBAC roles to Azure security group
- Added GitHub Actions workflow file to validate PR title adhere to Conventional Commits specification
- Updated SQLite database with more rows of development data
- Added [Jupyter notebook](./notebooks/query_database.ipynb) containing walkthrough on querying the SQLite database
- Added [scripts](./scripts/start.sh) to start up the backend server
- Added simple `send_chat` chat endpoint
- Updated [documentation](./docs/PROJECT_STRUCTURE.md) on project structure
- Replaced [Linkspector](https://github.com/UmbrellaDocs/action-linkspector) with [lychee](https://github.com/lycheeverse/lychee-action)
  - Removed `.linkspector.yml` as no longer needed

## March 17, 2025

- Setup Bicep Infrastructure-as-Code (IaC)
  - Added tests to validate that the Azure OpenAI infrastructures have been properly deployed
  - Added [scripts](./scripts/test.sh) that runs the test when trigger by [post-provision hook](azure.yaml)
- SQLite database [version-controlled](./data/vaccination_db.sqlite.dvc) into Azure Blob Storage
- Set up SAS token for DVC
- Store SAS token as secret in Azure Key Vault
- Added scripts to [set up DVC](./scripts/setup_dvc.sh), [fetch SAS token](./scripts/fetch_sas_token.py), and [get data](./scripts/get_data.sh)
- Added [documentation](./docs/DEVELOPMENT.md) on retrieving the synthetic data version-controlled in Azure Blob Storage for development
- Updated [documentation](./docs/PROJECT_STRUCTURE.md) on project structure

## March 14, 2025

- Generated dummy vaccination data
- Stored generated data into a SQLite database

## March 13, 2025

- Set up virtual environment with uv
  - Added [documentation](README.md#create-a-virtual-environment-) on virtual environment set up
  - Added [documentation](./docs/ALTERNATIVE_PYTHON_PACKAGE_MANAGERS.md) on alternative Python package and project managers
- Set up project structure
  - Added [documentation](./docs/PROJECT_STRUCTURE.md) on project structure
- Set up [pre-commit](./.githooks/commit-msg) and [pre-push](./.githooks/pre-push) hooks
  - Added [scripts](./scripts/setup_hooks.sh) to set up Git hooks
- Added [Contributing](CONTRIBUTING.md) guidelines documenting steps and best practices for contributing to the project

## March 12, 2025

- Initialized:
  - GitHub repository
  - Azure Developer (AZD) CLI
  - Data Version Control (DVC)
