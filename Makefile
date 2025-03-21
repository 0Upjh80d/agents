ifeq ($(OS),Windows_NT)
    SCRIPT_SUFFIX = ps1
	SCRIPT_RUNNER = pwsh -ExecutionPolicy Bypass -File
else
    SCRIPT_SUFFIX = sh
	SCRIPT_RUNNER =
endif

lint:
	pre-commit run --all-files

run-server: # Run the server
	@$(SCRIPT_RUNNER) ./scripts/start.$(SCRIPT_SUFFIX)
