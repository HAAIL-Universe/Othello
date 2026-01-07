param(
  [string]$Path = "build_docs/evidence/updatedifflog.md",
  [string]$CycleStatus = "IN_PROGRESS",
  [string[]]$Planned = @(),
  [string[]]$Completed = @(),
  [string[]]$Remaining = @(),
  [string]$NextAction = ""
)

# Non-interactive safety: avoid PowerShell confirmation prompts inside this script
$oldConfirm = $ConfirmPreference
$ConfirmPreference = 'None'
try {
  $utf8NoBom = New-Object System.Text.UTF8Encoding($false)

  $header = New-Object System.Text.StringBuilder
  [void]$header.AppendLine("# Cycle Status: $CycleStatus")
  [void]$header.AppendLine("")
  [void]$header.AppendLine("## Todo Ledger")

  if ($Planned.Count -gt 0) {
    [void]$header.AppendLine("Planned:")
    foreach ($x in $Planned) { [void]$header.AppendLine("- [ ] $x") }
  }
  if ($Completed.Count -gt 0) {
    [void]$header.AppendLine("Completed:")
    foreach ($x in $Completed) { [void]$header.AppendLine("- [x] $x") }
  }
  if ($Remaining.Count -gt 0) {
    [void]$header.AppendLine("Remaining:")
    foreach ($x in $Remaining) { [void]$header.AppendLine("- [ ] $x") }
  }

  [void]$header.AppendLine("")
  [void]$header.AppendLine("## Next Action")
  
  if ($NextAction.Trim().Length -gt 0) {
      [void]$header.AppendLine($NextAction.Trim())
  } else {
      [void]$header.AppendLine("Fill next action.")
  }
  
  [void]$header.AppendLine("")

  # Overwrite from scratch (no deletes needed)
  [System.IO.File]::WriteAllText($Path, $header.ToString(), $utf8NoBom)

  # Prefer staged diff for “single artifact per cycle”
  $diff = (& git diff --cached --text | Out-String)
  if ([string]::IsNullOrWhiteSpace($diff)) {
    $diff = (& git diff --text | Out-String)
  }

  # Sanitize diff to remove NUL bytes (which might strictly come from diffing binary files)
  if ($diff) {
      $diff = $diff.Replace("`0", "")
  }

  [System.IO.File]::AppendAllText($Path, $diff, $utf8NoBom)

  # Verify no NUL bytes
  $bytes = [System.IO.File]::ReadAllBytes($Path)
  if ($bytes -contains 0) {
    throw "updatedifflog.md contains NUL bytes (encoding mix). Do not use >>, Add-Content, Set-Content."
  }

  # Mirror to legacy path for backward compatibility
  if ($Path -match "build_docs[\\/]evidence[\\/]updatedifflog\.md$") {
      if (-not (Test-Path "evidence")) {
          New-Item -ItemType Directory -Force -Path "evidence" | Out-Null
      }
      Copy-Item -Path $Path -Destination "evidence/updatedifflog.md" -Force
  }
}
finally {
  $ConfirmPreference = $oldConfirm
}
