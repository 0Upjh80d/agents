# Set proper encoding at the script level
$OutputEncoding = [System.Text.Encoding]::UTF8
[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
chcp 65001 > $null  # Set console to UTF-8 codepage

# --- Function to clean up background processes on exit ---
function Cleanup {
    Write-Output "Received exit signal. Stopping background processes..."

    # Stop frontend job if it exists
    if (Get-Variable -Name frontendJob -ErrorAction SilentlyContinue) {
        Write-Output "Stopping frontend server job..."
        Stop-Job -Job $frontendJob -ErrorAction SilentlyContinue
        Remove-Job -Job $frontendJob -Force -ErrorAction SilentlyContinue
    }

    # Stop main backend job if it exists
    if (Get-Variable -Name mainJob -ErrorAction SilentlyContinue) {
        Write-Output "Stopping main server job..."
        Stop-Job -Job $mainJob -ErrorAction SilentlyContinue
        Remove-Job -Job $mainJob -Force -ErrorAction SilentlyContinue
    }

    # Stop agent backend job if it exists
    if (Get-Variable -Name agentJob -ErrorAction SilentlyContinue) {
        Write-Output "Stopping agent server job..."
        Stop-Job -Job $agentJob -ErrorAction SilentlyContinue
        Remove-Job -Job $agentJob -Force -ErrorAction SilentlyContinue
    }

    Set-Location ../../..

    Write-Output "All processes stopped."
    exit 0
}

# --- Trap signals for cleanup ---
$CleanupAction = {
    Cleanup
}

$event = Register-ObjectEvent -InputObject ([System.Console]) -EventName "CancelKeyPress" -Action $CleanupAction

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
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to create venv"; Cleanup }

Write-Output "Restoring frontend npm packages..."
npm install
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to restore frontend npm packages"; exit $LASTEXITCODE }

Write-Output ""

# --- Start Frontend Dev Server in Background ---
Write-Output "Starting frontend development server (ng serve) in background..."

# Remember current PATH with activated environment:
# This is required because when we use Start-Job, the new Powershell session
# does not inherit the environment variables from the parent session.
$activatedPath = $env:PATH


$frontendJob = Start-Job -ScriptBlock {
    param($workDir, $envPath)

    # Set working directory and path from parent shell
    Set-Location $workDir
    $env:PATH = $envPath

    # Run Angular
    npx ng serve --open
} -ArgumentList $frontendPath, $activatedPath

Write-Output ""
Write-Output "--- Backend Setup ---"
Write-Output "Changing to backend directory..."
$backendPath = Join-Path -Path $PSScriptRoot -ChildPath "..\app\backend\app"
Set-Location $backendPath
if ($LASTEXITCODE -ne 0) { Write-Error "Failed to change directory to app/backend/app"; Cleanup }

# Start backend servers in background jobs:
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
    uvicorn "main:app" --reload --host 127.0.0.1 --port 8000
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
    while ($true) {
        # Show output from all servers
        Show-NewJobOutput -Job $mainJob -Label "MAIN" -Color Cyan
        Show-NewJobOutput -Job $agentJob -Label "AGENT" -Color Yellow
        Show-NewJobOutput -Job $frontendJob -Label "FRONTEND" -Color Magenta

        Start-Sleep -Seconds 1

        # Check if jobs are still running
        if ($mainJob.State -ne "Running" -and $agentJob.State -ne "Running") {
            Write-Host "Both backend servers have stopped. Exiting." -ForegroundColor Red
            Cleanup
        }
    }
}
catch {
    Write-Error "An error occurred: $_"
    Cleanup
}

# Fall back if the script exits unexpectedly
Write-Host "Script completed unexpectedly." -ForegroundColor Red
Cleanup
