# Define colors
MAIN_COLOR="\033[1;36m"  # Cyan
AGENT_COLOR="\033[1;33m" # Yellow
RESET_COLOR="\033[0m"    # Reset to default

if ! command -v uv >/dev/null 2>&1; then
    echo "uv not installed. Installing..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
fi

echo "Creating python virtual environment..."
uv venv
source .venv/bin/activate

echo "Syncing dependencies..."
uv sync

cd app/backend/app

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
echo -e "${MAIN_COLOR}Starting main server on port 8000...${RESET_COLOR}"
echo -e "${AGENT_COLOR}Starting agent server on port 8001...${RESET_COLOR}"

# Start both servers in the background, pipe their output through the coloring function
run_server "main_app" 8000 "$MAIN_COLOR" "MAIN" &
main_pid=$!

run_server "agent_app" 8001 "$AGENT_COLOR" "AGENT" &
agent_pid=$!

# Trap Ctrl+C to kill both servers
trap "kill $main_pid $agent_pid 2>/dev/null" INT TERM

# Wait for both processes to exit
wait $main_pid $agent_pid
