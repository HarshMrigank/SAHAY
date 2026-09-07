Write-Host "Starting SAHAY Support System..."
Write-Host "==============================="

# Start backend
Write-Host "Starting FastAPI backend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd backend; if (!(Test-Path venv)) { python -m venv venv }; .\venv\Scripts\activate; pip install -r requirements.txt; uvicorn app.main:app --reload --port 8000"

# Start frontend
Write-Host "Starting Next.js frontend..."
Start-Process powershell -ArgumentList "-NoExit", "-Command", "cd frontend; npm run dev"

Write-Host "==============================="
Write-Host "Frontend running on http://localhost:3000"
Write-Host "Backend running on http://localhost:8000"
