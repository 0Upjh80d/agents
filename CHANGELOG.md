# Changelog

## March 17, 2025

- Setup Bicep Infrastructure-as-Code (IaC)
  - Added tests to validate that the Azure OpenAI infrastructures have been properly deployed
  - Added [script](./scripts/test.sh) that runs the test when trigger by [post-provision hook](azure.yaml)
- SQLite database [version-controlled](./data/vaccination_db.sqlite.dvc) into Azure Blob Storage
- Set up SAS token for DVC
- Store SAS token as secret in Azure Key Vault
- Added [scripts](./scripts/) to set up DVC, fetch SAS token, and get data
- Added [documentation](./docs/DEVELOPMENT.md) on retrieving the synthetic data version-controlled in Azure Blob Storage for development
- Updated [documentation](./docs/PROJECT_STRUCTURE.md) on project structure

## March 14, 2025

- Generated dummy vaccination data
- Stored generated data into a SQLite database

## March 13, 2025

- Setup virtual environment with uv
  - Added [documentation](./README.md#create-a-virtual-environment) on virtual environment setup
  - Added [documentation](./docs/ALTERNATIVE_PYTHON_PACKAGE_MANAGERS.md) on alternative Python package and project managers
- Setup project structure
  - Added [documentation](./docs/PROJECT_STRUCTURE.md) on project structure
- Setup pre-commit and pre-push hooks
  - Added scripts to set up Git hooks
- Added [Contributing](CONTRIBUTING.md) guidelines documenting steps and best practices for contributing to the project

## March 12, 2025

- Initialized:
  - GitHub repository
  - Azure Developer (AZD) CLI
  - Data Version Control (DVC)
