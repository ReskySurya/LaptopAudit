"""
Collector: Hardware — CPU, RAM, Storage.
"""
import platform
import psutil


def get_cpu_info() -> dict:
    """
    Ambil informasi CPU.

    Returns:
        dict: cpu_name, cpu_cores (fisik), cpu_threads (logis)
    """
    cpu_name = platform.processor() or "Unknown"

    # Di Windows, platform.processor() sering terlalu singkat,
    # coba ambil dari psutil atau environment
    if platform.system() == "Windows":
        import os
        env_cpu = os.environ.get("PROCESSOR_IDENTIFIER", "")
        if env_cpu:
            cpu_name = env_cpu

        # Coba WMI untuk nama lengkap
        try:
            import subprocess
            result = subprocess.run(
                'powershell -Command "(Get-CimInstance Win32_Processor | Select-Object -First 1).Name"',
                shell=True, capture_output=True, text=True, timeout=10
            )
            if result.stdout.strip():
                cpu_name = result.stdout.strip()
        except Exception:
            pass

    return {
        "cpu_name": cpu_name,
        "cpu_cores": psutil.cpu_count(logical=False) or "Unknown",
        "cpu_threads": psutil.cpu_count(logical=True) or "Unknown",
    }


def get_ram_info() -> dict:
    """
    Ambil informasi RAM.

    Returns:
        dict: ram_total_gb (float, 2 desimal)
    """
    mem = psutil.virtual_memory()
    ram_gb = round(mem.total / (1024 ** 3), 2)
    return {"ram_total_gb": ram_gb}


def get_storage_info() -> list:
    """
    Ambil informasi storage per partisi.

    Returns:
        list of dict: drive, total_gb, used_gb, free_gb, percent_used
    """
    partitions = psutil.disk_partitions(all=False)
    storage = []

    for part in partitions:
        try:
            usage = psutil.disk_usage(part.mountpoint)
            storage.append({
                "drive": part.device,
                "mountpoint": part.mountpoint,
                "fstype": part.fstype,
                "total_gb": round(usage.total / (1024 ** 3), 2),
                "used_gb": round(usage.used / (1024 ** 3), 2),
                "free_gb": round(usage.free / (1024 ** 3), 2),
                "percent_used": usage.percent,
            })
        except (PermissionError, OSError):
            continue

    return storage
