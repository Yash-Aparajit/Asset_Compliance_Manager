@echo off
cd /d "%~dp0"

echo ================================
echo   Starting ACM Application
echo ================================
echo.

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Running ACM Server...
echo Press CTRL+C to stop.
echo.

python app.py

pause

