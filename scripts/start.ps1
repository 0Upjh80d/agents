# --- Function to clean up background processes on exit ---
function Cleanup {
    Write-Output "Received exit signal. Stopping background processes..."
    if ($global:FRONTEND_PID -and (Get-Process -Id $global:FRONTEND_PID -ErrorAction SilentlyContinue)) {
        Write-Output "Stopping frontend server (PID: $global:FRONTEND_PID)..."
        Stop-Process -Id $global:FRONTEND_PID -Force
    } else {
        Write-Output "Frontend process not found or already stopped."
    }
    exit 0
}

# --- Trap signals for cleanup ---
$CleanupAction = {
    Cleanup
}

Register-ObjectEvent -InputObject ([System.Console]) -EventName "CancelKeyPress" -Action $CleanupAction

# --- Initial Setup ---
# Check if uv is installed
if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Output "uv not installed. Installing..."
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://astral.sh/uv/install.ps1'))
    $env:Path += ";C:\Users\$env:USERNAME\.local\bin"
}

Write-Output "Creating/updating Python virtual environment..."
uv venv
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to create venv"; exit 1 }

# Activate virtual environment
& .\.venv\Scripts\Activate
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to activate venv"; exit 1 }

Write-Output "Syncing Python dependencies..."
uv sync
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to sync Python dependencies"; exit 1 }

Write-Output ""
Write-Output "--- Frontend Setup ---"
Write-Output "Changing to frontend directory..."
$frontendPath = Join-Path -Path $PSScriptRoot -ChildPath "..\app\frontend"
Set-Location $frontendPath
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to change directory to app/frontend"; exit 1 }

Write-Output "Restoring frontend npm packages..."
npm install
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to restore frontend npm packages"; exit $LASTEXITCODE }

Write-Output ""

# --- Start Frontend Dev Server in Background ---
Write-Output "Starting frontend development server (ng serve) in background..."
$frontendProcess = Start-Process npx -ArgumentList "ng", "serve", "--open" -PassThru
$global:FRONTEND_PID = $frontendProcess.Id
Write-Output "Frontend server started in background with PID: $global:FRONTEND_PID"
Start-Sleep -Seconds 5

Write-Output ""
Write-Output "--- Backend Setup ---"
Write-Output "Changing to backend directory..."
$backendPath = Join-Path -Path $PSScriptRoot -ChildPath "..\app\backend\app"
Set-Location $backendPath
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to change directory to app/backend/app"; exit 1 }

# Remember current PATH with activated environment:
# This is required because when we use Start-Job, the new Powershell session
# does not inherit the environment variables from the parent session.
$activatedPath = $env:PATH

# Start both servers in background jobs:
# $workdir will be your Present Working Directory (PWD)
# $envPath will be the PATH variable from the parent shell

# main server
Write-Host "Starting main server on port 8000..." -ForegroundColor Cyan
$mainJob = Start-Job -ScriptBlock {
    param($workDir, $envPath)

    # Set working directory and path from parent shell
    Set-Location $workDir
    $env:PATH = $envPath

    # Run uvicorn
    uvicorn "main:main_app" --reload --host 127.0.0.1 --port 8000
} -ArgumentList $PWD, $activatedPath

# agent server
Write-Host "Starting agent server on port 8001..." -ForegroundColor Yellow
$agentJob = Start-Job -ScriptBlock {
    param($workDir, $envPath)

    # Set working directory and path from parent shell
    Set-Location $workDir
    $env:PATH = $envPath

    # Run uvicorn
    uvicorn "main:agent_app" --reload --host 127.0.0.1 --port 8001
} -ArgumentList $PWD, $activatedPath

# Display colored output
function Show-NewJobOutput {
    param(
        [System.Management.Automation.Job]$Job,  # PowerShell job object to retrieve output from
        [string]$Label,                          # Label for output ([MAIN] or [AGENT])
        [ConsoleColor]$Color                     # Color for output
    )

    $output = Receive-Job -Job $Job
    if ($output) {
        foreach ($line in $output) {
            Write-Host "[$Label] $line" -ForegroundColor $Color
        }
    }
}

# Main loop to display output and handle termination
try {
    Write-Host "Servers running. Press Ctrl+C to stop." -ForegroundColor Green

    while ($true) {
        # Show output from both servers (only new output)
        Show-NewJobOutput -Job $mainJob -Label "MAIN" -Color Cyan
        Show-NewJobOutput -Job $agentJob -Label "AGENT" -Color Yellow

        # Longer delay to reduce unnecessary polling
        Start-Sleep -Seconds 1

        # Check if jobs are still running
        if ($mainJob.State -ne "Running" -and $agentJob.State -ne "Running") {
            Write-Host "Both servers have stopped. Exiting." -ForegroundColor Red
            break
        }
    }
}
finally {
    # Clean up jobs on exit
    Write-Host "Stopping servers..." -ForegroundColor Gray

    if ($mainJob.State -eq "Running") {
        Stop-Job -Job $mainJob
        Remove-Job -Job $mainJob -Force
    }

    if ($agentJob.State -eq "Running") {
        Stop-Job -Job $agentJob
        Remove-Job -Job $agentJob -Force
    }

    Set-Location ../../..        # Go back to root directory

    Write-Host "Servers stopped." -ForegroundColor Gray
}


# # --- Start Backend Server in Foreground ---
# Write-Output "Starting backend server (uvicorn)... (Press CTRL+C to stop both servers)"
# Start-Process -NoNewWindow -Wait -FilePath uvicorn -ArgumentList "main:app --reload --host 0.0.0.0"

# Write-Output "Backend server stopped."
# Cleanup
