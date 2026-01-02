@echo off
echo ====================================
echo   PyService - Starting Server...
echo ====================================
echo.

cd /d "c:\Users\MERT\Desktop\servicenow python project\pyservice"

REM Check if virtual environment exists
if exist "env\Scripts\activate.bat" (
    call env\Scripts\activate.bat
    echo Virtual environment activated.
) else (
    echo No virtual environment found, using system Python.
)

echo.
echo Starting Django server on http://localhost:8000
echo Press Ctrl+C to stop the server.
echo.

start http://localhost:8000

python manage.py runserver 0.0.0.0:8000

pause
