#!/bin/bash
# Define colors
MAIN_COLOR="\033[1;36m"  # Cyan
AGENT_COLOR="\033[1;33m" # Yellow
RESET_COLOR="\033[0m"    # Reset to default

# --- Function to clean up all background processes on exit ---
cleanup() {
    echo "Received exit signal. Stopping all background processes..."

    # Stop frontend server
    if [[ ! -z "$FRONTEND_PID" && -e /proc/$FRONTEND_PID ]]; then
        echo "Stopping frontend server (PID: $FRONTEND_PID)..."
        kill $FRONTEND_PID
        sleep 2
        if [[ -e /proc/$FRONTEND_PID ]]; then
            kill -9 $FRONTEND_PID
        fi
    else
        echo "Frontend process not found or already stopped."
    fi

    # Stop backend servers
    if [[ ! -z "$main_pid" ]]; then
        echo "Stopping main server (PID: $main_pid)..."
        kill $main_pid 2>/dev/null
    fi

    if [[ ! -z "$agent_pid" ]]; then
        echo "Stopping agent server (PID: $agent_pid)..."
        kill $agent_pid 2>/dev/null
    fi

    echo "All processes stopped."
    exit 0
}

# --- Trap signals for cleanup ---
# Call the cleanup function when the script receives SIGINT (Ctrl+C) or SIGTERM
trap cleanup INT TERM

# ----- Initial Setup -----
# Check if uv is installed
if ! command -v uv >/dev/null 2>&1; then
    echo "uv not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh || { echo "Failed to install uv"; exit 1; }
    source "$HOME/.cargo/env" # Common location, adjust if uv installs elsewhere
fi

echo "Creating/updating python virtual environment..."
uv venv || { echo "Failed to create venv"; exit 1; }
source .venv/bin/activate || { echo "Failed to activate venv"; exit 1; }

echo "Syncing Python dependencies..."
uv sync || { echo "Failed to sync Python dependencies"; exit 1; }

# ----- Run frontend server -----
echo ""
echo "--- Frontend Setup ---"
echo "Changing to frontend directory..."
# Assuming your angular project root is app/frontend/app where package.json is
cd app/frontend || { echo "Failed to change directory to app/frontend/app"; exit 1; }

echo "Restoring frontend npm packages..."
npm install
if [ $? -ne 0 ]; then
    echo "Failed to restore frontend npm packages"
    exit $? # Exit using the error code from npm install
fi
echo ""

# --- Start Frontend Dev Server in Background ---
echo "Starting frontend development server (ng serve) in background..."
ng serve --open & # <-- Run in background

# Capture the Process ID (PID) of the backgrounded frontend server
FRONTEND_PID=$!
echo "Frontend server started in background with PID: $FRONTEND_PID"
# Give it a few seconds to start up (optional, helps avoid log mingling initially)
sleep 5

# ----- Run backend main and agent servers -----
echo ""
echo "--- Backend Setup ---"
echo "Changing to backend directory..."
# Navigate relative to the current frontend directory
cd ../backend/app || { echo "Failed to change directory to app/backend/app"; exit 1; }

# Function to run server with colored output
run_server() {
    local app_name=$1
    local port=$2
    local color=$3
    local label=$4

    # Run uvicorn with colored output
    uvicorn "main:$app_name" --reload --host 127.0.0.1 --port "$port" 2>&1 | \

        while IFS= read -r line; do
            printf "${color}[${label}]%s${RESET_COLOR}\n" "$line"
        done
}

# Run both servers in parallel
echo "${MAIN_COLOR}Starting main server on port 8000...${RESET_COLOR}"
echo "${AGENT_COLOR}Starting agent server on port 8001...${RESET_COLOR}"

# Start both servers in the background
run_server "main_app" 8000 "$MAIN_COLOR" "MAIN" &
main_pid=$!

run_server "agent_app" 8001 "$AGENT_COLOR" "AGENT" &
agent_pid=$!

# Wait for both processes to exit
wait $main_pid $agent_pid $FRONTEND_PID
