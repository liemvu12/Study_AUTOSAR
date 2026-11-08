@echo off
chcp 65001 >nul
title 1-Click Backup Study_AUTOSAR (GitLab & Base64 TXT)
cd /d "%~dp0"

echo ==========================================================
echo   1-CLICK BACKUP (Study_AUTOSAR)
echo   Pham vi: docs, myProject, tools, .agents, root scripts
echo   Loai tru: as, BackUp, .git, .vscode
echo ==========================================================
echo.

powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0BackUp\backup_daily.ps1"

echo.
echo Nhan phim bat ky de dong cua so nay...
pause >nul
exit /b 0
