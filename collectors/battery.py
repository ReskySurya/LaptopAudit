"""
Collector: Battery — status, kapasitas, health.
"""
import platform
import subprocess
import os
import time


def _run_cmd(cmd: str) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=15
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _get_windows_battery() -> dict:
    """Ambil data baterai di Windows via powercfg battery report XML."""
    info = {
        "has_battery": False,
        "percent": "N/A",
        "charging_status": "N/A",
        "design_capacity_wh": "N/A",
        "full_charge_capacity_wh": "N/A",
        "health_percent": "N/A",
    }

    # Cek apakah ada baterai via WMI
    bat_check = _run_cmd(
        'powershell -Command "(Get-CimInstance Win32_Battery).EstimatedChargeRemaining"'
    )
    if not bat_check or bat_check.lower() == "none":
        return info

    info["has_battery"] = True
    info["percent"] = f"{bat_check}%"

    # Charging status
    bat_status = _run_cmd(
        'powershell -Command "(Get-CimInstance Win32_Battery).BatteryStatus"'
    )
    if bat_status == "2":
        info["charging_status"] = "Sedang charging"
    else:
        info["charging_status"] = "Tidak charging"

    # Battery report via powercfg
    tmp_xml = os.path.join(os.environ.get("TEMP", "."), f"bat_audit_{os.getpid()}.xml")
    try:
        subprocess.run(
            f'powercfg /batteryreport /XML /OUTPUT "{tmp_xml}"',
            shell=True, capture_output=True, timeout=10
        )
        time.sleep(1)

        if os.path.exists(tmp_xml):
            import xml.etree.ElementTree as ET
            tree = ET.parse(tmp_xml)
            root = tree.getroot()

            # Cari namespace
            ns = ""
            if root.tag.startswith("{"):
                ns = root.tag.split("}")[0] + "}"

            batteries = root.find(f"{ns}Batteries")
            if batteries is not None:
                battery = batteries.find(f"{ns}Battery")
                if battery is not None:
                    dc_el = battery.find(f"{ns}DesignCapacity")
                    fc_el = battery.find(f"{ns}FullChargeCapacity")

                    dc = int(dc_el.text) if dc_el is not None and dc_el.text else 0
                    fc = int(fc_el.text) if fc_el is not None and fc_el.text else 0

                    if dc > 0 and fc > 0:
                        info["design_capacity_wh"] = f"{round(dc / 1000, 2)} Wh"
                        info["full_charge_capacity_wh"] = f"{round(fc / 1000, 2)} Wh"
                        info["health_percent"] = f"{round((fc / dc) * 100, 2)}%"

            os.remove(tmp_xml)
    except Exception:
        if os.path.exists(tmp_xml):
            try:
                os.remove(tmp_xml)
            except OSError:
                pass

    return info


def _get_darwin_battery() -> dict:
    """Ambil data baterai di macOS via ioreg."""
    info = {
        "has_battery": False,
        "percent": "N/A",
        "charging_status": "N/A",
        "design_capacity_wh": "N/A",
        "full_charge_capacity_wh": "N/A",
        "health_percent": "N/A",
    }

    ioreg = _run_cmd("ioreg -r -c AppleSmartBattery")
    if not ioreg:
        return info

    info["has_battery"] = True

    def _extract(key: str) -> str:
        for line in ioreg.splitlines():
            if f'"{key}"' in line:
                parts = line.split("=")
                if len(parts) >= 2:
                    return parts[-1].strip()
        return ""

    dc = _extract("DesignCapacity")
    fc = _extract("MaxCapacity")
    curr = _extract("CurrentCapacity")
    volt = _extract("Voltage")
    charging = _extract("IsCharging")

    try:
        dc_val = int(dc)
        fc_val = int(fc)
        volt_val = int(volt)

        if dc_val > 0 and volt_val > 0:
            info["design_capacity_wh"] = f"{round((dc_val * volt_val) / 1_000_000, 2)} Wh"
            info["full_charge_capacity_wh"] = f"{round((fc_val * volt_val) / 1_000_000, 2)} Wh"
            info["health_percent"] = f"{round((fc_val / dc_val) * 100, 2)}%"

        if curr and fc_val > 0:
            pct = round((int(curr) / fc_val) * 100)
            info["percent"] = f"{pct}%"
    except (ValueError, ZeroDivisionError):
        pass

    info["charging_status"] = "Sedang charging" if charging == "Yes" else "Tidak charging"
    return info


def _get_linux_battery() -> dict:
    """Ambil data baterai di Linux via upower atau /sys."""
    info = {
        "has_battery": False,
        "percent": "N/A",
        "charging_status": "N/A",
        "design_capacity_wh": "N/A",
        "full_charge_capacity_wh": "N/A",
        "health_percent": "N/A",
    }

    # Coba upower
    bat_path = _run_cmd("upower -e | grep BAT")
    if bat_path:
        upower_info = _run_cmd(f"upower -i {bat_path}")
        if upower_info:
            info["has_battery"] = True
            for line in upower_info.splitlines():
                line = line.strip()
                if "percentage:" in line:
                    info["percent"] = line.split(":")[-1].strip()
                elif "energy-full-design:" in line:
                    info["design_capacity_wh"] = line.split(":")[-1].strip()
                elif "energy-full:" in line and "design" not in line:
                    info["full_charge_capacity_wh"] = line.split(":")[-1].strip()
                elif "state:" in line:
                    info["charging_status"] = line.split(":")[-1].strip()

            # Hitung health
            try:
                dc = float(info["design_capacity_wh"].split()[0])
                fc = float(info["full_charge_capacity_wh"].split()[0])
                if dc > 0:
                    info["health_percent"] = f"{round((fc / dc) * 100, 1)}%"
            except (ValueError, IndexError):
                pass

    return info


def get_battery_info() -> dict:
    """
    Kumpulkan informasi baterai sesuai OS.

    Returns:
        dict: has_battery, percent, charging_status,
              design_capacity_wh, full_charge_capacity_wh, health_percent
    """
    system = platform.system()
    if system == "Windows":
        return _get_windows_battery()
    elif system == "Darwin":
        return _get_darwin_battery()
    else:
        return _get_linux_battery()
