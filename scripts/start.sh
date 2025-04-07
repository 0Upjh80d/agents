#!/bin/bash

# --- Function to clean up background processes on exit ---
cleanup() {
    echo "Received exit signal. Stopping background processes..."
    # Check if FRONTEND_PID is set and the process exists
    if [[ ! -z "$FRONTEND_PID" && -e /proc/$FRONTEND_PID ]]; then
        echo "Stopping frontend server (PID: $FRONTEND_PID)..."
        # Send TERM signal, wait a bit, then KILL if needed
        kill $FRONTEND_PID
        sleep 2
        if [[ -e /proc/$FRONTEND_PID ]]; then
           kill -9 $FRONTEND_PID
        fi
    else
         echo "Frontend process not found or already stopped."
    fi
    exit 0
}

# --- Trap signals for cleanup ---
# Call the cleanup function when the script receives SIGINT (Ctrl+C) or SIGTERM
trap cleanup INT TERM

# --- Initial Setup ---
# Check if uv is installed
if ! command -v uv >/dev/null 2>&1; then
    echo "uv not installed. Installing..."
    # Use -E for sudo if needed, handle potential errors
    curl -LsSf https://astral.sh/uv/install.sh | sh || { echo "Failed to install uv"; exit 1; }
    # Ensure uv is in PATH for the current script session
    source "$HOME/.cargo/env" # Common location, adjust if uv installs elsewhere
fi

echo "Creating/updating python virtual environment..."
uv venv || { echo "Failed to create venv"; exit 1; } # Ensure venv exists

# Activate - important for subsequent uv/python commands
source .venv/bin/activate || { echo "Failed to activate venv"; exit 1; }

echo "Syncing Python dependencies..."
uv sync || { echo "Failed to sync Python dependencies"; exit 1; }

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

echo ""
echo "--- Backend Setup ---"
echo "Changing to backend directory..."
# Navigate relative to the current frontend directory
cd ../../app/backend/app || { echo "Failed to change directory to app/backend/app"; exit 1; }

# --- Start Backend Server in Foreground ---
echo "Starting backend server (uvicorn)... (Press CTRL+C to stop both servers)"
# Uvicorn runs in the foreground. When you press Ctrl+C, the trap will trigger.
uvicorn main:app --reload --host 0.0.0.0

# --- Script waits here until uvicorn stops ---

echo "Backend server stopped."
cleanup # Call cleanup explicitly in case uvicorn exited without a signal
