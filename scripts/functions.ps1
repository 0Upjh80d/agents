function Initialize-PythonEnv {
    # Check if uv is installed
        if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Write-Output "📦 uv not installed. Installing..."
        Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://astral.sh/uv/install.ps1'))
        $env:Path += ";C:\Users\$env:USERNAME\.local\bin"
    }

    # Create virtual environment
    Write-Output "🛠️ Creating virtual environment..."
    uv venv
    if ($LASTEXITCODE -ne 0) { Write-Error "❌ Failed to intialize virtual environment."; exit 1 }

    # Activate virtual environment
    & ./.venv/Scripts/Activate
    if ($LASTEXITCODE -ne 0) { Write-Error "❌ Failed to activate virtual environment."; exit 1 }

    # Sync dependencies
    Write-Output "🔄 Syncing dependencies..."
    uv sync
    if ($LASTEXITCODE -ne 0) { Write-Error "❌ Failed to sync dependencies."; exit 1 }

    Write-Output "✅ Environment setup complete!"
}

function Start-BackendServer {
    param (
        [Parameter(Mandatory=$true)]
        [string]$AppName,

        [Parameter(Mandatory=$true)]
        [int]$Port,

        [Parameter(Mandatory=$false)]
        [string]$HostName = "127.0.0.1",

        [Parameter(Mandatory=$true)]
        [string]$color
    )

    $uvicornCommand = "uvicorn $AppName --host $HostName --port $Port --reload"

    Write-Host "🚀 Starting $AppName backend server on port:$Port" -ForegroundColor $color

    # Start the process as a background job and return the job object
    $job = Start-Job -ScriptBlock {
        param($command)

        # Execute the command and stream both stdout and stderr to PowerShell's output
        # This is used to ensure all uvicorn output can be captured by our Show-NewJobOutput function below,
        # such that it can capture both standard output (stdout) and uvicorn info messages (stderr)
        & cmd /c "$command 2>&1"
    } -ArgumentList $uvicornCommand

    return $job
}

function Start-FrontendServer {
    $job = Start-Job -ScriptBlock {
        # Set output encoding
        [Console]::OutputEncoding = [System.Text.Encoding]::UTF8
        $OutputEncoding = [System.Text.Encoding]::UTF8

        # Install dependencies
        Write-Output "🔄 Installing npm dependencies"
        npm install

        # Run Angular
        Write-Output "🚀 Starting Angular frontend server on port:4200"
        & cmd /c "npx ng serve --open 2>&1"
    }

    return $job
}

function Show-NewJobOutput {
    param(
        [System.Management.Automation.Job]$Job,  # PowerShell job
        [string]$Label,                          # Label for output
        [ConsoleColor]$Color                     # Color for output
    )

    $output = Receive-Job -Job $Job
    if ($output) {
        foreach ($line in $output) {
            Write-Host "[$Label] $line" -ForegroundColor $Color
        }
    }
}

function Stop-AllJobs {
    param(
        [Parameter(Mandatory=$true)]
        [System.Management.Automation.Job]$mainBackendJob,

        [Parameter(Mandatory=$true)]
        [System.Management.Automation.Job]$agentBackendJob,

        [Parameter(Mandatory=$true)]
        [System.Management.Automation.Job]$frontendJob
    )

    Write-Host "✋ Cleaning up" -ForegroundColor Red

    if ($MainBackendJob) {
        $stoppedMain = Stop-SingleJob -Job $MainBackendJob
    }

    if ($AgentBackendJob) {
        $stoppedAgent = Stop-SingleJob -Job $AgentBackendJob
    }

    if ($FrontendJob) {
        $stoppedFrontend = Stop-SingleJob -Job $FrontendJob
    }

    Write-Host "✅ All jobs stopped and removed." -ForegroundColor Green
}

Function Stop-SingleJob {
    param(
        [Parameter(Mandatory=$true)]
        [System.Management.Automation.Job]$Job
    )
    if ($Job) {
        Stop-Job -Job $Job -ErrorAction SilentlyContinue
        Remove-Job -Job $Job -Force -ErrorAction SilentlyContinue
        return $true
    }
    return $false
}
