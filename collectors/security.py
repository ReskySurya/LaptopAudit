"""
Collector: Security — Firewall status, Antivirus info.
"""
import platform
import subprocess


def _run_cmd(cmd: str) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=10
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _get_windows_security() -> dict:
    """Ambil status firewall dan antivirus di Windows."""
    info = {
        "firewall_status": "Unknown",
        "antivirus_name": "Unknown",
        "antivirus_status": "Unknown",
    }

    # Firewall
    fw = _run_cmd(
        'powershell -Command "'
        '$fw = Get-NetFirewallProfile -ErrorAction SilentlyContinue; '
        'if ($fw) { ($fw | ForEach-Object { \\"$($_.Name): $($_.Enabled)\\" }) -join \\", \\" } '
        'else { \\"Unknown\\" }'
        '"'
    )
    if fw:
        info["firewall_status"] = fw

    # Antivirus (Windows Defender)
    av = _run_cmd(
        'powershell -Command "'
        '$av = Get-MpComputerStatus -ErrorAction SilentlyContinue; '
        'if ($av) { \\"Windows Defender - RealTimeProtection: $($av.RealTimeProtectionEnabled)\\" } '
        'else { \\"Unknown\\" }'
        '"'
    )
    if av and "Unknown" not in av:
        info["antivirus_name"] = "Windows Defender"
        info["antivirus_status"] = av
    else:
        # Coba via WMI SecurityCenter2
        av2 = _run_cmd(
            'powershell -Command "'
            'Get-CimInstance -Namespace root/SecurityCenter2 -ClassName AntiVirusProduct '
            '-ErrorAction SilentlyContinue | '
            'Select-Object -ExpandProperty displayName'
            '"'
        )
        if av2:
            names = [n.strip() for n in av2.splitlines() if n.strip()]
            info["antivirus_name"] = ", ".join(names)
            info["antivirus_status"] = "Terdeteksi"

    return info


def _get_darwin_security() -> dict:
    """Ambil status firewall di macOS."""
    info = {
        "firewall_status": "Unknown",
        "antivirus_name": "XProtect (built-in)",
        "antivirus_status": "Active (macOS default)",
    }

    fw = _run_cmd("defaults read /Library/Preferences/com.apple.alf globalstate 2>/dev/null")
    if fw:
        states = {"0": "Off", "1": "On (specific services)", "2": "On (block all)"}
        info["firewall_status"] = states.get(fw, f"State: {fw}")

    return info


def _get_linux_security() -> dict:
    """Ambil status firewall di Linux."""
    info = {
        "firewall_status": "Unknown",
        "antivirus_name": "N/A",
        "antivirus_status": "N/A",
    }

    # ufw
    fw = _run_cmd("sudo ufw status 2>/dev/null || ufw status 2>/dev/null")
    if fw:
        info["firewall_status"] = fw.splitlines()[0] if fw.splitlines() else fw
    else:
        # iptables
        ipt = _run_cmd("sudo iptables -L -n --line-numbers 2>/dev/null | head -5")
        if ipt:
            info["firewall_status"] = "iptables active"

    # ClamAV
    clam = _run_cmd("clamscan --version 2>/dev/null")
    if clam:
        info["antivirus_name"] = "ClamAV"
        info["antivirus_status"] = clam

    return info


def get_security_status() -> dict:
    """
    Kumpulkan informasi keamanan (Firewall, Antivirus) sesuai OS.

    Returns:
        dict: firewall_status, antivirus_name, antivirus_status
    """
    system = platform.system()
    if system == "Windows":
        return _get_windows_security()
    elif system == "Darwin":
        return _get_darwin_security()
    else:
        return _get_linux_security()
