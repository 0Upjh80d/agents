# Changelog

## March 21, 2025

- Integrated SQLAlchemy as the ORM framework for the project
- Implemented FastAPI endpoints
  - **User**: `get_user`, `get_user_vaccination_records`, `get_vaccination_recommendation_for_user`
  - **Booking**: `get_booking_slot`, `get_available_booking_slots`, `schedule_vaccination_slot`, `cancel_vaccination_slot`
  - **Stock**: `get_vaccine_stock`
  - **Record**: `get_vaccine_record`
- Version-controlled update to SQLite DVC file for development data

## March 18, 2025

- Added scripts to assign RBAC roles to Azure security group

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
  - Added [documentation](./README.md#create-a-virtual-environment-) on virtual environment setup
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
