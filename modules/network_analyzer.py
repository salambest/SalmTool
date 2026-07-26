"""
Network Analyzer module.

Reports local networking information: IP address, DNS servers, default
gateway, active network interfaces, and a simple ping test utility.
"""

import socket
import subprocess
import platform as py_platform

try:
    import psutil
except ImportError:
    psutil = None


def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(1)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return None


def get_hostname():
    try:
        return socket.gethostname()
    except Exception:
        return None


def get_network_interfaces():
    if not psutil:
        return {}
    interfaces = {}
    try:
        for name, addrs in psutil.net_if_addrs().items():
            ipv4 = next((a.address for a in addrs if a.family == socket.AF_INET), None)
            if ipv4:
                interfaces[name] = ipv4
    except Exception:
        pass
    return interfaces


def get_gateway():
    system = py_platform.system().lower()
    try:
        if system in ("linux", "android"):
            with open("/proc/net/route") as f:
                for line in f.readlines()[1:]:
                    fields = line.strip().split()
                    if len(fields) >= 3 and fields[1] == "00000000":
                        gw_hex = fields[2]
                        return ".".join(str(int(gw_hex[i:i + 2], 16)) for i in (6, 4, 2, 0))
        elif system == "windows":
            out = subprocess.check_output("ipconfig", text=True, errors="ignore")
            for line in out.splitlines():
                if "Default Gateway" in line and ":" in line:
                    val = line.split(":")[-1].strip()
                    if val:
                        return val
    except Exception:
        pass
    return None


def get_dns_servers():
    servers = []
    try:
        with open("/etc/resolv.conf") as f:
            for line in f:
                if line.startswith("nameserver"):
                    servers.append(line.split()[1])
    except Exception:
        pass
    return servers


def ping_host(host="8.8.8.8", count=4):
    system = py_platform.system().lower()
    count_flag = "-n" if system == "windows" else "-c"
    try:
        proc = subprocess.run(
            ["ping", count_flag, str(count), host],
            capture_output=True, text=True, timeout=count * 2 + 5
        )
        return {"success": proc.returncode == 0, "output": proc.stdout or proc.stderr}
    except Exception as e:
        return {"success": False, "output": str(e)}


def get_full_report():
    return {
        "hostname": get_hostname(),
        "local_ip": get_local_ip(),
        "gateway": get_gateway(),
        "dns_servers": get_dns_servers(),
        "interfaces": get_network_interfaces(),
    }
