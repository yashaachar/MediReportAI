@echo off
echo.
echo  ==========================================
echo   MediReport AI — Frontend Server
echo   Open: http://127.0.0.1:3000
echo  ==========================================
echo.
py -3.12 -m http.server 3000 --directory "%~dp0frontend"
pause
