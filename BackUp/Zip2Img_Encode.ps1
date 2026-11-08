<#
    Zip2Img_Encode.ps1
    Ma hoa 1 file bat ky (zip, 7z, rar, ...) sang Base64, nhung Base64 duoi dang byte
    truc tiep vao du lieu pixel cua 1 anh PNG (khong qua render chu, nen khong mat du lieu).
#>
param(
    [Parameter(Mandatory=$true)][string]$InputFile,
    [Parameter(Mandatory=$true)][string]$OutputImage
)

$ErrorActionPreference = 'Stop'

try {
    if (-not (Test-Path -LiteralPath $InputFile)) {
        Write-Host "[LOI] Khong tim thay file: $InputFile"
        exit 1
    }

    Write-Host "[*] Dang doc file goc..."
    $bytes = [System.IO.File]::ReadAllBytes($InputFile)
    $origSize = $bytes.Length

    Write-Host "[*] Dang ma hoa Base64 ($([math]::Round($origSize/1MB,2)) MB)..."
    $b64 = [Convert]::ToBase64String($bytes)

    # Header: 10 chu so dau tien luu do dai chuoi Base64, de decode biet diem cat bo phan padding
    $header = $b64.Length.ToString().PadLeft(10,'0')
    $combined = $header + $b64
    $asciiBytes = [System.Text.Encoding]::ASCII.GetBytes($combined)
    $totalChars = $asciiBytes.Length

    # Tinh kich thuoc anh gan vuong nhat co the, moi pixel chua 3 byte (R,G,B)
    $pixelsNeeded = [math]::Ceiling($totalChars / 3.0)
    $width = [int][math]::Ceiling([math]::Sqrt($pixelsNeeded))
    if ($width -lt 1) { $width = 1 }
    $height = [int][math]::Ceiling($pixelsNeeded / $width)
    $totalBytesAvailable = $width * $height * 3

    Write-Host "[*] Kich thuoc anh: $width x $height pixel"

    $padded = New-Object byte[] $totalBytesAvailable
    [Array]::Copy($asciiBytes, $padded, $asciiBytes.Length)

    Add-Type -AssemblyName System.Drawing

    $bmp = New-Object System.Drawing.Bitmap($width, $height, [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
    $rect = New-Object System.Drawing.Rectangle(0, 0, $width, $height)
    $bmpData = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::WriteOnly, $bmp.PixelFormat)

    $stride = $bmpData.Stride
    $rowBytes = $width * 3

    Write-Host "[*] Dang ghi du lieu vao pixel anh..."
    for ($y = 0; $y -lt $height; $y++) {
        $srcOffset = $y * $rowBytes
        $destPtr = [IntPtr]::Add($bmpData.Scan0, $y * $stride)
        [System.Runtime.InteropServices.Marshal]::Copy($padded, $srcOffset, $destPtr, $rowBytes)
    }

    $bmp.UnlockBits($bmpData)

    Write-Host "[*] Dang luu file anh PNG..."
    $bmp.Save($OutputImage, [System.Drawing.Imaging.ImageFormat]::Png)
    $bmp.Dispose()

    $imgSize = (Get-Item -LiteralPath $OutputImage).Length

    Write-Host ""
    Write-Host "[THANH CONG]"
    Write-Host "  - File goc : $InputFile ($([math]::Round($origSize/1MB,2)) MB)"
    Write-Host "  - File anh : $OutputImage ($([math]::Round($imgSize/1MB,2)) MB)"
    exit 0
}
catch {
    Write-Host ""
    Write-Host "[LOI] $($_.Exception.Message)"
    exit 1
}
