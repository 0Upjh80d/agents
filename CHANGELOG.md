# Changelog

## Apr 9, 2025 (`v0.2.0`)

- Refactored PowerShell [start](./scripts/start.ps1) script to improve maintainability
- Updated [GitHub Action workflow](./.github/workflows/run-checks.yml) to run checks only when relevant file changes were detected

## Apr 8, 2025

- Updated [GitHub Action workflow](./.github/workflows/validate-pr.yml) for validating PR titles (i.e., first letter after type **must** be lowercased)
- Updated [GitHub Action workflow](./.github/workflows/run-tests.yml) for running unit tests by adding initial job to detect changes in certain files
- Refactored [scripts](./scripts/start.sh)
- Overhauled frontend to use dummy backend endpoint instead of mocking on the frontend
- Added change booking details flow for date/time only
- Added functionality to display responses to general user queries that include links

## Apr 7, 2025

- Implemented a dummy booking flow for vaccination with a dummy orchestrator agent
- Updated the [start](./scripts/start.sh) scripts to simplify the development environment setup and launch process
- Updated Running Locally section in [`README.md`](./README.md#running-locally)

## Apr 2, 2025

- Update GitHub Action workflow for link checker to only look at links in Markdown files
- Updated `Vaccines` table structure. Created new `VaccineCriteria` table.
  - Updated `generate_database.ipynb` to structure and populate `Vaccines` and `VaccineCriteria`
  - Updated `query_database.ipynb` to view updated tables
- Reflect changes to structures of `Vaccines` and `VaccineCriteria` in:
  - [`schema.sql`](./data/schema.sql)
  - [`models.py`](./app/backend/app/models/models.py)
  - [`DATABASE_MODELS.md`](./docs/DATABASE_MODELS.md) and [`erd.png`](./media/erd.png)
- Pushed latest database, with new `VaccineCriteria` table to DVC

## Apr 1, 2025

- Sorted available booking slots based distance if user’s address information is available; otherwise sorted based on date time only.
- Allowed `/clinics/nearest` endpoint to return either Polyclinics or General Practitioners if not specified
  - Updated API Endpoints documentation

## Mar 30, 2025

- Added [documentation](./docs/REVIEWERS_STEP_BY_STEP.md) on reviewer’s step-by-step guide

## March 28, 2025

- Frontend setup
  - Sets up the frontend application with the following key features:
    1. **Login and Sign Up Endpoints Integration** - integrated the backend login and sign up endpoints.
    2. **Dummy Login UI** - implemented a basic user interface for the login & sign up process.
    3. **Dummy Chat UI** - created a placeholder chat interface.
- Backend API unit tests setup
  - Added unit tests for the following APIs:
    - `root`
    - `authentication`
    - `user`
    - `record`
    - `vaccine`
    - `booking`
    - `clinic`
  - Added [scripts](./scripts/test_api.sh) to run the unit tests
  - Added [GitHub Actions Workflow file](./.github/workflows/run-tests.yml) to run the unit tests as required checks
- Documentation
  - Updated [documentation](./docs/API_ENDPOINTS.md) on backend API test cases
  - Added [documentation](./docs/DEBUGGING_GITHUB_ACTIONS_LOCALLY.md) on how to use `act` to test GitHub Actions workflow locally

## March 27, 2025 (`v0.1.0`)

- Added documentation for backend, guides to current API endpoints, database models and Postman testing guide
- Minor fixes to `Users` table — ensured `nric` and `email` columns are unique
- Removed user dependency injection for `get_available_booking_slots` and `get_booking_slot` endpoints
- Modified `get_user_vaccination_record` endpoint to ensure user can only get their own vaccination record
- Added optional arguments `polyclinic_name`, `start_datetime` and `end_datetime` to `get_available_booking_slots`
- Implemented new endpoints:

  - **Booking**: `reschedule_vaccination_slot`
  - **Clinic**: `get_nearest_clinic`

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

## March 21, 2025

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
  - Added [scripts](./scripts/test.sh) that runs the test when trigger by [post-provision hook](azure.yaml)
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
