@echo off
title CyberWatch Backend - KEEP THIS OPEN
color 0B
cls
echo.
echo  ============================================
echo   CyberWatch Backend API
echo   Port: 8000
echo   DO NOT CLOSE THIS WINDOW
echo  ============================================
echo.
cd /d "c:\Users\gagan\Desktop\Cybersecurity_Technology_Package_Hackathon\backend"
".venv\Scripts\uvicorn.exe" app.main:app --host 0.0.0.0 --port 8000 --reload
echo.
pause
