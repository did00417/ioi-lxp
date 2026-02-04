@echo off
setlocal
echo ==========================================
echo Python Virtual Environment Setup
echo ==========================================

:: 1. venv 폴더가 있는지 확인
if not exist venv (
    echo [INFO] Creating virtual environment...
    python -m venv venv
    if %errorlevel% neq 0 (
        echo [ERROR] Python is not installed or not in PATH.
        pause
        exit /b
    )
    echo [SUCCESS] Virtual environment created.
) else (
    echo [INFO] Virtual environment already exists.
)

:: 2. 가상환경 활성화 및 패키지 설치
echo [INFO] Activating environment and installing packages...
call venv\Scripts\activate

:: pip 자체를 최신 버전으로 업그레이드 (권장)
python -m pip install --upgrade pip

if exist requirements.txt (
    pip install -r requirements.txt
) else (
    echo [WARNING] requirements.txt not found. Skipping installation.
)

echo ==========================================
echo Setup Complete!
echo ==========================================
pause