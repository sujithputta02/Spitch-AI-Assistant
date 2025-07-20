@echo off
REM Activate the virtual environment
g_env\Scripts\activate
REM Start the backend in a new command window
start cmd /k "python main.py"
REM Open the landing page in the default browser
start "" "www\landing.html" 