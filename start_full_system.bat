@echo off
echo Starting Claimwise Full System...

echo.
echo [1/2] Starting Backend Server...
start "Claimwise Backend" cmd /k "cd backend && python -m uvicorn app.main:app --reload --port 8000"

echo Waiting for backend to start...
timeout /t 5 /nobreak >nul

echo.
echo [2/2] Starting Frontend...
start "Claimwise Frontend" cmd /k "cd frontend && streamlit run streamlit_app.py"

echo.
echo ✅ Claimwise system is starting!
echo Backend: http://localhost:8000
echo Frontend: http://localhost:8501
echo.
pause
