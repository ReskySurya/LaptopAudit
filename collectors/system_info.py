"""
Collector: Informasi Sistem (OS, hostname, vendor, model, serial number).
"""
import platform
import subprocess
import re


def _run_cmd(cmd: str, shell: bool = True) -> str:
    """Jalankan command dan return stdout, atau string kosong jika gagal."""
    try:
        result = subprocess.run(
            cmd, shell=shell, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _get_windows_info() -> dict:
    """Ambil info sistem di Windows via WMI/CIM."""
    info = {
        "os_name": "Unknown",
        "os_build": "Unknown",
        "vendor": "Unknown",
        "model": "Unknown",
        "serial_number": "Unknown",
    }

    # OS
    out = _run_cmd('powershell -Command "(Get-CimInstance Win32_OperatingSystem).Caption"')
    if out:
        info["os_name"] = out
    out = _run_cmd('powershell -Command "(Get-CimInstance Win32_OperatingSystem).BuildNumber"')
    if out:
        info["os_build"] = out

    # Vendor & Model
    out = _run_cmd('powershell -Command "(Get-CimInstance Win32_ComputerSystem).Manufacturer"')
    if out:
        info["vendor"] = out
    out = _run_cmd('powershell -Command "(Get-CimInstance Win32_ComputerSystem).Model"')
    if out:
        info["model"] = out

    # Serial Number
    out = _run_cmd('powershell -Command "(Get-CimInstance Win32_BIOS).SerialNumber"')
    if out:
        info["serial_number"] = out

    return info


def _get_darwin_info() -> dict:
    """Ambil info sistem di macOS."""
    info = {
        "os_name": "Unknown",
        "os_build": "Unknown",
        "vendor": "Apple",
        "model": "Unknown",
        "serial_number": "Unknown",
    }

    ver = _run_cmd("sw_vers -productVersion")
    build = _run_cmd("sw_vers -buildVersion")
    if ver:
        info["os_name"] = f"macOS {ver}"
    if build:
        info["os_build"] = build

    profiler = _run_cmd("system_profiler SPHardwareDataType")
    if profiler:
        for line in profiler.splitlines():
            if "Model Name" in line:
                info["model"] = line.split(":")[-1].strip()
            elif "Serial Number" in line:
                info["serial_number"] = line.split(":")[-1].strip()

    return info


def _get_linux_info() -> dict:
    """Ambil info sistem di Linux."""
    info = {
        "os_name": "Unknown",
        "os_build": "Unknown",
        "vendor": "Unknown",
        "model": "Unknown",
        "serial_number": "Unknown",
    }

    # OS name
    out = _run_cmd("lsb_release -d")
    if out:
        info["os_name"] = out.split(":")[-1].strip() if ":" in out else out
    else:
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME"):
                        info["os_name"] = line.split("=")[1].strip().strip('"')
                        break
        except FileNotFoundError:
            info["os_name"] = platform.platform()

    info["os_build"] = platform.release()

    # Vendor & Model via DMI (biasanya readable tanpa sudo)
    dmi_map = {
        "vendor": "/sys/class/dmi/id/sys_vendor",
        "model": "/sys/class/dmi/id/product_name",
    }
    for key, path in dmi_map.items():
        try:
            with open(path) as f:
                val = f.read().strip()
                if val:
                    info[key] = val
        except (FileNotFoundError, PermissionError):
            pass

    # Serial Number — perlu fallback chain karena biasanya butuh root/sudo
    serial_path = "/sys/class/dmi/id/product_serial"
    try:
        with open(serial_path) as f:
            val = f.read().strip()
            if val:
                info["serial_number"] = val
    except (FileNotFoundError, PermissionError):
        # Fallback 1: sudo cat
        val = _run_cmd(f"sudo cat {serial_path} 2>/dev/null")
        if val:
            info["serial_number"] = val
        else:
            # Fallback 2: sudo dmidecode
            val = _run_cmd("sudo dmidecode -s system-serial-number 2>/dev/null")
            if val:
                info["serial_number"] = val

    return info


def get_system_info() -> dict:
    """
    Kumpulkan informasi sistem secara otomatis.

    Returns:
        dict dengan keys: hostname, username, os_name, os_build,
                          vendor, model, serial_number
    """
    system = platform.system()

    base = {
        "hostname": platform.node(),
        "username": "",
    }

    # Username
    import getpass
    try:
        base["username"] = getpass.getuser()
    except Exception:
        base["username"] = "Unknown"

    # OS-specific info
    if system == "Windows":
        os_info = _get_windows_info()
    elif system == "Darwin":
        os_info = _get_darwin_info()
    else:
        os_info = _get_linux_info()

    base.update(os_info)
    return base
