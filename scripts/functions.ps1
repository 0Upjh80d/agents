function Initialize-PythonEnv {
    Write-Host "⏳ Loading azd .env file from current environment..."

    # 1. Pull environment values from 'azd env get-values'
    $azdOutput = azd env get-values
    if ($LASTEXITCODE -ne 0) {
        Write-Host "❌ Failed to load environment variables from azd environment."
        exit $LASTEXITCODE
    }

    foreach ($line in $azdOutput) {
        if ($line -match "([^=]+)=(.*)") {
            $key = $matches[1]
            $value = $matches[2] -replace '^"|"$'
            Set-Item -Path "env:\$key" -Value $value
        }
    }

    Write-Host "✅ Environment variables set!"

    # Check if 'uv' is installed
        if (-not (Get-Command uv -ErrorAction SilentlyContinue)) {
        Write-Output "📦 'uv' not installed. Installing..."
        # Download and install 'uv'
        $installScript = (New-Object System.Net.WebClient).DownloadString('https://astral.sh/uv/install.ps1')
        if (-not $?) {
            Write-Error "❌ Failed to download uv install script."
            exit 1
        }
        Invoke-Expression $installScript
        if ($LASTEXITCODE -ne 0) {
            Write-Error "❌ Failed to install 'uv'."
            exit $LASTEXITCODE
        }
        # Ensure the newly installed location is in PATH for this session
        $env:Path += ";C:\Users\$env:USERNAME\.local\bin"
    }

    # Create virtual environment
    Write-Output "🛠️ Creating virtual environment..."
    uv venv
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Failed to initialize virtual environment."
        exit $LASTEXITCODE
    }

    # Activate virtual environment
    Write-Host "🛠️ Activating virtual environment..."
    & ./.venv/Scripts/Activate
    # Because 'Activate' is usually a script, we check $?
    if (-not $?) {
        Write-Error "❌ Failed to activate virtual environment."
        exit 1
    }

    # Sync dependencies
    Write-Host "🔄 Syncing Python dependencies with 'uv sync'..."
    uv sync
    if ($LASTEXITCODE -ne 0) {
        Write-Error "❌ Failed to sync Python dependencies."
        exit $LASTEXITCODE
    }

    Write-Output "✅ Environment setup complete!"
}

function Start-BackendServer {
    param (
        [Parameter(Mandatory=$false)]
        [string]$AppName,

        [Parameter(Mandatory=$true)]
        [int]$Port,

        [Parameter(Mandatory=$false)]
        [string]$HostName = "127.0.0.1",

        [Parameter(Mandatory=$true)]
        [string]$color
    )

    if (-not $AppName) {
        Write-Warning "No AppName specified. Falling back to 'app:app'..."
        $AppName = "app:app"
    }

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
        Write-Output "🔄 Installing npm dependencies..."
        npm install
        if ($LASTEXITCODE -ne 0) {
            Write-Error "❌ npm install failed."
            exit $LASTEXITCODE
        }

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

function Stop-AllJobs {
    param(
        [Parameter(Mandatory=$false)]
        [System.Management.Automation.Job]$mainBackendJob = $null,

        [Parameter(Mandatory=$false)]
        [System.Management.Automation.Job]$agentBackendJob = $null,

        [Parameter(Mandatory=$false)]
        [System.Management.Automation.Job]$frontendJob = $null
    )

    Write-Host "✋ Cleaning up" -ForegroundColor Red

    if ($mainBackendJob) {
        $stoppedMain = Stop-SingleJob -Job $mainBackendJob
    }

    if ($agentBackendJob) {
        $stoppedAgent = Stop-SingleJob -Job $agentBackendJob
    }

    if ($frontendJob) {
        $stoppedFrontend = Stop-SingleJob -Job $frontendJob
    }

    Write-Host "✅ All jobs stopped and removed." -ForegroundColor Green
}
