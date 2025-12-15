# PowerShell script to run Othello backend locally
# Usage: powershell -ExecutionPolicy Bypass -File scripts/run_local.ps1

$env:PORT = $env:PORT -or 5000
$port = $env:PORT

Write-Host "[Othello] Starting backend on http://127.0.0.1:$port/"
Write-Host "[Othello] Health endpoint: http://127.0.0.1:$port/api/health/db"

# Activate venv if present
if (Test-Path ".venv/Scripts/Activate.ps1") {
    . .venv/Scripts/Activate.ps1
}

# Start Flask app using module:app syntax
$env:FLASK_APP = "api:app"
$env:FLASK_RUN_PORT = $port
$env:FLASK_RUN_HOST = "127.0.0.1"
py -m flask --app api:app run --host 127.0.0.1 --port $port
