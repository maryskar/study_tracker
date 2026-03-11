@echo off
setlocal

where python >nul 2>nul
if %errorlevel%==0 (
  python -m pip install -r requirements-dev.txt
  python -m pytest
  exit /b %errorlevel%
)

where py >nul 2>nul
if %errorlevel%==0 (
  py -m pip install -r requirements-dev.txt
  py -m pytest
  exit /b %errorlevel%
)

echo Python not found in PATH.
exit /b 1
