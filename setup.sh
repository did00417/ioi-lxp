#!/bin/bash

echo "=========================================="
echo "Python Virtual Environment Setup (Mac/Linux)"
echo "=========================================="

# 1. venv 폴더가 있는지 확인
if [ ! -d "venv" ]; then
    echo "[INFO] Creating virtual environment..."
    python3 -m venv venv
    
    if [ $? -ne 0 ]; then
        echo "[ERROR] Python3 is not installed or not in PATH."
        echo "Press enter to exit..."
        read
        exit 1
    fi
    echo "[SUCCESS] Virtual environment created."
else
    echo "[INFO] Virtual environment already exists."
fi

# 2. 가상환경 활성화 및 패키지 설치
echo "[INFO] Activating environment and installing packages..."
source venv/bin/activate

# pip 업그레이드
python -m pip install --upgrade pip

if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "[WARNING] requirements.txt not found. Skipping installation."
fi

echo "=========================================="
echo "Setup Complete! Virtual environment is active."
echo "Type 'exit' to close this session."
echo "=========================================="

$SHELL