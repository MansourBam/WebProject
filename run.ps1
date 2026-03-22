# Run University Management App
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

# Activate venv and run - browser opens after server starts
& "$scriptDir\.venv\Scripts\Activate.ps1"

# Open browser in 4 seconds (in background)
Start-Job -ScriptBlock {
    Start-Sleep -Seconds 4
    Start-Process "http://127.0.0.1:5001"
} | Out-Null

Write-Host "Starting server... Browser will open at http://127.0.0.1:5001" -ForegroundColor Cyan
python app.py
