@echo off
setlocal
cd /d "%~dp0"
if not exist "main.py" goto bad_folder
if not exist ".venv\Scripts\python.exe" goto no_venv
".venv\Scripts\python.exe" -m PyInstaller --noconfirm --clean --onefile --windowed --name Win11TrafficWidget main.py
if errorlevel 1 goto build_failed
echo Built: dist\Win11TrafficWidget.exe
pause
exit /b 0
:bad_folder
echo main.py not found. Extract the whole ZIP to a normal folder first.
pause
exit /b 1
:no_venv
echo Run start.cmd once before building the EXE.
pause
exit /b 1
:build_failed
echo EXE build failed. Copy the error messages above.
pause
exit /b 1
