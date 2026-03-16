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
    CORES=$(nproc --all 2>/dev/null || grep -c ^processor /proc/cpuinfo 2>/dev/null || echo "Unknown")
    THREADS=$CORES
    RAM_KB=$(grep MemTotal /proc/meminfo 2>/dev/null | awk '{print $2}')
    RAM_GB=$(echo "scale=2; $RAM_KB / 1048576" | bc 2>/dev/null || echo "Unknown")
fi

# ---- Storage ----
STORAGE_INFO=$(df -h --output=source,size,used,avail,target 2>/dev/null | grep "^/" | \
    awk '{printf "%s: Total %s | Used %s | Free %s | Mount %s\n", $1, $2, $3, $4, $5}' || \
    df -h 2>/dev/null | grep "^/" | awk '{printf "%s: Total %s | Used %s | Free %s | Mount %s\n", $1, $2, $3, $4, $5}')

# ---- IP & MAC ----
if [ "$OS_TYPE" = "Darwin" ]; then
    IP_ADDRESS=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "Unknown")
    MAC_ADDRESS=$(ifconfig en0 2>/dev/null | awk '/ether/{print $2}' || echo "Unknown")
else
    IP_ADDRESS=$(hostname -I 2>/dev/null | awk '{print $1}' || ip route get 1 2>/dev/null | awk '{print $7}' || echo "Unknown")
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
        FC=$(echo "$IOREG" | grep '"MaxCapacity" = '    | awk '{print $3}')
        CURR=$(echo "$IOREG" | grep '"CurrentCapacity" = ' | awk '{print $3}')
        VOLT=$(echo "$IOREG" | grep '"Voltage" = '     | awk '{print $3}')
        CHARG=$(echo "$IOREG" | grep '"IsCharging" = '  | awk '{print $3}')

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
    BAT_PATH="/sys/class/power_supply/BAT0"
    if [ ! -d "$BAT_PATH" ]; then BAT_PATH="/sys/class/power_supply/BAT1"; fi
    if [ -d "$BAT_PATH" ]; then
        [ -f "$BAT_PATH/capacity" ] && BAT_PCT="$(cat $BAT_PATH/capacity)%"
        [ -f "$BAT_PATH/status"   ] && BAT_STATUS=$(cat $BAT_PATH/status)

        if [ -f "$BAT_PATH/energy_full_design" ] && [ -f "$BAT_PATH/energy_full" ]; then
            DC=$(cat $BAT_PATH/energy_full_design)
            FC=$(cat $BAT_PATH/energy_full)
            BAT_DESIGN=$(echo "scale=2; $DC / 1000000" | bc)
            BAT_CURRENT=$(echo "scale=2; $FC / 1000000" | bc)
            BAT_DESIGN="${BAT_DESIGN} Wh"
            BAT_CURRENT="${BAT_CURRENT} Wh"
            if [ "$DC" -gt 0 ]; then
                BAT_HEALTH=$(echo "scale=2; ($FC * 100) / $DC" | bc)
                BAT_HEALTH="${BAT_HEALTH}%"
            fi
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

cat > "$OUTPUT_PATH" << EOF
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
RAM            : $RAM_GB GB
Storage        :
$STORAGE_INFO

IP Address     : $IP_ADDRESS
MAC Address    : $MAC_ADDRESS

=== BATTERY ===

Battery (%)      : $BAT_PCT
Charging Status  : $BAT_STATUS
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
