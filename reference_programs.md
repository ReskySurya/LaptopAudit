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


#!/bin/bash
# ============================================================
#  LAPTOP ASSET AUDIT — macOS / Linux
#  Cara pakai: Buka Terminal > bash audit_unix.sh
#  atau: chmod +x audit_unix.sh && ./audit_unix.sh
# ============================================================

# Warna output
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
GREEN='\033[0;32m'
GRAY='\033[0;37m'
NC='\033[0m'

clear
echo ""
echo -e "${CYAN}================================================${NC}"
echo -e "${CYAN}   LAPTOP ASSET AUDIT${NC}"
echo -e "${CYAN}================================================${NC}"
echo ""
read -p "  Masukkan Kode Asset (mis. LP-130) : " ASSET
read -p "  Masukkan Nama PIC Asset           : " PIC
echo ""
echo -e "${YELLOW}  Mengumpulkan data sistem...${NC}"

# ---- Tanggal ----
TANGGAL=$(date "+%Y-%m-%d %H:%M:%S")

# ---- Deteksi OS ----
OS_TYPE=$(uname -s)
HOSTNAME_STR=$(hostname)
USERNAME_STR=$(whoami)

# ---- Info OS ----
if [ "$OS_TYPE" = "Darwin" ]; then
    OS_NAME="macOS $(sw_vers -productVersion) ($(sw_vers -buildVersion))"
    VENDOR="Apple"
    MODEL=$(system_profiler SPHardwareDataType 2>/dev/null | awk -F': ' '/Model Name/{print $2}' | xargs)
    SERIAL=$(system_profiler SPHardwareDataType 2>/dev/null | awk -F': ' '/Serial Number/{print $2}' | xargs)
    CPU=$(sysctl -n machdep.cpu.brand_string 2>/dev/null || system_profiler SPHardwareDataType | awk -F': ' '/Chip/{print $2}')
    CORES=$(sysctl -n hw.physicalcpu 2>/dev/null || echo "Unknown")
    THREADS=$(sysctl -n hw.logicalcpu 2>/dev/null || echo "Unknown")
    RAM_BYTES=$(sysctl -n hw.memsize 2>/dev/null)
    RAM_GB=$(echo "scale=2; $RAM_BYTES / 1073741824" | bc 2>/dev/null || echo "Unknown")
else
    # Linux
    OS_NAME=$(lsb_release -d 2>/dev/null | cut -f2 || cat /etc/os-release 2>/dev/null | grep PRETTY_NAME | cut -d'"' -f2 || uname -sr)
    VENDOR=$(cat /sys/class/dmi/id/sys_vendor 2>/dev/null || dmidecode -s system-manufacturer 2>/dev/null || echo "Unknown")
    MODEL=$(cat /sys/class/dmi/id/product_name 2>/dev/null || dmidecode -s system-product-name 2>/dev/null || echo "Unknown")
    SERIAL=$(cat /sys/class/dmi/id/product_serial 2>/dev/null || sudo dmidecode -s system-serial-number 2>/dev/null || echo "Unknown")
    CPU=$(cat /proc/cpuinfo 2>/dev/null | grep "model name" | head -1 | awk -F': ' '{print $2}' || echo "Unknown")
    CORES=$(grep -P '^core id' /proc/cpuinfo | sort -u | wc -l || echo "Unknown")
    THREADS=$(nproc --all 2>/dev/null || grep -c ^processor /proc/cpuinfo 2>/dev/null || echo "Unknown")
    RAM_GB=$(free -h | awk '/Mem:/ {print $2}')
fi

# ---- Storage ----
STORAGE_INFO=$(df -h --output=source,size,used,avail,target 2>/dev/null | grep "^/" |
    awk '{printf "%s: Total %s | Used %s | Free %s | Mount %s\n", $1, $2, $3, $4, $5}' ||
    df -h 2>/dev/null | grep "^/" | awk '{printf "%s: Total %s | Used %s | Free %s | Mount %s\n", $1, $2, $3, $4, $5}')

# ---- IP & MAC ----
if [ "$OS_TYPE" = "Darwin" ]; then
    IP_ADDRESS=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "Unknown")
    MAC_ADDRESS=$(ifconfig en0 2>/dev/null | awk '/ether/{print $2}' || echo "Unknown")
else
    IP_ADDRESS=$(hostname -i 2>/dev/null | awk '{print $1}' || ip route get 1 2>/dev/null | awk '{print $7}' || echo "Unknown")
    MAC_ADDRESS=$(ip link show 2>/dev/null | awk '/ether/{print $2}' | head -1 || cat /sys/class/net/*/address 2>/dev/null | head -1 || echo "Unknown")
fi

# ---- Baterai ----
echo -e "${YELLOW}  Mengambil data baterai...${NC}"

BAT_PCT="Tidak ada baterai"
BAT_DESIGN="N/A"
BAT_CURRENT="N/A"
BAT_HEALTH="N/A"
BAT_STATUS="N/A"

if [ "$OS_TYPE" = "Darwin" ]; then
    IOREG=$(ioreg -r -c AppleSmartBattery 2>/dev/null)
    if [ -n "$IOREG" ]; then
        DC=$(echo "$IOREG" | grep '"DesignCapacity" = ' | awk '{print $3}')
        FC=$(echo "$IOREG" | grep '"MaxCapacity" = ' | awk '{print $3}')
        CURR=$(echo "$IOREG" | grep '"CurrentCapacity" = ' | awk '{print $3}')
        VOLT=$(echo "$IOREG" | grep '"Voltage" = ' | awk '{print $3}')
        CHARG=$(echo "$IOREG" | grep '"IsCharging" = ' | awk '{print $3}')

        if [ -n "$DC" ] && [ -n "$FC" ] && [ -n "$VOLT" ]; then
            BAT_DESIGN=$(echo "scale=2; ($DC * $VOLT) / 1000000" | bc)
            BAT_CURRENT=$(echo "scale=2; ($FC * $VOLT) / 1000000" | bc)
            BAT_DESIGN="${BAT_DESIGN} Wh"
            BAT_CURRENT="${BAT_CURRENT} Wh"
        fi
        if [ -n "$DC" ] && [ -n "$FC" ] && [ "$DC" -gt 0 ]; then
            BAT_HEALTH=$(echo "scale=2; ($FC * 100) / $DC" | bc)
            BAT_HEALTH="${BAT_HEALTH}%"
        fi
        if [ -n "$CURR" ] && [ -n "$FC" ] && [ "$FC" -gt 0 ]; then
            BAT_PCT=$(echo "scale=0; ($CURR * 100) / $FC" | bc)
            BAT_PCT="${BAT_PCT}%"
        fi
        BAT_STATUS=$([ "$CHARG" = "Yes" ] && echo "Sedang charging" || echo "Tidak charging")
    fi
else
    # Linux
    BAT=$(upower -i $(upower -e | grep 'BAT'))

    if [ -n "$BAT" ]; then
        INFO=$(upower -i "$BAT")

        BAT_PCT=$(echo "$INFO" | awk -F: '/percentage/ {gsub(/ /,"",$2); print $2}')
        BAT_DESIGN=$(echo "$INFO" | awk -F: '/energy-full-design/ {gsub(/^ +/,"",$2); print $2}')
        BAT_CURRENT=$(echo "$INFO" | awk -F: '/energy-full:/ {gsub(/^ +/,"",$2); print $2}')
        BAT_STATUS=$(echo "$INFO" | awk -F: '/state/ {gsub(/^ +/,"",$2); print $2}')

        DESIGN_NUM=$(echo "$BAT_DESIGN" | awk '{print $1}')
        CURRENT_NUM=$(echo "$BAT_CURRENT" | awk '{print $1}')

        if [[ -n "$DESIGN_NUM" && -n "$CURRENT_NUM" ]]; then
            BAT_HEALTH=$(awk "BEGIN {printf \"%.1f%%\", ($CURRENT_NUM/$DESIGN_NUM)*100}")
        else
            BAT_HEALTH="N/A"
        fi
    fi
fi

# ---- Software ----
echo -e "${YELLOW}  Mengambil daftar software...${NC}"

if [ "$OS_TYPE" = "Darwin" ]; then
    SOFTWARE=$(ls /Applications 2>/dev/null | sed 's/\.app$//' | sort)
    # Tambah Homebrew jika ada
    if command -v brew &>/dev/null; then
        BREW_LIST=$(brew list --formula 2>/dev/null | sort)
        BREW_CASK=$(brew list --cask 2>/dev/null | sort)
        SOFTWARE="${SOFTWARE}
--- Homebrew Formulae ---
${BREW_LIST}
--- Homebrew Cask ---
${BREW_CASK}"
    fi
else
    # Linux - coba berbagai package manager
    if command -v dpkg &>/dev/null; then
        SOFTWARE=$(dpkg --get-selections 2>/dev/null | awk '$2=="install"{print $1}' | sort)
    elif command -v rpm &>/dev/null; then
        SOFTWARE=$(rpm -qa --qf '%{NAME}\n' 2>/dev/null | sort)
    elif command -v pacman &>/dev/null; then
        SOFTWARE=$(pacman -Qq 2>/dev/null | sort)
    else
        SOFTWARE="Package manager tidak terdeteksi"
    fi
fi

# ---- Tulis file .txt ----
echo -e "${YELLOW}  Menyimpan laporan...${NC}"

FILENAME="asset_${ASSET}.txt"
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
OUTPUT_PATH="${SCRIPT_DIR}/${FILENAME}"

cat >"$OUTPUT_PATH" <<EOF
=== LAPORAN PENGECEKAN LAPTOP ===

Tanggal        : $TANGGAL
Kode Asset     : $ASSET
PIC Asset      : $PIC

=== INFORMASI SISTEM ===

Hostname       : $HOSTNAME_STR
Username       : $USERNAME_STR
OS             : $OS_NAME
Vendor         : $VENDOR
Model          : $MODEL
Serial Number  : $SERIAL

CPU            : $CPU
CPU Cores      : $CORES core / $THREADS thread
RAM            : $RAM_GB
Storage        :
$STORAGE_INFO

IP Address     : $IP_ADDRESS
MAC Address    : $MAC_ADDRESS

=== BATTERY ===

Battery (%)      : $BAT_PCT
Design Capacity  : $BAT_DESIGN
Current Max Cap  : $BAT_CURRENT
Battery Health   : $BAT_HEALTH

=== SOFTWARE INSTALLED ===

$SOFTWARE
EOF

# ---- Buka web app untuk review ----
HTML_PATH="${SCRIPT_DIR}/laptop_audit.html"
if [ -f "$HTML_PATH" ]; then
    if [ "$OS_TYPE" = "Darwin" ]; then
        open "$HTML_PATH" 2>/dev/null
    else
        xdg-open "$HTML_PATH" 2>/dev/null || sensible-browser "$HTML_PATH" 2>/dev/null || true
    fi
fi

# ---- Selesai ----
echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}  SELESAI!${NC}"
echo -e "${GREEN}  File laporan: ${OUTPUT_PATH}${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""