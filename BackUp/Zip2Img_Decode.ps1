<#
    Zip2Img_Decode.ps1
    Doc lai du lieu pixel tu anh PNG (duoc tao boi Zip2Img_Encode.ps1), giai ma Base64
    va ghi lai file nen (zip, 7z, rar, ...) ve dung nguyen ban goc.
#>
param(
    [Parameter(Mandatory=$true)][string]$InputImage,
    [Parameter(Mandatory=$true)][string]$OutputFile
)

$ErrorActionPreference = 'Stop'

try {
    if (-not (Test-Path -LiteralPath $InputImage)) {
        Write-Host "[LOI] Khong tim thay file anh: $InputImage"
        exit 1
    }

    Add-Type -AssemblyName System.Drawing

    Write-Host "[*] Dang doc file anh..."
    $srcBmp = New-Object System.Drawing.Bitmap($InputImage)
    $width = $srcBmp.Width
    $height = $srcBmp.Height

    # Dam bao dung dinh dang 24bpp RGB giong luc encode
    $bmp = $srcBmp.Clone((New-Object System.Drawing.Rectangle(0,0,$width,$height)), [System.Drawing.Imaging.PixelFormat]::Format24bppRgb)
    $srcBmp.Dispose()

    $rect = New-Object System.Drawing.Rectangle(0, 0, $width, $height)
    $bmpData = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadOnly, $bmp.PixelFormat)

    $stride = $bmpData.Stride
    $rowBytes = $width * 3
    $buffer = New-Object byte[] ($width * $height * 3)

    Write-Host "[*] Dang doc du lieu tu pixel anh..."
    for ($y = 0; $y -lt $height; $y++) {
        $srcPtr = [IntPtr]::Add($bmpData.Scan0, $y * $stride)
        $destOffset = $y * $rowBytes
        [System.Runtime.InteropServices.Marshal]::Copy($srcPtr, $buffer, $destOffset, $rowBytes)
    }

    $bmp.UnlockBits($bmpData)
    $bmp.Dispose()

    $headerStr = [System.Text.Encoding]::ASCII.GetString($buffer, 0, 10)
    $b64Len = [int]$headerStr

    Write-Host "[*] Dang giai ma Base64..."
    $b64Str = [System.Text.Encoding]::ASCII.GetString($buffer, 10, $b64Len)
    $fileBytes = [Convert]::FromBase64String($b64Str)

    [System.IO.File]::WriteAllBytes($OutputFile, $fileBytes)

    $outSize = (Get-Item -LiteralPath $OutputFile).Length

    Write-Host ""
    Write-Host "[THANH CONG]"
    Write-Host "  - File anh      : $InputImage"
    Write-Host "  - File khoi phuc: $OutputFile ($([math]::Round($outSize/1MB,2)) MB)"
    exit 0
}
catch {
    Write-Host ""
    Write-Host "[LOI] $($_.Exception.Message)"
    exit 1
}
