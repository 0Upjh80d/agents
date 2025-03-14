lint:
	pre-commit run --all-files

run-server: # Run the server
ifeq ($(OS),Windows_NT)
	powershell -ExecutionPolicy Bypass -File scripts/start.ps1
else
	./scripts/start.sh
endif
