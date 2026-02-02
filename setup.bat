@echo off
echo ==========================================
echo Python Virtual Environment Setup
echo ==========================================

call venv\Scripts\activate

echo Installing packages...
pip install -r requirements.txt

echo ==========================================
echo Setup Complete!
echo ==========================================
pause