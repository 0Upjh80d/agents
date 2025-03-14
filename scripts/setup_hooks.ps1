Write-Host "🚀 Setting up Git hooks..."

# 1) Ensure core.hooksPath is unset (so we use .git/hooks by default)
git config --unset core.hooksPath

# 2) Install Node modules (so commitlint and other dev deps are available)
if (Test-Path "package.json") {
    Write-Host "📦 Installing Node modules..."
    npm install
    Write-Host "✅ Node modules installed."
} else {
    Write-Host "⚠️  No package.json found, skipping npm install."
}

# 3) If using pre-commit for other checks, install it. (Optional)
if (Get-Command pre-commit -ErrorAction SilentlyContinue) {
    Write-Host "🔧 Installing pre-commit hooks..."
    pre-commit install
} else {
    Write-Host "⚠️  pre-commit is not installed (skipping pre-commit install)."
}

# 4) Copy custom commit-msg hook
if (Test-Path ".githooks/commit-msg") {
    Copy-Item ".githooks/commit-msg" ".git/hooks/commit-msg"
    Write-Host "✅ Copied commit-msg hook."
} else {
    Write-Host "❌ .githooks/commit-msg not found!"
}

# 5) Copy custom pre-push hook
if (Test-Path ".githooks/pre-push") {
    Copy-Item ".githooks/pre-push" ".git/hooks/pre-push"
    Write-Host "✅ Copied pre-push hook."
} else {
    Write-Host "❌ .githooks/pre-push not found!"
}

Write-Host "✅ Git hooks setup completed successfully!"
