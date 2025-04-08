. $PSScriptRoot/functions.ps1

try {

    # Backend setup
    Write-Host "======== Setting up Backend ========" -ForegroundColor Green

    Initialize-PythonEnv

    $backendPath = Join-Path -Path $PSScriptRoot -ChildPath "../app/backend/app"
    Set-Location $backendPath
    if ($LASTEXITCODE -ne 0) { Write-Error "❌ Failed to change directory to backend directory."}

    $mainBackendJob = Start-BackendServer -AppName "main:app" -Port 8000 -Color Cyan
    $agentBackendJob = Start-BackendServer -AppName "main:agent_app" -Port 8001 -Color Yellow

    Start-Sleep -Seconds 2

    # Frontend setup
    Write-Host "======== Setting up Frontend ========" -ForegroundColor Green
    $frontendPath = Join-Path -Path $PSScriptRoot -ChildPath "../app/frontend"
    Set-Location $frontendPath
    if ($LASTEXITCODE -ne 0) { Write-Error "❌ Failed to change directory to frontend directory."}

    $frontendJob = Start-FrontendServer

    $allJobs = @($mainBackendJob, $agentBackendJob, $frontendJob)

    while($true) {
        # Show output from all servers
        Show-NewJobOutput -Job $mainBackendJob -Label "MAIN" -Color Cyan
        Show-NewJobOutput -Job $agentBackendJob -Label "AGENT" -Color Yellow
        Show-NewJobOutput -Job $frontendJob -Label "FRONTEND" -Color Magenta
    }
} finally {

    Stop-AllJobs -MainBackendJob $mainBackendJob -AgentBackendJob $agentBackendJob -FrontendJob $frontendJob

    cd $PSScriptRoot/..
}

# Fall back if the script exits unexpectedly
Write-Host "Script completed unexpectedly." -ForegroundColor Red
Stop-AllJobs -MainBackendJob $mainBackendJob -AgentBackendJob $agentBackendJob -FrontendJob $frontendJob
