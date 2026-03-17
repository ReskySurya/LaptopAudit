"""
Collector: Software — daftar aplikasi yang terinstall.
"""
import platform
import subprocess


def _run_cmd(cmd: str) -> str:
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, text=True, timeout=30
        )
        return result.stdout.strip()
    except Exception:
        return ""


def _get_windows_software() -> list:
    """Ambil daftar software dari Windows Registry (3 paths)."""
    ps_script = """
        $paths = @(
            'HKLM:\\Software\\Wow6432Node\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',
            'HKLM:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*',
            'HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall\\*'
        )
        Get-ItemProperty $paths -ErrorAction SilentlyContinue |
            Where-Object { $_.DisplayName -and $_.DisplayName.Trim() -ne '' } |
            Select-Object -ExpandProperty DisplayName |
            Sort-Object -Unique
    """
    try:
        result = subprocess.run(
            ["powershell", "-Command", ps_script],
            capture_output=True, text=True, timeout=30
        )
        out = result.stdout.strip()
        if out:
            return [line.strip() for line in out.splitlines() if line.strip()]
    except Exception:
        pass
    return ["Gagal mengambil daftar software"]


def _get_darwin_software() -> list:
    """Ambil daftar software di macOS dari /Applications + brew."""
    apps = []

    # /Applications
    out = _run_cmd("ls /Applications 2>/dev/null")
    if out:
        for name in out.splitlines():
            name = name.strip()
            if name.endswith(".app"):
                name = name[:-4]
            if name:
                apps.append(name)

    # Homebrew
    brew_formula = _run_cmd("brew list --formula 2>/dev/null")
    if brew_formula:
        for name in brew_formula.splitlines():
            if name.strip():
                apps.append(f"[brew] {name.strip()}")

    brew_cask = _run_cmd("brew list --cask 2>/dev/null")
    if brew_cask:
        for name in brew_cask.splitlines():
            if name.strip():
                apps.append(f"[cask] {name.strip()}")

    return sorted(set(apps)) if apps else ["Tidak ada aplikasi terdeteksi"]


def _get_linux_software() -> list:
    """Ambil daftar software di Linux dari package manager."""
    # dpkg (Debian/Ubuntu)
    out = _run_cmd("dpkg --get-selections 2>/dev/null | awk '$2==\"install\"{print $1}' | sort")
    if out:
        return [l.strip() for l in out.splitlines() if l.strip()]

    # rpm (Fedora/RHEL)
    out = _run_cmd("rpm -qa --qf '%{NAME}\\n' 2>/dev/null | sort")
    if out:
        return [l.strip() for l in out.splitlines() if l.strip()]

    # pacman (Arch)
    out = _run_cmd("pacman -Qq 2>/dev/null | sort")
    if out:
        return [l.strip() for l in out.splitlines() if l.strip()]

    return ["Package manager tidak terdeteksi"]


def get_installed_software() -> list:
    """
    Kumpulkan daftar software terinstall sesuai OS.

    Returns:
        list of str: Nama-nama software, sorted.
    """
    system = platform.system()
    if system == "Windows":
        return _get_windows_software()
    elif system == "Darwin":
        return _get_darwin_software()
    else:
        return _get_linux_software()
