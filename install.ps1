# Ai-token install script for Windows (PowerShell)
# Run from the repo directory: .\install.ps1
$ErrorActionPreference = "Stop"

$RepoDir  = Split-Path -Parent $MyInvocation.MyCommand.Path
$CaiDir   = Join-Path $env:USERPROFILE ".cai"
$LibDir   = Join-Path $CaiDir "lib"
$BinDir   = Join-Path $CaiDir "bin"

New-Item -ItemType Directory -Force -Path $LibDir | Out-Null
New-Item -ItemType Directory -Force -Path $BinDir | Out-Null

# Save real claude path BEFORE we shadow it.
# Skip on re-install so we never overwrite with our own wrapper.
$SavedPath = Join-Path $CaiDir "real_claude"
if (-not (Test-Path $SavedPath)) {
    $RealClaude = (Get-Command claude -ErrorAction SilentlyContinue)
    if (-not $RealClaude) {
        Write-Error "claude not found in PATH. Install Claude Code CLI first: https://claude.ai/download"
        exit 1
    }
    $RealClaude.Source | Set-Content $SavedPath -Encoding UTF8
    Write-Host "  Real claude saved: $($RealClaude.Source)"
}

# Copy router + modules to stable location
Copy-Item "$RepoDir\claude"        "$LibDir\claude"        -Force
Copy-Item "$RepoDir\classifier.py" "$LibDir\classifier.py" -Force
Copy-Item "$RepoDir\logger.py"     "$LibDir\logger.py"     -Force

# Write claude.cmd shim — PowerShell and CMD both pick up .cmd files on PATH
$Shim = "@echo off`r`npython `"$LibDir\claude`" %*"
[System.IO.File]::WriteAllText("$BinDir\claude.cmd", $Shim)

# Add BinDir to user PATH if missing
$UserPath = [Environment]::GetEnvironmentVariable("PATH", "User")
if ($UserPath -notlike "*$BinDir*") {
    [Environment]::SetEnvironmentVariable("PATH", "$BinDir;$UserPath", "User")
    Write-Host "  Added $BinDir to user PATH"
    Write-Host "  Restart PowerShell (or run: `$env:PATH = `"$BinDir;`$env:PATH`")"
}

Write-Host ""
Write-Host "OK claude router installed."
Write-Host ""
Write-Host "  Usage (unchanged - just type claude as normal):"
Write-Host "    claude `"check apache logs for errors`"     -> Haiku (cheap)"
Write-Host "    claude `"write RCA report for incident`"    -> Sonnet"
Write-Host "    claude --stats                              -> 7-day savings"
Write-Host "    claude --dry-run `"your task`"               -> preview routing"
Write-Host "    claude --model sonnet `"task`"               -> manual override"
