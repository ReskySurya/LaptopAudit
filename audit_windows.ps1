# ============================================================
#  LAPTOP ASSET AUDIT — Windows
#  Jangan dijalankan langsung — gunakan file JALANKAN_AUDIT.bat
# ============================================================

$ErrorActionPreference = "SilentlyContinue"

trap {
    Write-Host ""
    Write-Host "  [!] Terjadi error: $_" -ForegroundColor Red
    Write-Host ""
    Write-Host "  Tekan Enter untuk menutup..." -ForegroundColor Gray
    Read-Host
    exit 1
}

Set-Location $PSScriptRoot

Clear-Host
Write-Host ""
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host "     LAPTOP ASSET AUDIT" -ForegroundColor Cyan
Write-Host "  ================================================" -ForegroundColor Cyan
Write-Host ""

do { $asset = (Read-Host "  Masukkan Kode Asset (mis. LP-130)").Trim() } while ($asset -eq "")
do { $pic   = (Read-Host "  Masukkan Nama PIC Asset").Trim()           } while ($pic -eq "")

Write-Host ""
Write-Host "  [1/5] Mengambil informasi sistem..." -ForegroundColor Yellow

$tanggal      = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
$hostname_str = $env:COMPUTERNAME
$username_str = $env:USERNAME

try {
    $cs       = Get-CimInstance Win32_ComputerSystem
    $os_obj   = Get-CimInstance Win32_OperatingSystem
    $cpu_obj  = Get-CimInstance Win32_Processor | Select-Object -First 1
    $bios_obj = Get-CimInstance Win32_BIOS
    $os_name  = $os_obj.Caption
    $os_build = $os_obj.BuildNumber
    $vendor   = $cs.Manufacturer
    $model    = $cs.Model
    $serial   = $bios_obj.SerialNumber
    $cpu_name = $cpu_obj.Name
    $cores    = $cpu_obj.NumberOfCores
    $threads  = $cpu_obj.NumberOfLogicalProcessors
    $ram_gb   = [math]::Round($cs.TotalPhysicalMemory / 1GB, 2)
} catch {
    $os_name  = "Unknown"
    $os_build = "Unknown"
    $vendor   = "Unknown"
    $model    = "Unknown"
    $serial   = "Unknown"
    $cpu_name = $env:PROCESSOR_IDENTIFIER
    $cores    = $env:NUMBER_OF_PROCESSORS
    $threads  = $cores
    $ram_gb   = "Unknown"
}

$storage_lines = @()
try {
    Get-PSDrive -PSProvider FileSystem | Where-Object { $_.Used -ne $null -and $_.Root -match '^[A-Z]:\\$' } | ForEach-Object {
        $total = [math]::Round(($_.Used + $_.Free) / 1GB, 2)
        $used  = [math]::Round($_.Used / 1GB, 2)
        $free  = [math]::Round($_.Free / 1GB, 2)
        $storage_lines += "$($_.Name): Total $total GB | Digunakan $used GB | Bebas $free GB"
    }
} catch {}
$storage_str = if ($storage_lines.Count -gt 0) { $storage_lines -join "`n               " } else { "Unknown" }

try {
    $ip_list = (Get-NetIPAddress -AddressFamily IPv4 | Where-Object { $_.IPAddress -notlike "127.*" -and $_.IPAddress -notlike "169.*" }).IPAddress
    $ip_str  = if ($ip_list) { ($ip_list -join ", ") } else { "Unknown" }
    $mac_list = (Get-NetAdapter | Where-Object { $_.Status -eq "Up" }).MacAddress
    $mac_str  = if ($mac_list) { ($mac_list -join ", ") } else { "Unknown" }
} catch {
    $ip_str  = "Unknown"
    $mac_str = "Unknown"
}

Write-Host "  [2/5] Mengambil data baterai..." -ForegroundColor Yellow

$bat_pct     = "Tidak ada baterai"
$bat_charge  = "N/A"
$bat_design  = "N/A"
$bat_current = "N/A"
$bat_health  = "N/A"

try {
    $battery = Get-CimInstance Win32_Battery
    if ($battery) {
        $bat_pct    = "$($battery.EstimatedChargeRemaining)%"
        $bat_charge = if ($battery.BatteryStatus -eq 2) { "Sedang charging" } else { "Tidak charging" }

        $tmp_xml = "$env:TEMP\bat_audit_$PID.xml"
        & powercfg /batteryreport /XML /OUTPUT $tmp_xml 2>$null
        Start-Sleep -Milliseconds 800

        if (Test-Path $tmp_xml) {
            [xml]$xml = Get-Content $tmp_xml -Encoding UTF8
            $bat_node = $xml.BatteryReport.Batteries.Battery
            if ($bat_node) {
                $dc = [int]$bat_node.DesignCapacity
                $fc = [int]$bat_node.FullChargeCapacity
                if ($dc -gt 0 -and $fc -gt 0) {
                    $bat_design  = "$([math]::Round($dc / 1000, 2)) Wh"
                    $bat_current = "$([math]::Round($fc / 1000, 2)) Wh"
                    $bat_health  = "$([math]::Round(($fc / $dc) * 100, 2))%"
                }
            }
            Remove-Item $tmp_xml -Force
        }
    }
} catch {}

Write-Host "  [3/5] Mengambil daftar software..." -ForegroundColor Yellow

$software_str = ""
try {
    $reg_paths = @(
        "HKLM:\Software\Wow6432Node\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*",
        "HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall\*"
    )
    $sw_list = Get-ItemProperty $reg_paths -ErrorAction SilentlyContinue |
        Where-Object { $_.DisplayName -and $_.DisplayName.Trim() -ne "" } |
        Select-Object -ExpandProperty DisplayName |
        Sort-Object -Unique
    $software_str = $sw_list -join "`n"
} catch {
    $software_str = "Gagal mengambil daftar software"
}

Write-Host "  [4/5] Menyimpan laporan..." -ForegroundColor Yellow

$filename    = "asset_${asset}.txt"
$output_path = Join-Path $PSScriptRoot $filename

$report = @"
=== LAPORAN PENGECEKAN LAPTOP ===

Tanggal        : $tanggal
Kode Asset     : $asset
PIC Asset      : $pic

=== INFORMASI SISTEM ===

Hostname       : $hostname_str
Username       : $username_str
OS             : $os_name (Build $os_build)
Vendor         : $vendor
Model          : $model
Serial Number  : $serial

CPU            : $cpu_name
CPU Cores      : $cores core / $threads thread
RAM            : $ram_gb GB
Storage        : $storage_str

IP Address     : $ip_str
MAC Address    : $mac_str

=== BATTERY ===

Battery (%)      : $bat_pct
Charging Status  : $bat_charge
Design Capacity  : $bat_design
Current Max Cap  : $bat_current
Battery Health   : $bat_health

=== SOFTWARE INSTALLED ===

$software_str
"@

$report | Out-File -FilePath $output_path -Encoding UTF8

Write-Host "  [5/5] Membuka review di browser..." -ForegroundColor Yellow

$html_path = Join-Path $PSScriptRoot "laptop_audit.html"
if (Test-Path $html_path) {
    Start-Process ("file:///" + $html_path.Replace("\", "/"))
}

Write-Host ""
Write-Host "  ================================================" -ForegroundColor Green
Write-Host "  SELESAI! Laporan tersimpan di:" -ForegroundColor Green
Write-Host "  $output_path" -ForegroundColor White
Write-Host "  ================================================" -ForegroundColor Green
Write-Host ""
Write-Host "  Tekan Enter untuk menutup..." -ForegroundColor Gray
Read-Host
