# GoalPredictor.AI - Quick Start
# Usage: .\run.ps1

Write-Host "Starting GoalPredictor.AI..." -ForegroundColor Green

# Activate virtual environment if exists
if (Test-Path "venv\Scripts\Activate.ps1") {
    Write-Host "Activating virtual environment..." -ForegroundColor Cyan
    & "venv\Scripts\Activate.ps1"
}

# Check .env file
if (-not (Test-Path ".env")) {
    Write-Host "WARNING: .env file not found!" -ForegroundColor Yellow
    Write-Host "Creating .env from template..." -ForegroundColor Yellow
    Copy-Item .env.example .env
    Write-Host "Please edit .env and add your API keys" -ForegroundColor Yellow
    exit
}

# Start Flask application
Write-Host ""
Write-Host "Starting Flask app on http://localhost:5000" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop" -ForegroundColor Yellow
Write-Host ""

python app.py
