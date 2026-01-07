param(
    [Parameter(Mandatory=$true)]
    [string]$Message
)

$ErrorActionPreference = "Stop"

# Detect current branch
$branch = git rev-parse --abbrev-ref HEAD
if (-not $branch) {
    Write-Error "Could not detect current branch."
    exit 1
}

Write-Host "[pushme] Branch: $branch" -ForegroundColor Gray

# Stage
Write-Host "[pushme] Staging all changes..." -ForegroundColor Cyan
git add .

# Commit
Write-Host "[pushme] Committing: '$Message'" -ForegroundColor Cyan
git commit -m "$Message"

# Push
Write-Host "[pushme] Pushing to origin/$branch..." -ForegroundColor Cyan
git push origin $branch

Write-Host "[pushme] Success!" -ForegroundColor Green
