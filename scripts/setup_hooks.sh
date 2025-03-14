#!/usr/bin/env bash

echo "🚀 Setting up Git hooks..."

# 1) Ensure core.hooksPath is unset (so we use .git/hooks by default)
git config --unset core.hooksPath

# 2) Install node modules (so commitlint and other dev deps are available)
if [ -f "package.json" ]; then
  echo "📦 Installing Node modules..."
  npm install
  echo "✅ Node modules installed."
else
  echo "⚠️  No package.json found, skipping npm install."
fi

# 3) If using pre-commit for other checks, install it. (Optional)
#    If you don't use pre-commit, you can remove these lines.
if command -v pre-commit &> /dev/null
then
  echo "🔧 Installing pre-commit hooks..."
  pre-commit install
else
  echo "⚠️  pre-commit is not installed (skipping pre-commit install)."
fi

# 4) Copy custom commit-msg hook
if [ -f ".githooks/commit-msg" ]; then
  cp .githooks/commit-msg .git/hooks/commit-msg
  chmod +x .git/hooks/commit-msg
  echo "✅ Copied commit-msg hook."
else
  echo "❌ .githooks/commit-msg not found!"
fi

# 5) Copy custom pre-push hook
if [ -f ".githooks/pre-push" ]; then
  cp .githooks/pre-push .git/hooks/pre-push
  chmod +x .git/hooks/pre-push
  echo "✅ Copied pre-push hook."
else
  echo "❌ .githooks/pre-push not found!"
fi

echo "✅ Git hooks setup completed successfully!"
