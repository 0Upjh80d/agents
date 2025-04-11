#!/bin/bash

# Recommended for safer scripting:
set -Eeuo pipefail

# We define functions used in start.sh here

export MAIN_COLOR="\033[1;36m"      # Cyan
export AGENT_COLOR="\033[1;33m"     # Yellow
export FRONTEND_COLOR="\033[1;35m"  # Magenta
export INFO_COLOR="\033[1;32m"      # Green
export ERROR_COLOR="\033[1;31m"     # Red (needed since it's referenced in a few places)
export RESET_COLOR="\033[0m"        # Reset to default

# --- Function to clean up processes ---
cleanup_process() {
    local pid="$1"
    local name="$2"
    local color="$3"

    if [[ -n "$pid" && -e "/proc/$pid" ]]; then
        echo -e "${color}✋ Stopping $name server (PID: $pid)...${RESET_COLOR}"
        kill "$pid"
        # Optionally sleep a bit so the kill is effective:
        # sleep 1
    else
        echo -e "${color}✅ $name process not found or already stopped.${RESET_COLOR}"
    fi
}

# --- Set up and Run Frontend Server ---
setup_and_run_frontend() {
    # Optionally, only install if node_modules is missing:
    if [ ! -d node_modules ]; then
        npm install
    fi
    npm install

    # --open will automatically open a browser tab.
    # Remove it if this is a headless environment.
    npx ng serve --open 2>&1 | \
        while IFS= read -r line; do
            printf "${FRONTEND_COLOR}[FRONTEND] %s${RESET_COLOR}\n" "$line"
        done
}


# --- Run Backend Server ---
run_server() {
    local app_name="$1"
    local port="$2"
    local color="$3"
    local label="$4"

    uvicorn "app.backend.app.main:${app_name}" \
            --reload \
            --host 127.0.0.1 \
            --port "$port" 2>&1 | \
        while IFS= read -r line; do
            printf "${color}[${label}] %s${RESET_COLOR}\n" "$line"
        done
}

# --- Create UV venv and Install Dependencies ---
setup_backend_env() {
    echo "⏳ Loading azd .env file from current environment..."

    # Read environment values from `azd env get-values`.
    # If `azd` or this command fails, the script will exit due to `set -Eeuo pipefail`.
    while IFS='=' read -r key value; do
        # Remove surrounding quotes from the value if present
        value="$(echo "$value" | sed 's/^"//;s/"$//')"
        export "$key=$value"
    done <<EOF
$(azd env get-values)
EOF

    echo "✅ Environment variables set!"

    # Check if 'uv' is installed
    if ! command -v uv >/dev/null 2>&1; then
        echo -e "${MAIN_COLOR}📦 'uv' not installed. Installing...${RESET_COLOR}"
        curl -LsSf https://astral.sh/uv/install.sh | sh || {
            echo -e "${ERROR_COLOR}❌ Failed to install uv.${RESET_COLOR}"
            return 1
        }
        source "$HOME/.cargo/env"
    fi

    echo -e "${MAIN_COLOR}🛠️ Creating virtual environment...${RESET_COLOR}"
    if ! uv venv; then
        echo -e "${ERROR_COLOR}❌ Failed to create virtual environment.${RESET_COLOR}"
        return 1
    fi

    if ! source .venv/bin/activate; then
        echo -e "${ERROR_COLOR}❌ Failed to activate virtual environment.${RESET_COLOR}"
        return 1
    fi

    echo -e "${MAIN_COLOR}🔄 Syncing dependencies...${RESET_COLOR}"
    if ! uv sync; then
        echo -e "${ERROR_COLOR}❌ Failed to sync dependencies.${RESET_COLOR}"
        return 1
    fi

    return 0
}
