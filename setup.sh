#!/bin/bash
echo ==========================================
echo Python Virtual Environment Setup
echo ==========================================

source venv/Scripts/activate

echo "Installing packages..."
pip install -r requirements.txt

echo ==========================================
echo Setup Complete!
echo ==========================================