@echo off
title InfoShield server (keep this window open)
cd /d "%~dp0backend"

if not exist venv\Scripts\activate.bat (
  echo.
  echo Setup not done yet. Please follow the setup steps first:
  echo   python -m venv venv
  echo   venv\Scripts\activate
  echo   pip install -r ..\requirements.txt
  echo   python train_model.py
  echo.
  pause
  exit /b
)

call venv\Scripts\activate.bat

rem open the browser after 4 seconds, once the server has started
start "" cmd /c "timeout /t 4 >nul & start http://localhost:8000"

python -m uvicorn main:app
pause
