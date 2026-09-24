@echo off
setlocal
cd /d "%~dp0"
if not exist "main.py" goto bad_folder
if not exist ".venv\Scripts\python.exe" (
  set "PY_CMD="
  py -3 -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>nul
  if not errorlevel 1 (
    py -3 -m venv .venv
  ) else (
    python -c "import sys; assert sys.version_info >= (3, 11)" >nul 2>nul
    if errorlevel 1 goto no_python
    python -m venv .venv
  )
  if errorlevel 1 goto setup_failed
)
".venv\Scripts\python.exe" -c "import PySide6, psutil; import winrt.windows.networking.connectivity" >nul 2>nul
if errorlevel 1 (
  echo Installing dependencies. Please wait...
  ".venv\Scripts\python.exe" -m pip install -r requirements-windows.txt
  if errorlevel 1 goto setup_failed
)
echo Starting traffic widget. If it exits, errors will appear below.
".venv\Scripts\python.exe" main.py
if errorlevel 1 goto run_failed
exit /b 0
:bad_folder
echo main.py not found. Extract the whole ZIP to a normal folder first.
pause
exit /b 1
:no_python
echo No supported Python found. Install Python 3.11 or newer from python.org.
pause
exit /b 1
:setup_failed
echo Setup failed. Check Python and network connectivity.
pause
exit /b 1
:run_failed
echo App failed to start. Copy the error messages above.
pause
exit /b 1
