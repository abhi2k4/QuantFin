@echo off
REM Quick training test script

echo Activating virtual environment...
call .venv\Scripts\activate.bat

echo.
echo Running training test with RELIANCE and linear_reg model...
echo This will take about 30 seconds...
echo.

python scripts\train_simple.py --symbols RELIANCE --models linear_reg --quick --save-summary

echo.
echo Done! Check training_summary.json for results.
pause
