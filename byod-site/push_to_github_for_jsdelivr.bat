@echo off
setlocal
echo ===================================================
echo  Deploy to GitHub (Serves directly via jsDelivr)
echo ===================================================
echo.
set /p REPO_URL="Enter your GitHub Repository HTTPS URL (e.g. https://github.com/username/my-site.git): "

if "%REPO_URL%"=="" (
    echo Error: No repository URL provided.
    pause
    exit /b 1
)

git init
git add .
git commit -m "Deploy site for jsDelivr"
git branch -M main
git remote remove origin >nul 2>&1
git remote add origin %REPO_URL%
git push -u origin main --force

echo.
echo ===================================================
echo Upload complete!
echo Your files are now mirrored and available via jsDelivr at:
echo https://cdn.jsdelivr.net/gh/<username>/<repo>@main/index.html
echo ===================================================
pause
