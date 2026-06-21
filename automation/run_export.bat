@echo off
setlocal
pushd "%~dp0.."
echo Running export...
python scripts\export_for_powerbi.py
if errorlevel 1 echo Export failed.
popd
endlocal
