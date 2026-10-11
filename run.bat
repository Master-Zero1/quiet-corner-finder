@echo off
echo ===================================================
echo  Starting Quiet Corner Finder
echo ===================================================
set PYTHONPATH=%~dp0backend
python "%~dp0backend\seed_data.py"
python "%~dp0run.py"
pause
