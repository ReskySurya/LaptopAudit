"""
Collector: Network — IP address, MAC address.
"""
import psutil
import socket


def get_network_info() -> dict:
    """
    Ambil IP dan MAC address dari interface yang aktif.

    Returns:
        dict: ip_addresses (list), mac_addresses (list)
    """
    ip_addresses = []
    mac_addresses = []

    try:
        addrs = psutil.net_if_addrs()
        stats = psutil.net_if_stats()

        for iface, addr_list in addrs.items():
            # Skip loopback dan interface yang down
            if iface.lower().startswith("lo"):
                continue
            if iface in stats and not stats[iface].isup:
                continue

            for addr in addr_list:
                # IPv4
                if addr.family == socket.AF_INET:
                    ip = addr.address
                    if not ip.startswith("127.") and not ip.startswith("169.254."):
                        ip_addresses.append(ip)
                # MAC
                elif addr.family == psutil.AF_LINK:
                    mac = addr.address
                    if mac and mac != "00:00:00:00:00:00" and mac != "":
                        mac_addresses.append(mac)
    except Exception:
        pass

    return {
        "ip_addresses": ip_addresses if ip_addresses else ["Unknown"],
        "mac_addresses": mac_addresses if mac_addresses else ["Unknown"],
    }
