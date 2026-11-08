@echo off
chcp 65001 >nul
setlocal EnableDelayedExpansion

rem Chuyen thu muc hien hanh ve thu muc chua script
cd /d "%~dp0"

:main_menu
cls
echo ==========================================================
echo   CONG CU CHUYEN DOI FILE NEN (ZIP, 7Z, RAR...) ^<==^> TXT/BAT
echo ==========================================================
echo.
echo   [1] Chuyen file nen thanh .txt (Encode Base64, co the chia nho ~4.9MB)
echo   [2] Chuyen file nen thanh .bat (Self-Extracting tu dong bung)
echo   [3] Ghep cac file .txt da chia nho thanh 1 file hoan chinh
echo   [4] Chuyen file .txt thanh file nen goc (Decode Base64)
echo   [0] Thoat chuong trinh
echo.
echo ==========================================================
choice /c 12340 /n /m "Bam phim lua chon [1/2/3/4/0]: "
set "key=!errorlevel!"

if "!key!"=="1" goto :compress_to_txt_menu
if "!key!"=="2" goto :compress_to_bat_menu
if "!key!"=="3" goto :merge_txt_menu
if "!key!"=="4" goto :txt_to_compress_menu
if "!key!"=="5" goto :exit_script
goto :main_menu

rem ==========================================================
rem 1. CHUYEN DOI FILE NEN THANH .TXT (ENCODE)
rem ==========================================================
:compress_to_txt_menu
cls
echo ==========================================================
echo        CHUYEN DOI: FILE NEN ==^> .TXT (ENCODE BASE64)
echo   (Ho tro: .zip, .7z, .rar, .tar, .gz, .tgz, .bz2, .xz, .cab, .iso)
echo ==========================================================
echo.

set "count=0"
for /f "delims=" %%F in ('dir /b /a-d *.zip *.7z *.rar *.tar *.gz *.tgz *.bz2 *.xz *.cab *.iso 2^>nul') do (
    set /a count+=1
    set "file_!count!=%%F"
    set "filename_!count!=%%~nF"
    set "fileext_!count!=%%~xF"
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
set "EXT_NAME=!fileext_%sel%!"

rem Lay timestamp hien tai (YYYYMMDD_HHmmss)
for /f "delims=" %%a in ('powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set "TIMESTAMP=%%a"

rem Ten file output giu nguyen duoi nen goc truoc duoi .txt de de phuc hoi
set "OUTPUT_FILE=!BASE_NAME!_!TIMESTAMP!!EXT_NAME!.txt"

echo.
echo [*] Dang ma hoa "!SELECTED_FILE!" sang "!OUTPUT_FILE!" ...
certutil -f -encode "!SELECTED_FILE!" "!OUTPUT_FILE!" >nul 2>&1

if !errorlevel! neq 0 (
    echo.
    echo [THAT BAI] Co loi xay ra khi chuyen doi file!
    echo Nhan phim bat ky de tiep tuc...
    pause >nul
    goto :compress_to_txt_menu
)

echo.
echo ==========================================================
echo [THANH CONG] Da tao file text thanh cong!
echo   - File goc   : !SELECTED_FILE!
echo   - File output: !OUTPUT_FILE!
echo ==========================================================

:post_action_txt
echo.
echo Hay chon thao tac tiep theo:
echo   [S] Chia nho file thanh cac phan ~4.9MB
echo   [C] Copy noi dung file .txt vao Clipboard
echo   [B] Quay lai menu chon file nen
echo   [H] Quay ve trang chu (Menu chinh)
echo   [0] Thoat chuong trinh
echo ==========================================================
choice /c SCBH0 /n /m "Bam phim lua chon [S/C/B/H/0]: "
set "act=!errorlevel!"

if "!act!"=="1" goto :do_split_now
if "!act!"=="2" (
    clip < "!OUTPUT_FILE!"
    echo.
    echo [OK] Da nap toan bo noi dung file "!OUTPUT_FILE!" vao Clipboard!
    echo      (Ban chi can sang email va bam Ctrl + V de dan)
    goto :post_action_txt
)
if "!act!"=="3" goto :compress_to_txt_menu
if "!act!"=="4" goto :main_menu
if "!act!"=="5" goto :exit_script
goto :post_action_txt

rem ----------------------------------------------------------
rem Chia nho file .txt thanh cac phan ~4.9MB (de gui qua email/chat)
rem ----------------------------------------------------------
:do_split_now
set "SPLIT_PREFIX=!OUTPUT_FILE:~0,-4!"
set "SPLIT_CHUNK_BYTES=5138022"
set "SPLIT_INPUT=!OUTPUT_FILE!"
echo.
echo [*] Dang chia nho "!OUTPUT_FILE!" thanh cac phan ~4.9MB ...
echo.
powershell -NoProfile -Command "$ErrorActionPreference='Stop'; $inFile=$env:SPLIT_INPUT; $prefix=$env:SPLIT_PREFIX; $chunkSize=[int64]$env:SPLIT_CHUNK_BYTES; $fs=[System.IO.File]::OpenRead($inFile); $buffer=New-Object byte[] $chunkSize; $idx=1; try { while(($read=$fs.Read($buffer,0,$buffer.Length)) -gt 0) { $partName=('{0}.part{1:D3}.txt' -f $prefix,$idx); [System.IO.File]::WriteAllBytes($partName,$buffer[0..($read-1)]); Write-Host ('  - Da tao: ' + $partName + ' (' + [math]::Round($read/1MB,2) + ' MB)'); $idx++ } } finally { $fs.Close() }"

if !errorlevel! neq 0 (
    echo.
    echo [THAT BAI] Co loi xay ra khi chia nho file!
    echo Nhan phim bat ky de tiep tuc...
    pause >nul
    goto :post_action_txt
)

set "TOTAL_PARTS=0"
for /f %%N in ('dir /b /a-d "!SPLIT_PREFIX!.part*.txt" 2^>nul ^| find /c /v ""') do set "TOTAL_PARTS=%%N"

echo.
echo ==========================================================
echo [THANH CONG] Da chia file thanh !TOTAL_PARTS! phan (~4.9MB/phan)!
echo   Mau ten file: !SPLIT_PREFIX!.part001.txt , part002.txt, ...
echo   Khi can phuc hoi: dung muc [3] Ghep file de ghep lai truoc khi giai ma.
echo ==========================================================
echo.
pause >nul
goto :post_action_txt

rem ==========================================================
rem 2. CHUYEN DOI FILE NEN THANH .BAT TU DONG BUNG
rem ==========================================================
:compress_to_bat_menu
cls
echo ==========================================================
echo        CHUYEN DOI: FILE NEN ==^> .BAT TU DONG GIAI NEN
echo   (Ho tro: .zip, .7z, .rar, .tar, .gz, .tgz, .bz2, .xz, .cab, .iso)
echo ==========================================================
echo.
echo   [1] Chuyen 1 file duy nhat
echo   [2] Chuyen TAT CA file nen (Hang loat)
echo   [0] Quay lai menu chinh
echo.
echo ==========================================================
choice /c 120 /n /m "Bam phim lua chon [1/2/0]: "
set "bat_mode=!errorlevel!"

if "!bat_mode!"=="1" goto :compress_to_bat_single
if "!bat_mode!"=="2" goto :compress_to_bat_all
if "!bat_mode!"=="3" goto :main_menu
goto :compress_to_bat_menu

rem ----------------------------------------------------------
rem 2.1 Chuyen 1 file nen thanh .bat
rem ----------------------------------------------------------
:compress_to_bat_single
cls
echo ==========================================================
echo        CHUYEN 1 FILE NEN ==^> .BAT TU DONG BUNG
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
    echo Nhan phim bat ky de quay lai menu...
    pause >nul
    goto :compress_to_bat_menu
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
echo   [0] Quay lai menu truoc
echo ==========================================================
choice /c !CHOICE_KEYS! /n /m "Bam phim chon file [hoac 0 de quay lai]: "
set "sel=!errorlevel!"

set /a back_val=!count!+1
if "!sel!"=="!back_val!" goto :compress_to_bat_menu

set "SELECTED_FILE=!file_%sel%!"
set "BASE_NAME=!filename_%sel%!"

for /f "delims=" %%a in ('powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set "TIMESTAMP=%%a"
set "OUTPUT_FILE=!BASE_NAME!_!TIMESTAMP!.bat"

echo.
echo [*] Dang tao file .bat tu dong bung "!OUTPUT_FILE!" ...
call :generate_bat "!SELECTED_FILE!" "!BASE_NAME!" "!TIMESTAMP!"

echo.
echo ==========================================================
echo [THANH CONG] Da tao file .bat tu bung thanh cong!
echo   - File goc   : !SELECTED_FILE!
echo   - File output: !OUTPUT_FILE!
echo ==========================================================

:post_action_bat_single
echo.
echo Hay chon thao tac tiep theo:
echo   [C] Copy noi dung file .bat vao Clipboard (Luu lich su Win+V)
echo   [B] Quay lai menu chon file nen
echo   [H] Quay ve trang chu (Menu chinh)
echo   [0] Thoat chuong trinh
echo ==========================================================
choice /c CBH0 /n /m "Bam phim lua chon [C/B/H/0]: "
set "act=!errorlevel!"

if "!act!"=="1" (
    clip < "!OUTPUT_FILE!"
    echo.
    echo [OK] Da copy toan bo noi dung file "!OUTPUT_FILE!" vao Clipboard!
    echo      Dau file co ten: [::!SELECTED_FILE!]
    echo      Ban co the bam to hop phim [Win + V] de kiem tra lich su.
    goto :post_action_bat_single
)
if "!act!"=="2" goto :compress_to_bat_single
if "!act!"=="3" goto :main_menu
if "!act!"=="4" goto :exit_script
goto :post_action_bat_single

rem ----------------------------------------------------------
rem 2.2 Chuyen TAT CA file nen thanh .bat (Hang loat)
rem ----------------------------------------------------------
:compress_to_bat_all
cls
echo ==========================================================
echo     CHUYEN TAT CA FILE NEN ==^> .BAT (HANG LOAT)
echo ==========================================================
echo.

set "count=0"
for /f "delims=" %%F in ('dir /b /a-d *.zip *.7z *.rar *.tar *.gz *.tgz *.bz2 *.xz *.cab *.iso 2^>nul') do (
    set /a count+=1
)

if !count!==0 (
    echo [THONG BAO] Khong tim thay file nen nao trong thu muc:
    echo             %cd%
    echo.
    echo Nhan phim bat ky de quay lai menu...
    pause >nul
    goto :compress_to_bat_menu
)

echo Tim thay !count! file nen. Bat dau chuyen doi hang loat...
echo.

for /f "delims=" %%a in ('powershell -NoProfile -Command "Get-Date -Format 'yyyyMMdd_HHmmss'"') do set "TIMESTAMP=%%a"

set "idx=0"
for /f "delims=" %%F in ('dir /b /a-d *.zip *.7z *.rar *.tar *.gz *.tgz *.bz2 *.xz *.cab *.iso 2^>nul') do (
    set /a idx+=1
    echo   [!idx!/!count!] Dang tao "%%~nF_!TIMESTAMP!.bat" tu "%%F" ...
    call :generate_bat "%%F" "%%~nF" "!TIMESTAMP!"
)

echo.
echo ==========================================================
echo [HOAN TAT] Da chuyen doi xong tat ca !count! file sang .bat!
echo ==========================================================

:post_action_bat_all
echo.
echo Hay chon thao tac tiep theo:
echo   [C] Copy TAT CA cac file vao Clipboard (Day lan luot vao Win+V)
echo   [B] Quay lai menu truoc
echo   [H] Quay ve trang chu (Menu chinh)
echo   [0] Thoat chuong trinh
echo ==========================================================
choice /c CBH0 /n /m "Bam phim lua chon [C/B/H/0]: "
set "act=!errorlevel!"

if "!act!"=="1" (
    echo.
    echo [*] Dang lan luot nap cac file vao Clipboard History...
    set "c_idx=0"
    for /f "delims=" %%F in ('dir /b /a-d *.zip *.7z *.rar *.tar *.gz *.tgz *.bz2 *.xz *.cab *.iso 2^>nul') do (
        set /a c_idx+=1
        set "TARGET_FILE=%%~nF_!TIMESTAMP!.bat"
        if exist "!TARGET_FILE!" (
            clip < "!TARGET_FILE!"
            echo   [OK] Da nap [!c_idx!/!count!]: !TARGET_FILE!
            powershell -NoProfile -Command "Start-Sleep -Milliseconds 400" >nul 2>&1
        )
    )
    echo.
    echo ==========================================================
    echo [THANH CONG] Da day toan bo !count! file vao lich su Clipboard!
    echo Ban co the bam to hop phim [Win + V] de kiem tra.
    echo Dong dau tien moi muc la ten file goc [::TenFile] de de kiem soat!
    echo ==========================================================
    goto :post_action_bat_all
)
if "!act!"=="2" goto :compress_to_bat_menu
if "!act!"=="3" goto :main_menu
if "!act!"=="4" goto :exit_script
goto :post_action_bat_all

rem ==========================================================
rem SUBROUTINE: Tao 1 file .bat tu dong bung file nen
rem ==========================================================
:generate_bat
set "GEN_FILE=%~1"
set "GEN_BASE=%~2"
set "GEN_TS=%~3"
set "GEN_OUT=%GEN_BASE%_%GEN_TS%.bat"

echo ::%GEN_FILE% > "%GEN_OUT%"
echo :: ========================================================== >> "%GEN_OUT%"
echo :: FILE: %GEN_OUT% >> "%GEN_OUT%"
echo :: Tu dong giai nen ra: %GEN_FILE% >> "%GEN_OUT%"
echo :: ========================================================== >> "%GEN_OUT%"
echo @echo off >> "%GEN_OUT%"
echo setlocal >> "%GEN_OUT%"
echo cd /d "%%~dp0" >> "%GEN_OUT%"
echo echo ========================================================== >> "%GEN_OUT%"
echo echo Dang tu dong khoi phuc file: %GEN_FILE% ... >> "%GEN_OUT%"
echo echo ========================================================== >> "%GEN_OUT%"
echo for /f "tokens=1 delims=:" %%%%n in ('findstr -n "^-----BEGIN CERTIFICATE-----" "%%~f0"') do set /a skip=%%%%n-1 >> "%GEN_OUT%"
echo more +%%skip%% "%%~f0" ^> "%%temp%%\temp_%%~nx0.b64" >> "%GEN_OUT%"
echo certutil -f -decode "%%temp%%\temp_%%~nx0.b64" "%GEN_FILE%" ^>nul 2^>^&1 >> "%GEN_OUT%"
echo del "%%temp%%\temp_%%~nx0.b64" ^>nul 2^>^&1 >> "%GEN_OUT%"
echo if exist "%GEN_FILE%" ( >> "%GEN_OUT%"
echo     echo. >> "%GEN_OUT%"
echo     echo [THANH CONG] Da phuc hoi file "%GEN_FILE%" thanh cong! >> "%GEN_OUT%"
echo ) else ( >> "%GEN_OUT%"
echo     echo. >> "%GEN_OUT%"
echo     echo [LOI] Khong the phuc hoi file! >> "%GEN_OUT%"
echo ) >> "%GEN_OUT%"
echo echo. >> "%GEN_OUT%"
echo pause >> "%GEN_OUT%"
echo exit /b 0 >> "%GEN_OUT%"

certutil -f -encode "%GEN_FILE%" "%temp%\temp_b64_%GEN_BASE%.tmp" >nul 2>&1
type "%temp%\temp_b64_%GEN_BASE%.tmp" >> "%GEN_OUT%"
del "%temp%\temp_b64_%GEN_BASE%.tmp" >nul 2>&1
exit /b 0

rem ==========================================================
rem 3. GHEP CAC FILE .TXT DA CHIA NHO THANH 1 FILE HOAN CHINH
rem ==========================================================
:merge_txt_menu
cls
echo ==========================================================
echo   GHEP CAC FILE .TXT DA CHIA NHO THANH 1 FILE HOAN CHINH
echo ==========================================================
echo.

if exist "%TEMP%\fc_prefixes.tmp" del "%TEMP%\fc_prefixes.tmp" >nul 2>&1
powershell -NoProfile -Command "Get-ChildItem -File -Filter '*.part*.txt' -ErrorAction SilentlyContinue | ForEach-Object { $_.Name -replace '\.part\d{3}\.txt$','' } | Sort-Object -Unique" > "%TEMP%\fc_prefixes.tmp" 2>nul

set "count=0"
for /f "usebackq delims=" %%F in ("%TEMP%\fc_prefixes.tmp") do (
    set /a count+=1
    set "file_!count!=%%F"
)
del "%TEMP%\fc_prefixes.tmp" >nul 2>&1

if !count!==0 (
    echo [THONG BAO] Khong tim thay bo file da chia nho ^(*.part*.txt^) nao trong thu muc:
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

echo Danh sach bo file da chia nho tim thay:
echo.
for /l %%i in (1,1,!count!) do (
    set "PARTCOUNT_TMP=0"
    for /f %%N in ('dir /b /a-d "!file_%%i!.part*.txt" 2^>nul ^| find /c /v ""') do set "PARTCOUNT_TMP=%%N"
    echo   [!file_key_%%i!] !file_%%i!  ^(!PARTCOUNT_TMP! phan^)
)
echo.
echo   [0] Quay lai menu chinh
echo ==========================================================
choice /c !CHOICE_KEYS! /n /m "Bam phim chon bo file can ghep [hoac 0 de quay lai]: "
set "sel=!errorlevel!"

set /a back_val=!count!+1
if "!sel!"=="!back_val!" goto :main_menu

set "MERGE_PREFIX=!file_%sel%!"
set "MERGE_OUTPUT=!MERGE_PREFIX!.txt"

if exist "!MERGE_OUTPUT!" (
    echo.
    echo [CANH BAO] File "!MERGE_OUTPUT!" da ton tai!
    choice /c YN /n /m "Ban co muon GHI DE len file nay khong? [Y/N]: "
    if "!errorlevel!"=="2" goto :merge_txt_menu
)

set "PARTLIST="
for /f "delims=" %%P in ('dir /b /a-d /o:n "!MERGE_PREFIX!.part*.txt" 2^>nul') do (
    if defined PARTLIST (
        set "PARTLIST=!PARTLIST!+"%%P""
    ) else (
        set "PARTLIST="%%P""
    )
)

echo.
echo [*] Dang ghep cac phan cua "!MERGE_PREFIX!" thanh "!MERGE_OUTPUT!" ...
copy /b !PARTLIST! "!MERGE_OUTPUT!" >nul

if !errorlevel! neq 0 (
    echo.
    echo [THAT BAI] Co loi xay ra khi ghep file!
    echo Nhan phim bat ky de tiep tuc...
    pause >nul
    goto :merge_txt_menu
)

echo.
echo ==========================================================
echo [THANH CONG] Da ghep xong file: !MERGE_OUTPUT!
echo ==========================================================

:post_action_merge
echo.
echo Hay chon thao tac tiep theo:
echo   [D] Giai ma ^(Decode^) file vua ghep ve file nen goc ngay bay gio
echo   [B] Quay lai menu chon bo file
echo   [H] Quay ve trang chu (Menu chinh)
echo   [0] Thoat chuong trinh
echo ==========================================================
choice /c DBH0 /n /m "Bam phim lua chon [D/B/H/0]: "
set "act=!errorlevel!"

if "!act!"=="1" (
    set "SELECTED_FILE=!MERGE_OUTPUT!"
    set "BASE_NAME=!MERGE_PREFIX!"
    goto :detect_and_decode
)
if "!act!"=="2" goto :merge_txt_menu
if "!act!"=="3" goto :main_menu
if "!act!"=="4" goto :exit_script
goto :post_action_merge

rem ==========================================================
rem 4. CHUYEN DOI .TXT THANH FILE NEN GOC (DECODE)
rem ==========================================================
:txt_to_compress_menu
cls
echo ==========================================================
echo        CHUYEN DOI: .TXT ==^> FILE NEN GOC (DECODE)
echo ==========================================================
echo.

set "count=0"
for /f "delims=" %%F in ('dir /b /a-d "*.txt" 2^>nul') do (
    set /a count+=1
    set "file_!count!=%%F"
    set "filename_!count!=%%~nF"
)

if !count!==0 (
    echo [THONG BAO] Khong tim thay file .txt nao trong thu muc:
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

echo Danh sach file .txt tim thay:
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

:detect_and_decode
rem Kiem tra xem ten file co chua duoi nen goc khong (vi du: Data_20260909_120000.7z)
for %%A in ("!BASE_NAME!") do set "INNER_EXT=%%~xA"

set "IS_KNOWN=0"
if /i "!INNER_EXT!"==".zip" set "IS_KNOWN=1"
if /i "!INNER_EXT!"==".7z" set "IS_KNOWN=1"
if /i "!INNER_EXT!"==".rar" set "IS_KNOWN=1"
if /i "!INNER_EXT!"==".tar" set "IS_KNOWN=1"
if /i "!INNER_EXT!"==".gz" set "IS_KNOWN=1"
if /i "!INNER_EXT!"==".tgz" set "IS_KNOWN=1"
if /i "!INNER_EXT!"==".bz2" set "IS_KNOWN=1"
if /i "!INNER_EXT!"==".xz" set "IS_KNOWN=1"
if /i "!INNER_EXT!"==".cab" set "IS_KNOWN=1"
if /i "!INNER_EXT!"==".iso" set "IS_KNOWN=1"

if "!IS_KNOWN!"=="1" (
    set "OUTPUT_FILE=!BASE_NAME!"
    goto :execute_decode
)

rem Neu ten file khong chua duoi nen, cho nguoi dung chon dinh dang can giai ma
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
if "!ext_choice!"=="5" goto :txt_to_compress_menu

:execute_decode
echo.
echo [*] Dang giai ma "!SELECTED_FILE!" sang "!OUTPUT_FILE!" ...
certutil -f -decode "!SELECTED_FILE!" "!OUTPUT_FILE!" >nul 2>&1

if !errorlevel! neq 0 (
    echo.
    echo [THAT BAI] Co loi xay ra khi giai ma file!
    echo (Luu y: File .txt can phai la dinh dang ma hoa CertUtil Base64 hop le)
    echo Nhan phim bat ky de tiep tuc...
    pause >nul
    goto :txt_to_compress_menu
)

echo.
echo ==========================================================
echo [THANH CONG] Da khoi phuc file nen thanh cong!
echo   - File goc   : !SELECTED_FILE!
echo   - File output: !OUTPUT_FILE!
echo ==========================================================

:post_action_compress
echo.
echo Hay chon thao tac tiep theo:
echo   [C] Copy duong dan file va mo thu muc
echo   [B] Quay lai menu chon file .txt
echo   [H] Quay ve trang chu (Menu chinh)
echo   [0] Thoat chuong trinh
echo ==========================================================
choice /c CBH0 /n /m "Bam phim lua chon [C/B/H/0]: "
set "act=!errorlevel!"

if "!act!"=="1" (
    powershell -NoProfile -Command "Set-Clipboard -Value '%cd%\!OUTPUT_FILE!'" >nul 2>&1
    explorer /select,"!OUTPUT_FILE!"
    echo.
    echo [OK] Da copy duong dan file "!OUTPUT_FILE!" vao Clipboard va mo Explorer!
    goto :post_action_compress
)
if "!act!"=="2" goto :txt_to_compress_menu
if "!act!"=="3" goto :main_menu
if "!act!"=="4" goto :exit_script
goto :post_action_compress

rem ==========================================================
rem THOAT CHUONG TRINH
rem ==========================================================
:exit_script
cls
echo Tam biet!
exit /b 0
 