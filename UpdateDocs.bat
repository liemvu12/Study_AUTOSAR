<# :
@echo off
setlocal
chcp 65001 >nul
cd /d "%~dp0"
powershell -NoProfile -ExecutionPolicy Bypass -Command "$f = [System.IO.File]::ReadAllText('%~f0', [System.Text.Encoding]::UTF8); & ([ScriptBlock]::Create($f))"
set SCRIPT_EXIT_CODE=%ERRORLEVEL%
if %SCRIPT_EXIT_CODE% neq 0 (
    echo.
    echo [THONG BAO] Script ket thuc voi ma thoat: %SCRIPT_EXIT_CODE%
)
echo.
echo Nhan phim bat ky de dong cua so...
pause >nul
exit /b %SCRIPT_EXIT_CODE%
#>

# ==============================================================================
# AUTOSAR DOCS SYNC & PUSH TOOL
# Tự động chọn file zip trong Backup, giải nén, so sánh (diff) với thư mục docs,
# cập nhật file mới / thay đổi, và commit & push lên GitHub với ngày update.
# ==============================================================================

[Console]::OutputEncoding = [System.Text.Encoding]::UTF8
try {
    $Host.UI.RawUI.WindowTitle = "AUTOSAR - Đồng Bộ Docs Từ Backup Lên GitHub"
} catch {}

Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "        CÔNG CỤ CẬP NHẬT THƯ MỤC DOCS TỪ FILE ZIP BACKUP              " -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host ""

# 1. Kiểm tra công cụ Git
$gitCmd = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCmd) {
    Write-Host "[LỖI] Không tìm thấy lệnh 'git' trong hệ thống. Vui lòng cài đặt Git!" -ForegroundColor Red
    exit 1
}

# 2. Xác định thư mục Git Repo, Backup và Docs
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

$backupDir = Join-Path $repoRoot "BackUp"
if (-not (Test-Path $backupDir)) {
    $backupDir = Join-Path $repoRoot "Backup"
}
$docsDir = Join-Path $repoRoot "docs"

if (-not (Test-Path $backupDir)) {
    Write-Host "[LỖI] Không tìm thấy thư mục Backup tại: $backupDir" -ForegroundColor Red
    exit 1
}

if (-not (Test-Path $docsDir)) {
    Write-Host "[CẢNH BÁO] Thư mục docs chưa tồn tại, sẽ được tạo mới tại: $docsDir" -ForegroundColor Yellow
    New-Item -ItemType Directory -Path $docsDir -Force | Out-Null
}

Write-Host "[*] Thư mục dự án  : $repoRoot" -ForegroundColor Gray
Write-Host "[*] Thư mục Backup : $backupDir" -ForegroundColor Gray
Write-Host "[*] Thư mục docs   : $docsDir" -ForegroundColor Gray
Write-Host ""

# 3. Quét danh sách file zip trong thư mục Backup
$zipFiles = Get-ChildItem -Path $backupDir -Filter "*.zip" | Sort-Object LastWriteTime -Descending

if (-not $zipFiles -or $zipFiles.Count -eq 0) {
    Write-Host "[THÔNG BÁO] Không tìm thấy file .zip nào trong thư mục Backup!" -ForegroundColor Yellow
    exit 0
}

Write-Host "Tìm thấy $($zipFiles.Count) file zip trong thư mục Backup:" -ForegroundColor White
for ($i = 0; $i -lt $zipFiles.Count; $i++) {
    $z = $zipFiles[$i]
    $sizeKb = [Math]::Round($z.Length / 1KB, 1)
    $dateStr = $z.LastWriteTime.ToString("yyyy-MM-dd HH:mm:ss")
    $tag = if ($i -eq 0) { " [Mới nhất]" } else { "" }
    $color = if ($i -eq 0) { "Green" } else { "Gray" }
    Write-Host "  [$($i + 1)] $($z.Name) ($sizeKb KB - $dateStr)$tag" -ForegroundColor $color
}
Write-Host "  [0] Thoát chương trình" -ForegroundColor DarkGray
Write-Host ""

# 4. Người dùng chọn file zip
$selectedIndex = 0
while ($true) {
    $prompt = "Chọn file zip cần cập nhật [Nhấn Enter chọn 1, hoặc nhập 0 để thoát]: "
    $inputChoice = Read-Host $prompt
    $inputChoice = $inputChoice.Trim()

    if ([string]::IsNullOrEmpty($inputChoice) -or $inputChoice -eq "1") {
        $selectedIndex = 0
        break
    } elseif ($inputChoice -eq "0" -or $inputChoice.ToUpper() -eq "Q") {
        Write-Host "Đã hủy thao tác." -ForegroundColor Yellow
        exit 0
    } else {
        $parsedNum = 0
        if ([int]::TryParse($inputChoice, [ref]$parsedNum) -and $parsedNum -ge 1 -and $parsedNum -le $zipFiles.Count) {
            $selectedIndex = $parsedNum - 1
            break
        } else {
            Write-Host "[!] Lựa chọn không hợp lệ, vui lòng nhập số từ 1 đến $($zipFiles.Count) hoặc 0 để thoát!" -ForegroundColor Red
        }
    }
}

$chosenZip = $zipFiles[$selectedIndex]
Write-Host ""
Write-Host "======================================================================" -ForegroundColor Cyan
Write-Host "[*] Đã chọn: $($chosenZip.Name)" -ForegroundColor Cyan
Write-Host "======================================================================" -ForegroundColor Cyan

# 5. Giải nén vào thư mục tạm thời
$tempExtract = Join-Path $env:TEMP ("autosar_docs_update_" + [System.Guid]::NewGuid().ToString("N"))
Write-Host "[*] Đang giải nén file zip vào thư mục tạm..." -ForegroundColor Gray

Add-Type -AssemblyName System.IO.Compression.FileSystem

try {
    [System.IO.Compression.ZipFile]::ExtractToDirectory($chosenZip.FullName, $tempExtract)

    # Nhận diện cấu trúc thư mục nguồn
    $srcDocsDir = $tempExtract
    $nestedDocs = Join-Path $tempExtract "docs"
    if (Test-Path $nestedDocs) {
        $srcDocsDir = $nestedDocs
    }

    Write-Host "[*] Thư mục nguồn sau giải nén: $srcDocsDir" -ForegroundColor Gray
    Write-Host "[*] Đang phân tích và so sánh (diff) với thư mục docs hiện tại..." -ForegroundColor Gray
    Write-Host ""

    # Hàm tính SHA-256
    function Get-FileSha256($filePath) {
        $sha = [System.Security.Cryptography.SHA256]::Create()
        $stream = [System.IO.File]::OpenRead($filePath)
        try {
            $hashBytes = $sha.ComputeHash($stream)
            return [System.BitConverter]::ToString($hashBytes) -replace '-'
        } finally {
            $stream.Dispose()
            $sha.Dispose()
        }
    }

    # 6. So sánh chi tiết từng file
    $srcFiles = Get-ChildItem -Path $srcDocsDir -Recurse -File
    $newFiles = @()
    $modifiedFiles = @()
    $unchangedFiles = @()

    foreach ($file in $srcFiles) {
        # Lấy relative path
        $relPath = $file.FullName.Substring($srcDocsDir.Length).TrimStart('\', '/')
        $targetFilePath = Join-Path $docsDir $relPath

        if (-not (Test-Path $targetFilePath)) {
            $newFiles += [PSCustomObject]@{
                RelPath  = $relPath
                SrcFile  = $file.FullName
                DestFile = $targetFilePath
                Size     = $file.Length
            }
        } else {
            $targetItem = Get-Item $targetFilePath
            if ($targetItem.Length -ne $file.Length) {
                $modifiedFiles += [PSCustomObject]@{
                    RelPath  = $relPath
                    SrcFile  = $file.FullName
                    DestFile = $targetFilePath
                    OldSize  = $targetItem.Length
                    NewSize  = $file.Length
                }
            } else {
                $srcHash = Get-FileSha256 $file.FullName
                $targetHash = Get-FileSha256 $targetFilePath
                if ($srcHash -ne $targetHash) {
                    $modifiedFiles += [PSCustomObject]@{
                        RelPath  = $relPath
                        SrcFile  = $file.FullName
                        DestFile = $targetFilePath
                        OldSize  = $targetItem.Length
                        NewSize  = $file.Length
                    }
                } else {
                    $unchangedFiles += $relPath
                }
            }
        }
    }

    # 7. Báo cáo kết quả Diff
    Write-Host "===================== BẢNG SO SÁNH (DIFF) ============================" -ForegroundColor Cyan
    Write-Host "  Tổng số file trong bản sao lưu: $($srcFiles.Count)"
    Write-Host "  - File tạo mới (New)         : $($newFiles.Count)" -ForegroundColor Green
    Write-Host "  - File đã thay đổi (Modified): $($modifiedFiles.Count)" -ForegroundColor Yellow
    Write-Host "  - File không đổi (Unchanged) : $($unchangedFiles.Count)" -ForegroundColor Gray
    Write-Host "======================================================================" -ForegroundColor Cyan
    Write-Host ""

    if ($newFiles.Count -gt 0) {
        Write-Host "--- DANH SÁCH FILE MỚI SẼ ĐƯỢC TẠO ($($newFiles.Count)) ---" -ForegroundColor Green
        foreach ($nf in $newFiles) {
            Write-Host "  [+] $($nf.RelPath) ($([Math]::Round($nf.Size / 1KB, 1)) KB)" -ForegroundColor Green
        }
        Write-Host ""
    }

    if ($modifiedFiles.Count -gt 0) {
        Write-Host "--- DANH SÁCH FILE ĐÃ THAY ĐỔI NỘI DUNG ($($modifiedFiles.Count)) ---" -ForegroundColor Yellow
        foreach ($mf in $modifiedFiles) {
            Write-Host "  [~] $($mf.RelPath) ($($mf.OldSize) B -> $($mf.NewSize) B)" -ForegroundColor Yellow
        }
        Write-Host ""
    }

    $totalChanges = $newFiles.Count + $modifiedFiles.Count
    if ($totalChanges -eq 0) {
        Write-Host "[THÀNH CÔNG] Thư mục docs đã hoàn toàn khớp với bản backup!" -ForegroundColor Green
        Write-Host "Không có file nào cần cập nhật hay push." -ForegroundColor Green
        return
    }

    # 8. Xác nhận copy & commit & push
    $confirm = Read-Host "Phát hiện $totalChanges file khác biệt. Tiến hành COPY sang docs và PUSH lên GitHub? (Y/N) [Mặc định Y]"
    if (-not [string]::IsNullOrWhiteSpace($confirm) -and $confirm.Trim().ToUpper() -ne "Y") {
        Write-Host "Đã hủy cập nhật theo yêu cầu người dùng." -ForegroundColor Yellow
        return
    }

    # 9. Thực hiện copy các file
    Write-Host ""
    Write-Host "[*] Đang sao chép các file vào thư mục docs..." -ForegroundColor Cyan
    $copiedCount = 0
    foreach ($item in ($newFiles + $modifiedFiles)) {
        $destDir = Split-Path -Parent $item.DestFile
        if (-not (Test-Path $destDir)) {
            New-Item -ItemType Directory -Path $destDir -Force | Out-Null
        }
        Copy-Item -Path $item.SrcFile -Destination $item.DestFile -Force
        $copiedCount++
    }
    Write-Host "[OK] Đã sao chép thành công $copiedCount file vào $docsDir" -ForegroundColor Green
    Write-Host ""

    # 10. Git Add docs, Commit với ngày update & Push
    Write-Host "[*] Đang kiểm tra trạng thái Git..." -ForegroundColor Cyan
    $gitStatus = git status --porcelain docs
    if (-not $gitStatus) {
        Write-Host "[THÔNG BÁO] Git không phát hiện thay đổi nào trong docs sau khi copy." -ForegroundColor Yellow
        return
    }

    Write-Host "[*] Đang thực hiện: git add docs ..." -ForegroundColor Gray
    git add docs

    # Ngày update hiện tại (yyyy-MM-dd)
    $updateDate = (Get-Date).ToString("yyyy-MM-dd")
    $commitMsg = "Update docs - $updateDate"

    Write-Host "[*] Đang tạo Git Commit: '$commitMsg' ..." -ForegroundColor Cyan
    git commit -m "$commitMsg"

    # Lấy nhánh hiện tại
    $currentBranch = (git rev-parse --abbrev-ref HEAD 2>$null)
    if ($currentBranch) { $currentBranch = $currentBranch.Trim() }
    if (-not $currentBranch) { $currentBranch = "main" }

    Write-Host "[*] Đang push lên GitHub (origin/$currentBranch)..." -ForegroundColor Cyan
    git push origin $currentBranch

    if ($LASTEXITCODE -eq 0) {
        Write-Host ""
        Write-Host "======================================================================" -ForegroundColor Green
        Write-Host "  [THÀNH CÔNG] ĐÃ CẬP NHẬT VÀ PUSH LÊN GITHUB HOÀN TẤT!              " -ForegroundColor Green
        Write-Host "  Commit: $commitMsg                                                 " -ForegroundColor Green
        Write-Host "  Branch: $currentBranch                                             " -ForegroundColor Green
        Write-Host "======================================================================" -ForegroundColor Green
    } else {
        Write-Host ""
        Write-Host "[LỖI] Quá trình 'git push' thất bại (Mã lỗi: $LASTEXITCODE)!" -ForegroundColor Red
        Write-Host "Vui lòng kiểm tra kết nối mạng hoặc thông tin xác thực GitHub." -ForegroundColor Yellow
    }

} catch {
    Write-Host ""
    Write-Host "[LỖI NGOẠI LỆ] $($_.Exception.Message)" -ForegroundColor Red
} finally {
    # 11. Dọn dẹp thư mục tạm
    if ($tempExtract -and (Test-Path $tempExtract)) {
        Remove-Item -Path $tempExtract -Recurse -Force -ErrorAction SilentlyContinue
    }
}