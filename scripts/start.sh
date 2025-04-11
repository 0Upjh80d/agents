#!/bin/bash
# Recommended for safer scripting:
set -Eeuo pipefail

# Import functions and colors
SCRIPT_DIR="$(dirname "${BASH_SOURCE[0]}")"
source "$SCRIPT_DIR/functions.sh"

# Clean-up processes
cleanup() {
    # Normal clean up
    echo -e "${MAIN_COLOR}======== 📡 Received exit signal. Stopping all processes ========${RESET_COLOR}"
    cleanup_process "${frontend_pid:-}" "frontend" "$FRONTEND_COLOR"
    cleanup_process "${main_pid:-}" "main" "$MAIN_COLOR"
    cleanup_process "${agent_pid:-}" "agent" "$AGENT_COLOR"
    echo -e "${MAIN_COLOR}✅ All processes stopped.${RESET_COLOR}"

    # Fallback: check if any processes are still using the ports
    if lsof -t -i:8000,8001 &>/dev/null; then
        echo -e "${MAIN_COLOR}🗑️ Detected services still running on ports 8000/8001. Performing forced cleanup...${RESET_COLOR}"
        kill -9 "$(lsof -t -i:8000,8001)" 2>/dev/null || true
    fi
    exit 0
}

# Trap signals (INT or TERM) for cleanup
trap cleanup INT TERM

# Set backend environment
echo -e "${INFO_COLOR}======== 🚀 Setting up Backend ========${RESET_COLOR}"
if ! setup_backend_env; then
    echo -e "${ERROR_COLOR}❌ Failed to set up environment.${RESET_COLOR}"
    exit 1
fi

# Run backend servers
echo -e "${MAIN_COLOR}🚀 Starting main server on port 8000...${RESET_COLOR}"
run_server "app" 8000 "$MAIN_COLOR" "MAIN" &
main_pid=$!

echo -e "${AGENT_COLOR}🚀 Starting agent server on port 8001...${RESET_COLOR}"
run_server "agent_app" 8001 "$AGENT_COLOR" "AGENT" &
agent_pid=$!

sleep 2

# Set up and run frontend server
echo -e "${INFO_COLOR}======== 🚀 Setting up Frontend ========${RESET_COLOR}"
cd ./app/frontend || {
    echo -e "${ERROR_COLOR}❌ Failed to change directory to app/frontend.${RESET_COLOR}"
    exit 1
}

setup_and_run_frontend &
frontend_pid=$!

echo -e "${FRONTEND_COLOR}✅ Frontend server running with PID: $frontend_pid.${RESET_COLOR}"

# Wait for all processes to exit
wait "$main_pid" "$agent_pid" "$frontend_pid"
