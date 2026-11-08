@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

rem Chuyen thu muc hien hanh ve thu muc chua script
cd /d "%~dp0"

:main_menu
cls
echo ==========================================================
echo   CONG CU CHUYEN DOI FILE NEN ^<==^> HINH ANH PNG (BASE64)
echo ==========================================================
echo.
echo   [1] Chuyen file nen (zip/7z/rar/...) thanh file anh PNG
echo   [2] Chuyen file anh PNG thanh file nen goc
echo   [0] Thoat chuong trinh
echo.
echo ==========================================================
choice /c 120 /n /m "Bam phim lua chon [1/2/0]: "
set "key=!errorlevel!"

if "!key!"=="1" goto :encode_menu
if "!key!"=="2" goto :decode_menu
if "!key!"=="3" goto :exit_script
goto :main_menu

rem ==========================================================
rem 1. ENCODE: FILE NEN ==> ANH PNG
rem ==========================================================
:encode_menu
cls
echo ==========================================================
echo     CHUYEN DOI: FILE NEN ==^> HINH ANH PNG (ENCODE)
echo   (Ho tro: .zip, .7z, .rar, .tar, .gz, .tgz, .bz2, .xz, .cab, .iso)
echo ==========================================================
echo.

set "count=0"
for /f "delims=" %%F in ('dir /b /a-d *.zip *.7z *.rar *.tar *.gz *.tgz *.bz2 *.xz *.cab *.iso 2^>nul') do (
    set /a count+=1
    set "file_!count!=%%F"
    set "filename_!count!=%%~nF"
)

if !count!==0 (
    echo [THONG BAO] Khong tim thay file nen nao trong thu muc:
    echo             %cd%
    echo.
    echo Nhan phim bat ky de quay lai menu chinh...
    pause >nul
    goto :main_menu
)

set "ALL_KEYS=123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
set "CHOICE_KEYS="
for /l %%i in (1,1,!count!) do (
    set /a idx=%%i-1
    for %%k in (!idx!) do set "k=!ALL_KEYS:~%%k,1!"
    set "file_key_%%i=!k!"
    set "CHOICE_KEYS=!CHOICE_KEYS!!k!"
)
set "CHOICE_KEYS=!CHOICE_KEYS!0"

echo Danh sach file nen tim thay:
echo.
for /l %%i in (1,1,!count!) do (
    echo   [!file_key_%%i!] !file_%%i!
)
echo.
echo   [0] Quay lai menu chinh
echo ==========================================================
choice /c !CHOICE_KEYS! /n /m "Bam phim chon file [hoac 0 de quay lai]: "
set "sel=!errorlevel!"

set /a back_val=!count!+1
if "!sel!"=="!back_val!" goto :main_menu

set "SELECTED_FILE=!file_%sel%!"
set "BASE_NAME=!filename_%sel%!"

for /f "delims=" %%a in ('powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set "TIMESTAMP=%%a"
set "OUTPUT_FILE=!BASE_NAME!_!TIMESTAMP!.png"

echo.
echo [*] Dang chuyen doi "!SELECTED_FILE!" sang anh "!OUTPUT_FILE!" ...
echo     (File lon co the mat vai phut, vui long cho...)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Zip2Img_Encode.ps1" -InputFile "!SELECTED_FILE!" -OutputImage "!OUTPUT_FILE!"

if !errorlevel! neq 0 (
    echo.
    echo [THAT BAI] Co loi xay ra khi chuyen doi file!
    echo Nhan phim bat ky de tiep tuc...
    pause >nul
    goto :encode_menu
)

:post_action_encode
echo.
echo Hay chon thao tac tiep theo:
echo   [M] Mo thu muc chua file anh
echo   [B] Quay lai menu chon file nen
echo   [H] Quay ve trang chu (Menu chinh)
echo   [0] Thoat chuong trinh
echo ==========================================================
choice /c MBH0 /n /m "Bam phim lua chon [M/B/H/0]: "
set "act=!errorlevel!"

if "!act!"=="1" (
    explorer /select,"!OUTPUT_FILE!"
    goto :post_action_encode
)
if "!act!"=="2" goto :encode_menu
if "!act!"=="3" goto :main_menu
if "!act!"=="4" goto :exit_script
goto :post_action_encode

rem ==========================================================
rem 2. DECODE: ANH PNG ==> FILE NEN GOC
rem ==========================================================
:decode_menu
cls
echo ==========================================================
echo     CHUYEN DOI: HINH ANH PNG ==^> FILE NEN GOC (DECODE)
echo ==========================================================
echo.

set "count=0"
for /f "delims=" %%F in ('dir /b /a-d *.png 2^>nul') do (
    set /a count+=1
    set "file_!count!=%%F"
    set "filename_!count!=%%~nF"
)

if !count!==0 (
    echo [THONG BAO] Khong tim thay file .png nao trong thu muc:
    echo             %cd%
    echo.
    echo Nhan phim bat ky de quay lai menu chinh...
    pause >nul
    goto :main_menu
)

set "ALL_KEYS=123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
set "CHOICE_KEYS="
for /l %%i in (1,1,!count!) do (
    set /a idx=%%i-1
    for %%k in (!idx!) do set "k=!ALL_KEYS:~%%k,1!"
    set "file_key_%%i=!k!"
    set "CHOICE_KEYS=!CHOICE_KEYS!!k!"
)
set "CHOICE_KEYS=!CHOICE_KEYS!0"

echo Danh sach file anh tim thay:
echo.
for /l %%i in (1,1,!count!) do (
    echo   [!file_key_%%i!] !file_%%i!
)
echo.
echo   [0] Quay lai menu chinh
echo ==========================================================
choice /c !CHOICE_KEYS! /n /m "Bam phim chon file [hoac 0 de quay lai]: "
set "sel=!errorlevel!"

set /a back_val=!count!+1
if "!sel!"=="!back_val!" goto :main_menu

set "SELECTED_FILE=!file_%sel%!"
set "BASE_NAME=!filename_%sel%!"

echo.
echo ==========================================================
echo Chon dinh dang file nen can phuc hoi:
echo   [1] .zip (Mac dinh - Pho bien nhat)
echo   [2] .7z  (Dinh dang 7-Zip)
echo   [3] .rar (Dinh dang WinRAR)
echo   [4] .tar.gz / .tar
echo   [0] Quay lai
echo ==========================================================
choice /c 12340 /n /m "Bam phim chon dinh dang [1/2/3/4/0]: "
set "ext_choice=!errorlevel!"

for /f "delims=" %%a in ('powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set "TIMESTAMP=%%a"

if "!ext_choice!"=="1" set "OUTPUT_FILE=!BASE_NAME!_!TIMESTAMP!.zip"
if "!ext_choice!"=="2" set "OUTPUT_FILE=!BASE_NAME!_!TIMESTAMP!.7z"
if "!ext_choice!"=="3" set "OUTPUT_FILE=!BASE_NAME!_!TIMESTAMP!.rar"
if "!ext_choice!"=="4" set "OUTPUT_FILE=!BASE_NAME!_!TIMESTAMP!.tar.gz"
if "!ext_choice!"=="5" goto :decode_menu

echo.
echo [*] Dang khoi phuc "!SELECTED_FILE!" sang "!OUTPUT_FILE!" ...
echo     (File lon co the mat vai phut, vui long cho...)
echo.
powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0Zip2Img_Decode.ps1" -InputImage "!SELECTED_FILE!" -OutputFile "!OUTPUT_FILE!"

if !errorlevel! neq 0 (
    echo.
    echo [THAT BAI] Co loi xay ra khi khoi phuc file!
    echo Nhan phim bat ky de tiep tuc...
    pause >nul
    goto :decode_menu
)

:post_action_decode
echo.
echo Hay chon thao tac tiep theo:
echo   [M] Mo thu muc chua file da khoi phuc
echo   [B] Quay lai menu chon file anh
echo   [H] Quay ve trang chu (Menu chinh)
echo   [0] Thoat chuong trinh
echo ==========================================================
choice /c MBH0 /n /m "Bam phim lua chon [M/B/H/0]: "
set "act=!errorlevel!"

if "!act!"=="1" (
    explorer /select,"!OUTPUT_FILE!"
    goto :post_action_decode
)
if "!act!"=="2" goto :decode_menu
if "!act!"=="3" goto :main_menu
if "!act!"=="4" goto :exit_script
goto :post_action_decode

rem ==========================================================
rem THOAT CHUONG TRINH
rem ==========================================================
:exit_script
cls
echo Tam biet!
exit /b 0
