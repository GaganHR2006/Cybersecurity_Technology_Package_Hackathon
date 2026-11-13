@echo off
title Deploy AcmeCorp to Vercel
color 0B
cls
echo.
echo ===================================================
echo   Deploy AcmeCorp Company Portal to Vercel
echo ===================================================
echo.
echo  This will deploy the vercel-site folder to Vercel.
echo  If not logged in, Vercel will prompt you in your browser.
echo.
pause
cd /d "c:\Users\gagan\Desktop\Cybersecurity_Technology_Package_Hackathon\vercel-site"
npx --yes vercel
echo.
echo ===================================================
echo  To deploy to production directly, run:
echo    npx --yes vercel --prod
echo ===================================================
echo.
pause
