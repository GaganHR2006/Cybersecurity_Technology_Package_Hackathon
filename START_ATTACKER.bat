@echo off
title Brute Force Attacker
color 0C
cls
echo.
echo  ============================================
echo   CyberWatch Demo - Brute Force Attacker
echo   Target: http://localhost:5001
echo   FOR DEMO PURPOSES ONLY
echo  ============================================
echo.
echo  Make sure START_PORTAL.bat and START_BACKEND.bat are running first!
echo.
pause
cd /d "c:\Users\gagan\Desktop\Cybersecurity_Technology_Package_Hackathon"
"backend\.venv\Scripts\python.exe" "demo_attacker\brute_force.py"
echo.
echo  Attack complete. Press any key to run again...
pause
goto :eof
