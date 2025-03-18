# Changelog

## March 27, 2025

- Added documentation for backend, guides to current API endpoints, database models and Postman testing guide
- Minor fixes to `Users` table — ensured `nric` and `email` columns are unique
- Removed user dependency injection for `get_available_booking_slots` and `get_booking_slot` endpoints
- Modified `get_user_vaccination_record` endpoint to ensure user can only get their own vaccination record
- Added optional arguments `polyclinic_name`, `start_datetime` and `end_datetime` to `get_available_booking_slots`
- Implemented new endpoints:
  - **Booking**: `reschedule_vaccination_slot`
  - **Clinic**: `get_nearest_clinic`

## March 25, 2025

- Combined the `Polyclincics` and `⁠GeneralPractioners` tables into one `⁠Clinics` table, with additional field `type` indicating if it’s a⁠ `polyclinic` or⁠ `gp`
- An additional field type `enrolled_clinic_id` in the `Users` table which references the `Clinics` table
- Version-controlled updated SQLite data
- Version-controlled institution data required to generate data for SQLite

---

- Updated response schemas to `UUID` data type for all `id` fields
- Updated SQLAlchemy models to account for data schema changes
- Replaced Polyclinic response schema with Clinic response schema
- Moved `get_user_vaccination_records` from `user` router to `record` router
- Moved `get_vaccine_recommendations_for_user` from `user` router to `vaccine` router
- Removed `get_vaccine_stock` endpoint as no longer required
- Implemented new endpoints:
  - **User**: `update_user` (meant only for development purposes — **not** to be integrated as tools for agents)
  - **Booking**: `get_booking_slot`

## March 24, 2025

- Updated all PK columns to `id`, with `UUID` date type
- Normalized `BookingSlots` table:
  - Removed `user_id` and `isbooked` columns
  - Renamed `slot_datetime` column to `datetime`
- Normalized `VaccineRecords` table:
  - Removed `polyclinic_id`, `vaccination_date` and `vaccine_id` columns
  - Added `status` (`completed` or `booked`) and `booking_slot_id` — which references the `BookingSlots` table — columns
- For `Vaccines` table:
  - Used [MOH NAIS](https://www.moh.gov.sg/seeking-healthcare/overview-of-diseases/communicable-diseases/nationally-recommended-vaccines) data to populate the `Vaccines` table
  - Changed `price` column to `float` data type
  - Changed `gender_criteria` column values to `M`, `F` or `None`
- For `Users` table:
  - Created `address_id`, `nric` and `password` columns
  - Splitted name into `first_name` and `last_name`
    - Generated gender based first and last names
  - Ensured `email` makes sense to `first_name` and `last_name`
  - Changed `gender` column values to `M` or `F`
- For `Polyclinics` table:
  - Added `address_id` column
  - Used institution data provided by Data Owner to populate the `Polyclinics` table
- Created `GeneralPractitioners` table with open source [Clinics onboard the Health Appointment System](https://data.gov.sg/datasets?query=clinic&page=1&resultId=d_3cd840069e95b6a521aa5301a084b25a) data by [data.gov.sg](https://data.gov.sg/) with `id`, `address_id` and `name` columns
- Removed `VaccineStock` table

---

- Implemented OAuth2 authentication flow
- Renamed `get_vaccine_record` to `get_user_vaccination_record`
- Implemented new endpoints:
  - **Authentication**: `signup`, `login`
  - **User**: `delete_user` (meant only for development purposes — **not** to be integrated as tools for agents)
  - **Vaccine**: `get_vaccine_recommendations_for_user`

## March 21, 2025 (Release v0.1.0)

- Integrated SQLAlchemy as the ORM framework for the project
- Implemented FastAPI endpoints:
  - **Booking**: `get_available_booking_slots`, `get_booking_slot`, `schedule_vaccination_slot`, `cancel_vaccination_slot`
  - **Record**: `get_vaccine_record`
  - **Stock**: `get_vaccine_stock`
  - **User**: `get_user`, `get_user_vaccination_records`, `get_vaccine_recommendations_for_user`
- Version-controlled updated SQLite data

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
  - Added [script](./scripts/test.sh) that runs the test when trigger by [post-provision hook](azure.yaml)
- SQLite database [version-controlled](./data/vaccination_db.sqlite.dvc) into Azure Blob Storage
- Set up SAS token for DVC
- Store SAS token as secret in Azure Key Vault
- Added scripts to [set up DVC](./scripts/setup_dvc.sh), [fetch SAS token](./scripts/fetch_sas_token.py), and [get data](./scripts/get_data.sh)
- Added [documentation](./docs/DATA_MANAGEMENT.md) on retrieving the synthetic data version-controlled in Azure Blob Storage for development
- Updated [documentation](./docs/PROJECT_STRUCTURE.md) on project structure

## March 14, 2025

- Generated dummy vaccination data
- Stored generated data into a SQLite database

## March 13, 2025

- Setup virtual environment with uv
  - Added [documentation](./README.md#create-a-virtual-environment-) on virtual environment setup
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
