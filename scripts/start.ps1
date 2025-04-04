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

# --- Start Backend Server in Foreground ---
Write-Output "Starting backend server (uvicorn)... (Press CTRL+C to stop both servers)"
Start-Process -NoNewWindow -Wait -FilePath uvicorn -ArgumentList "main:app --reload --host 0.0.0.0"

Write-Output "Backend server stopped."
Cleanup
