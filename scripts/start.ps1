if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
    Write-Output "uv not installed. Installing..."
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
    $env:Path = "C:\Users\$env:USERNAME\.local\bin;$env:Path"
}

Write-Output "Creating python virtual environment..."
uv venv
. .venv/Scripts/activate

Write-Output "Syncing dependencies..."
uv sync

Set-Location app/backend/app

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
