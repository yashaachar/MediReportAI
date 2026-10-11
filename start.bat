@echo off
echo.
echo  ==========================================
echo   MediReport AI — Starting Backend Server
echo  ==========================================
echo.
echo  Frontend: http://127.0.0.1:8000
echo  API docs: http://127.0.0.1:8000/docs
echo.
cd /d "%~dp0src"
py -3.12 -m uvicorn api:app --host 127.0.0.1 --port 8000 --reload
pause
