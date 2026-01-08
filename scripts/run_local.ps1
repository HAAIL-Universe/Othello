[CmdletBinding()]
param(
  [int]$Port,
  [string]$BindHost = "127.0.0.1",
  [switch]$Public,
  [switch]$NoEnv,
  [string]$EnvFile = ".env",
  [string]$App = "api:app",
  [switch]$NoVenv,
  [switch]$NoFlaskDebug,
  [string]$ServicesFile = ".\scripts\local_services.ps1",
  [string]$SmokeTestUrl = "",
  [string]$PythonExe = ""
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

if ($PSVersionTable.PSVersion.Major -ne 5) {
  throw "ENVIRONMENT_LIMITATION: Run this in Windows PowerShell 5.1 (detected $($PSVersionTable.PSVersion))."
}

$oldConfirmPreference = $ConfirmPreference
$ConfirmPreference = "None"

function Find-RepoRoot {
  param([string]$StartDir)
  $dir = Resolve-Path $StartDir
  for ($i = 0; $i -lt 8; $i++) {
    $candidate = $dir.Path
    if (Test-Path (Join-Path $candidate "api.py") -PathType Leaf) { return $candidate }
    if (Test-Path (Join-Path $candidate "requirements.txt") -PathType Leaf) { return $candidate }
    if (Test-Path (Join-Path $candidate "pyproject.toml") -PathType Leaf) { return $candidate }
    $parent = Split-Path $candidate -Parent
    if (-not $parent -or $parent -eq $candidate) { break }
    $dir = Resolve-Path $parent
  }
  throw "EVIDENCE_MISSING: Could not locate repo root walking up from $StartDir."
}

function Load-DotEnv {
  param([string]$Path)
  if (-not (Test-Path $Path -PathType Leaf)) { return }
  foreach ($line in (Get-Content -LiteralPath $Path)) {
    $t = $line.Trim()
    if ($t.Length -eq 0 -or $t.StartsWith("#")) { continue }
    if ($t -match '^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=\s*(.*)\s*$') {
      $key = $Matches[1]
      $val = $Matches[2].Trim()
      if (($val.StartsWith('"') -and $val.EndsWith('"')) -or ($val.StartsWith("'") -and $val.EndsWith("'"))) {
        $val = $val.Substring(1, $val.Length - 2)
      }
      [Environment]::SetEnvironmentVariable($key, $val, "Process")
    }
  }
}

function Get-PythonFromPyLauncher {
  # Return a real python.exe path discovered via `py -0p` that exists, else $null.
  $py = Get-Command "py" -ErrorAction SilentlyContinue
  if (-not $py) { return $null }

  try {
    $out = & $py.Source -0p 2>$null | Out-String
    if ([string]::IsNullOrWhiteSpace($out)) { return $null }

    $candidates = @()

    foreach ($line in ($out -split "`r?`n")) {
      # Updated regex to handle "-V:3.13", "-3.12-64", and optional "*" active marker
      if ($line -match '^\s*-\s*(?:V:)?([0-9]+)\.([0-9]+)[^\s]*\s+(?:\*\s+)?(.+python\.exe)\s*$') {
        $maj = [int]$Matches[1]
        $min = [int]$Matches[2]
        $path = $Matches[3].Trim()
        if (Test-Path $path -PathType Leaf) {
          $candidates += [PSCustomObject]@{ Maj=$maj; Min=$min; Path=$path }
        }
      }
    }

    if ($candidates.Count -eq 0) { return $null }

    $best = $candidates | Sort-Object Maj, Min -Descending | Select-Object -First 1
    return $best.Path
  } catch {
    return $null
  }
}

function Get-PythonExe {
  param([string]$RepoRoot)

  if ($PythonExe -and $PythonExe.Trim().Length -gt 0) {
    if (Test-Path $PythonExe -PathType Leaf) { return $PythonExe }
    throw "ENVIRONMENT_LIMITATION: -PythonExe was provided but not found: $PythonExe"
  }

  if (-not $NoVenv) {
    $venvCandidates = @(
      ".venv\Scripts\python.exe",
      "venv\Scripts\python.exe",
      ".env\Scripts\python.exe",
      "env\Scripts\python.exe"
    ) | ForEach-Object { Join-Path $RepoRoot $_ }

    foreach ($p in $venvCandidates) {
      if (Test-Path $p -PathType Leaf) { return $p }
    }
  }

  $pyDiscovered = Get-PythonFromPyLauncher
  if ($pyDiscovered) { return $pyDiscovered }

  $python = Get-Command "python" -ErrorAction SilentlyContinue
  if ($python) { return $python.Source }

  throw "ENVIRONMENT_LIMITATION: No usable Python found. Create .venv or repair/install Python so py -0p lists a real python.exe."
}

$serviceProcs = @()

try {
  $repoRoot = Find-RepoRoot -StartDir $PSScriptRoot
  Set-Location -LiteralPath $repoRoot

  $listenHost = if ($Public) { "0.0.0.0" } else { $BindHost }

  if (-not $NoEnv) {
    $envPath = Join-Path $repoRoot $EnvFile
    Load-DotEnv -Path $envPath
  }

  # FORCE AUTH: Override any complex .env settings to ensure local access works with the known code
  # This strips out hashes/keys that might conflict with the plaintext password
  [Environment]::SetEnvironmentVariable("OTHELLO_PIN_HASH", $null, "Process")
  [Environment]::SetEnvironmentVariable("OTHELLO_LOGIN_KEY", $null, "Process")
  [Environment]::SetEnvironmentVariable("OTHELLO_LOGIN_KEYS", $null, "Process")
  
  # Set the user's specific code
  [Environment]::SetEnvironmentVariable("OTHELLO_PASSWORD", "9465869", "Process")
  Write-Host "[run-local] Forced Authentication: Password set to '9465869'" -ForegroundColor Cyan

  # Default SECRET_KEY if missing (required for session)
  if (-not $env:OTHELLO_SECRET_KEY -and -not $env:SECRET_KEY) {
      Write-Host "[run-local] No SECRET_KEY found. Setting mock secret." -ForegroundColor Yellow
      [Environment]::SetEnvironmentVariable("OTHELLO_SECRET_KEY", "dev-secret-key-123", "Process")
  }
  # Default OPENAI_API_KEY placeholder if missing (app startup might complain or warn)
  if (-not $env:OPENAI_API_KEY) {
       Write-Host "[run-local] Warning: OPENAI_API_KEY is missing. AI features will fail." -ForegroundColor Magenta
  }

  # Check precise auth state to guide the user
  Write-Host "----------------------------------------------------------------" -ForegroundColor Gray
  if ($env:OTHELLO_LOGIN_KEYS) {
      Write-Host "Auth Mode:    LOGIN_KEYS (Multi-user)" -ForegroundColor Cyan
      Write-Host "Credentials:  Use one of the configured keys in .env" -ForegroundColor Cyan
  } elseif ($env:OTHELLO_PIN_HASH) {
      Write-Host "Auth Mode:    PIN_HASH (Bcrypt)" -ForegroundColor Cyan
      Write-Host "Credentials:  Use the pin matching the hash in .env" -ForegroundColor Cyan
  } elseif ($env:OTHELLO_LOGIN_KEY) {
      Write-Host "Auth Mode:    LOGIN_KEY (Direct Key)" -ForegroundColor Cyan
      Write-Host "Credentials:  Use the login key defined in .env" -ForegroundColor Cyan
  } elseif ($env:OTHELLO_PASSWORD) {
      Write-Host "Auth Mode:    PASSWORD (Plaintext)" -ForegroundColor Cyan
      Write-Host "Credentials:  Password is '$($env:OTHELLO_PASSWORD)'" -ForegroundColor Cyan
  } else {
      # This block normally unreachable due to defaults above, but good for safety
      Write-Host "Auth Mode:    NONE" -ForegroundColor Red
  }
  Write-Host "----------------------------------------------------------------" -ForegroundColor Gray
  Write-Host ""
    
  if (-not $PSBoundParameters.ContainsKey("Port") -or $Port -le 0) {
    $portEnv = [Environment]::GetEnvironmentVariable("PORT", "Process")
    $Port = if ($portEnv -and ($portEnv -match '^\d+$')) { [int]$portEnv } else { 5000 }
  }
  [Environment]::SetEnvironmentVariable("PORT", "$Port", "Process")

  $flaskDebug = -not $NoFlaskDebug
  $flaskDebugStr = if ($flaskDebug) { "1" } else { "0" }
  [Environment]::SetEnvironmentVariable("FLASK_DEBUG", $flaskDebugStr, "Process")
  [Environment]::SetEnvironmentVariable("DEBUG_INTENT", "1", "Process")

  $pyExe = Get-PythonExe -RepoRoot $repoRoot

  $flaskArgs = @("-m","flask","--app",$App,"run","--host",$listenHost,"--port","$Port")
  if ($flaskDebug) { $flaskArgs += "--debug" }

  Write-Host ""
  Write-Host "[run-local] Repo root: $repoRoot" -ForegroundColor Gray
  Write-Host "[run-local] Python: $pyExe" -ForegroundColor Gray
  Write-Host "[run-local] Flask: $pyExe $($flaskArgs -join ' ')" -ForegroundColor Green
  Write-Host ""

  $browserHost = if ($listenHost -eq "0.0.0.0") { "127.0.0.1" } else { $listenHost }
  $url = "http://${browserHost}:${Port}"
  Write-Host "Launching $url in default browser..." -ForegroundColor Cyan
  Start-Process $url

  & $pyExe @flaskArgs

} finally {
  $ConfirmPreference = $oldConfirmPreference
}
