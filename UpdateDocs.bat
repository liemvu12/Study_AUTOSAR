<# :
@echo off
setlocal
chcp 65001 >nul
title 1-Click Git Sync ^& Auto Push (Study_AUTOSAR)
cd /d "%~dp0"
set "USER_ARGS=%*"
powershell -NoProfile -ExecutionPolicy Bypass -Command "Invoke-Expression ([System.IO.File]::ReadAllText('%~f0', [System.Text.Encoding]::UTF8))"
set SCRIPT_EXIT_CODE=%ERRORLEVEL%
if %SCRIPT_EXIT_CODE% neq 0 (
    echo.
    echo [THONG BAO] Script ket thuc voi ma loi: %SCRIPT_EXIT_CODE%
)
echo.
echo Nhan phim bat ky de dong cua so nay...
pause >nul
exit /b %SCRIPT_EXIT_CODE%
#>

# ==============================================================================
# AUTOSAR 1-CLICK GIT SYNC & AUTO PUSH TOOL
# Tự động:
#   1. Quét và stage toàn bộ thay đổi (git add -A), bao gồm docs, .agents, tools,
#      BackUp, myProject, source code và các file cấu hình.
#   2. Thống kê chi tiết các tệp thay đổi (New, Modified, Deleted).
#   3. Tự động commit với thông điệp ngày giờ hoặc thông điệp người dùng truyền vào.
#   4. Tự động push lên nhánh hiện tại trên GitHub trong 1 cú click.
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
try {
    $Host.UI.RawUI.WindowTitle = "Study_AUTOSAR - 1-Click Git Add, Commit & Push"
} catch {}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "         1-CLICK GIT SYNC & AUTO PUSH (Study_AUTOSAR)                 " -ForegroundColor Cyan
Write-Host "   Tự động Git Add (docs, .agents, tools...) + Commit + Push          " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Kiểm tra Git trong hệ thống
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-Host "[LỖI NGHIÊM TRỌNG] Không tìm thấy lệnh 'git' trong hệ thống!" -ForegroundColor Red
    Write-Host "Vui lòng cài đặt Git và đảm bảo Git đã được thêm vào biến môi trường PATH." -ForegroundColor Yellow
    exit 1
}

# 2. Xác định thư mục gốc của Git Repository
$repoRoot = ""
try {
    $repoRoot = (git rev-parse --show-toplevel 2>$null)
    if ($repoRoot) {
        $repoRoot = (Resolve-Path $repoRoot).Path
    }
} catch {}

if (-not $repoRoot -or -not (Test-Path $repoRoot)) {
    $repoRoot = (Get-Location).Path
}

Set-Location $repoRoot
Write-Host "[*] Thư mục dự án    : $repoRoot" -ForegroundColor Gray

# 3. Xác định nhánh Git hiện tại và Remote URL
$currentBranch = (git rev-parse --abbrev-ref HEAD 2>$null)
if ($currentBranch) { $currentBranch = $currentBranch.Trim() }
if (-not $currentBranch -or $currentBranch -eq "HEAD") {
    $currentBranch = "main"
}

$remotes = @(git remote 2>$null)
$remoteName = "origin"
if ($remotes.Count -gt 0 -and (-not [string]::IsNullOrWhiteSpace($remotes[0]))) {
    $remoteName = $remotes[0].Trim()
}

$remoteUrl = (git remote get-url $remoteName 2>$null)
if ($remoteUrl) { $remoteUrl = $remoteUrl.Trim() }

Write-Host "[*] Nhánh hiện tại   : $currentBranch" -ForegroundColor Gray
Write-Host "[*] Remote đích      : $remoteName ($remoteUrl)" -ForegroundColor Gray
Write-Host ""

# 4. Thực hiện git add toàn bộ dự án
Write-Host "[1/3] Đang quét và thêm toàn bộ thay đổi (git add -A)..." -ForegroundColor Cyan
Write-Host "      (Bao gồm: .agents, docs, tools, BackUp, myProject, source code & scripts)" -ForegroundColor DarkGray

git add -A

# 5. Phân tích trạng thái sau khi stage
$statusLines = git status --porcelain 2>$null
$statusList = @()
if ($statusLines) {
    $statusList = $statusLines | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
}

if ($statusList.Count -eq 0) {
    # Kiểm tra xem có commit nào ở local chưa push lên remote không
    $unpushed = git log "$remoteName/$currentBranch..HEAD" --oneline 2>$null
    if ($unpushed) {
        $unpushedList = $unpushed | Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
        Write-Host ""
        Write-Host "[THÔNG BÁO] Không có file sửa đổi mới, nhưng phát hiện $($unpushedList.Count) commit cục bộ chưa push:" -ForegroundColor Yellow
        foreach ($c in $unpushedList) {
            Write-Host "  -> $c" -ForegroundColor Gray
        }
        Write-Host ""
        Write-Host "[3/3] Đang đẩy $($unpushedList.Count) commit lên $remoteName/$currentBranch..." -ForegroundColor Cyan
        git push $remoteName $currentBranch
        if ($LASTEXITCODE -eq 0) {
            Write-Host ""
            Write-Host "======================================================================" -ForegroundColor Green
            Write-Host "  [THÀNH CÔNG] ĐÃ PUSH CÁC COMMIT TỒN ĐỌNG LÊN GITHUB HOÀN TẤT!      " -ForegroundColor Green
            Write-Host "  Nhánh: $currentBranch -> $remoteName/$currentBranch                " -ForegroundColor Green
            Write-Host "======================================================================" -ForegroundColor Green
            exit 0
        } else {
            Write-Host ""
            Write-Host "[LỖI] Quá trình push thất bại (Mã lỗi: $LASTEXITCODE)!" -ForegroundColor Red
            exit $LASTEXITCODE
        }
    }

    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "  [THÔNG BÁO] Kho lưu trữ hoàn toàn sạch sẽ (Clean Working Tree)!     " -ForegroundColor Green
    Write-Host "  Không có bất kỳ file nào thay đổi hoặc cần commit & push.           " -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Green
    exit 0
}

# 6. Thống kê và hiển thị chi tiết các thay đổi
$newCount = 0
$modCount = 0
$delCount = 0

foreach ($line in $statusList) {
    $code = $line.Substring(0, 2)
    if ($code -match "A") { $newCount++ }
    elseif ($code -match "D") { $delCount++ }
    else { $modCount++ }
}

Write-Host ""
Write-Host "===================== BẢNG THỐNG KÊ THAY ĐỔI =========================" -ForegroundColor Cyan
Write-Host "  Tổng số tệp được xử lý : $($statusList.Count)" -ForegroundColor White
Write-Host "  - Tạo mới (New)        : $newCount" -ForegroundColor Green
Write-Host "  - Sửa đổi (Modified)   : $modCount" -ForegroundColor Yellow
Write-Host "  - Đã xóa (Deleted)     : $delCount" -ForegroundColor Red
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "--- CHI TIẾT CÁC FILE ĐƯỢC STAGE ---" -ForegroundColor White
$displayMax = 30
$displayed = 0
foreach ($line in $statusList) {
    $displayed++
    if ($displayed -le $displayMax) {
        $code = $line.Substring(0, 2).Trim()
        $path = $line.Substring(3).Trim()
        $color = "Yellow"
        if ($code -match "A") { $color = "Green" }
        elseif ($code -match "D") { $color = "Red" }
        Write-Host "  [$code] $path" -ForegroundColor $color
    }
}
if ($statusList.Count -gt $displayMax) {
    Write-Host "  ... và $($statusList.Count - $displayMax) file khác." -ForegroundColor Gray
}
Write-Host ""

# 7. Tạo Commit tự động
Write-Host "[2/3] Đang tiến hành Git Commit..." -ForegroundColor Cyan

$customMsg = ""
if ($env:USER_ARGS) {
    $customMsg = $env:USER_ARGS.Trim()
}

$commitDate = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
if (-not [string]::IsNullOrWhiteSpace($customMsg)) {
    $commitMsg = $customMsg
} else {
    $commitMsg = "Update project: docs, .agents, and codebase - $commitDate"
}

Write-Host "[*] Nội dung commit: '$commitMsg'" -ForegroundColor Gray
$commitOutput = git commit -m "$commitMsg" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "[LỖI] Không thể tạo commit!" -ForegroundColor Red
    Write-Host $commitOutput -ForegroundColor Yellow
    exit $LASTEXITCODE
}

$commitHash = (git rev-parse --short HEAD 2>$null)
if ($commitHash) { $commitHash = $commitHash.Trim() }
Write-Host "[OK] Đã tạo commit [$commitHash] thành công." -ForegroundColor Green
Write-Host ""

# 8. Thực hiện Git Push
Write-Host "[3/3] Đang đẩy lên GitHub ($remoteName/$currentBranch)..." -ForegroundColor Cyan
$pushOutput = git push $remoteName $currentBranch 2>&1
$pushCode = $LASTEXITCODE

if ($pushCode -eq 0) {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Green
    Write-Host "  [THÀNH CÔNG] ĐÃ TỰ ĐỘNG STAGE, COMMIT VÀ PUSH LÊN GITHUB HOÀN TẤT!  " -ForegroundColor Green
    Write-Host "  Commit  : [$commitHash] $commitMsg                                  " -ForegroundColor Green
    Write-Host "  Nhánh   : $currentBranch -> $remoteName/$currentBranch              " -ForegroundColor Green
    Write-Host "  Remote  : $remoteUrl                                                " -ForegroundColor Green
    Write-Host "======================================================================" -ForegroundColor Green
    exit 0
} else {
    Write-Host ""
    Write-Host "======================================================================" -ForegroundColor Red
    Write-Host "  [LỖI] QUÁ TRÌNH 'GIT PUSH' THẤT BẠI (Mã lỗi: $pushCode)!            " -ForegroundColor Red
    Write-Host "======================================================================" -ForegroundColor Red
    Write-Host $pushOutput -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Gợi ý khắc phục:" -ForegroundColor Gray
    Write-Host "  1. Kiểm tra kết nối mạng Internet." -ForegroundColor Gray
    Write-Host "  2. Nếu remote có thay đổi mới chưa kéo về, hãy chạy: git pull --rebase" -ForegroundColor Gray
    Write-Host "  3. Kiểm tra quyền truy cập (GitHub Personal Access Token hoặc SSH Key)." -ForegroundColor Gray
    exit $pushCode
}
