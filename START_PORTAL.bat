@echo off
title AcmeCorp Portal - KEEP THIS OPEN
color 0A
cls
echo.
echo  ============================================
echo   AcmeCorp Employee Portal - DEMO TARGET
echo   Port: 5001
echo   DO NOT CLOSE THIS WINDOW
echo  ============================================
echo.
cd /d "c:\Users\gagan\Desktop\Cybersecurity_Technology_Package_Hackathon"
"backend\.venv\Scripts\python.exe" "demo_target\app.py"
echo.
echo  Flask stopped. Press any key to restart...
pause
