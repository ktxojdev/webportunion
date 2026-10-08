@echo off
cd /d "%~dp0"
echo Deploying Nintendo WebAssembly Runtime to Vercel...
python deploy_to_vercel.py %*
pause
