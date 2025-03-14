lint:
	pre-commit run --all-files

run-server: # Run the server , TODO: check for os
	./scripts/start.sh
