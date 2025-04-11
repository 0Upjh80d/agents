. $PSScriptRoot/functions.ps1

# Pre-declare variables so they're always in scope for 'finally'
$mainBackendJob = $null
$agentBackendJob = $null
$frontendJob = $null

try {

    # Backend setup
    Write-Host "======== 🚀 Setting up Backend ========" -ForegroundColor Green

    Initialize-PythonEnv

    # Run backend servers
    $mainBackendJob = Start-BackendServer -AppName "app.backend.app.main:app" -Port 8000 -Color Cyan
    $agentBackendJob = Start-BackendServer -AppName "app.backend.app.main:agent_app" -Port 8001 -Color Yellow

    Start-Sleep -Seconds 2

    # Frontend setup
    Write-Host "======== 🚀 Setting up Frontend ========" -ForegroundColor Green
    $frontendPath = Join-Path -Path $PSScriptRoot -ChildPath "./app/frontend"
    Set-Location $frontendPath
    if (-not $?) {
        Write-Error "❌ Failed to change directory to the frontend directory."
        return
    }

    $frontendJob = Start-FrontendServer

    while($true) {
        # Show output from all servers
        Show-NewJobOutput -Job $mainBackendJob -Label "MAIN" -Color Cyan
        Show-NewJobOutput -Job $agentBackendJob -Label "AGENT" -Color Yellow
        Show-NewJobOutput -Job $frontendJob -Label "FRONTEND" -Color Magenta

        # Optional small delay to limit loop CPU usage
        Start-Sleep -Milliseconds 500
    }
} finally {
    Write-Host "======== 🛑 Stopping All Jobs ========" -ForegroundColor Red

    Stop-AllJobs -MainBackendJob $mainBackendJob -AgentBackendJob $agentBackendJob -FrontendJob $frontendJob

    # Restore original directory if needed
    Set-Location $PSScriptRoot/..

    Write-Host "======== ✅ Cleanup Complete. Exiting. ========"
}

# Fall back if the script exits unexpectedly
Write-Host "❌ Script completed unexpectedly." -ForegroundColor Red
# Ensure all jobs are stopped
Stop-AllJobs -MainBackendJob $mainBackendJob -AgentBackendJob $agentBackendJob -FrontendJob $frontendJob
