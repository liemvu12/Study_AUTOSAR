@echo off
chcp 65001 >nul
title 1-Click ARXML Tree View Converter
cd /d "%~dp0"

echo ==========================================================
echo   CONVERT ARXML TO ARXML TREE VIEW FORMAT
echo ==========================================================
python tools\convert_arxml_tree.py %*

echo.
echo Hoan tat! Bay gio ban co the mo cac file *_tree.arxml tren VS Code ARXML Tree View.
echo Nhan phim bat ky de dong...
pause >nul
exit /b 0
